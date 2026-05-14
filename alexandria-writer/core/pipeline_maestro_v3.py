#!/usr/bin/env python3
"""
ALEXANDRIA WRITER — PIPELINE MAESTRO v3
========================================
Orquesta los 8 módulos del sistema editorial inteligente.

Flujo:
  M0 Ingesta → M1 Diagnóstico → M2 Estrategia
       ↓              ↓               ↓
  M3 Evidencia ← M5 Riesgos ← M4 Editor Jefe
       ↓              ↓
  M6 Benchmarking → M7 Output Profesional

Uso:
  python core/pipeline_maestro_v3.py --autor Arturo_Ledezma --libro TSBN
  python core/pipeline_maestro_v3.py --autor Arturo_Ledezma --libro TSBN --modo rapido
  python core/pipeline_maestro_v3.py --autor Arturo_Ledezma --libro TSBN --skip m1
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# ─── Paths ───
CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from config_v3 import ProyectoPaths, AUTORES_ROOT
from schemas_v3 import MetricasEditoriales

# ─── Módulos v3 (se importan dinámicamente para permitir desarrollo incremental) ───

MODULOS_DISPONIBLES = {
    "m0": "m0_ingesta",
    "m1": "m1_diagnostico",
    "m2": "m2_estrategia",
    "m3": "m3_evidencia",
    "m4": "m4_editor_jefe",
    "m5": "m5_control_riesgo",
    "m6": "m6_benchmarking",
    "m7": "m7_output_profesional",
}


def importar_modulo(nombre: str):
    """Importa un módulo v3 si existe; de lo contrario devuelve None."""
    try:
        return __import__(nombre)
    except ImportError:
        return None


class PipelineMaestroV3:
    def __init__(
        self,
        autor: str,
        libro_id: str,
        modo: str = "completo",
        skip: Optional[List[str]] = None,
        solo: Optional[str] = None,
        pdf_nombre: Optional[str] = None,
    ):
        self.autor = autor
        self.libro_id = libro_id
        self.modo = modo
        self.skip = set(skip or [])
        self.solo = solo
        self.pdf_nombre = pdf_nombre
        self.paths = ProyectoPaths(autor, libro_id)
        self.start_time = datetime.now()
        self.log = {
            "version": "v3",
            "inicio": self.start_time.isoformat(),
            "autor": autor,
            "libro": libro_id,
            "modo": modo,
            "modulos": [],
        }
        self.metricas_sistema = {
            "total_hallazgos_generados": 0,
            "total_hallazgos_bloqueados": 0,
            "total_conflictos": 0,
            "tiempo_end_to_end_minutos": 0.0,
        }

    def print_banner(self):
        print("\n" + "=" * 70)
        print("   ALEXANDRIA WRITER — PIPELINE MAESTRO v3")
        print("   Sistema Editorial Inteligente")
        print("=" * 70)
        print(f"\n   Autor:  {self.autor}")
        print(f"   Libro:  {self.libro_id}")
        print(f"   Modo:   {self.modo}")
        if self.solo:
            print(f"   Solo módulo: {self.solo}")
        if self.skip:
            print(f"   Skip:   {', '.join(sorted(self.skip))}")
        print("\n   Flujo de trabajo:")
        print("   M0: Ingesta → M1: Diagnóstico → M2: Estrategia")
        print("        ↓            ↓                  ↓")
        print("   M3: Evidencia ← M5: Riesgos ← M4: Editor Jefe")
        print("        ↓                              ↓")
        print("   M6: Benchmarking → M7: Output Profesional")
        print("=" * 70)

    def _registrar_modulo(self, nombre: str, estado: str, detalles: dict = None):
        entry = {
            "modulo": nombre,
            "estado": estado,
            "timestamp": datetime.now().isoformat(),
        }
        if detalles:
            entry["detalles"] = detalles
        self.log["modulos"].append(entry)

    def ejecutar_m0(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 0: INGESTA Y CONTEXTO DEL AUTOR")
        print("─" * 70)
        mod = importar_modulo("m0_ingesta")
        if mod is None:
            print("   [SKIP] m0_ingesta.py aún no implementado.")
            self._registrar_modulo("m0", "SKIP_NO_IMPLEMENTADO")
            return True  # Permitir continuar

        try:
            runner = mod.ModuloIngesta(self.paths, pdf_nombre=self.pdf_nombre)
            success = runner.ejecutar()
            self._registrar_modulo("m0", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M0: {e}")
            self._registrar_modulo("m0", "ERROR", {"mensaje": str(e)})
            return False

    def ejecutar_m1(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 1: DIAGNÓSTICO EDITORIAL")
        print("─" * 70)
        mod = importar_modulo("m1_diagnostico")
        if mod is None:
            print("   [SKIP] m1_diagnostico.py aún no implementado.")
            self._registrar_modulo("m1", "SKIP_NO_IMPLEMENTADO")
            return True
        try:
            runner = mod.ModuloDiagnostico(self.paths, modo=self.modo)
            success = runner.ejecutar()
            self._registrar_modulo("m1", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M1: {e}")
            self._registrar_modulo("m1", "ERROR", {"mensaje": str(e)})
            return False

    def ejecutar_m2(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 2: ESTRATEGIA DE MERCADO")
        print("─" * 70)
        mod = importar_modulo("m2_estrategia")
        if mod is None:
            print("   [SKIP] m2_estrategia.py aún no implementado.")
            self._registrar_modulo("m2", "SKIP_NO_IMPLEMENTADO")
            return True
        try:
            runner = mod.ModuloEstrategia(self.paths)
            success = runner.ejecutar()
            self._registrar_modulo("m2", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M2: {e}")
            self._registrar_modulo("m2", "ERROR", {"mensaje": str(e)})
            return False

    def ejecutar_m3(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 3: EVIDENCIA Y TRAZABILIDAD")
        print("─" * 70)
        mod = importar_modulo("m3_evidencia")
        if mod is None:
            print("   [SKIP] m3_evidencia.py aún no implementado.")
            self._registrar_modulo("m3", "SKIP_NO_IMPLEMENTADO")
            return True
        try:
            runner = mod.ModuloEvidencia(self.paths)
            success = runner.ejecutar()
            self._registrar_modulo("m3", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M3: {e}")
            self._registrar_modulo("m3", "ERROR", {"mensaje": str(e)})
            return False

    def ejecutar_m4(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 4: EDITOR JEFE / ARBITRAJE CENTRAL")
        print("─" * 70)
        mod = importar_modulo("m4_editor_jefe")
        if mod is None:
            print("   [SKIP] m4_editor_jefe.py aún no implementado.")
            self._registrar_modulo("m4", "SKIP_NO_IMPLEMENTADO")
            return True
        try:
            runner = mod.ModuloEditorJefe(self.paths)
            success = runner.ejecutar()
            self._registrar_modulo("m4", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M4: {e}")
            self._registrar_modulo("m4", "ERROR", {"mensaje": str(e)})
            return False

    def ejecutar_m5(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 5: CONTROL DE RIESGO")
        print("─" * 70)
        mod = importar_modulo("m5_control_riesgo")
        if mod is None:
            print("   [SKIP] m5_control_riesgo.py aún no implementado.")
            self._registrar_modulo("m5", "SKIP_NO_IMPLEMENTADO")
            return True
        try:
            runner = mod.ModuloControlRiesgo(self.paths)
            success = runner.ejecutar()
            self._registrar_modulo("m5", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M5: {e}")
            self._registrar_modulo("m5", "ERROR", {"mensaje": str(e)})
            return False

    def ejecutar_m6(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 6: BENCHMARKING Y COMPARATIVA")
        print("─" * 70)
        mod = importar_modulo("m6_benchmarking")
        if mod is None:
            print("   [SKIP] m6_benchmarking.py aún no implementado.")
            self._registrar_modulo("m6", "SKIP_NO_IMPLEMENTADO")
            return True
        try:
            runner = mod.ModuloBenchmarking(self.paths)
            success = runner.ejecutar()
            self._registrar_modulo("m6", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M6: {e}")
            self._registrar_modulo("m6", "ERROR", {"mensaje": str(e)})
            return False

    def ejecutar_m7(self) -> bool:
        print("\n" + "─" * 70)
        print("   MÓDULO 7: OUTPUT PROFESIONAL")
        print("─" * 70)
        mod = importar_modulo("m7_output_profesional")
        if mod is None:
            print("   [SKIP] m7_output_profesional.py aún no implementado.")
            self._registrar_modulo("m7", "SKIP_NO_IMPLEMENTADO")
            return True
        try:
            runner = mod.ModuloOutputProfesional(self.paths)
            success = runner.ejecutar()
            self._registrar_modulo("m7", "COMPLETADO" if success else "FALLIDO")
            return success
        except Exception as e:
            print(f"   [ERROR] M7: {e}")
            self._registrar_modulo("m7", "ERROR", {"mensaje": str(e)})
            return False

    def guardar_log(self):
        self.log["fin"] = datetime.now().isoformat()
        duracion = (datetime.now() - self.start_time).total_seconds() / 60
        self.log["duracion_minutos"] = round(duracion, 2)
        self.metricas_sistema["tiempo_end_to_end_minutos"] = round(duracion, 2)
        self.log["metricas_sistema"] = self.metricas_sistema

        log_path = self.paths.proyecto_dir / "pipeline_log_v3.json"
        self.paths.proyecto_dir.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.log, f, indent=2, ensure_ascii=False)
        print(f"\n  Log guardado: {log_path}")

    def resumen_final(self):
        print("\n" + "=" * 70)
        print("   PIPELINE v3 COMPLETADO")
        print("=" * 70)
        print(f"\n   Duración total: {self.log['duracion_minutos']} minutos")
        print("\n   Estado por módulo:")
        for m in self.log["modulos"]:
            icono = "✅" if m["estado"] == "COMPLETADO" else "⏭️" if "SKIP" in m["estado"] else "❌"
            print(f"   {icono} {m['modulo'].upper()}: {m['estado']}")
        print("\n   Entregables finales (M7):")
        print(f"   → {self.paths.m7_entregas}")
        print("=" * 70)

    def ejecutar(self):
        self.print_banner()
        self.paths.ensure_dirs()

        # Si se especificó --solo, ejecutar solo ese módulo
        if self.solo:
            ejecutor = getattr(self, f"ejecutar_{self.solo}", None)
            if ejecutor:
                ejecutor()
            else:
                print(f"[ERROR] Módulo '{self.solo}' desconocido.")
            self.guardar_log()
            return

        # Orden de ejecución
        orden = ["m0", "m1", "m2", "m3", "m5", "m4", "m6", "m7"]

        for modulo in orden:
            if modulo in self.skip:
                print(f"\n  [SKIP] {modulo} omitido por flag.")
                self._registrar_modulo(modulo, "OMITIDO")
                continue

            ejecutor = getattr(self, f"ejecutar_{modulo}")
            success = ejecutor()

            # M0, M1 y M2 son críticos; si fallan, abortar
            if modulo in ("m0", "m1") and not success:
                print(f"\n  [ABORT] {modulo} falló. Deteniendo pipeline.")
                self.guardar_log()
                return

        self.guardar_log()
        self.resumen_final()


def main():
    parser = argparse.ArgumentParser(description="Pipeline Maestro v3 — Alexandria Writer")
    parser.add_argument("--autor", required=True, help="Nombre de la carpeta del autor (ej: Arturo_Ledezma)")
    parser.add_argument("--libro", required=True, help="ID del libro/proyecto (ej: TSBN)")
    parser.add_argument("--modo", default="completo",
                        choices=["completo", "rapido", "diagnostico", "estrategia", "editor_jefe"],
                        help="Modo de ejecución")
    parser.add_argument("--solo", default=None,
                        choices=["m0", "m1", "m2", "m3", "m4", "m5", "m6", "m7"],
                        help="Ejecutar solo un módulo específico")
    parser.add_argument("--skip", nargs="+", default=None,
                        choices=["m0", "m1", "m2", "m3", "m4", "m5", "m6", "m7"],
                        help="Saltar uno o más módulos")
    parser.add_argument("--pdf", default=None, help="Nombre específico del PDF (si hay varios)")
    args = parser.parse_args()

    pipeline = PipelineMaestroV3(
        autor=args.autor,
        libro_id=args.libro,
        modo=args.modo,
        skip=args.skip,
        solo=args.solo,
        pdf_nombre=args.pdf,
    )
    pipeline.ejecutar()


if __name__ == "__main__":
    main()
