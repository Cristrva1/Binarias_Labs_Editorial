#!/usr/bin/env python3
"""
MÓDULO 5: CONTROL DE RIESGO (v3)
===================================
Responsabilidad: actuar como CÁMARA DE SEGURIDAD del sistema.
Todo lo que sale del pipeline pasa por aquí antes de llegar al autor.

Cuatro guardianes (sin LLM — reglas deterministas + LLM para los sutiles):
  1. guardian_alucinaciones   — referencias inventadas, datos no verificables.
  2. guardian_voz_autor       — sugerencias que violan el voz_autor.yaml.
  3. guardian_sobreedicion    — cuando la densidad de cambios es excesiva.
  4. guardian_sesgo_comercial — cuando el diagnóstico editorial se contamina
                                 con lógica de ventas.

Salidas (en m5_control_riesgo/):
  - riesgos_detectados.json
  - recomendaciones_bloqueadas.json
  - informe_control_riesgo.md
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from config_v3 import ProyectoPaths
from schemas_v3 import Hallazgo, RiesgoDetectado, cargar_hallazgos
from llm_router import LLMRouter


# Palabras que delatan lenguaje comercial en diagnóstico editorial
MARCADORES_SESGO_COMERCIAL = [
    "bestseller", "viral", "monetizar", "engagement", "algoritmo",
    "nicho", "buyer persona", "funnel", "conversión", "kpi", "roi",
    "tendencia del mercado", "amazon", "ranking", "ventas estimadas",
]

# Palabras que delatan sobredición (propuestas que reescriben la voz)
MARCADORES_SOBREEDICION = [
    "reescribí", "reescribir", "reemplazá", "sustituí", "cambiá el tono",
    "cambiá la voz", "cambiá completamente", "reformulá", "redactá de nuevo",
    "eliminá este párrafo", "borrá", "suprimí",
]

# Patrones de alucinación: referencias con formato académico en texto editorial
PATRON_REFERENCIA_ACADEMICA = re.compile(
    r"\b(?:según|cita[:\s]+|fuente:|autor:\s+)"
    r"[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)+"
    r"(?:\s*,\s*\d{4})?",
    re.IGNORECASE,
)


class ModuloControlRiesgo:
    """
    Audita el output del pipeline antes de entregarlo al autor.
    """

    # Umbral: si más del X% de hallazgos proponen reescritura directa → alerta
    UMBRAL_SOBREEDICION = 0.25
    # Umbral: más de N marcadores comerciales en toda la salida → alerta
    UMBRAL_SESGO_COMERCIAL = 3

    def __init__(self, paths: ProyectoPaths):
        self.paths = paths
        self.router = LLMRouter()
        self.hallazgos: List[Hallazgo] = []
        self.riesgos: List[RiesgoDetectado] = []
        self.bloqueados: List[str] = []   # IDs de hallazgos bloqueados

    def cargar_insumos(self) -> bool:
        hallazgos_path = self.paths.hallazgos_path()
        if not hallazgos_path.exists():
            print("   [ERROR] hallazgos.json no encontrado.")
            return False
        self.hallazgos = cargar_hallazgos(str(hallazgos_path))
        print(f"   Hallazgos a auditar: {len(self.hallazgos)}")
        return True

    # ─── Guardianes ──────────────────────────────────────────────────────

    def guardian_sobreedicion(self) -> RiesgoDetectado:
        """Detecta si hay demasiadas propuestas de reescritura directa."""
        con_sobreedicion = []
        for h in self.hallazgos:
            propuesta = (h.intervencion_sugerida or "").lower()
            if any(m in propuesta for m in MARCADORES_SOBREEDICION):
                con_sobreedicion.append(h.id)
                self.bloqueados.append(h.id)

        ratio = len(con_sobreedicion) / max(len(self.hallazgos), 1)
        activado = ratio >= self.UMBRAL_SOBREEDICION

        return RiesgoDetectado(
            tipo="sobreedicion",
            activado=activado,
            severidad=4 if activado else 1,
            descripcion=(
                f"El {ratio:.0%} de hallazgos contiene propuestas de reescritura directa "
                f"({len(con_sobreedicion)} de {len(self.hallazgos)}). "
                f"Umbral: {self.UMBRAL_SOBREEDICION:.0%}."
                if activado else
                f"Densidad de reescrituras directas dentro del límite ({ratio:.0%})."
            ),
            hallazgos_afectados=con_sobreedicion,
            recomendacion=(
                "Revisar y reformular las propuestas marcadas para que sean señales, "
                "no reescrituras. La voz del autor no debe tocarse directamente."
                if activado else ""
            ),
        )

    def guardian_sesgo_comercial(self) -> RiesgoDetectado:
        """Detecta lenguaje comercial en el diagnóstico editorial."""
        texto_total = " ".join(
            (h.descripcion or "") + " " + (h.intervencion_sugerida or "")
            for h in self.hallazgos
        ).lower()

        encontrados = [m for m in MARCADORES_SESGO_COMERCIAL if m in texto_total]
        activado = len(encontrados) >= self.UMBRAL_SESGO_COMERCIAL

        return RiesgoDetectado(
            tipo="sesgo_comercial",
            activado=activado,
            severidad=3 if activado else 1,
            descripcion=(
                f"Se detectaron {len(encontrados)} marcadores de sesgo comercial: "
                f"{', '.join(encontrados[:5])}."
                if activado else
                f"Sin sesgo comercial detectado ({len(encontrados)} marcadores)."
            ),
            hallazgos_afectados=[],
            recomendacion=(
                "El diagnóstico editorial no debe hablar de ventas, tendencias ni algoritmos. "
                "Revisar las secciones que contienen estos términos."
                if activado else ""
            ),
        )

    def guardian_voz_autor(self) -> RiesgoDetectado:
        """Detecta propuestas que violaron palabras prohibidas del autor."""
        prohibidas_path = self.paths.proyecto_dir.parent.parent / "Proyectos" / self.paths.libro_id / "voz_autor.yaml"
        palabras_prohibidas: List[str] = []

        # Intentar cargar desde contexto_autor.yaml (M0)
        contexto_path = self.paths.contexto_autor_path()
        if contexto_path.exists():
            try:
                import yaml
                with open(contexto_path, encoding="utf-8") as f:
                    ctx = yaml.safe_load(f) or {}
                no_alterar = (ctx.get("restricciones") or {}).get("no_alterar") or []
                palabras_prohibidas = [str(p).lower() for p in no_alterar[:20]]
            except Exception:
                pass

        if not palabras_prohibidas:
            return RiesgoDetectado(
                tipo="voz_autor",
                activado=False,
                severidad=1,
                descripcion="No se encontraron restricciones de voz en contexto_autor.yaml. Guardián omitido.",
                hallazgos_afectados=[],
                recomendacion="",
            )

        violaciones = []
        for h in self.hallazgos:
            propuesta = (h.intervencion_sugerida or "").lower()
            for palabra in palabras_prohibidas:
                if palabra and palabra in propuesta:
                    violaciones.append(h.id)
                    self.bloqueados.append(h.id)
                    break

        activado = len(violaciones) > 0
        return RiesgoDetectado(
            tipo="voz_autor",
            activado=activado,
            severidad=5 if activado else 1,
            descripcion=(
                f"{len(violaciones)} propuestas usan vocabulario que el autor declaró prohibido."
                if activado else
                "Ninguna propuesta viola el vocabulario prohibido del autor."
            ),
            hallazgos_afectados=violaciones,
            recomendacion=(
                "Las propuestas marcadas deben ser bloqueadas o reformuladas antes de "
                "llegar al autor."
                if activado else ""
            ),
        )

    def guardian_alucinaciones(self) -> RiesgoDetectado:
        """Detecta referencias académicas o datos no verificables usando LLM."""
        texto_muestra = "\n".join(
            f"[{h.id}] {h.descripcion} | {h.intervencion_sugerida}"
            for h in self.hallazgos[:30]
        )

        # Detección determinista rápida
        matches = PATRON_REFERENCIA_ACADEMICA.findall(texto_muestra)

        if not matches:
            return RiesgoDetectado(
                tipo="alucinacion",
                activado=False,
                severidad=1,
                descripcion="Sin referencias académicas o datos inventados detectados.",
                hallazgos_afectados=[],
                recomendacion="",
            )

        # Si hay matches sospechosos, usar LLM para confirmar
        resultado = self.router.chat(
            user_prompt=(
                f"En el siguiente diagnóstico editorial, identificá SOLO los hallazgos que "
                f"contienen referencias a libros, autores, estudios o datos específicos que "
                f"podrían ser inventados (alucinaciones del modelo).\n\n"
                f"Devolvé solo los IDs de los hallazgos sospechosos, como JSON array: "
                f"[\"H-001\", \"H-002\"]. Si no hay ninguno, devolvé []\n\n{texto_muestra}"
            ),
            system="Sos un auditor de alucinaciones de IA. Solo devolvés IDs, nada más.",
            temperature=0.1,
            max_tokens=300,
        )

        sospechosos: List[str] = []
        if resultado.get("success"):
            try:
                contenido = resultado.get("content", "[]")
                inicio = contenido.find("[")
                fin = contenido.rfind("]") + 1
                sospechosos = json.loads(contenido[inicio:fin]) if inicio >= 0 else []
            except Exception:
                pass

        activado = len(sospechosos) > 0
        for h_id in sospechosos:
            self.bloqueados.append(h_id)

        return RiesgoDetectado(
            tipo="alucinacion",
            activado=activado,
            severidad=4 if activado else 1,
            descripcion=(
                f"{len(sospechosos)} hallazgos con posibles referencias inventadas: {sospechosos}"
                if activado else "Sin alucinaciones detectadas."
            ),
            hallazgos_afectados=sospechosos,
            recomendacion=(
                "Verificar manualmente los hallazgos marcados antes de compartirlos con el autor."
                if activado else ""
            ),
        )

    # ─── Guardado ────────────────────────────────────────────────────────

    def guardar_resultados(self) -> bool:
        self.paths.m5_control_riesgo.mkdir(parents=True, exist_ok=True)

        riesgos_data = [r.to_dict() for r in self.riesgos]
        ruta_riesgos = self.paths.riesgos_detectados_path()
        with open(ruta_riesgos, "w", encoding="utf-8") as f:
            json.dump(
                {"libro_id": self.paths.libro_id, "riesgos": riesgos_data},
                f, indent=2, ensure_ascii=False,
            )
        print(f"   riesgos_detectados.json guardado.")

        bloqueados_unicos = list(dict.fromkeys(self.bloqueados))
        ruta_bloqueadas = self.paths.recomendaciones_bloqueadas_path()
        with open(ruta_bloqueadas, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "libro_id": self.paths.libro_id,
                    "total_bloqueadas": len(bloqueados_unicos),
                    "ids_bloqueados": bloqueados_unicos,
                },
                f, indent=2, ensure_ascii=False,
            )
        print(f"   recomendaciones_bloqueadas.json guardado ({len(bloqueados_unicos)} bloqueadas).")
        return True

    def generar_informe(self) -> bool:
        lineas = [
            f"# Informe de Control de Riesgo — {self.paths.libro_id}\n",
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n",
        ]
        activados = [r for r in self.riesgos if r.activado]
        lineas.append(
            f"\n**{len(activados)}/{len(self.riesgos)} guardianes activados. "
            f"{len(self.bloqueados)} recomendaciones bloqueadas.**\n"
        )
        for r in self.riesgos:
            icono = "🔴" if r.activado else "✅"
            lineas.append(f"\n## {icono} Guardián: {r.tipo.replace('_', ' ').title()}")
            lineas.append(f"\n{r.descripcion}")
            if r.activado and r.recomendacion:
                lineas.append(f"\n**Acción requerida:** {r.recomendacion}")
            if r.hallazgos_afectados:
                lineas.append(f"\n**Hallazgos afectados:** {', '.join(r.hallazgos_afectados)}")

        ruta = self.paths.m5_control_riesgo / "informe_control_riesgo.md"
        ruta.write_text("\n".join(lineas), encoding="utf-8")
        print("   informe_control_riesgo.md guardado.")
        return True

    def ejecutar(self) -> bool:
        print("\n   [M5] Iniciando control de riesgo…")

        if not self.cargar_insumos():
            return False

        print("   Corriendo guardianes…")
        self.riesgos = [
            self.guardian_sobreedicion(),
            self.guardian_sesgo_comercial(),
            self.guardian_voz_autor(),
            self.guardian_alucinaciones(),
        ]
        activados = sum(1 for r in self.riesgos if r.activado)
        print(f"   Guardianes activados: {activados}/{len(self.riesgos)}")

        if not self.guardar_resultados():
            return False
        if not self.generar_informe():
            return False

        print("   [M5] Control de riesgo completado.")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 5: Control de Riesgo")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloControlRiesgo(paths)
    exit(0 if modulo.ejecutar() else 1)
