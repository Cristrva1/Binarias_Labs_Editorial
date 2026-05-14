<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-10B981?style=for-the-badge" alt="Production Ready">
  <img src="https://img.shields.io/badge/Licencia-MIT-6366F1?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Idioma-es--MX-F59E0B?style=for-the-badge" alt="es-MX">
</p>

<h1 align="center">
  <br>
  Binarias_Labs_Editorial
  <br>
</h1>

<p align="center">
  <strong>Taller editorial asistido por inteligencia artificial.</strong><br>
  Análisis profundo de manuscritos mediante orquestación multi-agente.<br>
  <em>Ficción · No ficción · Poesía · Ensayo · Espiritualidad · Memorias</em>
</p>

<p align="center">
  <a href="#arquitectura">Arquitectura</a> ·
  <a href="#cómo-funciona">Cómo funciona</a> ·
  <a href="#uso-rápido">Uso rápido</a> ·
  <a href="#estructura">Estructura</a> ·
  <a href="#tecnología">Tecnología</a> ·
  <a href="#principios">Principios</a>
</p>

---

## ¿Qué es Binarias_Labs_Editorial?

**Binarias_Labs_Editorial** es el núcleo del sistema **Alexandria Writer**: un pipeline automatizado de 4 equipos especializados que analiza un manuscrito completo (desde PDF) y genera un paquete de documentos editoriales profesionales de alto nivel.

El autor **no necesita saber de marketing ni de edición**. El sistema genera todo. El autor solo aporta su manuscrito y sus respuestas a un **Cuestionario de Exploración** que calibra el análisis a su visión personal.

### Dos arquitecturas, una misión

| Versión | Enfoque | Estado |
|---------|---------|--------|
| **v2 — Pipeline de 4 Equipos** | Análisis integral: inteligencia, edición, mercado y refinamiento. | Estable, ejecutado completamente en piloto. |
| **v3 — Casa Alexandria** | Modelo editorial humanista con 7 oficios, dictamen único por iteración y protección absoluta de la voz del autor. | En evolución activa. Ver [`MANIFIESTO_EDITORIAL.md`](MANIFIESTO_EDITORIAL.md). |

---

## Arquitectura

### Pipeline v2: Los 4 Equipos

```mermaid
flowchart LR
    A[PDF Manuscrito] --> B[Equipo 1: Inteligencia]
    B --> C[Equipo 2: Análisis Editorial]
    C --> D[Equipo 3: Estrategia]
    D --> E[Equipo 4: Refinamiento]
    E --> F[26 Documentos + JSON]
```

| Equipo | Función | Entregables |
|--------|---------|-------------|
| **1 · Inteligencia** | Extracción, sinopsis, mapeo de capítulos, temas, voz y público. | `BIBLE_DEL_LIBRO`, `MAPA_CAPITULOS`, `ANALISIS_TEMATICO`, `VOZ_TONO_ESTILO`, `PUBLICO_OBJETIVO`, `RESUMEN_EJECUTIVO` |
| **2 · Análisis Editorial v2** | 6 agentes especializados (5D, corrector, estilista, estructurista, teólogo, mercadólogo). Consolidador global + Editor Jefe con Top 30 priorizado. | `ANALISIS_5D`, `EDICIONES_CONSOLIDADAS`, `TOP30_PRIORITARIO`, `OPORTUNIDADES`, `METRICAS_CALIDAD`, `recomendaciones.json` |
| **3 · Estrategia de Mercado v2** | Buyer persona, comparables, Go-to-Market, marketing 12 meses, contenido 30 días, SEO, distribución, alianzas, forecast. | 10 documentos de estrategia |
| **4 · Refinamiento** | Calendario 8 semanas, resolución de conflictos, cronograma integrado, brief final, próximas iteraciones. | `PLAN_EDICION_CALENDARIO`, `CONFLICTOS_RESUELTOS`, `CRONOGRAMA_INTEGRADO`, `BRIEF_FINAL_EJECUTIVO`, `PROXIMAS_ITERACIONES` |

### Arquitectura v3: Casa Alexandria

Basada en el [`MANIFIESTO_EDITORIAL.md`](MANIFIESTO_EDITORIAL.md), la v3 refunda el sistema como una **casa editorial** con principios humanistas:

- **La voz del autor es ley** (`voz_autor.yaml`). El Lector de Voz veta cualquier sugerencia que la contradiga.
- **Un solo dictamen por iteración** (`dictamen_editorial.md`). El Director Editorial arbitra, modifica o escala al autor.
- **Siete oficios reales**: Director Editorial, Lector de Voz, Estructuralista de Ensayo, Editor de Línea, Lector Ideal Simulado, Custodio Doctrinal y Auditor de Continuidad.
- **El mercado se mira al final.** La casa edita primero; el comercial viene después, si el autor lo decide.

---

## Cómo funciona

```
1. Autor sube PDF  →  2. Responde Cuestionario de Exploración
         ↓
3. Pipeline Maestro orquesta los 4 equipos (o los 7 oficios en v3)
         ↓
4. Entrega documentos editoriales estructurados en Markdown/JSON/YAML
```

El sistema **nunca edita el manuscrito directamente**. Solo genera recomendaciones para que el autor las revise, apruebe o modifique. Cada sugerencia cita textualmente el manuscrito, explica el porqué y explicita qué se gana y qué se pierde.

---

## Uso rápido

### 1. Prepara tu proyecto

```bash
projects/
└── mi-libro/
    └── manuscrito.pdf
```

### 2. Ejecuta el pipeline

```bash
# Pipeline completo v2: E1 → E2 → E3 → E4
python alexandria-writer/core/pipeline_maestro.py --modo completo

# Solo un equipo específico
python alexandria-writer/core/pipeline_maestro.py --equipo 2 --modo completo

# Continuar saltando equipos completados
python alexandria-writer/core/pipeline_maestro.py --modo completo --skip-equipo 1 --skip-equipo 2
```

**Modos del Equipo 2:**
- `completo` — Análisis de todas las dimensiones
- `transiciones` — Fluidez entre capítulos y cohesión narrativa
- `tecnico` — Precisión teológica, bíblica o temática
- `marketing` — Potencial comercial, posicionamiento y hook

### 3. Revisa los entregables

Empieza por estos 3 documentos:

1. `equipo4/04_BRIEF_FINAL_EJECUTIVO.md` — Resumen ejecutivo de 1 página
2. `equipo2/03_TOP30_PRIORITARIO.md` — Los 30 cambios más importantes
3. `equipo4/01_PLAN_EDICION_CALENDARIO.md` — Qué hacer semana a semana

---

## Estructura

```
Binarias_Labs_Editorial/
├── MANIFIESTO_EDITORIAL.md          # Documento rector de la v3
├── PLAN_ARQUITECTURA_V3.md          # Plano técnico de la v3
├── alexandria-writer/
│   ├── core/                          # Motor del pipeline
│   │   ├── llm_router.py              # Router multi-API con failover
│   │   ├── pipeline_maestro.py        # Orquestador v2
│   │   ├── pipeline_maestro_v3.py     # Orquestador v3
│   │   ├── pipeline_equipo_1_inteligencia.py
│   │   ├── pipeline_equipo_2_analisis_v2.py
│   │   ├── pipeline_equipo_3_estrategia_v2.py
│   │   ├── pipeline_equipo_4_refinamiento.py
│   │   └── schemas_v3.py              # Esquemas de datos
│   ├── agents/
│   │   ├── editorial/                 # 7 oficios de la Casa Alexandria (v3)
│   │   └── _legacy_en/                # Agentes en inglés, archivados
│   ├── skills/
│   │   └── base_editorial.md          # Código de comportamiento
│   ├── projects/
│   │   └── tsbn/                      # Proyecto piloto activo
│   └── scripts/                       # Utilidades adicionales
├── docs/
│   └── Autores/<Autor>/Proyectos/<Libro>/
│       ├── voz_autor.yaml             # Ley vocal del autor
│       ├── cuestionario.md            # Respuestas del autor
│       └── iteracion_01/
│           ├── dictamen_editorial.md
│           ├── cambios_propuestos.json
│           ├── decisiones_autor.json
│           └── bloqueos_voz.json
└── README.md
```

---

## Tecnología

| Capa | Implementación |
|------|----------------|
| **Router LLM** | Multi-API con failover automático: SambaNova, Cerebras, Mistral, Groq, OpenRouter, Gemini, NVIDIA, Google Cloud Vertex AI |
| **Resiliencia** | Rate limiting, circuit breaker, reintentos exponenciales |
| **Procesamiento** | Segmentación por chunks con preservación de contexto |
| **Formatos** | Markdown, YAML, JSON — parseables y versionables |
| **Transcripción** | Integración con Whisper (OpenAI) para audio a texto |
| **Costo** | APIs gratuitas con tier gratuito; sin costo inicial |

---

## Principios

> *"El autor es el director, la IA es el taller."*

1. **El autor decide.** El sistema propone; el autor aprueba, rechaza o modifica.
2. **Nunca toca el manuscrito.** Solo recomendaciones estructuradas y justificadas.
3. **La voz es sagrada.** Ninguna sugerencia homogeniza al autor.
4. **Marketing solo si el autor lo pide.** La casa edita primero.
5. **Universal por diseño.** Funciona con cualquier libro, género o formato.
6. **Iterativo con memoria.** Cada ciclo aprende de las decisiones del autor.

---

## Estado del Proyecto Piloto

| Campo | Valor |
|-------|-------|
| **Título** | *<Título del Libro Piloto>* |
| **Autor** | *<Nombre del Autor Piloto>* |
| **Género** | Autoayuda espiritual / Desarrollo personal |
| **Páginas** | ~90 |
| **Pipeline v2** | Ejecutado completamente |
| **Equipos** | 4/4 completados |
| **Documentos generados** | 26 + 1 JSON |

---

## Documentos clave

- [`MANIFIESTO_EDITORIAL.md`](MANIFIESTO_EDITORIAL.md) — Filosofía y principios de la Casa Alexandria (v3)
- [`PLAN_ARQUITECTURA_V3.md`](PLAN_ARQUITECTURA_V3.md) — Especificación técnica del sistema v3
- [`alexandria-writer/skills/base_editorial.md`](alexandria-writer/skills/base_editorial.md) — Código de comportamiento de los agentes

---

<p align="center">
  <strong>Binarias_Labs_Editorial</strong> · Alexandria Writer · v2/v3 · 2026
</p>
