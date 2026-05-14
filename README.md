# Alexandria Writer

> Sistema multi-agente de IA para análisis editorial profundo de manuscritos.
> Versátil para cualquier libro: ficción, no ficción, poesía, ensayo, espiritualidad, memorias.

---

## ¿Qué es Alexandria Writer?

Alexandria Writer es un **pipeline automatizado de 4 equipos especializados** que analiza un manuscrito completo (desde un PDF) y genera un paquete de documentos editoriales profesionales:

- **Inteligencia** sobre la obra, su estructura, temas y voz.
- **Análisis editorial** con recomendaciones de mejora consolidadas y priorizadas.
- **Estrategia de mercado** (generada por agentes especializados, no por el autor).
- **Refinamiento** con calendario de edición, resolución de conflictos y plan de acción.

El autor **no necesita saber de marketing ni de edición**. El sistema genera todo. El autor solo aporta su manuscrito y sus respuestas a un **Cuestionario de Exploración** que calibra el análisis a su visión personal.

---

## Estructura del Proyecto

```
alexandria-writer/
├── core/                          # Motor del pipeline
│   ├── llm_router.py              # Router multi-API con failover y métricas
│   ├── pipeline_equipo_1_inteligencia.py
│   ├── pipeline_equipo_2_analisis_v2.py
│   ├── pipeline_equipo_3_estrategia_v2.py
│   ├── pipeline_equipo_4_refinamiento.py
│   └── pipeline_maestro.py        # Orquestador de los 4 equipos
├── agents/                        # Instrucciones y contexto por agente
│   ├── narrative-arch/
│   ├── character-dev/
│   ├── style-tone/
│   └── ...
├── projects/
│   └── tsbn/                      # Tu libro (ejemplo activo)
│       ├── TSBN-digital-A4.pdf    # Manuscrito fuente
│       ├── equipo1/               # Salida del Equipo 1 (6 docs)
│       ├── equipo2/               # Salida del Equipo 2 (5 docs + JSON)
│       ├── equipo3/               # Salida del Equipo 3 (10 docs)
│       ├── equipo4/               # Salida del Equipo 4 (5 docs)
│       └── pipeline_log.json      # Registro de ejecución
├── scripts/                       # Utilidades adicionales
├── skills/                        # Reglas base y contextos
└── INSTRUCCIONES_PARA_OTRO_MODELO_IA.md  # Guía para ejecución por IA
```

---

## Los 4 Equipos del Pipeline

| Equipo | Función | Documentos Generados |
|--------|---------|---------------------|
| **Equipo 1: Inteligencia** | Extrae texto, sintetiza sinopsis, mapea capítulos, identifica temas, analiza voz y define público objetivo inicial. | `01_BIBLE_DEL_LIBRO.md`, `02_MAPA_CAPITULOS.md`, `03_ANALISIS_TEMATICO.md`, `04_VOZ_TONO_ESTILO.md`, `05_PUBLICO_OBJETIVO.md`, `06_RESUMEN_EJECUTIVO.md` |
| **Equipo 2: Análisis Editorial v2** | 6 agentes especializados (5D, corrector, estilista, estructurista, teólogo, mercadólogo) analizan el texto por chunks. Consolidador global elimina duplicados. Editor Jefe prioriza Top 30. | `01_ANALISIS_5D.md`, `02_EDICIONES_CONSOLIDADAS.md` (127 recs), `recomendaciones.json`, `03_TOP30_PRIORITARIO.md`, `04_OPORTUNIDADES.md`, `05_METRICAS_CALIDAD.md` |
| **Equipo 3: Estrategia de Mercado v2** | Genera buyer persona, análisis de mercado, comparables reales, plan Go-to-Market, marketing 12 meses, contenido 30 días, keywords SEO, distribución, alianzas y forecast de ventas. | 10 documentos de estrategia (ver `projects/tsbn/equipo3/`) |
| **Equipo 4: Refinamiento** | Crea calendario de edición 8 semanas, resuelve conflictos entre recomendaciones, integra cronograma edición+marketing, brief ejecutivo final y plan de próximas iteraciones. | `01_PLAN_EDICION_CALENDARIO.md`, `02_CONFLICTOS_RESUELTOS.md`, `03_CRONOGRAMA_INTEGRADO.md`, `04_BRIEF_FINAL_EJECUTIVO.md`, `05_PROXIMAS_ITERACIONES.md` |

---

## Cómo Usar el Sistema (para Cualquier Libro)

### Paso 1: Coloca tu manuscrito

Guarda tu PDF en `projects/<tu-libro>/`.

```
projects/
└── mi-novela/
    └── manuscrito.pdf
```

### Paso 2: Completa el Cuestionario de Exploración

Descarga `CUESTIONARIO_GENERICO_ESCRITORES.docx` (o usa la plantilla Markdown).

Responde las preguntas en tus propias palabras. No se trata de vender el libro, sino de **entender tu visión** para que el sistema no la malinterprete.

Guarda tus respuestas como `RESPUESTAS_AUTOR_<LIBRO>.md` en la carpeta del proyecto.

### Paso 3: Ejecuta el Pipeline Maestro

```powershell
# Pipeline completo: E1 → E2 → E3 → E4
python core/pipeline_maestro.py --modo completo

# Solo un equipo específico
python core/pipeline_maestro.py --equipo 2 --modo completo

# Saltar equipos ya completados (para continuar)
python core/pipeline_maestro.py --modo completo --skip-equipo 1 --skip-equipo 2
```

Modos disponibles para el Equipo 2:
- `completo` — Análisis de todas las dimensiones
- `transiciones` — Fluidez entre capítulos y cohesión narrativa
- `tecnico` — Precisión teológica, bíblica o temática
- `marketing` — Potencial comercial, posicionamiento, hook

### Paso 4: Revisa los entregables

Todos los documentos se guardan en `projects/<tu-libro>/equipo1/` a `equipo4/`.

**Empieza por aquí:**
1. `equipo4/04_BRIEF_FINAL_EJECUTIVO.md` — Resumen de 1 página (2 minutos)
2. `equipo2/03_TOP30_PRIORITARIO.md` — Los 30 cambios más importantes
3. `equipo4/01_PLAN_EDICION_CALENDARIO.md` — Qué hacer semana a semana

---

## Tecnología

- **Router multi-API**: Fallover automático entre SambaNova, Cerebras, Mistral, Groq, OpenRouter, Gemini, NVIDIA, Google Cloud Vertex AI.
- **Rate limiting + circuit breaker**: Evita bloqueos y gestiona límites de uso gratuito.
- **Procesamiento por chunks**: Divide manuscritos largos en segmentos analizables sin perder contexto.
- **Formatos estructurados**: YAML y JSON para que las recomendaciones sean parseables por otros sistemas.
- **Sin costo inicial**: Usa APIs gratuitas de proveedores con tier gratuito.

---

## Principios del Sistema

1. **El autor es el director, la IA es el taller.** El sistema propone; el autor decide.
2. **Nunca edita el manuscrito directamente.** Solo genera recomendaciones para que el autor las aplique.
3. **Marketing automatizado, no impuesto.** Las estrategias de mercado se generan por agentes especializados, no por el autor.
4. **Universal por diseño.** Funciona con cualquier libro, género o formato.
5. **Iterativo.** Cada ejecución del pipeline genera un plan de próximas iteraciones para mejorar continuamente.

---

## Estado del Proyecto Piloto (TSBN)

| Campo | Valor |
|-------|-------|
| Título | Todas Son Buenas Noticias |
| Autor | Arturo Ledezma Ruan |
| Género | Autoayuda espiritual / Desarrollo personal |
| Páginas | 91 |
| Pipeline v2 | ✅ Ejecutado completamente |
| Equipos | 4/4 completados |
| Documentos generados | 26 + 1 JSON |

---

*Alexandria Writer — Pipeline v2 | 4 Equipos | 2026-05-12*
