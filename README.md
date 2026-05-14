<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-10B981?style=for-the-badge" alt="Production Ready">
  <img src="https://img.shields.io/badge/Licencia-MIT-6366F1?style=for-the-badge" alt="MIT License">
  <img src="https://img.shields.io/badge/Idioma-es--MX-F59E0B?style=for-the-badge" alt="es-MX">
</p>

<p align="center">
  <svg width="100%" height="120" viewBox="0 0 820 120" xmlns="http://www.w3.org/2000/svg" style="max-width: 820px;">
    <defs>
      <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" style="stop-color:#0f172a"/>
        <stop offset="100%" style="stop-color:#1e3a5f"/>
      </linearGradient>
      <filter id="glow">
        <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
        <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
      </filter>
    </defs>
    <rect width="820" height="120" fill="url(#bg)" rx="14"/>
    <text x="410" y="52" text-anchor="middle" fill="#f8fafc" font-family="system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="28" font-weight="300" letter-spacing="8" filter="url(#glow)">BINARIAS LABS</text>
    <text x="410" y="82" text-anchor="middle" fill="#94a3b8" font-family="system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" font-size="13" font-weight="400" letter-spacing="14">E D I T O R I A L</text>
    <path d="M0,102 Q205,82 410,102 T820,102" fill="none" stroke="#3b82f6" stroke-width="1.2" opacity="0.35">
      <animate attributeName="d" values="M0,102 Q205,82 410,102 T820,102;M0,102 Q205,118 410,102 T820,102;M0,102 Q205,82 410,102 T820,102" dur="10s" repeatCount="indefinite"/>
    </path>
    <path d="M0,108 Q205,95 410,108 T820,108" fill="none" stroke="#60a5fa" stroke-width="0.8" opacity="0.2">
      <animate attributeName="d" values="M0,108 Q205,95 410,108 T820,108;M0,108 Q205,115 410,108 T820,108;M0,108 Q205,95 410,108 T820,108" dur="7s" repeatCount="indefinite"/>
    </path>
  </svg>
</p>

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

<p align="center">
  <svg width="100%" height="28" viewBox="0 0 800 28" xmlns="http://www.w3.org/2000/svg" style="max-width: 800px;">
    <line x1="0" y1="14" x2="365" y2="14" stroke="#e2e8f0" stroke-width="1"/>
    <circle cx="400" cy="14" r="3.5" fill="#3b82f6">
      <animate attributeName="r" values="3.5;5;3.5" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/>
    </circle>
    <line x1="435" y1="14" x2="800" y2="14" stroke="#e2e8f0" stroke-width="1"/>
  </svg>
</p>

## Cómo nació esto

No fue en una incubadora. Ni en un hackathon. Fue una tarde cualquiera.

Arturo —amigo, mentor y figura a seguir— estaba mostrándome su libro. Hablamos de historias, de voces, de lo difícil que es darle forma a lo que sientes. Y de repente llegó un pensamiento: *estaría padre hacer una editorial*.

En paralelo, otro: ¿cómo se ve una editorial por dentro? La única que había visto era la del Daily Bugle. Sí, esa. *Poom*. Spider-Man.

Empecé a imaginar a Arturo como el editor en jefe —con su pasión, su exigencia, su visión— y a mí mismo como quien está detrás de la cámara, construyendo la herramienta que hace realidad cada edición.

De ahí surgió todo: los equipos, los oficios, los agentes. No los diseñé en un pizarrón. Los *imaginé* como colaboradores reales, con nombres, personalidades y tareas concretas. Un estructuralista que le dice al autor dónde su tesis se pierde. Un editor de línea que respeta su ritmo. Un lector ideal que siente exactamente lo que el autor quiere transmitir.

Esa tarde no nació un software. **Nació una casa editorial.**

<p align="center">
  <svg width="100%" height="28" viewBox="0 0 800 28" xmlns="http://www.w3.org/2000/svg" style="max-width: 800px;">
    <line x1="0" y1="14" x2="365" y2="14" stroke="#e2e8f0" stroke-width="1"/>
    <circle cx="400" cy="14" r="3.5" fill="#3b82f6">
      <animate attributeName="r" values="3.5;5;3.5" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/>
    </circle>
    <line x1="435" y1="14" x2="800" y2="14" stroke="#e2e8f0" stroke-width="1"/>
  </svg>
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

<p align="center">
  <svg width="100%" height="24" viewBox="0 0 800 24" xmlns="http://www.w3.org/2000/svg" style="max-width: 800px;">
    <line x1="0" y1="12" x2="365" y2="12" stroke="#e2e8f0" stroke-width="1"/>
    <circle cx="400" cy="12" r="3.5" fill="#3b82f6">
      <animate attributeName="r" values="3.5;5;3.5" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/>
    </circle>
    <line x1="435" y1="12" x2="800" y2="12" stroke="#e2e8f0" stroke-width="1"/>
  </svg>
</p>

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
│   │   └── <id_libro>/                # Proyecto piloto activo
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

<p align="center">
  <svg width="100%" height="24" viewBox="0 0 800 24" xmlns="http://www.w3.org/2000/svg" style="max-width: 800px;">
    <line x1="0" y1="12" x2="365" y2="12" stroke="#e2e8f0" stroke-width="1"/>
    <circle cx="400" cy="12" r="3.5" fill="#3b82f6">
      <animate attributeName="r" values="3.5;5;3.5" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/>
    </circle>
    <line x1="435" y1="12" x2="800" y2="12" stroke="#e2e8f0" stroke-width="1"/>
  </svg>
</p>

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

<p align="center">
  <svg width="100%" height="24" viewBox="0 0 800 24" xmlns="http://www.w3.org/2000/svg" style="max-width: 800px;">
    <line x1="0" y1="12" x2="365" y2="12" stroke="#e2e8f0" stroke-width="1"/>
    <circle cx="400" cy="12" r="3.5" fill="#3b82f6">
      <animate attributeName="r" values="3.5;5;3.5" dur="4s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.5;1;0.5" dur="4s" repeatCount="indefinite"/>
    </circle>
    <line x1="435" y1="12" x2="800" y2="12" stroke="#e2e8f0" stroke-width="1"/>
  </svg>
</p>

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
  <svg width="100%" height="40" viewBox="0 0 800 40" xmlns="http://www.w3.org/2000/svg" style="max-width: 800px;">
    <line x1="0" y1="20" x2="320" y2="20" stroke="#e2e8f0" stroke-width="1"/>
    <circle cx="360" cy="20" r="3" fill="#3b82f6" opacity="0.6">
      <animate attributeName="opacity" values="0.6;0.2;0.6" dur="3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="400" cy="20" r="3" fill="#3b82f6">
      <animate attributeName="opacity" values="1;0.4;1" dur="3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="440" cy="20" r="3" fill="#3b82f6" opacity="0.6">
      <animate attributeName="opacity" values="0.6;0.2;0.6" dur="3s" repeatCount="indefinite"/>
    </circle>
    <line x1="480" y1="20" x2="800" y2="20" stroke="#e2e8f0" stroke-width="1"/>
  </svg>
</p>

<p align="center">
  <strong>Binarias_Labs_Editorial</strong> · Alexandria Writer · v2/v3 · 2026
</p>
