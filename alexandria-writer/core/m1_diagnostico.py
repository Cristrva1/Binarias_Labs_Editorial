#!/usr/bin/env python3
"""
MÓDULO 1: DIAGNÓSTICO EDITORIAL (v3)
======================================
Responsabilidad: responder QUÉ ES el libro y QUÉ LE DUELE, sin
contaminación de marketing.

Agentes especializados (corren por chunks, luego consolidación global):
  - agente_estructura  — arco, ritmo, tensión, picos de lectura.
  - agente_voz         — consistencia de tono, distancia narrativa.
  - agente_continuidad — coherencia temática, callbacks, argumento.
  - agente_friccion    — puntos de abandono, confusión, fatiga lectora.
  - agente_fortaleza   — lo que funciona y por qué.

Salidas (en m1_diagnostico/):
  - hallazgos.json            (array de Hallazgo según schemas_v3)
  - metricas_editoriales.json
  - diagnostico_estructura.md
  - diagnostico_voz.md
  - diagnostico_continuidad.md
  - diagnostico_friccion.md
  - diagnostico_fortalezas.md

Dependencias: pip install pyyaml
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
    MetricasEditoriales,
    guardar_hallazgos,
    append_evidencia_store,
)
from llm_router import LLMRouter


# Taxonomía de tipos de agentes diagnósticos
AGENTES_DIAGNOSTICO = {
    "agente_estructura": {
        "tipo": "estructura",
        "categoria": "ritmo",
        "enfoque": (
            "Analizá el ARCO, el RITMO, la TENSIÓN y los PICOS DE LECTURA de este fragmento. "
            "¿El texto avanza? ¿Tiene clímax y valles? ¿Las transiciones entre ideas son fluidas? "
            "¿Hay capítulos de doble corazón (dos temas en uno)? "
            "Solo reportá lo que ves en el texto, con cita literal."
        ),
    },
    "agente_voz": {
        "tipo": "voz",
        "categoria": "estabilidad",
        "enfoque": (
            "Analizá la VOZ, el TONO y el REGISTRO de este fragmento. "
            "¿El autor mantiene una voz consistente? ¿Hay momentos donde la distancia narrativa cambia "
            "sin razón aparente? ¿Hay frases que suenan a otra persona? "
            "Citá literalmente los pasajes que lo muestren."
        ),
    },
    "agente_continuidad": {
        "tipo": "continuidad",
        "categoria": "coherencia tematica",
        "enfoque": (
            "Analizá la COHERENCIA TEMÁTICA y los CALLBACKS de este fragmento. "
            "¿Las ideas que se introducen se desarrollan? ¿Hay contradicciones internas? "
            "¿El argumento avanza o da vueltas? ¿Hay promesas al lector que se hacen y no se cumplen? "
            "Citá literalmente."
        ),
    },
    "agente_friccion": {
        "tipo": "friccion",
        "categoria": "confusion",
        "enfoque": (
            "Identificá los PUNTOS DE ABANDONO y FRICCIÓN en este fragmento. "
            "¿Dónde un lector dejaría de leer? ¿Hay párrafos confusos, repetitivos o que agotan? "
            "¿Hay jerga que excluye? ¿Hay digresiones que rompen el flujo? "
            "Sé específico: cita el párrafo problemático."
        ),
    },
    "agente_fortaleza": {
        "tipo": "fortaleza",
        "categoria": "potencial",
        "enfoque": (
            "Identificá las FORTALEZAS y lo que GENUINAMENTE FUNCIONA en este fragmento. "
            "¿Qué frases o pasajes son poderosos? ¿Qué diferencia a este texto? "
            "¿Dónde el autor está en su mejor momento? "
            "Estas observaciones son tan importantes como los problemas. Citá literalmente."
        ),
    },
}


PROMPT_SISTEMA = """Sos un agente de diagnóstico editorial del sistema Alexandria Writer v3.
Tu trabajo es analizar fragmentos de un manuscrito y reportar hallazgos precisos, con evidencia textual.

REGLAS DURAS:
1. Toda observación DEBE incluir una cita literal del manuscrito (cita_textual).
2. No inventés problemas. Si no encontrás nada relevante, reportá: "Sin hallazgos significativos."
3. No dés consejos de marketing. Solo diagnóstico editorial.
4. Severidad: 1 (estético) → 5 (crítico para la comprensión del libro).
5. Confianza: 0.0 (intuición) → 1.0 (certeza con evidencia sólida).

FORMATO DE SALIDA — devolvé un JSON array, sin texto adicional:
[
  {
    "tipo": "estructura|voz|continuidad|friccion|fortaleza",
    "categoria_taxonomica": "ritmo|estabilidad|coherencia tematica|confusion|potencial|...",
    "cita_textual": "fragmento literal exacto del manuscrito",
    "descripcion": "qué observás, en 2-3 frases",
    "severidad": 1-5,
    "confianza": 0.0-1.0,
    "intervencion_sugerida": "qué haría concretamente al respecto",
    "impacto_esperado": "qué cambiaría si se acepta"
  }
]

Si no hay hallazgos: devolvé exactamente []
"""


class ModuloDiagnostico:
    """
    Diagnóstico editorial del manuscrito.
    Lee los chunks de M0 y corre 5 agentes especializados sobre cada uno.
    """

    MAX_CHUNKS_POR_AGENTE = 30   # Límite para no exceder rate limits

    def __init__(self, paths: ProyectoPaths, modo: str = "completo"):
        self.paths = paths
        self.modo = modo
        self.router = LLMRouter()
        self.hallazgos: List[Hallazgo] = []
        self.contador_id = 0

    def _siguiente_id(self, tipo: str) -> str:
        self.contador_id += 1
        prefijos = {
            "estructura": "EST", "voz": "VOZ", "continuidad": "CON",
            "friccion": "FRC", "fortaleza": "FOR",
        }
        pref = prefijos.get(tipo, "GEN")
        return f"H-{self.contador_id:03d}-{pref}"

    def cargar_chunks(self) -> Optional[List[Dict]]:
        mapa_path = self.paths.mapa_chunks_path()
        if not mapa_path.exists():
            print(f"   [ERROR] No existe {mapa_path}. Ejecutá M0 primero.")
            return None
        with open(mapa_path, encoding="utf-8") as f:
            mapa = json.load(f)
        chunks = mapa.get("chunks", [])
        print(f"   Chunks cargados: {len(chunks)}")
        return chunks

    def cargar_texto_completo(self) -> Optional[str]:
        bible_path = self.paths.bible_path()
        if not bible_path.exists():
            print(f"   [ERROR] No existe {bible_path}.")
            return None
        with open(bible_path, encoding="utf-8") as f:
            bible = json.load(f)
        pdf_fuente = bible.get("pdf_fuente", "")
        return bible

    def analizar_chunk(
        self, chunk: Dict, nombre_agente: str, config_agente: Dict
    ) -> List[Dict]:
        """Corre un agente sobre un único chunk. Devuelve lista de hallazgos crudos."""
        texto_chunk = chunk.get("texto_resumen", "")
        if not texto_chunk or len(texto_chunk.strip()) < 50:
            return []

        user_prompt = (
            f"AGENTE: {nombre_agente}\n"
            f"CHUNK: {chunk['id']} (pág. {chunk.get('pagina_inicio','?')}"
            f"–{chunk.get('pagina_fin','?')})\n\n"
            f"ENFOQUE: {config_agente['enfoque']}\n\n"
            f"FRAGMENTO DEL MANUSCRITO:\n{texto_chunk}\n"
        )

        resultado = self.router.chat(
            user_prompt=user_prompt,
            system=PROMPT_SISTEMA,
            temperature=0.2,
            max_tokens=2000,
        )

        if not resultado.get("success"):
            return []

        contenido = resultado.get("content", "").strip()
        if not contenido or contenido == "[]":
            return []

        try:
            inicio = contenido.find("[")
            fin = contenido.rfind("]") + 1
            if inicio == -1 or fin == 0:
                return []
            datos = json.loads(contenido[inicio:fin])
            return datos if isinstance(datos, list) else []
        except Exception:
            return []

    def procesar_agentes(self, chunks: List[Dict]) -> bool:
        """Corre todos los agentes sobre todos los chunks."""
        agentes_activos = AGENTES_DIAGNOSTICO
        if self.modo == "diagnostico":
            agentes_activos = {
                k: v for k, v in AGENTES_DIAGNOSTICO.items()
                if k in ("agente_estructura", "agente_voz", "agente_friccion")
            }

        chunks_a_procesar = chunks[:self.MAX_CHUNKS_POR_AGENTE]
        total_chunks = len(chunks_a_procesar)

        for nombre_agente, config in agentes_activos.items():
            print(f"\n   [{nombre_agente}] procesando {total_chunks} chunks…")
            hallazgos_agente = 0

            for i, chunk in enumerate(chunks_a_procesar, 1):
                crudos = self.analizar_chunk(chunk, nombre_agente, config)
                for crudo in crudos:
                    if not isinstance(crudo, dict):
                        continue
                    h = Hallazgo(
                        id=self._siguiente_id(config["tipo"]),
                        modulo="m1_diagnostico",
                        agente=nombre_agente,
                        tipo=config["tipo"],
                        categoria_taxonomica=crudo.get(
                            "categoria_taxonomica", config["categoria"]
                        ),
                        chunk_ref=chunk["id"],
                        pagina_aprox=chunk.get("pagina_inicio"),
                        cita_textual=str(crudo.get("cita_textual", ""))[:500],
                        descripcion=str(crudo.get("descripcion", ""))[:800],
                        severidad=min(5, max(1, int(crudo.get("severidad", 2)))),
                        confianza=min(1.0, max(0.0, float(crudo.get("confianza", 0.5)))),
                        intervencion_sugerida=str(crudo.get("intervencion_sugerida", ""))[:500],
                        impacto_esperado=str(crudo.get("impacto_esperado", ""))[:400],
                    )
                    self.hallazgos.append(h)
                    hallazgos_agente += 1

                if i % 5 == 0 or i == total_chunks:
                    print(f"      {i}/{total_chunks} chunks | {hallazgos_agente} hallazgos")

        print(f"\n   Total hallazgos generados: {len(self.hallazgos)}")
        return True

    def guardar_hallazgos(self) -> bool:
        self.paths.m1_diagnostico.mkdir(parents=True, exist_ok=True)
        guardar_hallazgos(str(self.paths.hallazgos_path()), self.hallazgos)
        print(f"   hallazgos.json guardado: {self.paths.hallazgos_path()}")

        # También append al evidencia_store si M3 ya existe
        evidencia_path = self.paths.evidencia_store_path()
        if evidencia_path.parent.exists():
            for h in self.hallazgos:
                append_evidencia_store(str(evidencia_path), h)
        return True

    def calcular_metricas(self, chunks: List[Dict]) -> bool:
        total_palabras = sum(
            len(c.get("texto_resumen", "").split()) for c in chunks
        ) * (self.paths.mapa_chunks_path().stat().st_size // max(1, len(chunks)) + 1)

        alta_severidad = [h for h in self.hallazgos if h.severidad >= 3]
        total_palabras_real = max(total_palabras, 1)
        densidad = len(alta_severidad) / (total_palabras_real / 1000)

        if self.hallazgos:
            gravedad = sum(h.severidad * h.confianza for h in self.hallazgos) / len(self.hallazgos)
        else:
            gravedad = 0.0

        voces = [h for h in self.hallazgos if h.tipo == "voz"]
        estabilidad_voz = 1.0 - (len([v for v in voces if v.severidad >= 3]) / max(len(voces), 1))

        metricas = MetricasEditoriales(
            libro_id=self.paths.libro_id,
            total_palabras=total_palabras_real,
            total_capitulos=0,
            total_hallazgos=len(self.hallazgos),
            hallazgos_severidad_alta=len(alta_severidad),
            densidad_problemas=round(densidad, 3),
            gravedad_editorial=round(gravedad, 3),
            estabilidad_voz=round(estabilidad_voz, 3),
        )

        metricas_path = self.paths.metricas_editoriales_path()
        with open(metricas_path, "w", encoding="utf-8") as f:
            json.dump(metricas.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"   metricas_editoriales.json guardado: {metricas_path}")
        return True

    def generar_reportes_md(self) -> bool:
        """Genera un .md de diagnóstico por tipo de agente."""
        tipos = ["estructura", "voz", "continuidad", "friccion", "fortaleza"]
        nombres = {
            "estructura": "diagnostico_estructura.md",
            "voz": "diagnostico_voz.md",
            "continuidad": "diagnostico_continuidad.md",
            "friccion": "diagnostico_friccion.md",
            "fortaleza": "diagnostico_fortalezas.md",
        }

        for tipo in tipos:
            grupo = [h for h in self.hallazgos if h.tipo == tipo]
            if not grupo:
                continue

            nombre_archivo = nombres[tipo]
            lineas = [
                f"# Diagnóstico: {tipo.title()} — {self.paths.libro_id}\n",
                f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
                f"{len(grupo)} hallazgos*\n\n---\n",
            ]

            grupo_ordenado = sorted(grupo, key=lambda h: -h.severidad)
            for h in grupo_ordenado:
                lineas.append(f"\n## {h.id} — Severidad {h.severidad}/5 · Confianza {h.confianza:.0%}")
                lineas.append(f"\n**Chunk:** {h.chunk_ref} · Pág. aprox. {h.pagina_aprox}")
                if h.cita_textual:
                    lineas.append(f"\n> {h.cita_textual}")
                lineas.append(f"\n**Hallazgo:** {h.descripcion}")
                if h.intervencion_sugerida:
                    lineas.append(f"\n**Intervención sugerida:** {h.intervencion_sugerida}")
                if h.impacto_esperado:
                    lineas.append(f"\n**Impacto esperado:** {h.impacto_esperado}")
                lineas.append("\n")

            ruta = self.paths.m1_diagnostico / nombre_archivo
            ruta.write_text("\n".join(lineas), encoding="utf-8")
            print(f"   {nombre_archivo} guardado.")

        return True

    def generar_densidad_por_capitulo(self, chunks: List[Dict]) -> bool:
        """Genera densidad_problemas_por_capitulo.md agrupando hallazgos por chunk."""
        if not self.hallazgos:
            return True

        # Agrupar chunks por página aproximada (proxy de capítulo)
        por_chunk: Dict[str, List] = {}
        for h in self.hallazgos:
            por_chunk.setdefault(h.chunk_ref, []).append(h)

        # Calcular densidad por chunk
        filas: List[Dict] = []
        for chunk in chunks:
            cid = chunk["id"]
            grupo = por_chunk.get(cid, [])
            alta = [h for h in grupo if h.severidad >= 3]
            filas.append({
                "chunk": cid,
                "paginas": f"{chunk.get('pagina_inicio','?')}–{chunk.get('pagina_fin','?')}",
                "total": len(grupo),
                "alta_severidad": len(alta),
                "tipos": list({h.tipo for h in grupo}),
                "max_severidad": max((h.severidad for h in grupo), default=0),
            })

        # Reporte Markdown
        lineas = [
            f"# Densidad de Problemas por Capítulo — {self.paths.libro_id}\n",
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
            f"{len(self.hallazgos)} hallazgos totales en {len(chunks)} chunks*\n\n",
            "| Chunk | Páginas | Hallazgos | Alta Sev. | Tipos | Máx. Sev. |",
            "|-------|---------|-----------|-----------|-------|-----------|",
        ]
        for f in filas:
            bar = "█" * f["max_severidad"] + "░" * (5 - f["max_severidad"])
            tipos_str = ", ".join(f["tipos"]) if f["tipos"] else "—"
            lineas.append(
                f"| {f['chunk']} | {f['paginas']} | {f['total']} | "
                f"{f['alta_severidad']} | {tipos_str} | {bar} {f['max_severidad']}/5 |"
            )

        # Chunks más problemáticos al final
        top5 = sorted(filas, key=lambda x: -(x["alta_severidad"] * 2 + x["total"]))[:5]
        lineas.append("\n\n## Chunks más problemáticos\n")
        for i, f in enumerate(top5, 1):
            if f["total"] == 0:
                break
            lineas.append(
                f"{i}. **{f['chunk']}** (págs. {f['paginas']}) — "
                f"{f['alta_severidad']} hallazgos de alta severidad, "
                f"tipos: {', '.join(f['tipos'])}"
            )

        ruta = self.paths.m1_diagnostico / "densidad_problemas_por_capitulo.md"
        ruta.write_text("\n".join(lineas), encoding="utf-8")
        print("   densidad_problemas_por_capitulo.md guardado.")
        return True

    def ejecutar(self) -> bool:
        print("\n   [M1] Iniciando diagnóstico editorial…")

        chunks = self.cargar_chunks()
        if chunks is None:
            return False

        if not self.procesar_agentes(chunks):
            return False

        if not self.guardar_hallazgos():
            return False

        if not self.calcular_metricas(chunks):
            return False

        if not self.generar_reportes_md():
            return False

        if not self.generar_densidad_por_capitulo(chunks):
            return False

        print("   [M1] Diagnóstico completado.")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 1: Diagnóstico Editorial")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    parser.add_argument("--modo", default="completo",
                        choices=["completo", "diagnostico"])
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloDiagnostico(paths, modo=args.modo)
    exit(0 if modulo.ejecutar() else 1)
