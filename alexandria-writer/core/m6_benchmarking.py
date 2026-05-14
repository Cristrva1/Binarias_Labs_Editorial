#!/usr/bin/env python3
"""
MÓDULO 6: BENCHMARKING Y COMPARATIVA (v3)
===========================================
Responsabilidad: posicionar el manuscrito en su ecosistema de mercado
a partir de las métricas editoriales de M1 y el análisis de M2.

No es un módulo de marketing. Es un módulo de calibración:
  - ¿En qué percentil editorial está el libro respecto a su género?
  - ¿Cuánto trabajo queda vs. libros comparables publicados?
  - ¿Las fortalezas del libro son diferenciadores reales o genéricos?

Salidas (en m6_benchmarking/):
  - benchmark.json               (datos estructurados)
  - posicionamiento_relativo.md  (informe legible)
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


# Umbrales editoriales de referencia (basados en práctica editorial)
UMBRALES_EDITORIALES = {
    "gravedad_baja":     (0.0, 1.5),
    "gravedad_media":    (1.5, 2.8),
    "gravedad_alta":     (2.8, 4.0),
    "gravedad_critica":  (4.0, 5.0),
    "estabilidad_voz_excelente":  (0.85, 1.0),
    "estabilidad_voz_buena":      (0.70, 0.85),
    "estabilidad_voz_fragil":     (0.50, 0.70),
    "estabilidad_voz_inestable":  (0.0, 0.50),
    "densidad_limpia":   (0.0, 3.0),
    "densidad_trabajosa": (3.0, 7.0),
    "densidad_densa":    (7.0, float("inf")),
}


def clasificar_metrica(valor: float, pares: List[tuple]) -> str:
    for nombre, (lo, hi) in [
        (k, v) for k, v in UMBRALES_EDITORIALES.items()
        if k.startswith(pares[0])
    ]:
        if lo <= valor < hi:
            return nombre
    return "sin_clasificar"


class ModuloBenchmarking:
    """
    Calibra el manuscrito frente a umbrales editoriales de referencia.
    """

    def __init__(self, paths: ProyectoPaths):
        self.paths = paths
        self.router = LLMRouter()
        self.metricas: Dict = {}
        self.bible: Dict = {}
        self.comparables_md: str = ""

    def cargar_insumos(self) -> bool:
        metricas_path = self.paths.metricas_editoriales_path()
        if not metricas_path.exists():
            print("   [ERROR] metricas_editoriales.json no encontrado. Ejecutá M1.")
            return False
        with open(metricas_path, encoding="utf-8") as f:
            self.metricas = json.load(f)
        print(f"   Métricas cargadas.")

        bible_path = self.paths.bible_path()
        if bible_path.exists():
            with open(bible_path, encoding="utf-8") as f:
                self.bible = json.load(f)

        comparables_path = self.paths.m2_estrategia / "analisis_comparables.md"
        if comparables_path.exists():
            self.comparables_md = comparables_path.read_text(encoding="utf-8")[:3000]
        return True

    def clasificar_posicion(self) -> Dict:
        """Clasifica el libro según los umbrales de referencia."""
        gravedad = self.metricas.get("gravedad_editorial", 0.0)
        estabilidad = self.metricas.get("estabilidad_voz", 1.0)
        densidad = self.metricas.get("densidad_problemas", 0.0)
        total_h = self.metricas.get("total_hallazgos", 0)
        h_alta = self.metricas.get("hallazgos_severidad_alta", 0)

        # Clasificación de gravedad
        if gravedad < 1.5:
            nivel_gravedad = "bajo"
            label_gravedad = "Listo para revisión final"
        elif gravedad < 2.8:
            nivel_gravedad = "medio"
            label_gravedad = "Necesita trabajo focalizado"
        elif gravedad < 4.0:
            nivel_gravedad = "alto"
            label_gravedad = "Revisión estructural recomendada"
        else:
            nivel_gravedad = "critico"
            label_gravedad = "Revisión profunda requerida"

        # Clasificación de voz
        if estabilidad >= 0.85:
            nivel_voz = "excelente"
            label_voz = "Voz muy estable y consistente"
        elif estabilidad >= 0.70:
            nivel_voz = "buena"
            label_voz = "Voz estable con quiebres menores"
        elif estabilidad >= 0.50:
            nivel_voz = "fragil"
            label_voz = "Voz con inestabilidades notables"
        else:
            nivel_voz = "inestable"
            label_voz = "Voz requiere trabajo urgente"

        # Percentil estimado (basado en umbrales empíricos)
        score = (
            (1.0 - gravedad / 5.0) * 0.4
            + estabilidad * 0.4
            + (1.0 - min(densidad / 10.0, 1.0)) * 0.2
        )
        percentil = min(99, max(1, round(score * 100)))

        return {
            "gravedad_editorial": {
                "valor": gravedad,
                "nivel": nivel_gravedad,
                "label": label_gravedad,
            },
            "estabilidad_voz": {
                "valor": estabilidad,
                "nivel": nivel_voz,
                "label": label_voz,
            },
            "densidad_problemas": {
                "valor": densidad,
                "label": (
                    "Densidad limpia" if densidad < 3.0
                    else "Densidad trabajosa" if densidad < 7.0
                    else "Alta densidad"
                ),
            },
            "resumen": {
                "total_hallazgos": total_h,
                "hallazgos_alta_severidad": h_alta,
                "percentil_editorial_estimado": percentil,
                "listo_para_lanzar": nivel_gravedad in ("bajo", "medio") and nivel_voz in ("excelente", "buena"),
            },
        }

    def generar_analisis_con_llm(self, posicion: Dict) -> str:
        """Genera el análisis narrativo del posicionamiento."""
        percentil = posicion["resumen"]["percentil_editorial_estimado"]
        listo = posicion["resumen"]["listo_para_lanzar"]

        user = (
            f"Libro: {self.paths.libro_id}\n"
            f"Métricas editoriales:\n"
            f"  • Gravedad editorial: {posicion['gravedad_editorial']['valor']:.2f} → "
            f"{posicion['gravedad_editorial']['label']}\n"
            f"  • Estabilidad de voz: {posicion['estabilidad_voz']['valor']:.2f} → "
            f"{posicion['estabilidad_voz']['label']}\n"
            f"  • Densidad de problemas: {posicion['densidad_problemas']['valor']:.2f} → "
            f"{posicion['densidad_problemas']['label']}\n"
            f"  • Percentil editorial estimado: {percentil}º\n"
            f"  • ¿Listo para lanzar? {'Sí' if listo else 'No aún'}\n\n"
            f"Análisis de comparables disponible:\n{self.comparables_md[:1500]}\n\n"
            "Escribí un ANÁLISIS DE POSICIONAMIENTO RELATIVO de 300-500 palabras que incluya:\n"
            "1. Dónde está el libro en relación a los comparables de su género.\n"
            "2. Sus diferenciadores reales (no los genéricos que tiene cualquier libro).\n"
            "3. La distancia entre el estado actual y el estado publicable.\n"
            "4. Si el percentil estimado es consistente con la percepción cualitativa.\n\n"
            "Tono: editorial honesto. Sin exageraciones ni minimizaciones."
        )
        resultado = self.router.chat(
            user_prompt=user,
            system=(
                "Sos un especialista en benchmarking editorial. Tu trabajo es calibrar "
                "la posición de un manuscrito en su mercado, con honestidad y precisión."
            ),
            temperature=0.3,
            max_tokens=2000,
        )
        if not resultado.get("success"):
            return "*Error al generar análisis de posicionamiento.*"
        return resultado.get("content", "")

    def guardar_resultados(self, posicion: Dict, analisis: str) -> bool:
        self.paths.m6_benchmarking.mkdir(parents=True, exist_ok=True)

        # benchmark.json
        benchmark = {
            "libro_id": self.paths.libro_id,
            "timestamp": datetime.now().isoformat(),
            "posicion": posicion,
            "umbrales_referencia": {
                k: list(v) for k, v in UMBRALES_EDITORIALES.items()
                if not isinstance(v[1], float) or v[1] != float("inf")
            },
        }
        ruta_json = self.paths.benchmark_path()
        with open(ruta_json, "w", encoding="utf-8") as f:
            json.dump(benchmark, f, indent=2, ensure_ascii=False)
        print("   benchmark.json guardado.")

        # posicionamiento_relativo.md
        listo = posicion["resumen"]["listo_para_lanzar"]
        percentil = posicion["resumen"]["percentil_editorial_estimado"]
        ruta_md = self.paths.m6_benchmarking / "posicionamiento_relativo.md"
        ruta_md.write_text(
            f"# Posicionamiento Relativo — {self.paths.libro_id}\n\n"
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n"
            f"**Percentil editorial estimado: {percentil}º | "
            f"Listo para lanzar: {'Sí' if listo else 'No'}**\n\n---\n\n"
            + analisis,
            encoding="utf-8",
        )
        print("   posicionamiento_relativo.md guardado.")
        return True

    def ejecutar(self) -> bool:
        print("\n   [M6] Iniciando benchmarking y comparativa…")

        if not self.cargar_insumos():
            return False

        posicion = self.clasificar_posicion()
        percentil = posicion["resumen"]["percentil_editorial_estimado"]
        print(f"   Percentil editorial estimado: {percentil}º")

        analisis = self.generar_analisis_con_llm(posicion)

        if not self.guardar_resultados(posicion, analisis):
            return False

        print("   [M6] Benchmarking completado.")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 6: Benchmarking y Comparativa")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloBenchmarking(paths)
    exit(0 if modulo.ejecutar() else 1)
