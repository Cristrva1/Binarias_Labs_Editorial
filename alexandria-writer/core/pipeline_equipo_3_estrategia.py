#!/usr/bin/env python3
"""
EQUIPO 3: ESTRATEGIA DE MERCADO Y GO-TO-MARKET
===============================================
Mision: Recibir la Bible + Ediciones y generar la estrategia completa
para convertir TSBN en un producto editorial exitoso.

Agentes:
  - Buyer Persona: Perfil detallado del comprador ideal
  - Analista de Mercado: Competencia, tendencias, oportunidades
  - Estratega de Precios: Modelo de precios, canales, formatos
  - Growth Marketer: Plan de adquisicion de lectores
  - Content Marketer: Estrategia de contenido para lanzamiento
  - Distribuidor: Canales fisicos, digitales, internacionales

Salidas (en projects/tsbn/equipo3/):
  - 01_BUYER_PERSONA.md           → Perfil detallado del lector-comprador
  - 02_ANALISIS_MERCADO.md         → Competencia, tendencias, nichos
  - 03_GO_TO_MARKET.md             → Estrategia de lanzamiento completa
  - 04_MARKETING_PLAN.md           → Plan de marketing digital 12 meses
  - 05_ESTRATEGIA_CONTENIDO.md     → Contenido para redes, blog, email
  - 06_DISTRIBUCION.md             → Canales y alianzas estrategicas
  - 07_FORECAST_VENTAS.md          → Proyeccion realista de ventas
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
OUTPUT = PROJECT / "projects" / "tsbn" / "equipo3"
os.makedirs(OUTPUT, exist_ok=True)


class Equipo3Estrategia:
    def __init__(self):
        self.router = LLMRouter()
        self.bible = ""
        self.ediciones = ""
        self.analisis_5d = ""

        print("=" * 65)
        print("  EQUIPO 3: ESTRATEGIA DE MERCADO Y GO-TO-MARKET")
        print("=" * 65)

    def cargar_entradas(self):
        print("\n[FASE 0] Cargando documentos de Equipos 1 y 2...")

        for path, name, attr in [
            (EQUIPO1_OUT / "01_BIBLE_DEL_LIBRO.md", "Bible", "bible"),
            (EQUIPO2_OUT / "02_EDICIONES.md", "Ediciones", "ediciones"),
            (EQUIPO2_OUT / "01_ANALISIS_5D.md", "Analisis 5D", "analisis_5d"),
        ]:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                setattr(self, attr, content)
                print(f"  {name}: {len(content)} chars")
            else:
                print(f"  WARNING: {name} no encontrado en {path}")

    def _llamar(self, prompt, system, temp=0.3, max_tok=4000):
        result = self.router.chat(prompt, system=system, temperature=temp, max_tokens=max_tok)
        if result["success"]:
            return result["content"], result["provider"]
        return f"ERROR: {result['error']}", "FAIL"

    def buyer_persona(self):
        print("\n[AGENTE] Buyer Persona...", end=" ", flush=True)
        system = "Eres estratega de marketing editorial con 10 anos creando buyer personas para libros de autoayuda espiritual en LATAM. Generas perfiles detallados y accionables."
        prompt = f"""Basandote en la Bible del libro y el analisis editorial, crea un BUYER PERSONA detallado.

CONTEXTO DEL LIBRO:
{self.bible[:4000]}

DEBILIDADES IDENTIFICADAS (para ajustar mensaje):
{self.ediciones[:2000]}

Genera:
1. NOMBRE ficticio del persona
2. FICHA DEMOGRAFICA completa (edad, ciudad, ocupacion, ingreso, familia)
3. PSICOGRAFIA detallada (valores, miedos, aspiraciones, dolor actual)
4. JORNADA DE COMPRA (como descubre, evalua y compra libros)
5. OBJECIONES (por que NO compraria este libro)
6. GANCHOS (que lo convencerian)
7. DONDE ENCONTRARLO (grupos de FB, podcasts, influencers, iglesias)
8. MENSAJE CLAVE para este persona (max 50 palabras)
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def analisis_mercado(self):
        print("\n[AGENTE] Analista de Mercado...", end=" ", flush=True)
        system = "Eres analista de mercado editorial especializado en libros espirituales en Mexico y LATAM. Conoces datos reales del mercado, competidores directos e indirectos."
        prompt = f"""Analiza el mercado para "Todas Son Buenas Noticias" de Arturo Ledezma Ruan.

CONTEXTO:
{self.bible[:3000]}

Genera:
1. TAMANO DEL MERCADO: Estimacion del mercado de autoayuda espiritual en Mexico/LATAM
2. COMPETENCIA DIRECTA: 5 libros similares (autor, ano, fortalezas, debilidades)
3. COMPETENCIA INDIRECTA: 5 libros que el lector podria comprar en vez de este
4. TENDENCIAS: Que esta funcionando ahora en el nicho espiritual
5. BRECHA DE MERCADO: Que necesidad NO esta cubierta que este libro podria cubrir
6. VENTAJA COMPETITIVA: Por que alguien elegiria TSBN sobre los competidores
7. RIESGOS: Factores que podrian hacer fracasar el libro
8. OPORTUNIDADES: Ventanas de tiempo, eventos, tendencias a aprovechar
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def go_to_market(self):
        print("\n[AGENTE] Estratega Go-to-Market...", end=" ", flush=True)
        system = "Eres director de lanzamiento editorial. Has lanzado 50+ libros exitosos. Planificas estrategias de lanzamiento de 0 a 90 dias con milestones concretos."
        prompt = f"""Crea una estrategia GO-TO-MARKET completa para el lanzamiento de TSBN.

CONTEXTO:
{self.bible[:3000]}

EDICIONES PENDIENTES (el libro necesita estos cambios antes de lanzar):
{self.ediciones[:1500]}

Estructura el plan asi:

FASE 1: PRE-LANZAMIENTO (meses -3 a 0)
- Tareas de edicion y produccion
- Construccion de audiencia
- Creacion de contenido previo
- Landing page y funnel
- Beta readers / ARC team

FASE 2: LANZAMIENTO (semanas 1-4)
- Evento de lanzamiento
- Promociones de lanzamiento
- Alcance de medios
- Estrategia de reviews
- Amazon A+ Content / categorias

FASE 3: POST-LANZAMIENTO (meses 2-6)
- Retargeting
- Cross-promotion
- Audiobook / formatos adicionales
- Expansion internacional
- Metricas y ajustes

Incluye fechas especificas (ej: 'Semana 1: X'), presupuestos estimados, y KPIs.
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def marketing_plan(self):
        print("\n[AGENTE] Growth Marketer...", end=" ", flush=True)
        system = "Eres growth marketer especializado en libros y productos digitales. Dominas Meta Ads, Google Ads, Amazon Ads, email marketing, y marketing de afiliados."
        prompt = f"""Crea un PLAN DE MARKETING DIGITAL de 12 meses para TSBN.

CONTEXTO:
{self.bible[:3000]}

Incluye:
1. CANALES: Que canales usar (FB/IG, TikTok, YouTube, email, podcast, PR)
2. CONTENIDO: Tipos de contenido por canal (reels, carruseles, shorts, blogs)
3. CALENDARIOS: Frecuencia de publicacion por canal
4. ADS: Estrategia de pauta (presupuesto mensual sugerido, segmentacion)
5. EMAIL MARKETING: Secuencia de bienvenida, newsletter, campanas
6. INFLUENCERS: 10 micro-influencers ideales en el nicho espiritual
7. AFILIADOS: Programa de afiliados para pastors, coaches, terapeutas
8. METRICAS: KPIs por canal, CAC objetivo, ROAS esperado
9. PRESUPUESTO TOTAL: Desglose mensual recomendado (minimo, optimo)
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def estrategia_contenido(self):
        print("\n[AGENTE] Content Marketer...", end=" ", flush=True)
        system = "Eres content strategist para autores. Creas calendars de contenido, hooks virales, y estrategias de contenido que venden libros sin ser spam."
        prompt = f"""Crea una ESTRATEGIA DE CONTENIDO para construir audiencia antes y durante el lanzamiento.

CONTEXTO:
{self.bible[:3000]}

Genera:
1. 30 HOOKS para redes sociales (frases que detengan el scroll)
2. 15 TEMAS de blog/articulo que posicionen al autor como experto
3. 10 REELS/TIKTOK ideas con guion (escena + texto + CTA)
4. 5 CARRUSELES de Instagram (slide 1 a slide 5)
5. SECUENCIA DE EMAILS de bienvenida (5 emails con asunto y body)
6. PILLARS DE CONTENIDO: 3 temas pilares para todo el ano
7. HASHTAGS y KEYWORDS por plataforma
8. ESTRATEGIA DE CONTENIDO GRATIS vs PAGO (lead magnets)
"""
        content, provider = self._llamar(prompt, system, temp=0.35, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def distribucion(self):
        print("\n[AGENTE] Distribuidor...", end=" ", flush=True)
        system = "Eres distribuidor editorial con experiencia en Mexico, LATAM y mercados hispanos en USA. Conoces Amazon KDP, Kindle Unlimited, IngramSpark, librerias fisicas, y derechos internacionales."
        prompt = f"""Crea una estrategia de DISTRIBUCION para TSBN.

CONTEXTO:
{self.bible[:3000]}

Incluye:
1. FORMATOS: Fisico (tapa blanda/dura), Digital (ebook), Audio (audiolibro)
2. PLATAFORMAS DIGITALES: Amazon KDP, Apple Books, Google Play, Kobo, Scribd
3. DISTRIBUCION FISICA: Gandhi, Casa del Libro, Porrua, Walmart, aeropuertos
4. AUDIOLIBRO: ACX, Findaway, Storytel
5. DERECHOS: Traduccion (ingles, portugues), adaptacion (curso online), coedicion
6. ALIANZAS: Iglesias, centros de retiro, empresas (B2B para bienestar laboral)
7. BARRERAS: Que obstaculos anticipas y como los superas
8. PRIORIDAD: En que orden lanzar en cada canal (timeline)
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def forecast_ventas(self):
        print("\n[AGENTE] Forecast de Ventas...", end=" ", flush=True)
        system = "Eres analista financiero editorial. Creas proyecciones realistas basadas en benchmarks del mercado de autoayuda en LATAM."
        prompt = f"""Crea una PROYECCION DE VENTAS realista para TSBN en sus primeros 24 meses.

CONTEXTO:
{self.bible[:3000]}

Genera:
1. ESCANARIOS: Pesimista, Realista, Optimista (unidades y revenue)
2. PRECIO SUGERIDO: Por formato (ebook, tapa blanda, audiolibro)
3. ROYALTIES: Ingreso neto estimado por unidad vendida
4. MES A MES: Proyeccion de unidades vendidas (mes 1 a mes 24)
5. BREAK-EVEN: Cuando recupera la inversion de edicion/marketing
6. COSTOS: Edicion, diseno, marketing, distribucion estimados
7. FACTORES DE EXITO: Que haria que se acerque al escenario optimista
8. ROADBLOCKS: Que haria que se acerque al escenario pesimista
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}]")
        return content

    def compilar_documentos(self, buyer, mercado, gtm, marketing, contenido, distribucion, forecast):
        print("\n[COMPILACION] Generando documentos del Equipo 3...")

        docs = [
            ("01_BUYER_PERSONA.md", "Buyer Persona", buyer),
            ("02_ANALISIS_MERCADO.md", "Analisis de Mercado", mercado),
            ("03_GO_TO_MARKET.md", "Go-to-Market", gtm),
            ("04_MARKETING_PLAN.md", "Marketing Plan", marketing),
            ("05_ESTRATEGIA_CONTENIDO.md", "Estrategia de Contenido", contenido),
            ("06_DISTRIBUCION.md", "Distribucion", distribucion),
            ("07_FORECAST_VENTAS.md", "Forecast de Ventas", forecast),
        ]

        for fname, title, content in docs:
            full_content = f"# {title} — TSBN\n\n> Generado por: Equipo 3 de Estrategia (Alexandria Writer)\n> Fecha: {datetime.now().isoformat()}\n\n{content}"
            with open(OUTPUT / fname, "w", encoding="utf-8") as f:
                f.write(full_content)
            print(f"  -> {fname}")

    def ejecutar(self):
        self.cargar_entradas()

        buyer = self.buyer_persona()
        mercado = self.analisis_mercado()
        gtm = self.go_to_market()
        marketing = self.marketing_plan()
        contenido = self.estrategia_contenido()
        distribucion = self.distribucion()
        forecast = self.forecast_ventas()

        self.compilar_documentos(buyer, mercado, gtm, marketing, contenido, distribucion, forecast)

        print("\n" + "=" * 65)
        print("  EQUIPO 3 COMPLETADO")
        print("=" * 65)
        print(f"\n  Documentos en: {OUTPUT}")
        print("  Pipeline de 3 equipos FINALIZADO")
        print("\n  Resumen de entregables:")
        print("  - Equipo 1: Bible + Mapa + Temas + Voz + Publico")
        print("  - Equipo 2: Analisis 5D + Ediciones + Prioridades")
        print("  - Equipo 3: Buyer Persona + GTM + Marketing + Distribucion + Forecast")
        return True


def main():
    equipo = Equipo3Estrategia()
    equipo.ejecutar()


if __name__ == "__main__":
    main()
