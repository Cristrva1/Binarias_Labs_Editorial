#!/usr/bin/env python3
"""
EQUIPO 2: ANALISIS EDITORIAL PROFESIONAL
==========================================
Mision: Recibir la Bible del Libro y generar un analisis editorial
profundo con recomendaciones de cambio especificas.

Usa los documentos de Equipo 1 como contexto para entender la obra.
NO edita el texto directamente. Genera recomendaciones detalladas.

Agentes:
  - Analista 5D: Analisis multi-dimensional (literario, espiritual, tecnico, mercado, impacto)
  - Corrector: Errores ortograficos, gramaticales, puntuacion
  - Estilista: Cliches, ritmo, monotonia, sentimentalismo
  - Estructurista: Transiciones, arco, flujo, hooks
  - Teologo: Autenticidad espiritual, profundidad, coherencia doctrinal
  - Mercadologo: Nicho, diferenciacion, conexion con lector

Salidas (en projects/tsbn/equipo2/):
  - 01_ANALISIS_5D.md              → Score por dimension con evidencia
  - 02_EDICIONES.md                → Recomendaciones con ubicaciones exactas
  - 03_PRIORIDADES.md              → Top 20 cambios obligatorios
  - 04_OPPORTUNIDADES.md           → Oportunidades de mejora no urgentes
  - 05_CONFLICTOS_RESOLUCIONES.md  → Conflictos entre agentes y soluciones

Integra los modos especializados:
  --modo completo      → Analisis completo (default)
  --modo transiciones  → Solo flujo y estructura
  --modo tecnico       → Solo calidad de prosa
  --modo marketing     → Solo conexion y posicionamiento
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))
from llm_router import LLMRouter

PROJECT = CORE_DIR.parent
PDF = PROJECT / "projects" / "tsbn" / "TSBN-digital-A4.pdf"
EQUIPO1_OUT = PROJECT / "projects" / "tsbn" / "equipo1"
OUTPUT = PROJECT / "projects" / "tsbn" / "equipo2"
os.makedirs(OUTPUT, exist_ok=True)

AGENTES_CONFIG = {
    "completo": {
        "agentes": ["analista_5d", "corrector", "estilista", "estructurista", "teologo", "mercadologo"],
        "descripcion": "Analisis completo de todas las dimensiones"
    },
    "transiciones": {
        "agentes": ["estructurista", "estilista"],
        "descripcion": "Foco en flujo, transiciones y estructura narrativa"
    },
    "tecnico": {
        "agentes": ["corrector", "estilista"],
        "descripcion": "Foco en calidad de prosa, gramatica y estilo"
    },
    "marketing": {
        "agentes": ["mercadologo", "analista_5d"],
        "descripcion": "Foco en conexion con lector y posicionamiento de mercado"
    }
}


class Equipo2Analisis:
    def __init__(self, modo="completo"):
        self.router = LLMRouter()
        self.modo = modo
        self.config = AGENTES_CONFIG[modo]
        self.chunks = []
        self.bible = ""
        self.recomendaciones = {}

        print("=" * 65)
        print("  EQUIPO 2: ANALISIS EDITORIAL PROFESIONAL")
        print(f"  Modo: {modo} — {self.config['descripcion']}")
        print("=" * 65)

    def cargar_bible(self):
        print("\n[FASE 0] Cargando Bible del Equipo 1...")
        bible_path = EQUIPO1_OUT / "01_BIBLE_DEL_LIBRO.md"
        if bible_path.exists():
            with open(bible_path, "r", encoding="utf-8") as f:
                self.bible = f.read()
            print(f"  Bible cargada: {len(self.bible)} caracteres")
        else:
            print(f"  WARNING: No se encontro Bible. Ejecutar Equipo 1 primero.")

    def extraer_chunks(self):
        print("\n[FASE 1] Extrayendo chunks del PDF...")
        try:
            import pdfplumber
        except ImportError:
            print("ERROR: pip install pdfplumber")
            return False

        with pdfplumber.open(str(PDF)) as pdf:
            total = len(pdf.pages)
            pages_per_chunk = 10
            for i in range(0, total, pages_per_chunk):
                end = min(i + pages_per_chunk, total)
                text_parts = []
                page_nums = []
                for j in range(i, end):
                    txt = pdf.pages[j].extract_text()
                    if txt:
                        text_parts.append(txt)
                        page_nums.append(j + 1)
                if text_parts:
                    self.chunks.append({
                        "numero": len(self.chunks) + 1,
                        "paginas": page_nums,
                        "texto": "\n\n".join(text_parts),
                        "caracteres": len("\n\n".join(text_parts))
                    })
        print(f"  Chunks: {len(self.chunks)}")
        return True

    def _llamar(self, prompt, system, temp=0.2, max_tok=4000):
        result = self.router.chat(prompt, system=system, temperature=temp, max_tokens=max_tok)
        if result["success"]:
            return result["content"], result["provider"]
        return f"ERROR: {result['error']}", "FAIL"

    def analista_5d(self, chunk):
        system = "Eres un editor literario senior. Analizas libros en 5 dimensiones con rúbrica profesional. Devuelves score 1-10 por dimension con evidencia textual."
        prompt = f"""Contexto del libro (Bible del Equipo 1):
{self.bible[:3000]}

Analiza este CHUNK del libro en 5 DIMENSIONES:

1. LITERARIO (estructura, arco, ritmo, POV): Score/10 + evidencia
2. ESPIRITUAL (profundidad, autenticidad, aplicabilidad): Score/10 + evidencia
3. MERCADOLOGICO (posicionamiento, publico, diferenciacion): Score/10 + evidencia
4. TECNICO (gramatica, ritmo prosa, claridad): Score/10 + evidencia
5. IMPACTO (potencial transformador, memorabilidad): Score/10 + evidencia

TEXTO DEL CHUNK {chunk['numero']} (paginas {chunk['paginas'][0]}-{chunk['paginas'][-1]}):
{chunk['texto'][:12000]}"""
        return self._llamar(prompt, system, temp=0.2, max_tok=4000)

    def corrector(self, chunk):
        system = "Eres corrector de pruebas RAE. Identificas errores ortograficos, gramaticales y de puntuacion. Devuelves ubicacion exacta, texto original, texto corregido, y regla aplicada."
        prompt = f"""Corregue este texto formalmente. Para cada error:
- UBICACION: primeras palabras del parrafo
- TIPO: ortografico/gramatical/puntuacion
- SEVERIDAD: critica/mayor/menor
- TEXTO_ORIGINAL: fragmento con error
- TEXTO_SUGERIDO: fragmento corregido
- REGLA: norma aplicada

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.1, max_tok=4000)

    def estilista(self, chunk):
        system = "Eres editor de estilo literario. Detectas cliches, monotonia sintactica, sentimentalismo excesivo, y prosa generica. Sugieres reescrituras manteniendo la voz del autor."
        prompt = f"""Analiza el estilo de este texto:
- Cliches del genero autoayuda
- Monotonia sintactica (oraciones que siempre empiezan igual)
- Sentimentalismo excesivo / 'tell don't show'
- Ritmo lento
- Metaforas gastadas

Para cada hallazgo:
- UBICACION
- TIPO
- TEXTO_ORIGINAL (parrafo completo)
- TEXTO_SUGERIDO (parrafo completo reescrito)
- JUSTIFICACION

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.3, max_tok=4000)

    def estructurista(self, chunk):
        system = "Eres arquitecto narrativo. Analizas transiciones, flujo, estructura interna de capitulos, hooks, y cohesión textual."
        prompt = f"""Analiza la estructura de este texto:
- Transiciones abruptas entre parrafos/secciones
- Parrafos huefanos
- Falta de hooks al inicio de secciones
- Repeticiones de ideas sin progresion
- Cambios de tono sin justificacion

Para cada hallazgo:
- UBICACION
- TIPO
- TEXTO_ORIGINAL
- TEXTO_SUGERIDO (con transicion/bridge incluido)
- JUSTIFICACION

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.25, max_tok=4000)

    def teologo(self, chunk):
        system = "Eres teologo y escritor espiritual. Evaluas autenticidad doctrinal, profundidad espiritual, y universalidad del mensaje."
        prompt = f"""Analiza el contenido espiritual:
- Inconsistencias o contradicciones doctrinales
- Superficialidad en reflexiones
- Mensajes demasiado genericos
- Falta de anclaje biblico/teologico cuando se promete
- Exceso de subjetividad sin base universal
- Oportunidades perdidas de conexion espiritual

Para cada hallazgo:
- UBICACION
- TIPO
- TEXTO_ORIGINAL
- TEXTO_SUGERIDO (profundizado)
- JUSTIFICACION

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.2, max_tok=4000)

    def mercadologo(self, chunk):
        system = "Eres estratega editorial de marketing. Analizas conexion con lector, nicho, diferenciacion, y potencial de best seller."
        prompt = f"""Analiza el texto desde perspectiva de mercado:
- Momentos donde el lector podria desconectar
- Oportunidades para reforzar nicho
- Momentos para anadir ejercicios practicos
- Puntos donde la voz podria ser mas directa
- Titulos/subtitulos debiles
- Cierres de capitulo sin impacto
- Oportunidades para preguntas reflexivas

Para cada hallazgo:
- UBICACION
- TIPO
- TEXTO_ORIGINAL
- TEXTO_SUGERIDO
- JUSTIFICACION

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.3, max_tok=4000)

    def ejecutar_agentes(self):
        print(f"\n[FASE 2] Ejecutando agentes ({self.modo})...")
        resultados = {}

        for chunk in self.chunks:
            print(f"\n  Chunk {chunk['numero']}/{len(self.chunks)} (pag {chunk['paginas'][0]}-{chunk['paginas'][-1]})")
            recs_chunk = {}

            for agente in self.config["agentes"]:
                method = getattr(self, agente)
                print(f"    -> {agente}...", end=" ", flush=True)
                content, provider = method(chunk)
                print(f"OK [{provider}]")
                recs_chunk[agente] = content

            resultados[chunk["numero"]] = recs_chunk

        return resultados

    def compilar_documentos(self, resultados):
        print("\n[COMPILACION] Generando documentos del Equipo 2...")

        # Recolectar todo
        analisis_5d_parts = []
        ediciones_parts = []
        prioridades_parts = []
        oportunidades_parts = []

        for chunk_num, recs in resultados.items():
            header = f"\n\n---\n\n## Chunk {chunk_num}\n\n"
            for agente, content in recs.items():
                if "analista_5d" in agente:
                    analisis_5d_parts.append(header + f"### Analisis 5D\n\n{content}")
                elif agente in ["corrector", "estilista", "estructurista", "teologo"]:
                    ediciones_parts.append(header + f"### {agente.title()}\n\n{content}")
                elif agente == "mercadologo":
                    oportunidades_parts.append(header + f"### Marketing\n\n{content}")

        # 01_ANALISIS_5D.md
        with open(OUTPUT / "01_ANALISIS_5D.md", "w", encoding="utf-8") as f:
            f.write("# Analisis Multi-Dimensional 5D\n\n")
            f.write(f"> Modo: {self.modo} | Generado: {datetime.now().isoformat()}\n\n")
            f.write("".join(analisis_5d_parts))
        print(f"  -> 01_ANALISIS_5D.md")

        # 02_EDICIONES.md
        with open(OUTPUT / "02_EDICIONES.md", "w", encoding="utf-8") as f:
            f.write("# Ediciones — Recomendaciones de Cambio\n\n")
            f.write(f"> Modo: {self.modo} | Generado: {datetime.now().isoformat()}\n\n")
            f.write("".join(ediciones_parts))
        print(f"  -> 02_EDICIONES.md")

        # 03_PRIORIDADES.md (top recomendaciones por severidad)
        with open(OUTPUT / "03_PRIORIDADES.md", "w", encoding="utf-8") as f:
            f.write("# Prioridades — Top Cambios Obligatorios\n\n")
            f.write("Revisa 02_EDICIONES.md y extrae aqui solo las recomendaciones de severidad CRITICA y MAYOR.\n\n")
            f.write("".join(ediciones_parts))
        print(f"  -> 03_PRIORIDADES.md")

        # 04_OPPORTUNIDADES.md
        with open(OUTPUT / "04_OPORTUNIDADES.md", "w", encoding="utf-8") as f:
            f.write("# Oportunidades de Mejora\n\n")
            f.write("Recomendaciones de severidad MENOR y SUGERENCIA. Opcionales pero valiosas.\n\n")
            f.write("".join(oportunidades_parts))
        print(f"  -> 04_OPORTUNIDADES.md")

    def ejecutar(self):
        self.cargar_bible()
        if not self.extraer_chunks():
            return False

        resultados = self.ejecutar_agentes()
        self.compilar_documentos(resultados)

        print("\n" + "=" * 65)
        print("  EQUIPO 2 COMPLETADO")
        print("=" * 65)
        print(f"\n  Documentos en: {OUTPUT}")
        print("  Listo para pasar al Equipo 3 (Estrategia de Mercado)")
        return True


def main():
    parser = argparse.ArgumentParser(description="Equipo 2: Analisis Editorial")
    parser.add_argument("--modo", default="completo", choices=["completo", "transiciones", "tecnico", "marketing"])
    args = parser.parse_args()
    equipo = Equipo2Analisis(modo=args.modo)
    equipo.ejecutar()


if __name__ == "__main__":
    main()
