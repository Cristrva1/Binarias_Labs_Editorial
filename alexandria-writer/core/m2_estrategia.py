#!/usr/bin/env python3
"""
MÓDULO 2: ESTRATEGIA DE MERCADO (v3)
======================================
Responsabilidad: responder CÓMO SE VENDERÍA Y POSICIONARÍA el libro,
basándose SOLO en el diagnóstico de M1 y el contexto del autor de M0.
No puede contradecir el diagnóstico. No inventa datos.

REGLA DE ORO: Si M1 dice "voz inestable", este módulo no puede
prometer "bestseller de referencia".

Agentes:
  - agente_comparables    — benchmarking contra obras del mismo género.
  - agente_posicionamiento — promesa comercial, hook, propuesta de valor.
  - agente_canales        — distribución, alianzas, formato óptimo.
  - agente_forecast       — estimación de ventas basada en comparables y diagnóstico.

Salidas (en m2_estrategia/):
  - analisis_comparables.md
  - posicionamiento_y_promesa.md
  - plan_go_to_market.md
  - forecast_ventas.md
  - alertas_riesgo.md  (conflictos diagnóstico ↔ marketing)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from config_v3 import ProyectoPaths
from schemas_v3 import MetricasEditoriales
from llm_router import LLMRouter


PROMPT_SISTEMA_ESTRATEGIA = """Sos un agente de estrategia de mercado del sistema Alexandria Writer v3.
Tu trabajo es analizar el potencial comercial de un manuscrito BASÁNDOTE en su diagnóstico editorial.

REGLAS DURAS:
1. NO podés contradecir el diagnóstico editorial. Si el libro tiene problemas graves de voz o estructura,
   tu análisis debe reflejarlo en las alertas de riesgo.
2. NO inventés datos de mercado. Si no tenés datos reales, decí "estimación sin datos" y explicá tu razonamiento.
3. NO hagas promesas comerciales que el libro no pueda sostener según su diagnóstico actual.
4. Devolvé SOLO el contenido solicitado, en Markdown bien formateado.
"""


class ModuloEstrategia:
    """
    Estrategia de mercado basada en M0 (contexto autor) + M1 (diagnóstico).
    """

    def __init__(self, paths: ProyectoPaths):
        self.paths = paths
        self.router = LLMRouter()
        self.bible: Dict = {}
        self.contexto_autor: Dict = {}
        self.metricas: Dict = {}
        self.alertas_riesgo: List[str] = []

    def cargar_insumos(self) -> bool:
        """Carga outputs de M0 y M1."""
        bible_path = self.paths.bible_path()
        if bible_path.exists():
            with open(bible_path, encoding="utf-8") as f:
                self.bible = json.load(f)
            print(f"   Bible cargada: {bible_path.name}")
        else:
            print(f"   [ADVERTENCIA] bible_del_libro.json no encontrado. M0 no corrió.")

        metricas_path = self.paths.metricas_editoriales_path()
        if metricas_path.exists():
            with open(metricas_path, encoding="utf-8") as f:
                self.metricas = json.load(f)
            print(f"   Métricas cargadas: {metricas_path.name}")
        else:
            print(f"   [ADVERTENCIA] metricas_editoriales.json no encontrado. M1 no corrió.")
            self.metricas = {}

        hallazgos_path = self.paths.hallazgos_path()
        self.hallazgos_resumen = ""
        if hallazgos_path.exists():
            with open(hallazgos_path, encoding="utf-8") as f:
                hallazgos = json.load(f)
            criticos = [h for h in hallazgos if h.get("severidad", 0) >= 4]
            fortalezas = [h for h in hallazgos if h.get("tipo") == "fortaleza"]
            self.hallazgos_resumen = (
                f"Total hallazgos: {len(hallazgos)} | "
                f"Críticos (sev≥4): {len(criticos)} | "
                f"Fortalezas: {len(fortalezas)}"
            )
            if criticos:
                self.alertas_riesgo.append(
                    f"El diagnóstico detectó {len(criticos)} hallazgos críticos. "
                    "Resolver estos antes de lanzar al mercado."
                )
        return True

    def _contexto_para_prompt(self) -> str:
        """Construye el bloque de contexto inyectable en todos los prompts de M2."""
        genero = (self.bible.get("estructura_detectada") or {}).get("genero", "no detectado")
        total_palabras = (self.bible.get("extraccion") or {}).get("total_palabras", "desconocido")
        gravedad = self.metricas.get("gravedad_editorial", "N/A")
        estabilidad_voz = self.metricas.get("estabilidad_voz", "N/A")
        densidad = self.metricas.get("densidad_problemas", "N/A")

        return (
            f"LIBRO: {self.paths.libro_id} | Autor: {self.paths.autor}\n"
            f"Palabras aprox.: {total_palabras}\n"
            f"Diagnóstico editorial:\n"
            f"  • Gravedad editorial: {gravedad} (umbral de alerta: 3.5)\n"
            f"  • Estabilidad de voz: {estabilidad_voz} (mínimo aceptable: 0.7)\n"
            f"  • Densidad de problemas: {densidad} por 1000 palabras\n"
            f"  • {self.hallazgos_resumen}\n"
        )

    def _llamar_agente(self, nombre: str, instruccion: str) -> str:
        contexto = self._contexto_para_prompt()
        user = f"{contexto}\n\n{instruccion}"
        resultado = self.router.chat(
            user_prompt=user,
            system=PROMPT_SISTEMA_ESTRATEGIA,
            temperature=0.3,
            max_tokens=3000,
        )
        if not resultado.get("success"):
            return f"*Error al generar {nombre}: {resultado.get('error', 'desconocido')}*\n"
        return resultado.get("content", "")

    def generar_comparables(self) -> bool:
        print("   [agente_comparables] analizando…")
        instruccion = (
            "Generá un análisis de COMPARABLES para este libro. Incluí:\n"
            "1. 5 libros del mismo género/subgénero con datos reales (autor, año, editorial).\n"
            "2. Para cada comparable: qué tiene en común con este manuscrito y qué lo diferencia.\n"
            "3. Posicionamiento relativo: ¿dónde encaja este libro en el mercado actual?\n"
            "4. Alertas: si el diagnóstico editorial indica problemas que afectan la comparabilidad, nombralos.\n\n"
            "Si no tenés datos de comparables reales para este nicho, decílo claramente y usá estimaciones."
        )
        contenido = self._llamar_agente("comparables", instruccion)
        ruta = self.paths.m2_estrategia / "analisis_comparables.md"
        ruta.write_text(
            f"# Análisis de Comparables — {self.paths.libro_id}\n\n"
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
            + contenido,
            encoding="utf-8",
        )
        print(f"   analisis_comparables.md guardado.")
        return True

    def generar_posicionamiento(self) -> bool:
        print("   [agente_posicionamiento] analizando…")
        instruccion = (
            "Generá el POSICIONAMIENTO COMERCIAL de este libro. Incluí:\n"
            "1. Hook de una línea (el gancho que engancha al lector en 15 palabras).\n"
            "2. Promesa central del libro (qué le entrega al lector).\n"
            "3. Propuesta de valor diferencial (por qué este y no otro).\n"
            "4. Subgénero y categoría de librería recomendada.\n"
            "5. Posibles subtítulos (3 opciones).\n\n"
            "IMPORTANTE: Si el diagnóstico indica problemas graves que aún no están resueltos, "
            "reflejalo en el nivel de confianza de esta propuesta."
        )
        contenido = self._llamar_agente("posicionamiento", instruccion)
        ruta = self.paths.m2_estrategia / "posicionamiento_y_promesa.md"
        ruta.write_text(
            f"# Posicionamiento y Promesa — {self.paths.libro_id}\n\n"
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
            + contenido,
            encoding="utf-8",
        )
        print(f"   posicionamiento_y_promesa.md guardado.")
        return True

    def generar_go_to_market(self) -> bool:
        print("   [agente_canales] analizando…")
        instruccion = (
            "Generá un PLAN GO-TO-MARKET para este libro. Incluí:\n"
            "1. Canales de distribución recomendados (digital, físico, audiolibro).\n"
            "2. Formato óptimo de publicación y precio sugerido.\n"
            "3. Alianzas estratégicas posibles (comunidades, influencers, instituciones).\n"
            "4. Primeras 4 semanas de lanzamiento: acciones concretas.\n"
            "5. Métricas de éxito a 90 días.\n\n"
            "Basate en el diagnóstico editorial: si el libro no está listo, el GTM debe incluir "
            "una fase de revisión antes del lanzamiento."
        )
        contenido = self._llamar_agente("canales", instruccion)
        ruta = self.paths.m2_estrategia / "plan_go_to_market.md"
        ruta.write_text(
            f"# Plan Go-To-Market — {self.paths.libro_id}\n\n"
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
            + contenido,
            encoding="utf-8",
        )
        print(f"   plan_go_to_market.md guardado.")
        return True

    def generar_forecast(self) -> bool:
        print("   [agente_forecast] analizando…")
        instruccion = (
            "Generá un FORECAST DE VENTAS conservador, realista y honesto. Incluí:\n"
            "1. Estimación de ventas a 3, 6 y 12 meses (rangos, no cifras exactas).\n"
            "2. Escenario pesimista / base / optimista.\n"
            "3. Factores que afectan el forecast positiva o negativamente.\n"
            "4. Cuándo tendría sentido lanzar según el estado actual del manuscrito.\n\n"
            "Advertencia: si los datos son insuficientes para una estimación confiable, "
            "decílo explícitamente. No infles las cifras."
        )
        contenido = self._llamar_agente("forecast", instruccion)
        ruta = self.paths.m2_estrategia / "forecast_ventas.md"
        ruta.write_text(
            f"# Forecast de Ventas — {self.paths.libro_id}\n\n"
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n\n"
            + contenido,
            encoding="utf-8",
        )
        print(f"   forecast_ventas.md guardado.")
        return True

    def generar_alertas_riesgo(self) -> bool:
        ruta = self.paths.m2_estrategia / "alertas_riesgo.md"
        lineas = [
            f"# Alertas de Riesgo Diagnóstico ↔ Estrategia — {self.paths.libro_id}\n",
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n---\n",
        ]
        if self.alertas_riesgo:
            lineas.append("\n## Conflictos detectados\n")
            for i, alerta in enumerate(self.alertas_riesgo, 1):
                lineas.append(f"\n{i}. {alerta}")
        else:
            lineas.append("\nNo se detectaron conflictos entre el diagnóstico y la estrategia.")
        ruta.write_text("\n".join(lineas), encoding="utf-8")
        print(f"   alertas_riesgo.md guardado.")
        return True

    def ejecutar(self) -> bool:
        print("\n   [M2] Iniciando estrategia de mercado…")
        self.paths.m2_estrategia.mkdir(parents=True, exist_ok=True)

        if not self.cargar_insumos():
            return False
        if not self.generar_comparables():
            return False
        if not self.generar_posicionamiento():
            return False
        if not self.generar_go_to_market():
            return False
        if not self.generar_forecast():
            return False
        if not self.generar_alertas_riesgo():
            return False

        print("   [M2] Estrategia de mercado completada.")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 2: Estrategia de Mercado")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloEstrategia(paths)
    exit(0 if modulo.ejecutar() else 1)
