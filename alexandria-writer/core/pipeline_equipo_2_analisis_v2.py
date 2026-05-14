#!/usr/bin/env python3
"""
EQUIPO 2 v2: ANALISIS EDITORIAL PROFESIONAL MEJORADO
======================================================
Mejoras sobre v1:
  - Consolidador de recomendaciones (elimina duplicados entre chunks)
  - Editor Jefe que prioriza y resuelve conflictos
  - Formato YAML estructurado para cada recomendacion (parseable)
  - Metricas de calidad automaticas
  - Archivo JSON con todas las recomendaciones para procesamiento automatico

Agentes:
  - analista_5d, corrector, estilista, estructurista, teologo, mercadologo (por chunk)
  - consolidador (global: unifica recomendaciones de todos los chunks)
  - editor_jefe (global: prioriza top 30, resuelve conflictos)

Salidas (en projects/tsbn/equipo2/):
  - 01_ANALISIS_5D.md
  - 02_EDICIONES_CONSOLIDADAS.md   ← NUEVO: sin duplicados, con contexto global
  - 02_EDICIONES_YAML.yml          ← NUEVO: formato estructurado parseable
  - 03_TOP30_PRIORITARIO.md        ← Mejorado: Top 30 con justificacion
  - 04_OPORTUNIDADES.md
  - 05_METRICAS_CALIDAD.md         ← NUEVO: estadisticas del analisis
  - recomendaciones.json           ← NUEVO: todas las recs en JSON
"""

import sys
import os
import re
import json
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


class Equipo2AnalisisV2:
    def __init__(self, modo="completo"):
        self.router = LLMRouter()
        self.modo = modo
        self.config = AGENTES_CONFIG[modo]
        self.chunks = []
        self.bible = ""
        self.resultados_raw = {}
        self.recomendaciones_consolidadas = []
        self.metricas = {}

        print("=" * 65)
        print("  EQUIPO 2 v2: ANALISIS EDITORIAL PROFESIONAL MEJORADO")
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

    # Agentes por chunk (igual que v1, pero prompts mejorados para formato YAML)
    def analista_5d(self, chunk):
        system = "Eres un editor literario senior. Analizas libros en 5 dimensiones con rúbrica profesional. Devuelves score 1-10 por dimension con evidencia textual."
        prompt = f"""Contexto del libro (Bible del Equipo 1):
{self.bible[:3000]}

Analiza este CHUNK del libro en 5 DIMENSIONES. Para cada dimension:
- Dimension: [nombre]
- Score: [1-10]/10
- Fortalezas: [2-3 bullets]
- Debilidades: [2-3 bullets]
- Evidencia_textual: [cita exacta del chunk que soporta el score]

DIMENSIONES: LITERARIO, ESPIRITUAL, MERCADOLOGICO, TECNICO, IMPACTO

TEXTO DEL CHUNK {chunk['numero']} (paginas {chunk['paginas'][0]}-{chunk['paginas'][-1]}):
{chunk['texto'][:12000]}"""
        return self._llamar(prompt, system, temp=0.2, max_tok=4000)

    def corrector(self, chunk):
        system = "Eres corrector de pruebas RAE. Identificas errores ortograficos, gramaticales y de puntuacion. Devuelves EXACTAMENTE este formato YAML por error:"
        prompt = f"""Analiza el texto buscando errores formales. Por cada error, usa EXACTAMENTE este formato:

```yaml
- ubicacion: "primeras 10 palabras del parrafo"
  tipo: "ortografico"  # o gramatical, puntuacion, sintaxis
  severidad: "menor"   # o mayor, critica
  texto_original: "fragmento exacto con error"
  texto_sugerido: "fragmento corregido completo"
  regla: "norma RAE aplicada"
  chunk: {chunk['numero']}
  paginas: "{chunk['paginas'][0]}-{chunk['paginas'][-1]}"
```

IMPORTANTE: El texto_sugerido debe ser el FRAGMENTO COMPLETO corregido, no solo la palabra. Si no hay errores, responde "Sin hallazgos".

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.1, max_tok=4000)

    def estilista(self, chunk):
        system = "Eres editor de estilo literario. Detectas cliches, monotonia, sentimentalismo, y prosa generica. Devuelves EXACTAMENTE este formato YAML:"
        prompt = f"""Analiza el estilo del texto. Por cada hallazgo, usa EXACTAMENTE este formato:

```yaml
- ubicacion: "primeras 10 palabras del parrafo"
  tipo: "cliche"  # o monotonia, sentimentalismo, ritmo_lento, metafora_gastada, adverbios
  severidad: "mayor"  # o critica, menor
  texto_original: "parrafo completo problemático"
  texto_sugerido: "parrafo completo reescrito manteniendo VOZ del autor"
  justificacion: "explicacion editorial de la mejora"
  chunk: {chunk['numero']}
  paginas: "{chunk['paginas'][0]}-{chunk['paginas'][-1]}"
```

IMPORTANTE: El TEXTO_SUGERIDO debe ser un PARRAFO COMPLETO y COHERENTE. NO solo el fragmento corregido.

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.3, max_tok=4000)

    def estructurista(self, chunk):
        system = "Eres arquitecto narrativo. Analizas transiciones, flujo, estructura, hooks. Devuelves EXACTAMENTE este formato YAML:"
        prompt = f"""Analiza la estructura. Por cada hallazgo:

```yaml
- ubicacion: "primeras 10 palabras del parrafo"
  tipo: "transicion_abrupta"  # o parrafo_huerfano, falta_hook, cambio_tono, repeticion_idea
  severidad: "mayor"
  texto_original: "parrafo(s) con problema"
  texto_sugerido: "parrafo(s) con transicion/bridge incluido"
  justificacion: "como mejora la cohesion"
  chunk: {chunk['numero']}
  paginas: "{chunk['paginas'][0]}-{chunk['paginas'][-1]}"
```

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.25, max_tok=4000)

    def teologo(self, chunk):
        system = "Eres teologo y escritor espiritual. Evaluas autenticidad, profundidad, universalidad. Formato YAML:"
        prompt = f"""Analiza el contenido espiritual. Por cada hallazgo:

```yaml
- ubicacion: "primeras 10 palabras del parrafo"
  tipo: "superficialidad"  # o inconsistencia, genericidad, falta_anclaje, exceso_subjetividad
  severidad: "mayor"
  texto_original: "fragmento con problema"
  texto_sugerido: "fragmento profundizado"
  justificacion: "como fortalece el mensaje espiritual"
  chunk: {chunk['numero']}
  paginas: "{chunk['paginas'][0]}-{chunk['paginas'][-1]}"
```

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.2, max_tok=4000)

    def mercadologo(self, chunk):
        system = "Eres estratega editorial de marketing. Analizas conexion, nicho, potencial best seller. Formato YAML:"
        prompt = f"""Analiza desde perspectiva de mercado. Por cada hallazgo:

```yaml
- ubicacion: "primeras 10 palabras del parrafo"
  tipo: "desconexion"  # o falta_nicho, falta_ejercicio, cierre_debil, titulo_debil, falta_pregunta
  severidad: "menor"
  texto_original: "fragmento"
  texto_sugerido: "fragmento mejorado"
  justificacion: "como aumenta conexion con lector"
  chunk: {chunk['numero']}
  paginas: "{chunk['paginas'][0]}-{chunk['paginas'][-1]}"
```

TEXTO:
{chunk['texto'][:15000]}"""
        return self._llamar(prompt, system, temp=0.3, max_tok=4000)

    def ejecutar_agentes(self):
        print(f"\n[FASE 2] Ejecutando agentes por chunk ({self.modo})...")
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

        self.resultados_raw = resultados
        return resultados

    def parsear_yaml_recomendaciones(self, texto):
        """Extrae bloques YAML de recomendaciones del texto del agente."""
        recs = []
        # Buscar bloques ```yaml ... ```
        pattern = r'```yaml\s*\n(.*?)\n```'
        matches = re.findall(pattern, texto, re.DOTALL)

        for match in matches:
            try:
                # Intentar parsear YAML simple
                import yaml
                data = yaml.safe_load(match)
                if isinstance(data, list):
                    recs.extend(data)
                elif isinstance(data, dict):
                    recs.append(data)
            except Exception:
                # Fallback: extraer campos manualmente con regex
                items = re.split(r'\n-(?:\s*)', match.strip())
                for item in items[1:]:
                    rec = {}
                    for campo in ['ubicacion', 'tipo', 'severidad', 'texto_original', 'texto_sugerido', 'justificacion', 'chunk', 'paginas']:
                        m = re.search(rf'{campo}:\s*"?(.*?)"?\s*(?:\n|$)', item)
                        if m:
                            rec[campo] = m.group(1).strip().strip('"')
                    if rec:
                        recs.append(rec)

        return recs

    def consolidador_global(self):
        print("\n[FASE 3] Consolidador Global: Unificando recomendaciones de todos los chunks...")

        todas_recs = []
        for chunk_num, recs in self.resultados_raw.items():
            for agente, content in recs.items():
                if agente == "analista_5d":
                    continue  # El analista_5d no genera recomendaciones de edicion
                parsed = self.parsear_yaml_recomendaciones(content)
                for r in parsed:
                    r["agente"] = agente
                todas_recs.extend(parsed)

        print(f"  Recomendaciones parseadas: {len(todas_recs)}")

        # Eliminar duplicados por ubicacion + tipo
        vistas = set()
        unicas = []
        for r in todas_recs:
            key = (r.get("ubicacion", ""), r.get("tipo", ""))
            if key not in vistas:
                vistas.add(key)
                unicas.append(r)

        print(f"  Recomendaciones unicas tras deduplicacion: {len(unicas)}")
        self.recomendaciones_consolidadas = unicas
        return unicas

    def editor_jefe(self):
        print("\n[FASE 4] Editor Jefe: Priorizando TOP 30 y resolviendo conflictos...")

        # Preparar muestra de recomendaciones para el LLM
        recs_muestra = self.recomendaciones_consolidadas[:50]
        yaml_muestra = ""
        for i, r in enumerate(recs_muestra, 1):
            yaml_muestra += f"\n{i}. [{r.get('severidad', 'menor')}] {r.get('tipo', '')} — {r.get('ubicacion', '')[:60]}\n"
            yaml_muestra += f"   Original: {r.get('texto_original', '')[:120]}\n"
            yaml_muestra += f"   Sugerido: {r.get('texto_sugerido', '')[:120]}\n"

        prompt = f"""Eres el Editor Jefe de una editorial hispana con 30 anos de experiencia.

Tienes {len(self.recomendaciones_consolidadas)} recomendaciones de edicion de 6 agentes especializados.

Tu tarea:
1. Identifica conflictos (dos agentes sugieren cambios opuestos en mismo parrafo)
2. Resuelve cada conflicto con criterio editorial
3. Selecciona las TOP 30 recomendaciones mas importantes, ordenadas por IMPACTO en el lector
4. Para cada una de las TOP 30, indica:
   - Prioridad: 1-30
   - Severidad: critica/mayor/menor
   - Tipo: ortografico/estilo/estructura/espiritual/marketing
   - Ubicacion: primeras palabras del parrafo
   - Accion: "reescribir" / "corregir" / "agregar" / "eliminar"
   - TEXTO_SUGERIDO completo
   - JUSTIFICACION de por que esta en el top 30

MUESTRA DE RECOMENDACIONES (primeras 50):
{yaml_muestra}

Genera la lista de TOP 30 en formato estructurado."""

        system = "Eres editor jefe. Priorizas cambios por impacto en lector, resuelves conflictos entre editores, y generas documentos ejecutivos."
        content, provider = self._llamar(prompt, system, temp=0.15, max_tok=8000)
        print(f"  OK [{provider}] | Top 30 generado")
        return content

    def calcular_metricas(self):
        print("\n[FASE 5] Calculando metricas de calidad...")

        total = len(self.recomendaciones_consolidadas)
        por_severidad = {"critica": 0, "mayor": 0, "menor": 0}
        por_tipo = {}
        por_agente = {}

        for r in self.recomendaciones_consolidadas:
            sev = r.get("severidad", "menor").lower()
            por_severidad[sev] = por_severidad.get(sev, 0) + 1

            tipo = r.get("tipo", "otro")
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

            agente = r.get("agente", "desconocido")
            por_agente[agente] = por_agente.get(agente, 0) + 1

        self.metricas = {
            "total_recomendaciones": total,
            "por_severidad": por_severidad,
            "por_tipo": por_tipo,
            "por_agente": por_agente,
            "chunks_analizados": len(self.chunks),
            "modo": self.modo,
            "fecha": datetime.now().isoformat()
        }

        print(f"  Total recomendaciones: {total}")
        print(f"  Por severidad: {por_severidad}")
        print(f"  Por tipo: {por_tipo}")
        return self.metricas

    def compilar_documentos(self, top30, metricas):
        print("\n[COMPILACION] Generando documentos finales del Equipo 2...")

        # 01_ANALISIS_5D.md (igual que antes)
        analisis_parts = []
        for chunk_num, recs in self.resultados_raw.items():
            if "analista_5d" in recs:
                analisis_parts.append(f"\n\n## Chunk {chunk_num}\n\n{recs['analista_5d']}")

        with open(OUTPUT / "01_ANALISIS_5D.md", "w", encoding="utf-8") as f:
            f.write("# Analisis Multi-Dimensional 5D\n\n")
            f.write(f"> Modo: {self.modo} | Generado: {datetime.now().isoformat()}\n\n")
            f.write("".join(analisis_parts))
        print(f"  -> 01_ANALISIS_5D.md")

        # 02_EDICIONES_CONSOLIDADAS.md — NUEVO: sin duplicados
        lines = ["# Ediciones Consolidadas — Recomendaciones de Cambio", ""]
        lines.append(f"> Total recomendaciones unicas: {metricas['total_recomendaciones']}")
        lines.append(f"> Modo: {self.modo} | Generado: {datetime.now().isoformat()}")
        lines.append("")

        for r in self.recomendaciones_consolidadas:
            lines.append(f"## [{r.get('severidad', 'menor').upper()}] {r.get('tipo', '').upper()} — {r.get('ubicacion', '')}")
            lines.append(f"- **Agente:** {r.get('agente', '')}")
            lines.append(f"- **Chunk:** {r.get('chunk', '')} | **Paginas:** {r.get('paginas', '')}")
            lines.append(f"- **Original:** {r.get('texto_original', '')}")
            lines.append(f"- **Sugerido:** {r.get('texto_sugerido', '')}")
            lines.append(f"- **Justificacion:** {r.get('justificacion', '')}")
            lines.append("")

        with open(OUTPUT / "02_EDICIONES_CONSOLIDADAS.md", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"  -> 02_EDICIONES_CONSOLIDADAS.md ({metricas['total_recomendaciones']} recs)")

        # recomendaciones.json — NUEVO: parseable por otro modelo
        with open(OUTPUT / "recomendaciones.json", "w", encoding="utf-8") as f:
            json.dump(self.recomendaciones_consolidadas, f, ensure_ascii=False, indent=2)
        print(f"  -> recomendaciones.json")

        # 03_TOP30_PRIORITARIO.md — Mejorado con Editor Jefe
        with open(OUTPUT / "03_TOP30_PRIORITARIO.md", "w", encoding="utf-8") as f:
            f.write("# Top 30 — Cambios Obligatorios Priorizados\n\n")
            f.write("> Seleccionados por el Editor Jefe segun impacto en el lector\n\n")
            f.write(top30)
        print(f"  -> 03_TOP30_PRIORITARIO.md")

        # 04_OPORTUNIDADES.md — severidad menor
        oportunidades = [r for r in self.recomendaciones_consolidadas
                        if r.get("severidad", "").lower() == "menor"]
        with open(OUTPUT / "04_OPORTUNIDADES.md", "w", encoding="utf-8") as f:
            f.write("# Oportunidades de Mejora — Severidad Menor\n\n")
            f.write(f"> {len(oportunidades)} recomendaciones opcionales pero valiosas\n\n")
            for r in oportunidades:
                f.write(f"### {r.get('tipo', '').upper()} — {r.get('ubicacion', '')}\n\n")
                f.write(f"- **Original:** {r.get('texto_original', '')}\n")
                f.write(f"- **Sugerido:** {r.get('texto_sugerido', '')}\n")
                f.write(f"- **Justificacion:** {r.get('justificacion', '')}\n\n")
        print(f"  -> 04_OPORTUNIDADES.md ({len(oportunidades)} recs)")

        # 05_METRICAS_CALIDAD.md — NUEVO
        with open(OUTPUT / "05_METRICAS_CALIDAD.md", "w", encoding="utf-8") as f:
            f.write("# Metricas de Calidad del Analisis Editorial\n\n")
            f.write(f"| Metrica | Valor |\n|---------|-------|\n")
            f.write(f"| Total recomendaciones | {metricas['total_recomendaciones']} |\n")
            f.write(f"| Chunks analizados | {metricas['chunks_analizados']} |\n")
            f.write(f"| Modo | {metricas['modo']} |\n")
            f.write(f"| Criticas | {metricas['por_severidad'].get('critica', 0)} |\n")
            f.write(f"| Mayores | {metricas['por_severidad'].get('mayor', 0)} |\n")
            f.write(f"| Menores | {metricas['por_severidad'].get('menor', 0)} |\n")
            f.write("")
            f.write("## Por Tipo\n\n")
            for tipo, count in sorted(metricas['por_tipo'].items(), key=lambda x: -x[1]):
                f.write(f"- {tipo}: {count}\n")
            f.write("")
            f.write("## Por Agente\n\n")
            for agente, count in sorted(metricas['por_agente'].items(), key=lambda x: -x[1]):
                f.write(f"- {agente}: {count}\n")
        print(f"  -> 05_METRICAS_CALIDAD.md")

    def ejecutar(self):
        self.cargar_bible()
        if not self.extraer_chunks():
            return False

        self.ejecutar_agentes()
        self.consolidador_global()
        top30 = self.editor_jefe()
        metricas = self.calcular_metricas()
        self.compilar_documentos(top30, metricas)

        print("\n" + "=" * 65)
        print("  EQUIPO 2 v2 COMPLETADO")
        print("=" * 65)
        print(f"\n  Documentos en: {OUTPUT}")
        print(f"  Recomendaciones unicas: {metricas['total_recomendaciones']}")
        print("  Listo para pasar al Equipo 3 (Estrategia de Mercado)")
        return True


def main():
    parser = argparse.ArgumentParser(description="Equipo 2 v2: Analisis Editorial Mejorado")
    parser.add_argument("--modo", default="completo", choices=["completo", "transiciones", "tecnico", "marketing"])
    args = parser.parse_args()
    equipo = Equipo2AnalisisV2(modo=args.modo)
    equipo.ejecutar()


if __name__ == "__main__":
    main()
