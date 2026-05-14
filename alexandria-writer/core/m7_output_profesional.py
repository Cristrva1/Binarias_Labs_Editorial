#!/usr/bin/env python3
"""
MÓDULO 7: OUTPUT PROFESIONAL (v3)
====================================
Responsabilidad: producir los ENTREGABLES FINALES del pipeline.
Es el módulo que el autor y los editores realmente leen.

Lee los outputs de todos los módulos anteriores y genera documentos
listos para usar — no para el sistema, sino para personas.

Documentos generados (en m7_output_profesional/):
  - memo_adquisicion.md          (para editores externos / agentes)
  - diagnostico_desarrollo.md    (para el autor: estado real del libro)
  - plan_intervencion.md         (para el autor: qué hacer, en qué orden)
  - estrategia_publicacion.md    (para el autor: cómo lanzar)
  - brief_final_ejecutivo.md     (1 página: todo lo importante)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from config_v3 import ProyectoPaths
from llm_router import LLMRouter


PROMPT_SISTEMA_OUTPUT = """Sos el redactor de entregables finales del sistema Alexandria Writer v3.
Escribís documentos que van a personas reales: autores, editores, agentes.

PRINCIPIOS:
1. Claridad ante todo. Nada de jerga del sistema.
2. Honestidad. No suavices los problemas ni infles las fortalezas.
3. Accionabilidad. Cada documento debe responder: ¿qué hago yo con esto?
4. Protección de la voz del autor. Nunca describas el libro con palabras que el autor no usaría para sí mismo.
5. Brevedad. Si podés decirlo en 1 página, no uses 3.
"""


class ModuloOutputProfesional:
    """
    Sintetiza todos los módulos anteriores en entregables para personas reales.
    """

    def __init__(self, paths: ProyectoPaths):
        self.paths = paths
        self.router = LLMRouter()
        self.contexto: Dict = {}   # Acumula datos de todos los módulos

    def cargar_todos_los_insumos(self) -> bool:
        """Carga lo que exista de cada módulo anterior."""
        print("   Cargando insumos de módulos anteriores…")

        # M0
        bible_path = self.paths.bible_path()
        if bible_path.exists():
            with open(bible_path, encoding="utf-8") as f:
                self.contexto["bible"] = json.load(f)

        # M1
        metricas_path = self.paths.metricas_editoriales_path()
        if metricas_path.exists():
            with open(metricas_path, encoding="utf-8") as f:
                self.contexto["metricas"] = json.load(f)

        hallazgos_path = self.paths.hallazgos_path()
        if hallazgos_path.exists():
            with open(hallazgos_path, encoding="utf-8") as f:
                h = json.load(f)
                self.contexto["total_hallazgos"] = len(h)
                self.contexto["hallazgos_criticos"] = [
                    x for x in h if x.get("severidad", 0) >= 4
                ][:5]
                self.contexto["fortalezas"] = [
                    x for x in h if x.get("tipo") == "fortaleza"
                ][:5]

        # M4
        dictamen_path = self.paths.m4_editor_jefe / "dictamen_editor_jefe.md"
        if dictamen_path.exists():
            self.contexto["dictamen_editor_jefe"] = dictamen_path.read_text(encoding="utf-8")[:4000]

        resumen_exec_path = self.paths.m4_editor_jefe / "resumen_ejecutivo_editorial.md"
        if resumen_exec_path.exists():
            self.contexto["resumen_ejecutivo"] = resumen_exec_path.read_text(encoding="utf-8")[:2000]

        # M5
        riesgos_path = self.paths.riesgos_detectados_path()
        if riesgos_path.exists():
            with open(riesgos_path, encoding="utf-8") as f:
                r = json.load(f)
                self.contexto["riesgos_activos"] = [
                    x for x in r.get("riesgos", []) if x.get("activado")
                ]

        # M6
        benchmark_path = self.paths.benchmark_path()
        if benchmark_path.exists():
            with open(benchmark_path, encoding="utf-8") as f:
                self.contexto["benchmark"] = json.load(f)

        posic_path = self.paths.m6_benchmarking / "posicionamiento_relativo.md"
        if posic_path.exists():
            self.contexto["posicionamiento"] = posic_path.read_text(encoding="utf-8")[:2000]

        # M2
        for nombre in ["analisis_comparables.md", "posicionamiento_y_promesa.md",
                        "plan_go_to_market.md", "forecast_ventas.md"]:
            ruta = self.paths.m2_estrategia / nombre
            if ruta.exists():
                clave = nombre.replace(".md", "").replace("-", "_")
                self.contexto[clave] = ruta.read_text(encoding="utf-8")[:1500]

        campos_cargados = [k for k in self.contexto if k]
        print(f"   Insumos disponibles: {', '.join(campos_cargados)}")
        return True

    def _bloque_contexto(self, incluir: List[str] = None) -> str:
        """Construye el bloque de contexto para un prompt específico."""
        partes: List[str] = []
        campos = incluir or list(self.contexto.keys())

        libro_id = self.paths.libro_id
        autor = self.paths.autor
        partes.append(f"LIBRO: {libro_id} | AUTOR: {autor}\n")

        m = self.contexto.get("metricas") or {}
        if m:
            partes.append(
                f"Métricas: gravedad={m.get('gravedad_editorial','N/A')} | "
                f"estabilidad_voz={m.get('estabilidad_voz','N/A')} | "
                f"total_hallazgos={m.get('total_hallazgos','N/A')}\n"
            )

        b = (self.contexto.get("benchmark") or {}).get("posicion") or {}
        if b:
            percentil = (b.get("resumen") or {}).get("percentil_editorial_estimado", "N/A")
            listo = (b.get("resumen") or {}).get("listo_para_lanzar", False)
            partes.append(
                f"Benchmark: percentil={percentil}º | listo_para_lanzar={'Sí' if listo else 'No'}\n"
            )

        if "dictamen_editor_jefe" in campos and self.contexto.get("dictamen_editor_jefe"):
            partes.append(
                f"\n--- DICTAMEN DEL EDITOR JEFE ---\n"
                f"{self.contexto['dictamen_editor_jefe'][:2000]}\n"
            )

        if "posicionamiento" in campos and self.contexto.get("posicionamiento"):
            partes.append(
                f"\n--- POSICIONAMIENTO ---\n{self.contexto['posicionamiento'][:1000]}\n"
            )

        return "\n".join(partes)

    def _llamar_llm(self, user: str, max_tokens: int = 3000) -> str:
        resultado = self.router.chat(
            user_prompt=user,
            system=PROMPT_SISTEMA_OUTPUT,
            temperature=0.3,
            max_tokens=max_tokens,
        )
        if not resultado.get("success"):
            return f"*Error al generar: {resultado.get('error', 'desconocido')}*"
        return resultado.get("content", "")

    def generar_memo_adquisicion(self) -> bool:
        print("   Generando memo_adquisicion.md…")
        ctx = self._bloque_contexto()
        user = (
            f"{ctx}\n\n"
            "Escribí un MEMO DE ADQUISICIÓN de 1-2 páginas para un editor externo o agente literario. "
            "Debe incluir:\n"
            "1. Quién es el autor y qué hace único este libro.\n"
            "2. Para qué lector es (1 frase, concreta).\n"
            "3. La propuesta del libro en 2-3 frases.\n"
            "4. Estado editorial actual (honesto, sin exagerar ni minimizar).\n"
            "5. Potencial comercial con base en el benchmark.\n"
            "6. Lo que el libro necesita antes de estar listo.\n\n"
            "Tono: profesional, directo, como lo escribiría un editor que cree en el proyecto."
        )
        contenido = self._llamar_llm(user, max_tokens=2000)
        self._guardar_doc("memo_adquisicion.md", "Memo de Adquisición", contenido)
        return True

    def generar_diagnostico_desarrollo(self) -> bool:
        print("   Generando diagnostico_desarrollo.md…")
        criticos = self.contexto.get("hallazgos_criticos") or []
        fortalezas = self.contexto.get("fortalezas") or []

        criticos_texto = "\n".join(
            f"  - [{h.get('id')}] {h.get('descripcion','')[:100]}" for h in criticos
        ) or "  (ninguno con severidad ≥4)"
        fortalezas_texto = "\n".join(
            f"  - [{h.get('id')}] {h.get('descripcion','')[:100]}" for h in fortalezas
        ) or "  (ninguna registrada)"

        ctx = self._bloque_contexto(["metricas", "dictamen_editor_jefe"])
        user = (
            f"{ctx}\n\n"
            f"Hallazgos críticos:\n{criticos_texto}\n\n"
            f"Fortalezas registradas:\n{fortalezas_texto}\n\n"
            "Escribí el DIAGNÓSTICO DE DESARROLLO del libro, dirigido al autor. Incluye:\n"
            "1. Estado actual del libro en una frase directa.\n"
            "2. Las 3-5 cosas que el libro tiene bien (con evidencia).\n"
            "3. Las 3-5 cosas que necesitan trabajo (con evidencia y sin catastrofismo).\n"
            "4. Qué tipo de libro es este en verdad (no el que el autor cree que escribió, "
            "sino el que el diagnóstico muestra).\n\n"
            "Tono: carta de editor a autor. Directo, respetuoso, honesto. No condescendiente."
        )
        contenido = self._llamar_llm(user, max_tokens=2500)
        self._guardar_doc("diagnostico_desarrollo.md", "Diagnóstico de Desarrollo", contenido)
        return True

    def generar_plan_intervencion(self) -> bool:
        print("   Generando plan_intervencion.md…")
        ctx = self._bloque_contexto(["metricas", "dictamen_editor_jefe", "benchmark"])
        backlog_path = self.paths.backlog_path()
        backlog_resumen = ""
        if backlog_path.exists():
            with open(backlog_path, encoding="utf-8") as f:
                backlog = json.load(f)
            top10 = (backlog.get("backlog") or [])[:10]
            backlog_resumen = "\n".join(
                f"  {i}. [{item['id']}] sev:{item.get('severidad','?')} — "
                f"{item.get('descripcion','')[:80]}"
                for i, item in enumerate(top10, 1)
            )

        user = (
            f"{ctx}\n\n"
            f"Top 10 del backlog priorizado:\n{backlog_resumen or '  (backlog no disponible)'}\n\n"
            "Escribí el PLAN DE INTERVENCIÓN, dirigido al autor. Debe:\n"
            "1. Dividir el trabajo en FASES (máximo 3). Cada fase con objetivo claro y tiempo estimado.\n"
            "2. Para cada fase, listar las acciones concretas (no más de 5 por fase).\n"
            "3. Indicar qué NO tocar en esta ronda (para proteger la voz).\n"
            "4. Dar una secuencia: qué resolver antes de qué, y por qué ese orden.\n\n"
            "Tono: plan de trabajo, no lista de deseos. Cada ítem debe ser accionable hoy."
        )
        contenido = self._llamar_llm(user, max_tokens=2500)
        self._guardar_doc("plan_intervencion.md", "Plan de Intervención", contenido)
        return True

    def generar_estrategia_publicacion(self) -> bool:
        print("   Generando estrategia_publicacion.md…")
        ctx = self._bloque_contexto(["posicionamiento", "analisis_comparables",
                                      "posicionamiento_y_promesa", "plan_go_to_market",
                                      "forecast_ventas"])
        user = (
            f"{ctx}\n\n"
            "Sintetizá la ESTRATEGIA DE PUBLICACIÓN en un documento para el autor. Incluye:\n"
            "1. Propuesta de valor definitiva (la que el autor debería decir cuando le pregunten).\n"
            "2. Canal de publicación recomendado y por qué.\n"
            "3. Cronograma de lanzamiento (basado en el estado editorial actual).\n"
            "4. 3 acciones de pre-lanzamiento.\n"
            "5. Expectativas realistas de alcance en los primeros 6 meses.\n\n"
            "Tono: asesor editorial. Honesto sobre los plazos y las posibilidades."
        )
        contenido = self._llamar_llm(user, max_tokens=2500)
        self._guardar_doc("estrategia_publicacion.md", "Estrategia de Publicación", contenido)
        return True

    def generar_brief_ejecutivo(self) -> bool:
        print("   Generando brief_final_ejecutivo.md…")
        resumen = self.contexto.get("resumen_ejecutivo") or ""
        ctx = self._bloque_contexto(["metricas", "benchmark"])
        user = (
            f"{ctx}\n\n"
            f"Resumen ejecutivo del Editor Jefe:\n{resumen[:1500]}\n\n"
            "Escribí el BRIEF FINAL EJECUTIVO: exactamente 1 página (350-450 palabras). "
            "Este documento es lo primero que alguien lee. Debe responder en orden:\n"
            "  1. ¿Qué es este libro?\n"
            "  2. ¿Está listo para publicarse?\n"
            "  3. ¿Cuál es su fortaleza principal?\n"
            "  4. ¿Cuál es su problema principal?\n"
            "  5. ¿Qué pasa primero?\n\n"
            "Tono: ejecutivo. Una sola lectura alcanza para entender todo."
        )
        contenido = self._llamar_llm(user, max_tokens=800)
        self._guardar_doc("brief_final_ejecutivo.md", "Brief Final Ejecutivo", contenido)
        return True

    def _guardar_doc(self, nombre_archivo: str, titulo: str, contenido: str) -> None:
        ruta = self.paths.m7_output_profesional / nombre_archivo
        ruta.write_text(
            f"# {titulo} — {self.paths.libro_id}\n\n"
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
            f"Alexandria Writer v3*\n\n---\n\n"
            + contenido,
            encoding="utf-8",
        )
        print(f"   {nombre_archivo} guardado.")

    def ejecutar(self) -> bool:
        print("\n   [M7] Iniciando generación de output profesional…")
        self.paths.m7_output_profesional.mkdir(parents=True, exist_ok=True)

        if not self.cargar_todos_los_insumos():
            return False

        if not self.generar_brief_ejecutivo():
            return False
        if not self.generar_diagnostico_desarrollo():
            return False
        if not self.generar_plan_intervencion():
            return False
        if not self.generar_estrategia_publicacion():
            return False
        if not self.generar_memo_adquisicion():
            return False

        print("   [M7] Output profesional completado.")
        print(f"   Entregables en: {self.paths.m7_output_profesional}")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 7: Output Profesional")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloOutputProfesional(paths)
    exit(0 if modulo.ejecutar() else 1)
