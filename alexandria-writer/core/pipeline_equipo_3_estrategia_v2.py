#!/usr/bin/env python3
"""
EQUIPO 3 v2: ESTRATEGIA DE MERCADO Y GO-TO-MARKET MEJORADO
===========================================================
Mejoras sobre v1:
  - Prompts mas profundos y especificos (generan documentos 3x mas largos)
  - Agente de Comparables: analisis real de autores similares en Mexico/LATAM
  - Agente de Keywords: palabras clave para Amazon, SEO, ads
  - Agente de Contenido Premium: 30 dias de contenido listo para publicar
  - Agente de Alianzas: iglesias, coaches, influencers reales del nicho
  - Formato estructurado con tablas, calendarios, y ejemplos concretos

Salidas (en projects/tsbn/equipo3/):
  - 01_BUYER_PERSONA.md           → Perfil detallado con nombre, foto mental, jornada
  - 02_ANALISIS_MERCADO.md         → Competencia real, brechas, riesgos
  - 03_COMPARABLES.md              ← NUEVO: autores similares con datos
  - 04_GO_TO_MARKET.md             → Plan de lanzamiento con fechas y presupuestos
  - 05_MARKETING_PLAN.md           → 12 meses con calendario, presupuestos, KPIs
  - 06_ESTRATEGIA_CONTENIDO.md     → 30 dias de contenido listo + pillars
  - 07_KEYWORDS_SEO.md             ← NUEVO: Amazon, SEO, ads keywords
  - 08_DISTRIBUCION.md             → Canales, alianzas, expansion
  - 09_ALIANZAS_ESTRATEGICAS.md    ← NUEVO: contactos potenciales
  - 10_FORECAST_VENTAS.md          → Proyeccion 24 meses con escenarios
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


class Equipo3EstrategiaV2:
    def __init__(self):
        self.router = LLMRouter()
        self.bible = ""
        self.ediciones = ""
        self.analisis_5d = ""

        print("=" * 65)
        print("  EQUIPO 3 v2: ESTRATEGIA DE MERCADO Y GO-TO-MARKET MEJORADO")
        print("=" * 65)

    def cargar_entradas(self):
        print("\n[FASE 0] Cargando documentos de Equipos 1 y 2...")

        for path, name, attr in [
            (EQUIPO1_OUT / "01_BIBLE_DEL_LIBRO.md", "Bible", "bible"),
            (EQUIPO2_OUT / "02_EDICIONES_CONSOLIDADAS.md", "Ediciones", "ediciones"),
            (EQUIPO2_OUT / "01_ANALISIS_5D.md", "Analisis 5D", "analisis_5d"),
        ]:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                setattr(self, attr, content)
                print(f"  {name}: {len(content)} chars")
            else:
                print(f"  WARNING: {name} no encontrado en {path}")

    def _llamar(self, prompt, system, temp=0.3, max_tok=8000):
        result = self.router.chat(prompt, system=system, temperature=temp, max_tokens=max_tok)
        if result["success"]:
            return result["content"], result["provider"]
        return f"ERROR: {result['error']}", "FAIL"

    def buyer_persona(self):
        print("\n[AGENTE] Buyer Persona Premium...", end=" ", flush=True)
        system = "Eres estratega de marketing editorial con 10 anos creando buyer personas para best sellers de autoayuda espiritual en Mexico y LATAM. Generas perfiles tan detallados que parecen personas reales."
        prompt = f"""Crea un BUYER PERSONA PREMIUM detallado para "Todas Son Buenas Noticias" de Arturo Ledezma Ruan.

CONTEXTO DEL LIBRO:
{self.bible[:4000]}

DEBILIDADES Y FORTALEZAS IDENTIFICADAS:
{self.ediciones[:2000]}

Estructura obligatoria (minimo 800 palabras):

## 1. IDENTIDAD
- Nombre completo ficticio
- Edad exacta
- Ciudad y colonia tipo (ej: "vive en Coyoacan, CDMX")
- Ocupacion exacta y nivel jerarquico
- Ingreso mensual en MXN
- Estado civil, num de hijos, edades
- Tipo de vivienda, si tiene auto, nivel socioeconomico (A/B/C+)

## 2. PSICOGRAFIA PROFUNDA
- Historia personal (2 parrafos): que le paso que la llevo a buscar este libro?
- Dolor principal (fisico/emocional/existencial)
- Suenio dorado: como seria su vida ideal en 3 anos?
- Frustracion actual: que la mantiene despierta a las 3am?
- Valores en orden de importancia (top 5)
- Creencias religiosas/espirituales (especifica denominacion o tipo)
- Politica (general, no partidista)
- Estilo de vida (rutina diaria, hobbies, consumo de media)

## 3. COMPORTAMIENTO LECTOR
- Ultimos 3 libros que compro (titulos reales del genero)
- Donde compra (Amazon, Gandhi, Kindle, audiolibros)
- Como descubre libros (recomendacion, algoritmo, influencer, pastor)
- Cuanto gasta al mes en libros
- Formato preferido y por que
- Leer por placer o por necesidad?

## 4. OBJECIONES DE COMPRA
- 5 razones por las que NO compraria este libro (sean validas)
- Precio, autor desconocido, genero saturado, etc.

## 5. GANCHOS CONVERTIDORES
- 5 frases o promesas que la harian comprar INMEDIATAMENTE
- Que evento o momento la haria buscar este libro (crisis, transicion)

## 6. DONDE ENCONTRARLA (ESPECIFICO)
- 5 grupos de Facebook exactos (nombres)
- 3 podcasts que escucha
- 5 influencers/accounts que sigue
- 3 iglesias o centros espirituales que frecuenta
- 3 apps que usa diariamente
- Horarios de mayor actividad en redes

## 7. MENSAJE CLAVE (max 50 palabras)
- La frase que la haria clickear "comprar ahora"
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=8000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def analisis_mercado(self):
        print("\n[AGENTE] Analista de Mercado Profundo...", end=" ", flush=True)
        system = "Eres analista de mercado editorial especializado en Mexico, LATAM y mercado hispano en USA. Conoces datos reales: ventas de libros autoayuda, competidores directos, tendencias 2024-2026."
        prompt = f"""Analiza el mercado para "Todas Son Buenas Noticias" con datos reales y especificos.

CONTEXTO:
{self.bible[:3000]}

Estructura obligatoria (minimo 1000 palabras):

## 1. TAMANO DEL MERCADO
- Mercado total de autoayuda en Mexico (ventas anuales en MXN)
- Crecimiento anual del segmento (%)
- Tamano del segmento espiritual dentro de autoayuda
- Proyeccion para 2026-2028

## 2. COMPETENCIA DIRECTA (5 libros)
Para cada uno:
| Titulo | Autor | Ano | Editorial | Precio | Fortalezas | Debilidades vs TSBN |
- Por que ganaron y que podemos aprender

## 3. COMPETENCIA INDIRECTA (5)
Libros que el lector compraria en vez de TSBN (no espirituales pero que cubren la misma necesidad emocional)

## 4. TENDENCIAS 2024-2026
- Que esta funcionando en redes para autores espirituales
- Formatos en crecimiento (audiobook, newsletter, cursos)
- Plataformas emergentes
- Como ha cambiado el consumo post-pandemia

## 5. BRECHA DE MERCADO
- Que necesidad NO esta cubierta por los competidores
- Por que TSBN podria llenar ese vacio
- Ventana de oportunidad (cuanto tiempo tenemos)

## 6. VENTAJA COMPETITIVA
- 5 razones por las que alguien elegiria TSBN
- 3 diferenciadores unicos
- Narrativa de posicionamiento (como presentamos el libro vs competencia)

## 7. RIESGOS DEL MERCADO
- 5 factores que podrian hacer fracasar el libro
- Como mitigar cada uno

## 8. OPORTUNIDADES DE TIEMPO
- Eventos, fechas, temporadas ideales para lanzar
- Ventanas de marketing (cuaresma, ano nuevo, septiembre)
"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=8000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def comparables(self):
        print("\n[AGENTE] Comparables de Autores...", end=" ", flush=True)
        system = "Eres editor de desarrollo con conocimiento profundo del mercado hispano de autoayuda espiritual. Conoces a los autores mas vendidos, sus tacticas de marketing, y sus debilidades."
        prompt = f"""Identifica autores COMPARABLES a Arturo Ledezma Ruan en Mexico/LATAM.

Para cada autor comparable (minimo 5):
- Nombre completo
- 3 libros mas vendidos (con anos)
- Estimacion de ventas totales
- Estilo de marketing (redes, eventos, podcast)
- Fortalezas que podriamos emular
- Debilidades que TSBN puede aprovechar
- Audiencia (edad, genero, ubicacion)

Al final:
- Tabla comparativa: TSBN vs cada comparable
- Recomendacion de posicionamiento diferenciado"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def go_to_market(self):
        print("\n[AGENTE] Estratega Go-to-Market Detallado...", end=" ", flush=True)
        system = "Eres director de lanzamiento editorial. Has lanzado 50+ libros exitosos en Mexico. Planificas con fechas reales, presupuestos en MXN, y milestones concretos."
        prompt = f"""Crea un plan GO-TO-MARKET detallado para TSBN.

CONTEXTO:
{self.bible[:3000]}

EDICIONES PENDIENTES:
{self.ediciones[:1500]}

Estructura obligatoria (minimo 1500 palabras):

## FASE 1: PRE-LANZAMIENTO (meses -3 a 0)

### Mes -3: Fundamentos
- [ ] Tarea concreta
- Presupuesto: $X MXN
- Responsable: (autor/editor/marketer)
- KPI: metrica medible

### Mes -2: Audiencia
- Lista de tareas con presupuesto y KPI

### Mes -1: Preparacion
- Beta readers (como seleccionarlos, cuantos, donde encontrarlos)
- ARC copies (Amazon, BookSirens, NetGalley)
- Landing page (herramienta, contenido, funnel)
- Email list (secuencia de bienvenida, lead magnet)

## FASE 2: LANZAMIENTO (semanas 1-4)

### Semana 1: Impacto
- Evento de lanzamiento (formato, plataforma, invitados, costo)
- Descuentos de lanzamiento (% y duracion)
- Sorteos (mecanica, premios, alcance esperado)

### Semana 2-3: Medios
- Lista de 10 medios/contactos de prensa a contactar
- Pitch templates (3 variantes)
- Entrevistas (podcasts, canales de YT, estaciones de radio)

### Semana 3-4: Reviews
- 20 reviewers potenciales (nombres de canales/blogs)
- Estrategia de reviews Amazon (cuantas necesitamos, como conseguirlas)

## FASE 3: POST-LANZAMIENTO (meses 2-6)

### Mes 2-3: Escalar
- Retargeting (presupuesto mensual, segmentacion, plataformas)
- Cross-promotion (autores para colaborar)

### Mes 3-4: Formatos
- Audiolibro (costo de produccion, narrador, plataformas)
- Ebook promociones (Kindle Countdown, Free Book Promotions)

### Mes 4-6: Expansion
- Internacional (USA hispanos, Espana, Colombia, Argentina)
- Derechos (traduccion, coedicion)
- Alianzas B2B (empresas, iglesias, centros de retiro)"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=8000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def marketing_plan(self):
        print("\n[AGENTE] Growth Marketer 12 Meses...", end=" ", flush=True)
        system = "Eres growth marketer. Dominas Meta Ads, Google Ads, Amazon Ads, email marketing, y afiliados en Mexico. Generas planes concretos con numeros."
        prompt = f"""Crea un PLAN DE MARKETING DIGITAL de 12 meses para TSBN en Mexico.

CONTEXTO:
{self.bible[:3000]}

Estructura obligatoria (minimo 1500 palabras):

## 1. CANALES Y PRESUPUESTOS
| Canal | Presupuesto Mensual | Objetivo | KPI Principal |
|-------|---------------------|----------|---------------|
| Meta Ads (FB/IG) | $X | Adquisicion | CAC |
| Google Ads | $X | Intencion de compra | ROAS |
| Amazon Ads | $X | Visibilidad en Amazon | ACOS |
| TikTok Organic | $0 | Viralidad | Views |
| Email Marketing | $X | Retencion | Open rate |
| PR/Entrevistas | $X | Credibilidad | Alcance |

## 2. CALENDARIO EDITORIAL MENSUAL
Para cada mes (1-12):
- Tema del mes
- 4 posts de FB/IG (con copy especifico)
- 2 reels/tiktoks (con guion)
- 1 email newsletter
- 1 blog articulo
- Campana de pauta activa (si/no)

## 3. FUNNEL DE CONVERSION
- Top of Funnel: contenido gratuito (que, donde, como)
- Middle of Funnel: lead magnet (ebook gratuito, checklist, etc.)
- Bottom of Funnel: secuencia de emails de venta (5 emails con asuntos)

## 4. INFLUENCERS Y AFILIADOS
- 10 micro-influencers ideales (niches, seguidores, como contactarlos)
- 5 macro-influencers para alianza
- Programa de afiliados (comision, mecanica, tracking)

## 5. METRICAS Y OBJETIVOS
| Mes | Objetivo Ventas | Gasto Marketing | ROAS Esperado |
|-----|-----------------|-----------------|---------------|
| 1-3 | ... | ... | ... |
| 4-6 | ... | ... | ... |
| 7-12 | ... | ... | ... |

## 6. PRESUPUESTO TOTAL ANUAL
- Minimo viable: $X MXN
- Optimico: $X MXN
- Desglose por trimestre"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=8000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def estrategia_contenido(self):
        print("\n[AGENTE] Content Marketer Premium...", end=" ", flush=True)
        system = "Eres content strategist para autores best seller. Creas contenido que vende libros sin ser spam. Conoces algoritmos de Meta, TikTok, y YouTube."
        prompt = f"""Crea una ESTRATEGIA DE CONTENIDO de 30 DIAS listo para publicar.

CONTEXTO:
{self.bible[:3000]}

Genera contenido especifico y listo para usar:

## 1. 30 HOOKS (uno por dia)
Formato: Dia X: "Hook exacto para copiar y pegar"
- 10 hooks inspiracionales
- 10 hooks de dolor/problema
- 10 hooks de transformacion/resultado

## 2. 15 TEMAS DE BLOG (con outline)
Cada uno con:
- Titulo SEO-optimizado
- 5 subtitulos (outline)
- Meta descripcion (155 chars)
- Keywords principales

## 3. 10 REELS/TIKTOK (con guion completo)
Cada uno con:
- Hook de apertura (texto en pantalla)
- Escena/visual descripta
- Texto superpuesto paso a paso
- CTA final exacto
- Musica/sugerencia de estilo

## 4. 5 CARRUSELES DE INSTAGRAM
Cada uno con:
- Slide 1: cover text
- Slide 2-4: contenido paso a paso
- Slide 5: CTA + link

## 5. SECUENCIA DE EMAILS (5 emails listos)
Cada uno con:
- Asunto exacto
- Preview text
- Cuerpo completo (300-500 palabras)
- CTA boton text

## 6. PILLARS DE CONTENIDO (3)
- Definicion de cada pillar
- 10 ideas de contenido por pillar
- Formato principal por pillar

## 7. HASHTAGS Y KEYWORDS
- 20 hashtags por plataforma (IG, TikTok, YT)
- Keywords para SEO de blog
- Keywords para Amazon A+ Content"""
        content, provider = self._llamar(prompt, system, temp=0.35, max_tok=8000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def keywords_seo(self):
        print("\n[AGENTE] Keywords y SEO...", end=" ", flush=True)
        system = "Eres especialista en SEO para libros en Amazon y Google. Conoces Amazon KDP keywords, search volume, y competencia de palabras clave."
        prompt = f"""Genera palabras clave para TSBN en 3 categorias:

## 1. AMAZON KDP KEYWORDS (7 backend keywords, 50 chars cada una)
- Lista exacta de 7 strings para backend de KDP
- Justificacion de cada una

## 2. AMAZON A+ CONTENT / LISTING
- Titulo optimizado (200 chars)
- Subtitulo (60 chars)
- 5 bullet points optimizados
- Descripcion HTML optimizada
- 15 palabras clave para search terms

## 3. SEO BLOG/WEB
- 10 keywords de alto volumen (estimado)
- 10 keywords de nicho largo (long-tail)
- 5 temas de blog basados en keyword gap

## 4. ADS KEYWORDS
- 20 keywords para Google Ads (match types)
- 20 keywords para Meta Ads (intereses)
- Audiencias similares sugeridas

## 5. COMPETENCIA DE KEYWORDS
- 5 libros competidores y sus keywords principales
- Oportunidades de keyword no cubiertas"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def distribucion(self):
        print("\n[AGENTE] Distribucion y Canales...", end=" ", flush=True)
        system = "Eres distribuidor editorial con experiencia en Mexico, LATAM, USA hispano, y Espana. Conoces Amazon KDP, IngramSpark, Gandhi, Casa del Libro, ACX, Findaway."
        prompt = f"""Crea estrategia de DISTRIBUCION para TSBN.

CONTEXTO:
{self.bible[:3000]}

Estructura:

## 1. FORMATOS Y PRECIOS
| Formato | Precio Sugerido (MXN) | Precio Sugerido (USD) | Margen Estimado |
|---------|----------------------|----------------------|-----------------|
| Ebook | ... | ... | ... |
| Tapa Blanda | ... | ... | ... |
| Tapa Dura | ... | ... | ... |
| Audiolibro | ... | ... | ... |

## 2. PLATAFORMAS DIGITALES
Para cada plataforma:
- Amazon KDP (proceso, costos, timeline)
- Apple Books
- Google Play Books
- Kobo
- Scribd
- Storytel
- 24symbols

## 3. DISTRIBUCION FISICA EN MEXICO
- Gandhi (como contactar, requisitos, margen)
- Porrua
- Casa del Libro
- Walmart / Soriana / Chedraui
- Aeropuertos (libros de viaje)
- Ferias del libro

## 4. DISTRIBUCION INTERNACIONAL
- USA hispanos (Amazon US, IngramSpark)
- Espana (Amazon ES, Casa del Libro online)
- Colombia, Argentina, Chile (plataformas locales)
- Audiolibro internacional (ACX, Findaway Voices)

## 5. DERECHOS Y EXPANSION
- Traduccion a ingles (costo, mercado potencial)
- Coedicion con editorial tradicional
- Adaptacion a curso online
- Coaching/mentoria basada en el libro
- Derechos para iglesias/organizaciones

## 6. TIMELINE DE LANZAMIENTO POR CANAL
| Fase | Canales | Fecha Aprox |
|------|---------|-------------|
| 1 | ... | Mes X |
| 2 | ... | Mes X |"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def alianzas(self):
        print("\n[AGENTE] Alianzas Estrategicas...", end=" ", flush=True)
        system = "Eres networker en el mundo editorial y espiritual de Mexico. Conoces iglesias, coaches, terapeutas, y organizaciones que podrian promover el libro."
        prompt = f"""Identifica ALIANZAS ESTRATEGICAS para TSBN en Mexico/LATAM.

CONTEXTO:
{self.bible[:3000]}

Para cada categoria (minimo 5 por categoria):

## 1. IGLESIAS Y CENTROS ESPIRITUALES
- Nombre del lugar o tipo
- Por que es buena alianza
- Como contactarlos
- Que ofrecerles (descuentos, eventos, donaciones)

## 2. COACHES Y TERAPEUTAS
- Nichos especificos (coach espiritual, terapeuta familiar)
- Como contactarlos
- Programa de referidos

## 3. INFLUENCERS DEL NICHO
- Micro (10k-50k seguidores): 10 nombres o tipos
- Macro (50k-500k): 5 nombres o tipos
- Mega (500k+): 2 nombres o tipos
- Como contactarlos y que ofrecer

## 4. EMPRESAS (B2B)
- Tipos de empresas que comprarian bulk
- Programas de bienestar laboral
- Como contactar RH

## 5. EVENTOS Y FERIAS
- 10 eventos en Mexico donde vender/promover
- Fechas aproximadas
- Costo de stand/participacion

## 6. PROGRAMA DE EMBAJADORES
- Como reclutar 20 embajadores del libro
- Beneficios para ellos
- Contenido que compartiran
- Tracking de resultados"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def forecast_ventas(self):
        print("\n[AGENTE] Forecast de Ventas...", end=" ", flush=True)
        system = "Eres analista financiero editorial. Creas proyecciones realistas basadas en benchmarks de autoayuda en LATAM. Trabajas en MXN y USD."
        prompt = f"""Crea PROYECCION DE VENTAS para TSBN (24 meses).

CONTEXTO:
{self.bible[:3000]}

Estructura:

## 1. PRECIOS Y MARGENES
| Formato | Precio Publico | Costo | Margen | Royalty Neto |
|---------|---------------|-------|--------|--------------|
| Ebook MXN | ... | ... | ... | ... |
| Tapa Blanda MXN | ... | ... | ... | ... |
| Audiolibro MXN | ... | ... | ... | ... |
| Ebook USD | ... | ... | ... | ... |

## 2. ESCANARIOS (unidades vendidas)

### Escenario Pesimista
| Mes | Ebook | Fisico | Audio | Total | Revenue |
|-----|-------|--------|-------|-------|---------|
| 1 | ... | ... | ... | ... | ... |
...(meses 1-24)
- Total 24 meses: X unidades, $Y MXN

### Escenario Realista
(misma tabla)

### Escenario Optimista
(misma tabla)

## 3. BREAK-EVEN ANALYSIS
- Inversion total (edicion + diseno + marketing inicial)
- Mes de break-even por escenario
- ROI a 12 meses y 24 meses

## 4. COSTOS DETALLADOS
| Rubro | Costo Estimado (MXN) | Notas |
|-------|----------------------|-------|
| Edicion profesional | ... | ... |
| Diseno portada | ... | ... |
| Formateo interior | ... | ... |
| Marketing mes 0 | ... | ... |
| Marketing mensual | ... | ... |
| Audiolibro | ... | ... |
| Traduccion | ... | ... |
| TOTAL | ... | ... |

## 5. FACTORES DE EXITO/FRACASO
- 5 factores que nos llevan al optimista
- 5 factores que nos llevan al pesimista
- Estrategia de contingencia"""
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"OK [{provider}] | {len(content)} chars")
        return content

    def compilar_documentos(self, **docs):
        print("\n[COMPILACION] Generando documentos del Equipo 3 v2...")

        mapping = [
            ("01_BUYER_PERSONA.md", "Buyer Persona Premium", docs["buyer"]),
            ("02_ANALISIS_MERCADO.md", "Analisis de Mercado", docs["mercado"]),
            ("03_COMPARABLES.md", "Autores Comparables", docs["comparables"]),
            ("04_GO_TO_MARKET.md", "Go-to-Market", docs["gtm"]),
            ("05_MARKETING_PLAN.md", "Marketing Plan 12 Meses", docs["marketing"]),
            ("06_ESTRATEGIA_CONTENIDO.md", "Estrategia de Contenido 30 Dias", docs["contenido"]),
            ("07_KEYWORDS_SEO.md", "Keywords y SEO", docs["keywords"]),
            ("08_DISTRIBUCION.md", "Distribucion", docs["distribucion"]),
            ("09_ALIANZAS_ESTRATEGICAS.md", "Alianzas Estrategicas", docs["alianzas"]),
            ("10_FORECAST_VENTAS.md", "Forecast de Ventas", docs["forecast"]),
        ]

        total_chars = 0
        for fname, title, content in mapping:
            full = f"# {title} — Todas Son Buenas Noticias\n\n"
            full += f"> Generado por: Equipo 3 v2 de Estrategia (Alexandria Writer)\n"
            full += f"> Fecha: {datetime.now().isoformat()}\n\n"
            full += content
            with open(OUTPUT / fname, "w", encoding="utf-8") as f:
                f.write(full)
            total_chars += len(content)
            print(f"  -> {fname} ({len(content)} chars)")

        print(f"\n  Total generado: {total_chars} caracteres en {len(mapping)} documentos")

    def ejecutar(self):
        self.cargar_entradas()

        buyer = self.buyer_persona()
        mercado = self.analisis_mercado()
        comparables = self.comparables()
        gtm = self.go_to_market()
        marketing = self.marketing_plan()
        contenido = self.estrategia_contenido()
        keywords = self.keywords_seo()
        distribucion = self.distribucion()
        alianzas = self.alianzas()
        forecast = self.forecast_ventas()

        self.compilar_documentos(
            buyer=buyer, mercado=mercado, comparables=comparables,
            gtm=gtm, marketing=marketing, contenido=contenido,
            keywords=keywords, distribucion=distribucion,
            alianzas=alianzas, forecast=forecast
        )

        print("\n" + "=" * 65)
        print("  EQUIPO 3 v2 COMPLETADO")
        print("=" * 65)
        print(f"\n  Documentos en: {OUTPUT}")
        print("  10 documentos generados")
        return True


def main():
    equipo = Equipo3EstrategiaV2()
    equipo.ejecutar()


if __name__ == "__main__":
    main()
