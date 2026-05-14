#!/usr/bin/env python3
"""
EQUIPO 4: ITERACION DE REFINAMIENTO Y PLAN DE IMPLEMENTACION
=============================================================
Mision: Tomar los outputs de Equipos 1, 2 y 3 y generar el documento
final de accion para el autor/editor humano.

Este equipo responde la pregunta: "Ahora que tengo todo el analisis,
que hago y en que orden?"

Agentes:
  - Planificador de Edicion: Calendario de cambios al manuscrito
  - Resolutor de Conflictos: Soluciona recomendaciones contradictorias
  - Optimizador de Lanzamiento: Alinea edicion con marketing
  - Brief Final: Documento ejecutivo de 1 pagina

Salidas (en projects/tsbn/equipo4/):
  - 01_PLAN_EDICION_CALENDARIO.md     → Semana a semana que cambiar
  - 02_CONFLICTOS_RESUELTOS.md        → Recomendaciones contradictorias y decision
  - 03_CHECKLIST_IMPLEMENTACION.md    → Lista de tareas con checkboxes
  - 04_BRIEF_FINAL_EJECUTIVO.md       → One-pager para el autor
  - 05_PROXIMAS_ITERACIONES.md        → Que hacer en la siguiente ronda
"""

import sys
import os
from pathlib import Path
from datetime import datetime

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))
from llm_router import LLMRouter

PROJECT = CORE_DIR.parent
EQUIPO1_OUT = PROJECT / "projects" / "tsbn" / "equipo1"
EQUIPO2_OUT = PROJECT / "projects" / "tsbn" / "equipo2"
EQUIPO3_OUT = PROJECT / "projects" / "tsbn" / "equipo3"
OUTPUT = PROJECT / "projects" / "tsbn" / "equipo4"
os.makedirs(OUTPUT, exist_ok=True)


class Equipo4Refinamiento:
    def __init__(self):
        self.router = LLMRouter()
        self.entradas = {}

        print("=" * 65)
        print("  EQUIPO 4: ITERACION DE REFINAMIENTO")
        print("  Plan de Implementacion Final")
        print("=" * 65)

    def cargar_entradas(self):
        print("\n[FASE 0] Cargando outputs de Equipos 1, 2 y 3...")

        archivos = {
            "bible": (EQUIPO1_OUT / "01_BIBLE_DEL_LIBRO.md", "Bible E1"),
            "mapa": (EQUIPO1_OUT / "02_MAPA_CAPITULOS.md", "Mapa E1"),
            "voz": (EQUIPO1_OUT / "04_VOZ_TONO_ESTILO.md", "Voz E1"),
            "top30": (EQUIPO2_OUT / "03_TOP30_PRIORITARIO.md", "Top30 E2"),
            "ediciones": (EQUIPO2_OUT / "02_EDICIONES_CONSOLIDADAS.md", "Ediciones E2"),
            "metricas": (EQUIPO2_OUT / "05_METRICAS_CALIDAD.md", "Metricas E2"),
            "buyer": (EQUIPO3_OUT / "01_BUYER_PERSONA.md", "Buyer E3"),
            "gtm": (EQUIPO3_OUT / "04_GO_TO_MARKET.md", "GTM E3"),
            "marketing": (EQUIPO3_OUT / "05_MARKETING_PLAN.md", "Marketing E3"),
            "forecast": (EQUIPO3_OUT / "10_FORECAST_VENTAS.md", "Forecast E3"),
        }

        for key, (path, name) in archivos.items():
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.entradas[key] = content
                print(f"  {name}: {len(content)} chars")
            else:
                print(f"  WARNING: {name} no encontrado")

    def _llamar(self, prompt, system, temp=0.2, max_tok=4000):
        result = self.router.chat(prompt, system=system, temperature=temp, max_tokens=max_tok)
        if result["success"]:
            return result["content"], result["provider"]
        return f"ERROR: {result['error']}", "FAIL"

    def planificador_edicion(self):
        print("\n[AGENTE] Planificador de Edicion...", end=" ", flush=True)
        system = "Eres editor de proyectos literarios. Creas calendarios de edicion realistas con dependencias entre tareas y recursos necesarios."

        top30 = self.entradas.get("top30", "")[:4000]
        metricas = self.entradas.get("metricas", "")[:1500]

        prompt = f"""Crea un PLAN DE EDICION SEMANA A SEMANA para aplicar los cambios al manuscrito de TSBN.

RECOMENDACIONES TOP 30:
{top30}

METRICAS:
{metricas}

Genera un calendario de 8 semanas:

| Semana | Tarea Principal | Cambios a Aplicar | Tiempo Estimado | Dependencias |
|--------|----------------|-------------------|-----------------|--------------|
| 1 | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... |
...(hasta semana 8)

Para cada semana incluye:
1. OBJETIVO: que se logra esa semana
2. CAMBIOS: lista de ubicaciones exactas a modificar
3. TEXTO_SUGERIDO: referencias a los parrafos
4. REVISION: como verificar que quedo bien
5. RIESGOS: que podria salir mal

Al final:
- FASE 1: Edicion (semanas 1-4)
- FASE 2: Revision (semanas 5-6)
- FASE 3: Formateo/Diseno (semanas 7-8)
- Milestones de aprobacion por fase"""

        content, provider = self._llamar(prompt, system, temp=0.2, max_tok=8000)
        print(f"OK [{provider}]")
        return content

    def resolutor_conflictos(self):
        print("\n[AGENTE] Resolutor de Conflictos...", end=" ", flush=True)
        system = "Eres editor jefe que resuelve conflictos entre recomendaciones de diferentes agentes. Tomas decisiones firmes basadas en el beneficio para el lector."

        ediciones = self.entradas.get("ediciones", "")[:5000]

        prompt = f"""Revisa las recomendaciones de edicion y busca CONFLICTOS o CONTRADICCIONES.

RECOMENDACIONES:
{ediciones}

Identifica conflictos como:
- Un agente sugiere acortar un parrafo que otro quiere expandir
- Dos agentes sugieren cambios opuestos en la misma frase
- Una recomendacion de marketing contradice la voz del autor segun el analista de voz
- Una correccion ortografica cambiaria el estilo intencional del autor

Para cada conflicto encontrado:
1. DESCRIPCION del conflicto
2. AGENTES involucrados
3. CRITERIO DE RESOLUCION (por que decidimos asi)
4. DECISION FINAL (cual recomendacion seguir, o nueva propuesta)
5. TEXTO FINAL APROBADO

Si no hay conflictos, indica: \"No se detectaron conflictos significativos.\""""

        content, provider = self._llamar(prompt, system, temp=0.2, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def optimizador_lanzamiento(self):
        print("\n[AGENTE] Optimizador de Lanzamiento...", end=" ", flush=True)
        system = "Eres director de proyectos editoriales. Alineas el calendario de edicion con el calendario de marketing para maximizar el impacto del lanzamiento."

        gtm = self.entradas.get("gtm", "")[:3000]
        buyer = self.entradas.get("buyer", "")[:2000]
        voz = self.entradas.get("voz", "")[:1500]

        prompt = f"""Crea un CRONOGRAMA INTEGRADO que alinee edicion + marketing.

GO-TO-MARKET:
{gtm}

BUYER PERSONA:
{buyer}

VOZ DEL AUTOR:
{voz}

Genera un timeline de 6 meses que integre:
- Termino de edicion del manuscrito
- Produccion (portada, formateo, ISBN)
- Construccion de audiencia
- Pre-venta / pre-lanzamiento
- Lanzamiento oficial
- Post-lanzamiento

Formato:
| Mes | Edicion | Produccion | Marketing | Eventos | KPIs |
|-----|---------|------------|-----------|---------|------|
| -3 | ... | ... | ... | ... | ... |

Incluye:
- Fechas clave (Dia del libro, Navidad, Cuaresma)
- Dependencias (no se puede lanzar marketing sin portada)
- Decisiones pendientes que bloquean el timeline
- Contingencias (que pasa si la edicion se retrasa)"""

        content, provider = self._llamar(prompt, system, temp=0.25, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def brief_final(self):
        print("\n[AGENTE] Brief Final Ejecutivo...", end=" ", flush=True)
        system = "Eres consultor ejecutivo. Sintetizas informacion compleja en documentos de 1 pagina que un CEO puede leer en 2 minutos y tomar decisiones."

        bible = self.entradas.get("bible", "")[:2000]
        metricas = self.entradas.get("metricas", "")[:1000]
        forecast = self.entradas.get("forecast", "")[:1000]

        prompt = f"""Crea un BRIEF EJECUTIVO de 1 pagina para Arturo Ledezma Ruan (el autor).

CONTEXTO:
{bible}

METRICAS DEL ANALISIS:
{metricas}

FORECAST:
{forecast}

Estructura (max 1 pagina, lenguaje claro, sin jerga):

# Brief Ejecutivo — Todas Son Buenas Noticias

## El Estado Actual
(3 bullets: que bien esta el libro, que necesita mejora, score general)

## Las 5 Decisiones que Debes Tomar
1. (decision concreta con opciones A/B)
2.
3.
4.
5.

## El Plan en 3 Fases
- Fase 1 (4 semanas): X → $Y → Resultado Z
- Fase 2 (4 semanas): X → $Y → Resultado Z
- Fase 3 (4 meses): X → $Y → Resultado Z

## Inversion Total Requerida
| Rubro | Monto (MXN) |
|-------|-------------|
| ... | ... |
| TOTAL | ... |

## ROI Esperado (24 meses)
- Escenario conservador: $X
- Escenario realista: $Y
- Escenario optimista: $Z

## Proximo Paso Inmediato
(La UNICA accion que debe hacer esta semana)"""

        content, provider = self._llamar(prompt, system, temp=0.2, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def proximas_iteraciones(self):
        print("\n[AGENTE] Proximas Iteraciones...", end=" ", flush=True)
        system = "Eres estratega de procesos editoriales. Planificas ciclos de mejora continua para libros en desarrollo."

        metricas = self.entradas.get("metricas", "")[:1000]

        prompt = f"""Planifica las PROXIMAS ITERACIONES del proceso para TSBN.

METRICAS ACTUALES:
{metricas}

Estructura:

## ITERACION 1: Correccion Inmediata (ya hecha)
- Que se logro
- Que falta

## ITERACION 2: Refinamiento de Estilo
- Objetivo: mejorar prosa, ritmo, eliminar cliches restantes
- Agente focal: Estilista + Voz
- Duracion: 2 semanas
- Entregable: Manuscrito con prosa pulida

## ITERACION 3: Profundizacion Espiritual
- Objetivo: fortalecer mensaje, anclaje doctrinal
- Agente focal: Teologo
- Duracion: 1 semana

## ITERACION 4: Estructura y Transiciones
- Objetivo: arco narrativo perfecto, hooks potentes
- Agente focal: Estructurista
- Duracion: 2 semanas

## ITERACION 5: Beta Readers
- Objetivo: feedback real de lectores del nicho
- Metodologia: como seleccionar, que preguntar
- Duracion: 3 semanas

## ITERACION 6: Marketing Refinado
- Objetivo: ajustar GTM con datos reales
- Agente focal: Mercadologo + Datos de beta readers
- Duracion: 1 semana

Para cada iteracion:
- Entradas necesarias
- Proceso
- Entregables
- Criterios de exito
- Que haria falta para empezar"""

        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def compilar_documentos(self, plan, conflictos, cronograma, brief, iteraciones):
        print("\n[COMPILACION] Generando documentos del Equipo 4...")

        docs = [
            ("01_PLAN_EDICION_CALENDARIO.md", "Plan de Edicion — Calendario", plan),
            ("02_CONFLICTOS_RESUELTOS.md", "Conflictos Resueltos", conflictos),
            ("03_CRONOGRAMA_INTEGRADO.md", "Cronograma Integrado", cronograma),
            ("04_BRIEF_FINAL_EJECUTIVO.md", "Brief Final Ejecutivo", brief),
            ("05_PROXIMAS_ITERACIONES.md", "Proximas Iteraciones", iteraciones),
        ]

        for fname, title, content in docs:
            full = f"# {title}\n\n"
            full += f"> Generado por: Equipo 4 de Refinamiento (Alexandria Writer)\n"
            full += f"> Fecha: {datetime.now().isoformat()}\n\n"
            full += content
            with open(OUTPUT / fname, "w", encoding="utf-8") as f:
                f.write(full)
            print(f"  -> {fname}")

    def ejecutar(self):
        self.cargar_entradas()

        plan = self.planificador_edicion()
        conflictos = self.resolutor_conflictos()
        cronograma = self.optimizador_lanzamiento()
        brief = self.brief_final()
        iteraciones = self.proximas_iteraciones()

        self.compilar_documentos(plan, conflictos, cronograma, brief, iteraciones)

        print("\n" + "=" * 65)
        print("  EQUIPO 4 COMPLETADO")
        print("=" * 65)
        print(f"\n  Documentos en: {OUTPUT}")
        print("\n  Pipeline de 4 equipos FINALIZADO")
        print("\n  Resumen completo del pipeline:")
        print("  - E1: Inteligencia (6 docs)")
        print("  - E2: Analisis Editorial (5 docs)")
        print("  - E3: Estrategia Mercado (10 docs)")
        print("  - E4: Refinamiento (5 docs)")
        return True


def main():
    equipo = Equipo4Refinamiento()
    equipo.ejecutar()


if __name__ == "__main__":
    main()
