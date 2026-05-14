#!/usr/bin/env python3
"""
MÓDULO 3: EVIDENCIA Y TRAZABILIDAD (v3)
=========================================
Responsabilidad: ser el LIBRO MAYOR del sistema.
Todo hallazgo, recomendación y decisión pasa por aquí.

No usa LLM. Es procesamiento puro de datos:
  1. Consolida hallazgos de M1 en evidencia_store.jsonl.
  2. Detecta duplicados semánticos simples (por similitud de texto).
  3. Construye trazabilidad_graph.md (quién generó qué y por qué sobrevivió).
  4. Inicializa conflict_log.json (lo rellena M4).

Salidas (en m3_evidencia/):
  - evidencia_store.jsonl   (registro inmutable, append-only)
  - trazabilidad_graph.md   (dependencia hallazgo → agente → chunk)
  - conflict_log.json       (inicializado aquí, completado por M4)
  - resumen_evidencia.json  (métricas de calidad del sistema)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from config_v3 import ProyectoPaths
from schemas_v3 import Hallazgo, cargar_hallazgos, append_evidencia_store


class ModuloEvidencia:
    """
    Construye el registro de evidencia auditable del sistema.
    Opera sobre las salidas de M1 (y opcionalmente M2 si tiene hallazgos).
    """

    # Umbral de similitud para detectar duplicados por texto
    UMBRAL_SIMILITUD_CHARS = 0.6

    def __init__(self, paths: ProyectoPaths):
        self.paths = paths
        self.hallazgos: List[Hallazgo] = []
        self.hallazgos_deduplicados: List[Hallazgo] = []
        self.conflictos_potenciales: List[Dict] = []

    def cargar_hallazgos_m1(self) -> bool:
        hallazgos_path = self.paths.hallazgos_path()
        if not hallazgos_path.exists():
            print(f"   [ERROR] hallazgos.json no encontrado. Ejecutá M1 primero.")
            return False
        self.hallazgos = cargar_hallazgos(str(hallazgos_path))
        print(f"   Hallazgos cargados de M1: {len(self.hallazgos)}")
        return True

    def _similitud_texto(self, a: str, b: str) -> float:
        """Similitud simple por palabras comunes (Jaccard)."""
        a_words = set(a.lower().split())
        b_words = set(b.lower().split())
        if not a_words or not b_words:
            return 0.0
        interseccion = a_words & b_words
        union = a_words | b_words
        return len(interseccion) / len(union)

    def deduplicar_hallazgos(self) -> bool:
        """
        Elimina duplicados semánticos usando similitud de texto en `descripcion`.
        Marca el hallazgo sobreviviente con `razon_sobrevivencia`.
        """
        print("   Deduplicando hallazgos por similitud de texto…")
        vistos: List[Hallazgo] = []
        duplicados: Set[str] = set()

        for h in self.hallazgos:
            if h.id in duplicados:
                continue
            es_duplicado = False
            for existente in vistos:
                if existente.tipo != h.tipo:
                    continue
                sim = self._similitud_texto(h.descripcion, existente.descripcion)
                if sim >= self.UMBRAL_SIMILITUD_CHARS:
                    duplicados.add(h.id)
                    es_duplicado = True
                    # Guardar como conflicto potencial para M4
                    self.conflictos_potenciales.append({
                        "hallazgo_a": existente.id,
                        "hallazgo_b": h.id,
                        "similitud": round(sim, 3),
                        "tipo": "duplicado_semantico",
                    })
                    break
            if not es_duplicado:
                if not h.razon_sobrevivencia:
                    h.razon_sobrevivencia = "Hallazgo único — sin duplicados detectados."
                vistos.append(h)

        self.hallazgos_deduplicados = vistos
        eliminados = len(self.hallazgos) - len(vistos)
        print(f"   Hallazgos únicos: {len(vistos)} (eliminados {eliminados} duplicados)")
        return True

    def construir_evidencia_store(self) -> bool:
        """Escribe evidencia_store.jsonl con los hallazgos deduplicados."""
        self.paths.m3_evidencia.mkdir(parents=True, exist_ok=True)
        evidencia_path = self.paths.evidencia_store_path()

        # Escribir desde cero (no append en este paso inicial)
        with open(evidencia_path, "w", encoding="utf-8") as f:
            for h in self.hallazgos_deduplicados:
                f.write(json.dumps(h.to_dict(), ensure_ascii=False) + "\n")

        print(f"   evidencia_store.jsonl: {len(self.hallazgos_deduplicados)} entradas")
        return True

    def construir_trazabilidad_graph(self) -> bool:
        """Genera trazabilidad_graph.md con la cadena hallazgo → agente → chunk."""
        por_agente: Dict[str, List[Hallazgo]] = {}
        for h in self.hallazgos_deduplicados:
            por_agente.setdefault(h.agente, []).append(h)

        lineas = [
            f"# Grafo de Trazabilidad — {self.paths.libro_id}\n",
            f"*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
            f"*Total hallazgos: {len(self.hallazgos_deduplicados)}*\n\n---\n",
        ]

        for agente, grupo in sorted(por_agente.items()):
            lineas.append(f"\n## Agente: `{agente}` ({len(grupo)} hallazgos)\n")
            for h in sorted(grupo, key=lambda x: -x.severidad)[:10]:
                lineas.append(
                    f"- **{h.id}** | chunk: {h.chunk_ref} | "
                    f"sev: {h.severidad} | conf: {h.confianza:.0%} | "
                    f"{h.descripcion[:80]}…"
                )
            if len(grupo) > 10:
                lineas.append(f"- *… y {len(grupo) - 10} más*")

        # Métricas de trazabilidad
        con_cita = sum(1 for h in self.hallazgos_deduplicados if h.cita_textual)
        pct_cita = con_cita / max(len(self.hallazgos_deduplicados), 1)
        lineas.append(f"\n---\n\n## Métricas de trazabilidad\n")
        lineas.append(f"- Hallazgos con cita textual: {con_cita}/{len(self.hallazgos_deduplicados)} ({pct_cita:.0%})")
        lineas.append(f"- Meta: ≥ 90%")
        if pct_cita < 0.9:
            lineas.append(f"- ⚠️ Por debajo del umbral. El sistema debe mejorar la extracción de citas.")

        ruta = self.paths.m3_evidencia / "trazabilidad_graph.md"
        ruta.write_text("\n".join(lineas), encoding="utf-8")
        print(f"   trazabilidad_graph.md guardado.")
        return True

    def inicializar_conflict_log(self) -> bool:
        """Inicializa conflict_log.json con los conflictos detectados en deduplicación."""
        conflict_log = {
            "libro_id": self.paths.libro_id,
            "timestamp_inicializacion": datetime.now().isoformat(),
            "nota": "Inicializado por M3. Completado por M4 (Editor Jefe).",
            "conflictos": self.conflictos_potenciales,
        }
        conflict_path = self.paths.conflict_log_path()
        with open(conflict_path, "w", encoding="utf-8") as f:
            json.dump(conflict_log, f, indent=2, ensure_ascii=False)
        print(f"   conflict_log.json inicializado con {len(self.conflictos_potenciales)} conflictos potenciales.")
        return True

    def guardar_resumen(self) -> bool:
        con_cita = sum(1 for h in self.hallazgos_deduplicados if h.cita_textual)
        resumen = {
            "libro_id": self.paths.libro_id,
            "timestamp": datetime.now().isoformat(),
            "total_hallazgos_m1": len(self.hallazgos),
            "total_hallazgos_deduplicados": len(self.hallazgos_deduplicados),
            "duplicados_eliminados": len(self.hallazgos) - len(self.hallazgos_deduplicados),
            "conflictos_potenciales": len(self.conflictos_potenciales),
            "hallazgos_con_cita_textual": con_cita,
            "pct_trazabilidad_completa": round(
                con_cita / max(len(self.hallazgos_deduplicados), 1), 3
            ),
            "alerta_trazabilidad": con_cita / max(len(self.hallazgos_deduplicados), 1) < 0.9,
        }
        ruta = self.paths.m3_evidencia / "resumen_evidencia.json"
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)
        print(f"   resumen_evidencia.json guardado.")
        return True

    def ejecutar(self) -> bool:
        print("\n   [M3] Iniciando evidencia y trazabilidad…")

        if not self.cargar_hallazgos_m1():
            return False
        if not self.deduplicar_hallazgos():
            return False
        if not self.construir_evidencia_store():
            return False
        if not self.construir_trazabilidad_graph():
            return False
        if not self.inicializar_conflict_log():
            return False
        if not self.guardar_resumen():
            return False

        print("   [M3] Evidencia y trazabilidad completadas.")
        return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 3: Evidencia y Trazabilidad")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloEvidencia(paths)
    exit(0 if modulo.ejecutar() else 1)
