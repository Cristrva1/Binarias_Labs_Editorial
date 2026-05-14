#!/usr/bin/env python3
"""
ALEXANDRIA WRITER — PIPELINE MAESTRO DE 4 EQUIPOS v2
=====================================================
Orquesta el trabajo secuencial de 4 equipos especializados:

  Equipo 1 → Inteligencia y Preparacion
     ↓ (entrega Bible del Libro)
  Equipo 2 → Analisis Editorial Profesional (v2: consolidado + YAML)
     ↓ (entrega Ediciones consolidadas, Top 30, metricas)
  Equipo 3 → Estrategia de Mercado y Go-to-Market (v2: 10 docs)
     ↓ (entrega Buyer Persona, GTM, Marketing, Distribucion, Forecast)
  Equipo 4 → Refinamiento e Implementacion
     ↓ (entrega Plan de edicion, conflictos resueltos, brief final)

Modos de operacion:
  --modo completo      → Pipeline completo (default)
  --modo transiciones  → Equipo 2 foco en flujo y estructura
  --modo tecnico       → Equipo 2 foco en calidad de prosa
  --modo marketing     → Equipo 2+3 foco en mercado
  --equipo N           → Ejecutar solo un equipo (1-4)
  --skip-equipo N      → Saltar un equipo (para continuar)

Uso:
  python core/pipeline_maestro.py
  python core/pipeline_maestro.py --modo transiciones
  python core/pipeline_maestro.py --equipo 1
  python core/pipeline_maestro.py --skip-equipo 1  (si ya hiciste E1)
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime

# Importar equipos v2
CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))
from pipeline_equipo_1_inteligencia import Equipo1Inteligencia
from pipeline_equipo_2_analisis_v2 import Equipo2AnalisisV2
from pipeline_equipo_3_estrategia_v2 import Equipo3EstrategiaV2
from pipeline_equipo_4_refinamiento import Equipo4Refinamiento

PROJECT = CORE_DIR.parent
PIPELINE_LOG = PROJECT / "projects" / "tsbn" / "pipeline_log.json"


class PipelineMaestro:
    def __init__(self, modo="completo", solo_equipo=None, skip_equipo=None):
        self.modo = modo
        self.solo_equipo = solo_equipo
        self.skip_equipo = skip_equipo
        self.start_time = datetime.now()
        self.log = {
            "inicio": self.start_time.isoformat(),
            "modo": modo,
            "equipos": []
        }
        # Leer respuestas del autor si existen
        self.contexto_autor = self._cargar_respuestas_autor()

    def _cargar_respuestas_autor(self):
        """Carga las respuestas del autor para calibrar el pipeline."""
        respuestas_path = PROJECT / "projects" / "tsbn" / "RESPUESTAS_AUTOR_TSBN.md"
        if respuestas_path.exists():
            with open(respuestas_path, "r", encoding="utf-8") as f:
                contenido = f.read()
            print(f"\n  [CONTEXT] Respuestas del autor cargadas: {len(contenido)} caracteres")
            return contenido
        print("\n  [CONTEXT] No se encontraron respuestas del autor. Ejecutando con defaults.")
        return ""

    def print_banner(self):
        print("\n" + "=" * 70)
        print("   ALEXANDRIA WRITER - PIPELINE MAESTRO v2")
        print("   4 Equipos de Trabajo Secuenciales")
        print("=" * 70)
        print(f"\n   Modo: {self.modo}")
        if self.solo_equipo:
            print(f"   Solo Equipo: {self.solo_equipo}")
        if self.skip_equipo:
            print(f"   Saltando Equipo: {self.skip_equipo}")
        if self.contexto_autor:
            print("\n   [CALIBRADO CON RESPUESTAS DEL AUTOR]")
            print("   Arturo Ledezma Ruan - 'Todas Son Buenas Noticias'")
            print("   Contexto cargado: intencion, lector ideal, estilo, prioridades")
        print("\n   Flujo de trabajo:")
        print("   E1: Inteligencia → E2: Analisis → E3: Estrategia → E4: Refinamiento")
        print("=" * 70)

    def ejecutar_equipo_1(self):
        print("\n" + "=" * 70)
        print("   INICIANDO EQUIPO 1: INTELIGENCIA Y PREPARACION")
        print("=" * 70)
        equipo = Equipo1Inteligencia()
        success = equipo.ejecutar()
        self.log["equipos"].append({
            "equipo": 1,
            "nombre": "Inteligencia y Preparacion",
            "estado": "COMPLETADO" if success else "FALLIDO",
            "timestamp": datetime.now().isoformat()
        })
        return success

    def ejecutar_equipo_2(self):
        print("\n" + "=" * 70)
        print("   INICIANDO EQUIPO 2: ANALISIS EDITORIAL PROFESIONAL v2")
        print("=" * 70)
        equipo = Equipo2AnalisisV2(modo=self.modo)
        success = equipo.ejecutar()
        self.log["equipos"].append({
            "equipo": 2,
            "nombre": "Analisis Editorial v2",
            "modo": self.modo,
            "estado": "COMPLETADO" if success else "FALLIDO",
            "timestamp": datetime.now().isoformat()
        })
        return success

    def ejecutar_equipo_3(self):
        print("\n" + "=" * 70)
        print("   INICIANDO EQUIPO 3: ESTRATEGIA DE MERCADO v2")
        print("=" * 70)
        equipo = Equipo3EstrategiaV2()
        success = equipo.ejecutar()
        self.log["equipos"].append({
            "equipo": 3,
            "nombre": "Estrategia de Mercado v2",
            "estado": "COMPLETADO" if success else "FALLIDO",
            "timestamp": datetime.now().isoformat()
        })
        return success

    def ejecutar_equipo_4(self):
        print("\n" + "=" * 70)
        print("   INICIANDO EQUIPO 4: REFINAMIENTO E IMPLEMENTACION")
        print("=" * 70)
        equipo = Equipo4Refinamiento()
        success = equipo.ejecutar()
        self.log["equipos"].append({
            "equipo": 4,
            "nombre": "Refinamiento e Implementacion",
            "estado": "COMPLETADO" if success else "FALLIDO",
            "timestamp": datetime.now().isoformat()
        })
        return success

    def guardar_log(self):
        self.log["fin"] = datetime.now().isoformat()
        self.log["duracion_minutos"] = round((datetime.now() - self.start_time).total_seconds() / 60, 2)

        os.makedirs(PIPELINE_LOG.parent, exist_ok=True)
        with open(PIPELINE_LOG, "w", encoding="utf-8") as f:
            import json
            json.dump(self.log, f, indent=2, ensure_ascii=False)
        print(f"\n  Log guardado: {PIPELINE_LOG}")

    def resumen_final(self):
        print("\n" + "=" * 70)
        print("   PIPELINE COMPLETADO")
        print("=" * 70)
        print(f"\n   Duracion total: {self.log['duracion_minutos']} minutos")
        print("\n   Entregables por equipo:")
        print("   ┌──────────────────────────────────────────────────────────┐")
        print("   │ EQUIPO 1 — Inteligencia                                  │")
        print("   │   → equipo1/01_BIBLE_DEL_LIBRO.md (documento maestro)  │")
        print("   │   → equipo1/02_MAPA_CAPITULOS.md                         │")
        print("   │   → equipo1/03_ANALISIS_TEMATICO.md                      │")
        print("   │   → equipo1/04_VOZ_TONO_ESTILO.md                        │")
        print("   │   → equipo1/05_PUBLICO_OBJETIVO.md                     │")
        print("   │   → equipo1/06_RESUMEN_EJECUTIVO.md                      │")
        print("   ├──────────────────────────────────────────────────────────┤")
        print("   │ EQUIPO 2 — Analisis Editorial v2                         │")
        print("   │   → equipo2/01_ANALISIS_5D.md (score por dimension)     │")
        print("   │   → equipo2/02_EDICIONES_CONSOLIDADAS.md (sin duplicados)│")
        print("   │   → equipo2/recomendaciones.json (parseable)             │")
        print("   │   → equipo2/03_TOP30_PRIORITARIO.md (cambios obligatorios)│")
        print("   │   → equipo2/04_OPORTUNIDADES.md (mejoras opcionales)    │")
        print("   │   → equipo2/05_METRICAS_CALIDAD.md (estadisticas)       │")
        print("   ├──────────────────────────────────────────────────────────┤")
        print("   │ EQUIPO 3 — Estrategia de Mercado v2                      │")
        print("   │   → equipo3/01_BUYER_PERSONA.md (perfil premium)        │")
        print("   │   → equipo3/02_ANALISIS_MERCADO.md (con datos reales)   │")
        print("   │   → equipo3/03_COMPARABLES.md (autores similares)        │")
        print("   │   → equipo3/04_GO_TO_MARKET.md (lanzamiento 0-90 dias)  │")
        print("   │   → equipo3/05_MARKETING_PLAN.md (12 meses)             │")
        print("   │   → equipo3/06_ESTRATEGIA_CONTENIDO.md (30 dias listo)   │")
        print("   │   → equipo3/07_KEYWORDS_SEO.md (Amazon + Google)         │")
        print("   │   → equipo3/08_DISTRIBUCION.md (canales y formatos)      │")
        print("   │   → equipo3/09_ALIANZAS_ESTRATEGICAS.md (contactos)    │")
        print("   │   → equipo3/10_FORECAST_VENTAS.md (24 meses)            │")
        print("   ├──────────────────────────────────────────────────────────┤")
        print("   │ EQUIPO 4 — Refinamiento e Implementacion                   │")
        print("   │   → equipo4/01_PLAN_EDICION_CALENDARIO.md (8 semanas)  │")
        print("   │   → equipo4/02_CONFLICTOS_RESUELTOS.md                   │")
        print("   │   → equipo4/03_CRONOGRAMA_INTEGRADO.md                     │")
        print("   │   → equipo4/04_BRIEF_FINAL_EJECUTIVO.md (1 pagina)     │")
        print("   │   → equipo4/05_PROXIMAS_ITERACIONES.md                   │")
        print("   └──────────────────────────────────────────────────────────┘")
        print("\n   Proximos pasos:")
        print("   1. Leer equipo4/04_BRIEF_FINAL_EJECUTIVO.md (2 minutos)")
        print("   2. Revisar equipo4/01_PLAN_EDICION_CALENDARIO.md y aplicar cambios")
        print("   3. Usar equipo3/04_GO_TO_MARKET.md para planificar lanzamiento")
        print("   4. Ejecutar el plan de marketing de equipo3/05_MARKETING_PLAN.md")
        print("=" * 70)

    def ejecutar(self):
        self.print_banner()

        # Ejecutar equipos segun configuracion
        if self.solo_equipo:
            if self.solo_equipo == 1:
                self.ejecutar_equipo_1()
            elif self.solo_equipo == 2:
                self.ejecutar_equipo_2()
            elif self.solo_equipo == 3:
                self.ejecutar_equipo_3()
            elif self.solo_equipo == 4:
                self.ejecutar_equipo_4()
        else:
            # Pipeline completo con skips opcionales
            if self.skip_equipo != 1:
                if not self.ejecutar_equipo_1():
                    print("\n  ERROR: Equipo 1 fallo. Abortando pipeline.")
                    self.guardar_log()
                    return
            else:
                print("\n  [SKIP] Equipo 1 omitido por flag --skip-equipo 1")
                self.log["equipos"].append({
                    "equipo": 1, "estado": "OMITIDO", "timestamp": datetime.now().isoformat()
                })

            if self.skip_equipo != 2:
                if not self.ejecutar_equipo_2():
                    print("\n  ERROR: Equipo 2 fallo. Abortando pipeline.")
                    self.guardar_log()
                    return
            else:
                print("\n  [SKIP] Equipo 2 omitido por flag --skip-equipo 2")
                self.log["equipos"].append({
                    "equipo": 2, "estado": "OMITIDO", "timestamp": datetime.now().isoformat()
                })

            if self.skip_equipo != 3:
                if not self.ejecutar_equipo_3():
                    print("\n  ERROR: Equipo 3 fallo.")
                    self.guardar_log()
                    return
            else:
                print("\n  [SKIP] Equipo 3 omitido por flag --skip-equipo 3")
                self.log["equipos"].append({
                    "equipo": 3, "estado": "OMITIDO", "timestamp": datetime.now().isoformat()
                })

            if self.skip_equipo != 4:
                if not self.ejecutar_equipo_4():
                    print("\n  ERROR: Equipo 4 fallo.")
                    self.guardar_log()
                    return
            else:
                print("\n  [SKIP] Equipo 4 omitido por flag --skip-equipo 4")
                self.log["equipos"].append({
                    "equipo": 4, "estado": "OMITIDO", "timestamp": datetime.now().isoformat()
                })

        self.guardar_log()
        self.resumen_final()


def main():
    parser = argparse.ArgumentParser(description="Pipeline Maestro de 4 Equipos v2")
    parser.add_argument("--modo", default="completo",
                        choices=["completo", "transiciones", "tecnico", "marketing"],
                        help="Modo de analisis del Equipo 2")
    parser.add_argument("--equipo", type=int, default=None, choices=[1, 2, 3, 4],
                        help="Ejecutar solo un equipo especifico")
    parser.add_argument("--skip-equipo", type=int, default=None, choices=[1, 2, 3, 4],
                        help="Saltar un equipo (para continuar desde donde quedo)")
    args = parser.parse_args()

    pipeline = PipelineMaestro(
        modo=args.modo,
        solo_equipo=args.equipo,
        skip_equipo=args.skip_equipo
    )
    pipeline.ejecutar()


if __name__ == "__main__":
    main()
