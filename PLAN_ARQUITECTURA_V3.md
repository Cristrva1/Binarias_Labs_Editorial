# Plan de Arquitectura v3 — Alexandria Writer

> **Marco mental nuevo:** Sistema editorial inteligente para diagnóstico, posicionamiento y plan de desarrollo de manuscritos.
>
> Objetivo: dejar de verse como un *pipeline de documentos* y empezar a verse como *infraestructura editorial auditable*.

---

## 1. Principios Arquitectónicos v3

| # | Principio | Implicación técnica |
|---|-----------|---------------------|
| 1 | **El diagnóstico es independiente de la estrategia** | Los equipos de análisis editorial y de mercado no comparten prompts ni modelos. Sus salidas se cruzan solo en la capa de arbitraje. |
| 2 | **Toda recomendación lleva evidencia** | Cada hallazgo debe ser rastreable a: chunk del manuscrito, agente origen, severidad, confianza y tipo de intervención. |
| 3 | **El Editor Jefe es un árbitro, no un consolidador pasivo** | Decide conflictos, detecta duplicados semánticos, impone coherencia global y filtra por riesgo. |
| 4 | **La salida habla el idioma editorial** | Plantillas de informe, memo de adquisición, diagnóstico de desarrollo y plan de intervención. No “salida de IA”. |
| 5 | **El sistema se mide** | Métricas de calidad editorial, densidad de problemas, estabilidad de voz y probabilidad de ejecución. |
| 6 | **El autor es director, con veto verificable** | El autor puede aceptar, rechazar o modificar cualquier recomendación; el sistema registra su decisión y ajusta el plan. |

---

## 2. Módulos del Sistema

### Módulo 0: Ingesta y Contexto del Autor
**Responsabilidad:** Recibir el manuscrito y calibrar el sistema a la visión del autor.

- **Entradas:**
  - Manuscrito: `docs/Autores/<autor>/Libros/<libro>.pdf`
  - Cuestionario: `docs/Autores/<autor>/Proyectos/<id_libro>/RESPUESTAS_AUTOR_<LIBRO>.md`
- **Proceso:**
  1. Extracción de texto por chunks con overlap semántico.
  2. Validación de calidad de extracción (detección de OCR fallido, fragmentos truncados).
  3. Inyección de contexto del autor en todos los prompts del pipeline (tono, intención, género, lector ideal, dudas pendientes).
- **Salidas** (en `docs/Autores/<autor>/Proyectos/<id_libro>/m0_ingesta/`):
  - `bible_del_libro.json` (metadatos estructurados).
  - `mapa_chunks.json` (índice con coordenadas de cada chunk: capítulo, página, posición).
  - `contexto_autor.yaml` (perfil calibrado).

### Módulo 1: Diagnóstico Editorial (antes Equipo 2, ahora aislado)
**Responsabilidad:** Responder **qué es el libro y qué le duele**, sin contaminación de marketing.

- **Agentes especializados (por chunk, luego global):**
  - `agente_estructura` — arco, ritmo, tensión, picos de lectura.
  - `agente_voz` — consistencia de tono, distancia narrativa, estabilidad de voz.
  - `agente_continuidad` — coherencia temática, callbacks, continuidad de argumento.
  - `agente_friccion` — puntos de abandono, confusión, fatiga lectora.
  - `agente_fortaleza` — lo que funciona y por qué.
- **Consolidador diagnóstico:**
  - Elimina duplicados semánticos.
  - Agrupa por severidad y capítulo.
  - Calcula métricas de densidad de problemas por capítulo.
- **Salidas:**
  - `diagnostico_estructural.md`
  - `diagnostico_voz_y_ritmo.md`
  - `diagnostico_continuidad.md`
  - `diagnostico_friccion.md`
  - `hallazgos.json` — array de hallazgos con campos obligatorios:
    - `id`, `chunk_ref`, `capitulo`, `pagina_aprox`, `agente`, `tipo` (estructura/voz/continuidad/fricción/fortaleza), `descripcion`, `cita_textual`, `severidad` (1–5), `confianza` (0.0–1.0), `intervencion_sugerida`, `impacto_esperado`.
  - `metricas_editoriales.json` (ver sección 5).

### Módulo 2: Estrategia de Mercado (antes Equipo 3, ahora aislado)
**Responsabilidad:** Responder **cómo se vendería y posicionaría**, basándose en el diagnóstico, sin inventar datos.

- **Regla de oro:** No puede contradecir el diagnóstico. Si el diagnóstico dice “voz inestable”, la estrategia no puede prometer “bestseller de referencia”.
- **Agentes:**
  - `agente_comparables` — benchmarking contra obras del mismo género (usando títulos reales).
  - `agente_posicionamiento` — promesa comercial, hook, propuesta de valor.
  - `agente_canales` — distribución, alianzas, formato óptimo.
  - `agente_forecast` — estimación de ventas basada en comparables y diagnóstico de calidad.
- **Salidas:**
  - `analisis_comparables.md`
  - `posicionamiento_y_promesa.md`
  - `plan_go_to_market.md`
  - `forecast_ventas.md`
  - `alertas_riesgo.md` (conflictos entre lo que pide el marketing y lo que permite el diagnóstico).

### Módulo 3: Evidencia y Trazabilidad (nuevo, transversal)
**Responsabilidad:** Ser el *libro mayor* del sistema. Todo hallazgo, recomendación y decisión pasa por aquí.

- **Componentes:**
  - `evidencia_store.jsonl` — registro inmutable de cada hallazgo.
  - `trazabilidad_graph.md` — grafo de dependencias (hallazgo → agente → chunk → consolidación → editor_jefe → autor).
  - `conflict_log.json` — registro de conflictos entre agentes y cómo se resolvieron.
- **Campos obligatorios por recomendación:**
  - `origen_chunk` (id del chunk que disparó el hallazgo).
  - `agente_productor` (nombre del agente).
  - `conflicto_con` (si otro agente contradijo el hallazgo y por qué).
  - `razon_sobrevivencia` (por qué pasó al consolidado).
  - `impacto_esperado` (qué cambiaría si se acepta).

### Módulo 4: Editor Jefe / Arbitraje Central (nuevo)
**Responsabilidad:** Actuar como dirección editorial. No es un consolidador más; tiene poder de veto, merge y escalamiento.

- **Funciones:**
  1. **Árbitro de conflictos:** Cuando dos agentes discrepan (ej. estructurista vs. estilista), decide con criterio explícito o escala al autor.
  2. **Juez de prioridad:** Ordena el backlog de recomendaciones por ratio `impacto / esfuerzo / riesgo`.
  3. **Detector de duplicados semánticos:** No por string matching; por embedding de la intención de la recomendación.
  4. **Guardián de coherencia global:** Verifica que la suma de recomendaciones no rompa la voz del autor ni el mensaje central.
  5. **Modo "Editor Jefe Resumen":** Entrega solo 3 artefactos:
     - `TOP10_PROBLEMAS_CRITICOS.md`
     - `TOP10_CAMBIOS_ALTO_RETORNO.md`
     - `RIESGO_PRINCIPAL_INTERVENCION.md`
- **Inputs:** Salidas de Módulo 1, Módulo 2 y Módulo 3.
- **Outputs:**
  - `dictamen_editor_jefe.md`
  - `backlog_priorizado.json`
  - `resumen_ejecutivo_editorial.md`

### Módulo 5: Control de Riesgo (nuevo)
**Responsabilidad:** Evitar alucinaciones, sobreedición, sesgo comercial excesivo y contradicción de la voz del autor.

- **Agentes de control:**
  - `guardian_alucinaciones` — verifica que una recomendación tenga cita textual en el manuscrito.
  - `guardian_voz_autor` — compara la recomendación contra `contexto_autor.yaml`; si contradice la intención del autor, bloquea o escala.
  - `guardian_sobreedición` — detecta si la densidad de recomendaciones en un capítulo supera el umbral saludable (ej. >30% del texto marcado para cambio).
  - `guardian_sesgo_comercial` — detecta si Módulo 2 está sobreprometiendo en contradicción con Módulo 1.
- **Salida:**
  - `riesgos_detectados.json`
  - `recomendaciones_bloqueadas.json` (con razón del bloqueo).

### Módulo 6: Benchmarking y Comparativa (nuevo)
**Responsabilidad:** Posicionar el manuscrito en contexto, no opinar en vacío.

- **Fuentes de datos:**
  - Historial del propio autor (manuscritos previos analizados).
  - Obras del mismo género (lista curada por el agente_comparables o proporcionada por el autor).
  - Patrones de manuscritos fuertes (heurísticas de éxito por género).
- **Métricas comparativas:**
  - `percentil_ritmo` vs. comparables.
  - `percentil_claridad_promesa` vs. comparables.
  - `percentil_densidad_problemas` vs. manuscritos previos del autor.
- **Salida:**
  - `benchmark.json`
  - `posicionamiento_relativo.md`

### Módulo 7: Output Profesional (nuevo)
**Responsabilidad:** Convertir los datos estructurados en documentos que parezcan producidos por una editorial, no por un chatbot.

- **Plantillas de salida:**
  - `memo_adquisicion.md` — ¿merece la pena editar este libro? (para uso interno o del autor).
  - `diagnostico_desarrollo.md` — qué tiene y qué le duele.
  - `plan_intervencion.md` — qué hacer, en qué orden, con qué riesgo.
  - `estrategia_publicacion.md` — posicionamiento, canales, forecast.
  - `brief_final_ejecutivo.md` — 1 página, 3 minutos de lectura.
- **Motor de plantillas:** Jinja2/Mustache sobre datos JSON. Separación total de datos y presentación.

---

## 3. Roles y Responsabilidades

| Rol | Tipo | Responsabilidad Principal |
|-----|------|---------------------------|
| **Autor** | Humano | Provee manuscrito, responde cuestionario, aprueba/rechaza/modifica recomendaciones. |
| **Pipeline Maestro** | Orquestador | Ejecuta los módulos en orden, gestiona dependencias y errores. |
| **Agentes de Diagnóstico** | IA (especializado) | Analizan el texto y producen hallazgos con evidencia. |
| **Agentes de Mercado** | IA (especializado) | Analizan posicionamiento sin inventar ni contradecir diagnóstico. |
| **Consolidador Diagnóstico** | IA | Deduplica y estructura hallazgos del Módulo 1. |
| **Editor Jefe** | IA (agente superior) | Arbitra, prioriza, protege la coherencia global y la voz del autor. |
| **Guardianes de Riesgo** | IA (filtros) | Bloquean alucinaciones, sobreedición y sesgos antes de que lleguen al autor. |
| **Motor de Plantillas** | Software | Renderiza los documentos finales desde datos estructurados. |
| **Revisor Humano** | Humano (opcional) | Valida el dictamen del Editor Jefe en casos delicados o de alta severidad. |

---

## 4. Flujo de Datos (Pipeline v3)

```
[Manuscrito PDF] + [Respuestas Autor]
         │
         ▼
┌──────────────────────────────┐
│ Módulo 0: Ingesta + Contexto │
└──────────────┬─────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Módulo 1        │   │ Módulo 2        │
│ Diagnóstico     │   │ Estrategia      │
│ Editorial       │   │ Mercado         │
└──────┬──────────┘   └──────┬──────────┘
       │                     │
       ▼                     ▼
┌─────────────────────────────────────┐
│ Módulo 3: Evidencia y Trazabilidad  │
│ (registra todo en evidencia_store)   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Módulo 5: Control de Riesgo       │
│ (filtra y bloquea lo peligroso)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Módulo 4: Editor Jefe / Arbitraje │
│ (prioriza, resuelve, protege voz)  │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────────────┐   ┌─────────────────┐
│ Módulo 6        │   │ Módulo 7        │
│ Benchmarking    │   │ Output          │
│ (contexto)      │   │ Profesional     │
└─────────────────┘   └─────────────────┘
               │
               ▼
        [Documentos Finales]
        + [Dashboard de Trazabilidad]
```

---

## 5. Taxonomía Editorial Estándar

Toda salida del sistema debe usar este vocabulario unificado:

| Categoría | Términos permitidos | Definición operativa |
|-----------|---------------------|----------------------|
| **Estructura** | arco, ritmo, tensión, pico, valle, cliffhanger, resolución | Organización narrativa y progresión emocional. |
| **Voz** | distancia, tono, registro, estabilidad, autenticidad | Manera consistente (o no) de presentar el contenido. |
| **Promesa** | hook, promesa, expectativa, payoff | Qué le promete al lector y si lo cumple. |
| **Fricción** | confusión, fatiga, repetición, bache, abandono | Puntos donde el lector se detiene o se va. |
| **Coherencia** | continuidad, callback, contradicción, coherencia temática | Unidad lógica y temática del texto. |
| **Legibilidad** | fluidez, densidad, claridad, jerga, accesibilidad | Facilidad de lectura sin evaluar calidad literaria. |
| **Riesgo** | sobreedición, alucinación, sesgo, incompatibilidad | Peligro de que la intervención empeore la obra. |
| **Oportunidad** | fortaleza, diferenciador, ventaja, potencial | Lo que ya funciona y se puede potenciar. |

> **Regla:** Si un agente usa un término fuera de esta taxonomía, el Consolidador o el Editor Jefe lo traduce o lo rechaza.

---

## 6. Métricas de Calidad y Severidad

### Métricas del Manuscrito (por capítulo y global)

| Métrica | Fórmula / Fuente | Umbral de alerta |
|---------|------------------|------------------|
| **Densidad de problemas** | `count(hallazgos severidad ≥3) / palabras_del_capítulo × 1000` | > 5 por 1000 palabras |
| **Gravedad editorial** | `promedio_ponderado(severidad × confianza)` | > 3.5 global |
| **Estabilidad de voz** | `1 - (variación de tono detectada / chunks analizados)` | < 0.7 |
| **Continuidad temática** | `count(callbacks temáticos) / temas introducidos` | < 0.5 |
| **Claridad de promesa comercial** | Score 1–5 del agente_posicionamiento | < 3 |
| **Coherencia autor–posicionamiento** | `similitud_semántica(contexto_autor, promesa_generada)` | < 0.6 |
| **Probabilidad de ejecución** | Ratio `recomendaciones_bloqueadas / total_generadas` | > 0.3 (alerta de calidad del sistema) |

### Métricas del Sistema (meta)

| Métrica | Meta |
|---------|------|
| Trazabilidad completa | 100% de hallazgos con `chunk_ref` y `agente` |
| Hallazgos con cita textual | ≥ 90% |
| Conflictos resueltos por Editor Jefe | 100% registrados en `conflict_log` |
| Bloqueos por Guardian de Riesgo | ≤ 15% (si es más, el sistema está generando mucha basura) |
| Tiempo end-to-end | < 4 horas para manuscritos ≤ 100k palabras |

---

## 7. Formato de Datos Estructurados

### `hallazgo` (objeto JSON mínimo)

```json
{
  "id": "H-001-EST",
  "modulo": "diagnostico_editorial",
  "agente": "agente_estructura",
  "tipo": "estructura",
  "categoria_taxonomica": "ritmo",
  "chunk_ref": "C12-P45",
  "capitulo": 3,
  "pagina_aprox": 45,
  "cita_textual": "El personaje aparece muerto y en la siguiente página habla.",
  "descripcion": "Contradicción narrativa que rompe la inmersión.",
  "severidad": 4,
  "confianza": 0.92,
  "intervencion_sugerida": "Reescribir la transición o eliminar la escena intermedia.",
  "impacto_esperado": "Recupera la credibilidad del arco en el clímax del capítulo.",
  "conflicto_con": null,
  "estado": "aprobado_por_editor_jefe",
  "bloqueos_riesgo": [],
  "decision_autor": "pendiente"
}
```

### `dictamen_editor_jefe` (extracto)

```json
{
  "top10_problemas_criticos": ["H-001-EST", "H-034-VOZ", ...],
  "top10_cambios_alto_retorno": ["H-089-FRT", ...],
  "riesgo_principal_intervencion": {
    "tipo": "sobreedición",
    "descripcion": "El capítulo 7 tiene 23 recomendaciones. Aplicarlas todas podría homogeneizar la voz.",
    "recomendacion_global": "Agrupar en 5 intervenciones de alto nivel en lugar de 23 microcambios."
  },
  "coherencia_global": "aprobada",
  "alertas_mercado": ["El posicionamiento como 'bestseller' contradice el diagnóstico de voz inestable."]
}
```

---

## 8. Roadmap de Implementación

### Fase 1: Evidencia y Trazabilidad (semanas 1–2)
- [ ] Refactorizar Equipo 2 (v2) para que emita `hallazgos.json` en lugar de texto libre.
- [x] Crear `evidencia_store.jsonl` y `trazabilidad_graph.md`. → `m3_evidencia.py`
- [x] Agregar `chunk_ref` obligatorio a todo hallazgo. → `schemas_v3.py`
- [x] Validar que ≥ 90% de hallazgos incluyan `cita_textual`. → `m3_evidencia.py` (alerta si < 90%)

### Fase 2: Métricas de Calidad Editorial (semanas 3–4)
- [x] Implementar `metricas_editoriales.json` con las 7 métricas de manuscrito. → `m1_diagnostico.py`
- [x] Crear `densidad_problemas_por_capitulo.md`. → `m1_diagnostico.py`
- [x] Implementar score de `estabilidad_de_voz` y `continuidad_tematica`. → `m1_diagnostico.py`
- [x] Añadir `probabilidad_de_ejecucion` del sistema. → campo en `MetricasEditoriales`

### Fase 3: Editor Jefe y Arbitraje (semanas 5–7)
- [x] Diseñar agente `editor_jefe` con prompts de arbitraje explícito. → `m4_editor_jefe.py`
- [x] Implementar detector de duplicados semánticos. → `m3_evidencia.py` (Jaccard, sin embeddings)
- [x] Crear modo “Editor Jefe Resumen”: `TOP10_PROBLEMAS`, `TOP10_RETORNO`, `RIESGO_PRINCIPAL`. → `m4_editor_jefe.py`
- [x] Implementar `conflict_log.json` y registro de decisiones. → `m3_evidencia.py` + `m4_editor_jefe.py`

### Fase 4: Separar Diagnóstico de Estrategia (semanas 8–9)
- [x] Aislar M2 (mercado) para que solo lea el diagnóstico, no el texto directamente. → `m2_estrategia.py`
- [x] Implementar `guardian_sesgo_comercial`. → `m5_control_riesgo.py`
- [x] Crear `alertas_riesgo.md` en salida de M2. → `m2_estrategia.py`

### Fase 5: Control de Riesgo (semanas 10–11)
- [x] Implementar `guardian_alucinaciones`. → `m5_control_riesgo.py`
- [x] Implementar `guardian_voz_autor`. → `m5_control_riesgo.py`
- [x] Implementar `guardian_sobreedición`. → `m5_control_riesgo.py`
- [x] Crear `recomendaciones_bloqueadas.json` con razones. → `m5_control_riesgo.py`

### Fase 6: Profesionalizar Output (semanas 12–13)
- [ ] Diseñar plantillas Jinja2. (pendiente — se usa generación LLM directa, sin Jinja2)
- [x] Separar datos (JSON) de presentación (Markdown). → todos los módulos producen JSON + .md
- [x] Implementar `brief_final_ejecutivo.md` de 1 página. → `m7_output_profesional.py`

### Fase 7: Benchmarking (semanas 14–15)
- [x] Crear base de datos de comparables por género (seed). → `data/comparables/autoayuda_espiritual.json`
- [x] Implementar cálculo de percentiles con umbrales de referencia. → `m6_benchmarking.py`
- [x] Generar `posicionamiento_relativo.md`. → `m6_benchmarking.py`

### Fase 8: Dashboard e Interfaz Humana (semanas 16–18)
- [x] Crear dashboard Streamlit para navegar:
  - Hallazgos por capítulo con citas.
  - Backlog priorizado.
  - Estado de decisiones del autor.
  - Métricas globales.
  - Entregables de M7 + iteraciones del pipeline editorial.
  → `alexandria-writer/dashboard.py`
- [x] Permitir al autor marcar hallazgos como: aceptado / rechazado / modificado. → dashboard.py
- [x] Exportar decisiones del autor como JSON descargable. → dashboard.py
- [x] Exportar plan de edición actualizado según decisiones (Markdown + Word). → `core/exportar_plan.py`

---

## 9. Cambios en la Estructura de Carpetas (propuesta)

```
alexandria-writer/
├── core/                          # Motor del pipeline
│   ├── llm_router.py
│   ├── pipeline_maestro_v3.py
│   ├── m0_ingesta.py
│   ├── m1_diagnostico.py
│   ├── m2_estrategia.py
│   ├── m3_evidencia.py
│   ├── m4_editor_jefe.py
│   ├── m5_control_riesgo.py
│   ├── m6_benchmarking.py
│   └── m7_output_profesional.py
├── agents/                        # Instrucciones y prompts por agente
│   ├── diagnostico/               # agente_estructura, agente_voz, etc.
│   ├── mercado/
│   ├── editor_jefe/
│   └── guardianes/
├── templates/                     # Jinja2 para output profesional
│   ├── memo_adquisicion.md.j2
│   ├── diagnostico_desarrollo.md.j2
│   ├── plan_intervencion.md.j2
│   ├── estrategia_publicacion.md.j2
│   └── brief_ejecutivo.md.j2
├── docs/
│   └── Autores/                   # Inputs y outputs por autor
│       └── <Nombre_Autor>/
│           ├── Libros/            # Manuscritos fuente (PDF)
│           │   └── <libro>.pdf
│           ├── Proyectos/
│           │   └── <id_libro>/    # Todo el ciclo de análisis de una obra
│           │       ├── m0_ingesta/
│           │       │   ├── bible_del_libro.json
│           │       │   ├── mapa_chunks.json
│           │       │   └── contexto_autor.yaml
│           │       ├── m1_diagnostico/
│           │       │   ├── hallazgos.json
│           │       │   ├── metricas_editoriales.json
│           │       │   └── *.md
│           │       ├── m2_estrategia/
│           │       │   └── *.md
│           │       ├── m3_evidencia/
│           │       │   ├── evidencia_store.jsonl
│           │       │   ├── trazabilidad_graph.md
│           │       │   └── conflict_log.json
│           │       ├── m4_editor_jefe/
│           │       │   ├── dictamen_editor_jefe.md
│           │       │   ├── backlog_priorizado.json
│           │       │   └── resumen_ejecutivo_editorial.md
│           │       ├── m5_control_riesgo/
│           │       │   ├── riesgos_detectados.json
│           │       │   └── recomendaciones_bloqueadas.json
│           │       ├── m6_benchmarking/
│           │       │   ├── benchmark.json
│           │       │   └── posicionamiento_relativo.md
│           │       └── m7_output_profesional/
│           │           ├── memo_adquisicion.md
│           │           ├── diagnostico_desarrollo.md
│           │           ├── plan_intervencion.md
│           │           ├── estrategia_publicacion.md
│           │           └── brief_final_ejecutivo.md
│           └── Historial/         # Obras previas del autor para benchmarking
│               └── <libro_anterior>/
├── data/
│   └── comparables/               # Base de benchmarking por género (global)
└── PLAN_ARQUITECTURA_V3.md        # Este documento
```

**Convención de rutas:**
- Manuscrito fuente: `docs/Autores/<autor>/Libros/<libro>.pdf`
- Ciclo de análisis: `docs/Autores/<autor>/Proyectos/<id_libro>/`
- Historial del autor: `docs/Autores/<autor>/Historial/` (usado por Módulo 6)

**Ejemplo activo (autor piloto):**
- `docs/Autores/<autor>/Libros/<libro>.pdf`
- `docs/Autores/<autor>/Proyectos/<id_libro>/...`

---

## 10. Veredicto Esperado post-v3

| Dimensión | Estado v2 | Estado v3 objetivo |
|-----------|-----------|-------------------|
| Posicionamiento | Pipeline de 4 equipos | Sistema editorial inteligente |
| Trazabilidad | Logs de ejecución | Evidencia auditable por hallazgo |
| Métricas | Ninguna | 7 métricas editoriales + 4 del sistema |
| Arbitraje | Consolidador pasivo | Editor Jefe con veto y prioridad |
| Riesgo | Principio declarativo | Guardianes operativos con bloqueo |
| Salida | Documentos de IA | Memos editoriales profesionales |
| Benchmarking | Ninguno | Percentil vs. comparables y propio historial |
| Interacción autor | Pasiva (lee docs) | Activa (acepta/rechaza/modifica) |

---

*Plan de Arquitectura v3 — Alexandria Writer | 2026-05-12*
