#!/usr/bin/env python3
"""
MÓDULO 4: EDITOR JEFE / ARBITRAJE CENTRAL (v3)
================================================
Responsabilidad: actuar como DIRECCIÓN EDITORIAL. No es un consolidador
pasivo; tiene poder de veto, merge, prioridad y escalamiento.

Funciones:
  1. Árbitro de conflictos: cuando dos agentes discrepan, decide con
     criterio explícito o escala al autor.
  2. Juez de prioridad: ordena el backlog por ratio impacto/esfuerzo/riesgo.
  3. Guardián de coherencia global: verifica que la suma de recomendaciones
     no rompa la voz del autor ni el mensaje central.
  4. Modo "Editor Jefe Resumen": TOP10_PROBLEMAS, TOP10_RETORNO,
     RIESGO_PRINCIPAL.

Salidas (en m4_editor_jefe/):
  - dictamen_editor_jefe.md
  - backlog_priorizado.json
  - resumen_ejecutivo_editorial.md
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from config_v3 import ProyectoPaths
from schemas_v3 import (
    Hallazgo,
    DictamenEditorJefe,
    Conflicto,
    cargar_hallazgos,
)
from llm_router import LLMRouter


PROMPT_SISTEMA_EDITOR_JEFE = """Sos el Editor Jefe del sistema Alexandria Writer v3.
Tu rol es el de un director editorial con autoridad real: no consolidás pasivamente, sino que
arbitrás, priorizás y proteges la voz del autor y la coherencia del libro.

RESPONSABILIDADES:
1. Detectar conflictos entre hallazgos de diferentes agentes y resolverlos con criterio explícito.
2. Ordenar el backlog de hallazgos por ratio impacto/esfuerzo/riesgo.
3. Detectar si la suma de recomendaciones amenaza la voz del autor.
4. Producir un dictamen claro, concreto y accionable.

TONO: Autoritativo pero justo. El autor es el director; vos sos el editor que lo sirve.
No infles el dictamen con elogios. Sé directo sobre los problemas y sobre las fortalezas.
"""


class ModuloEditorJefe:
    """
    Editor Jefe: árbitro central del pipeline v3.
    Lee M1 (hallazgos) + M3 (evidencia + conflictos) y produce el dictamen.
    """

    TOP_N = 10  # Tamaño de los top-lists del dictamen

    def __init__(self, paths: ProyectoPaths):
        self.paths = paths
        self.router = LLMRouter()
        self.hallazgos: List[Hallazgo] = []
        self.conflict_log: Dict = {}
        self.bible: Dict = {}

    def cargar_insumos(self) -> bool:
        hallazgos_path = self.paths.hallazgos_path()
        if not hallazgos_path.exists():
            print("   [ERROR] hallazgos.json no encontrado. Ejecutá M1 primero.")
            return False
        self.hallazgos = cargar_hallazgos(str(hallazgos_path))
        print(f"   Hallazgos cargados: {len(self.hallazgos)}")

        conflict_path = self.paths.conflict_log_path()
        if conflict_path.exists():
            with open(conflict_path, encoding="utf-8") as f:
                self.conflict_log = json.load(f)
            conflictos = self.conflict_log.get("conflictos", [])
            print(f"   Conflictos potenciales cargados: {len(conflictos)}")

        bible_path = self.paths.bible_path()
        if bible_path.exists():
            with open(bible_path, encoding="utf-8") as f:
                self.bible = json.load(f)
        return True

    def _top_criticos(self) -> List[str]:
        """Los N hallazgos más críticos por severidad × confianza."""
        ordenados = sorted(
            self.hallazgos,
            key=lambda h: -(h.severidad * h.confianza),
        )
        return [h.id for h in ordenados[: self.TOP_N]]

    def _top_alto_retorno(self) -> List[str]:
        """Fortalezas y hallazgos de severidad media con alta confianza."""
        retorno = [
            h for h in self.hallazgos
            if h.tipo == "fortaleza" or (2 <= h.severidad <= 3 and h.confianza >= 0.7)
        ]
        ordenados = sorted(retorno, key=lambda h: -(h.confianza))
        return [h.id for h in ordenados[: self.TOP_N]]

    def _construir_resumen_hallazgos(self) -> str:
        """Texto compacto de los hallazgos más importantes para el prompt."""
        criticos_ids = set(self._top_criticos())
        lineas: List[str] = []
        for h in self.hallazgos:
            marker = "★" if h.id in criticos_ids else " "
            cita = h.cita_textual[:80].replace("\n", " ") if h.cita_textual else "(sin cita)"
            lineas.append(
                f"{marker} [{h.id}] {h.tipo.upper()} sev:{h.severidad} conf:{h.confianza:.0%} "
                f"| {h.descripcion[:100]} | cita: «{cita}»"
            )
        return "\n".join(lineas[:60])  # Limitar para no saturar el contexto

    def generar_dictamen(self) -> Optional[str]:
        print("   Generando dictamen del Editor Jefe…")
        resumen = self._construir_resumen_hallazgos()
        total = len(self.hallazgos)
        criticos = sum(1 for h in self.hallazgos if h.severidad >= 4)
        fortalezas = sum(1 for h in self.hallazgos if h.tipo == "fortaleza")
        conflictos = len(self.conflict_log.get("conflictos", []))

        user = (
            f"Libro: {self.paths.libro_id} | Autor: {self.paths.autor}\n"
            f"Total hallazgos: {total} | Críticos (sev≥4): {criticos} | "
            f"Fortalezas: {fortalezas} | Conflictos potenciales: {conflictos}\n\n"
            f"HALLAZGOS (★ = en TOP10 críticos):\n{resumen}\n\n"
            "Producí el DICTAMEN DEL EDITOR JEFE. Debe incluir:\n\n"
            "## 1. Lectura global\n"
            "En 3-5 frases: el estado real del libro. Sin eufemismos, sin catastrofismo.\n\n"
            "## 2. Top 10 problemas críticos\n"
            "Lista ordenada (mayor impacto primero). Cada ítem: ID del hallazgo + descripción "
            "en 1 línea + por qué es prioritario.\n\n"
            "## 3. Top 10 cambios de alto retorno\n"
            "Lo que más mejora el libro con el menor riesgo. Puede incluir fortalezas a potenciar.\n\n"
            "## 4. Riesgo principal de intervención\n"
            "¿Hay riesgo de sobredición? ¿De homogeneizar la voz? ¿De perder el eje central? "
            "Una sola alerta, concreta.\n\n"
            "## 5. Próximo paso para el autor\n"
            "Una acción concreta. No una lista de 20 cosas. Una.\n\n"
            "## 6. Resolución de conflictos\n"
            f"Hay {conflictos} conflictos potenciales detectados por M3 (duplicados semánticos). "
            "Indicá si alguno requiere decisión del autor o si se resuelven internamente."
        )

        resultado = self.router.chat(
            user_prompt=user,
            system=PROMPT_SISTEMA_EDITOR_JEFE,
            temperature=0.25,
            max_tokens=4000,
        )
        if not resultado.get("success"):
            print(f"   [ERROR] LLM falló: {resultado.get('error')}")
            return None
        return resultado.get("content", "")

    def construir_backlog_priorizado(self) -> List[Dict]:
        """Ordena todos los hallazgos por prioridad editorial."""
        def score(h: Hallazgo) -> float:
            # Fortalezas van al fondo del backlog (no son "problemas a resolver")
            if h.tipo == "fortaleza":
                return -h.confianza
            return -(h.severidad * h.confianza)

        ordenados = sorted(self.hallazgos, key=score)
        backlog = []
        for rank, h in enumerate(ordenados, 1):
            backlog.append({
                "rank": rank,
                "id": h.id,
                "tipo": h.tipo,
                "agente": h.agente,
                "chunk_ref": h.chunk_ref,
                "severidad": h.severidad,
                "confianza": h.confianza,
                "score_editorial": round(h.severidad * h.confianza, 3),
                "descripcion": h.descripcion[:200],
                "cita_textual": h.cita_textual[:150],
                "intervencion_sugerida": h.intervencion_sugerida[:200],
                "estado": h.estado,
            })
        return backlog

    def guardar_dictamen(self, contenido_dictamen: str) -> bool:
        self.paths.m4_editor_jefe.mkdir(parents=True, exist_ok=True)

        # dictamen_editor_jefe.md
        encabezado = (
            f"# Dictamen del Editor Jefe — {self.paths.libro_id}\n\n"
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
            f"Hallazgos analizados: {len(self.hallazgos)}*\n\n---\n\n"
        )
        ruta_dictamen = self.paths.m4_editor_jefe / "dictamen_editor_jefe.md"
        ruta_dictamen.write_text(encabezado + contenido_dictamen, encoding="utf-8")
        print(f"   dictamen_editor_jefe.md guardado.")

        # backlog_priorizado.json
        backlog = self.construir_backlog_priorizado()
        ruta_backlog = self.paths.backlog_path()
        with open(ruta_backlog, "w", encoding="utf-8") as f:
            json.dump(
                {"libro_id": self.paths.libro_id, "total": len(backlog), "backlog": backlog},
                f, indent=2, ensure_ascii=False,
            )
        print(f"   backlog_priorizado.json guardado ({len(backlog)} ítems).")

        # Guardar también como JSON estructurado (DictamenEditorJefe schema)
        dictamen_schema = DictamenEditorJefe(
            libro_id=self.paths.libro_id,
            top10_problemas_criticos=self._top_criticos(),
            top10_cambios_alto_retorno=self._top_alto_retorno(),
            riesgo_principal_intervencion={
                "tipo": "sobreedicion" if len(self.hallazgos) > 40 else "ninguno_detectado",
                "descripcion": (
                    f"Se generaron {len(self.hallazgos)} hallazgos. "
                    "Aplicarlos todos podría fragmentar la voz del autor."
                    if len(self.hallazgos) > 40
                    else "Densidad de hallazgos dentro de límites saludables."
                ),
            },
        )
        ruta_json = self.paths.dictamen_editor_jefe_path()
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(dictamen_schema.to_dict(), f, indent=2, ensure_ascii=False)

        return True

    def generar_resumen_ejecutivo(self, contenido_dictamen: str) -> bool:
        print("   Generando resumen ejecutivo (1 página)…")
        user = (
            f"Basándote en este dictamen del Editor Jefe:\n\n{contenido_dictamen[:3000]}\n\n"
            "Escribí un RESUMEN EJECUTIVO EDITORIAL de exactamente 1 página (300-400 palabras). "
            "Debe poder leerse en 3 minutos y responder:\n"
            "  1. ¿Está el libro listo para publicarse?\n"
            "  2. ¿Cuál es el problema más importante?\n"
            "  3. ¿Cuál es la fortaleza más importante?\n"
            "  4. ¿Qué pasa primero?\n\n"
            "Tono: editorial profesional, directo, sin jerga técnica. "
            "El autor debe poder leer este resumen y saber exactamente en qué está parado."
        )
        resultado = self.router.chat(
            user_prompt=user,
            system=PROMPT_SISTEMA_EDITOR_JEFE,
            temperature=0.2,
            max_tokens=1000,
        )
        contenido = resultado.get("content", "") if resultado.get("success") else (
            "*Error al generar resumen ejecutivo.*"
        )
        ruta = self.paths.m4_editor_jefe / "resumen_ejecutivo_editorial.md"
        ruta.write_text(
            f"# Resumen Ejecutivo Editorial — {self.paths.libro_id}\n\n"
            f"*{datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
            + contenido,
            encoding="utf-8",
        )
        print("   resumen_ejecutivo_editorial.md guardado.")
        return True

    def ejecutar(self) -> bool:
        print("\n   [M4] Iniciando arbitraje del Editor Jefe…")

        if not self.cargar_insumos():
            return False

        dictamen = self.generar_dictamen()
        if not dictamen:
            return False

        if not self.guardar_dictamen(dictamen):
            return False

        if not self.generar_resumen_ejecutivo(dictamen):
            return False

        print("   [M4] Editor Jefe completado.")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 4: Editor Jefe / Arbitraje Central")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloEditorJefe(paths)
    exit(0 if modulo.ejecutar() else 1)
