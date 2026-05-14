# Casa Alexandria — Sistema Editorial

Un taller editorial asistido por inteligencia artificial para manuscritos en español. El sistema trabaja para el manuscrito y para el autor. Nada más.

---

## Filosofía

Tres principios duros:

1. **La voz del autor es ley.** Antes de analizar una línea, todos los agentes leen el `voz_autor.yaml` del proyecto. Las sugerencias que contradigan esa voz no llegan al autor.
2. **El Director Editorial arbitra; no agrega.** No hay consolidador pasivo. El Director decide qué entra al dictamen, en qué orden, por qué, y qué debe el autor decidir.
3. **Un solo dictamen por iteración.** Una carta al autor, clara, firmada. No tres verdades paralelas.

El sistema no produce buyer personas, ROI ni comparables de mercado mientras el manuscrito está abierto. El flujo de marketing está separado y se activa solo cuando el autor lo decide.

---

## Arquitectura

```
alexandria-writer/
├── MANIFIESTO_EDITORIAL.md          ← documento rector del sistema
├── skills/
│   └── base_editorial.md            ← código de comportamiento de la casa
├── agents/
│   ├── editorial/                   ← siete oficios editoriales, en español
│   │   ├── 00_lector_de_voz.md      ← filtro de voz (determinista)
│   │   ├── 01_director_editorial.md ← árbitro y redactor del dictamen
│   │   ├── 02_estructuralista_de_ensayo.md
│   │   ├── 03_editor_de_linea_es_mx.md
│   │   ├── 04_lector_ideal_simulado.md   ← pendiente de implementación en Python
│   │   ├── 05_custodio_doctrinal.md      ← pendiente de implementación en Python
│   │   └── 06_auditor_de_continuidad.md  ← pendiente de implementación en Python
│   └── _legacy_en/                  ← agentes en inglés archivados (v2)
├── core/
│   └── editorial/
│       ├── pipeline_editorial.py    ← punto de entrada
│       ├── agente_director_editorial.py
│       ├── agente_estructuralista.py
│       ├── agente_editor_de_linea.py
│       ├── agente_lector_de_voz.py
│       ├── base_agente.py           ← clase base para todos los oficios
│       ├── manuscrito.py            ← extracción PDF y segmentación por capítulo
│       └── voz_autor.py             ← carga y servicio del voz_autor.yaml
└── docs/
    └── Autores/<Autor>/Proyectos/<Libro>/
        ├── voz_autor.yaml           ← huella vocal del autor (ley dura)
        ├── Libros/                  ← PDF del manuscrito
        └── iteracion_NN/
            ├── dictamen_editorial.md   ← carta al autor (única salida)
            ├── cambios_propuestos.json ← sugerencias estructuradas
            ├── bloqueos_voz.json       ← lo que se bloqueó y por qué
            ├── decisiones_autor.json   ← esqueleto que el autor llena
            ├── lectura_inicial.md      ← nota interna del Director (no para el autor)
            └── log_iteracion.json      ← métricas de la corrida
```

---

## Los siete oficios

| Oficio | Qué cuida | Estado |
|---|---|---|
| **Lector de Voz** | Filtra toda sugerencia antes de que llegue al autor. 5 filtros deterministas. | Implementado |
| **Director Editorial** | Lee el manuscrito, arbitra, redacta el dictamen. Entra dos veces por iteración. | Implementado |
| **Estructuralista de Ensayo** | Tesis, testimonios, desarrollo, invitación. Curva interna del libro. | Implementado |
| **Editor de Línea (es-MX)** | Gramática, puntuación, ritmo. Sin tocar la voz. | Implementado |
| **Lector Ideal Simulado** | UX lectora: dónde el lector subraya, se cansa, llora. | Pendiente (`.md` definido) |
| **Custodio Doctrinal** | Coherencia espiritual. Solo activo en libros que hablan de fe. | Pendiente (`.md` definido) |
| **Auditor de Continuidad** | Mantras, promesas, callbacks, contradicciones internas. Entra al final. | Pendiente (`.md` definido) |

---

## Uso

### Requisitos

```bash
pip install pdfplumber pyyaml
```

El sistema usa un `LLMRouter` con failover entre proveedores gratuitos (Cerebras, SambaNova, Mistral, Groq, OpenRouter, Gemini). Configurá tus API keys en variables de entorno o en `core/llm_router.py`.

### Correr el pipeline

```bash
# Corrida completa sobre todos los capítulos
python core/editorial/pipeline_editorial.py --autor Arturo_Ledezma --libro TSBN

# Correr solo capítulos específicos (para pruebas rápidas)
python core/editorial/pipeline_editorial.py --autor Arturo_Ledezma --libro TSBN --bloques 7 15 16

# Correr solo un oficio
python core/editorial/pipeline_editorial.py --autor Arturo_Ledezma --libro TSBN --oficios estructuralista
```

La salida aparece en `docs/Autores/<Autor>/Proyectos/<Libro>/iteracion_NN/`. El número de iteración se asigna automáticamente.

### Registrar un nuevo autor

1. Crear la carpeta `docs/Autores/<Nombre>/Proyectos/<Libro>/`.
2. Colocar el PDF del manuscrito en `docs/Autores/<Nombre>/Libros/`.
3. Completar el cuestionario (`docs/Cuestionario/CUESTIONARIO_DEL_AUTOR.md`) y guardarlo en la carpeta del proyecto.
4. Crear el `voz_autor.yaml` a partir de las respuestas del cuestionario. Secciones mínimas requeridas: `autor`, `libro`, `intencion`, `lector_imaginado`, `prohibido`, `recursos_intencionales_del_autor`.

---

## El flujo iterativo

Cada iteración es un ciclo de cuatro pasos:

1. **Diagnóstico** — los agentes leen, el Lector de Voz filtra, el Director arbitra, se entrega `dictamen_editorial.md`.
2. **Lectura del autor** — el autor lee y marca *aceptado / rechazado / modificado* en `decisiones_autor.json`.
3. **Aplicación** — solo lo aceptado o modificado entra al manuscrito.
4. **Re-diagnóstico del diff** — la siguiente iteración analiza el cambio, no el libro entero.

---

## Libro piloto

**«<Título del libro piloto>»** de <Autor del proyecto piloto>. Ensayo confesional, ~30 capítulos, 8 iteraciones completadas al momento de este documento. Los archivos están en `docs/Autores/<autor>/Proyectos/<id_libro>/`.

---

## Lo que el sistema nunca hace

- Reescribir una frase del autor sin aprobación del Lector de Voz y el Director Editorial.
- Marcar como debilidad un recurso declarado intencional en el `voz_autor.yaml`.
- Confundir la voz del autor con la de prologuistas, epígrafes o citas de terceros.
- Mezclar registro editorial con registro de marketing.
- Entregar más de un dictamen por iteración.

---

*Casa Alexandria — v1 — 2026-05-13*
