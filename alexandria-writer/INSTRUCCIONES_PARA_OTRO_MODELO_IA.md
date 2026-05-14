# Instrucciones para Ejecución por Otro Modelo de IA
# Casa Alexandria — Pipeline Editorial v1

> **PROPÓSITO:** Este documento permite que cualquier modelo de IA ejecute el pipeline editorial sin intervención humana adicional. El pipeline v2 de 4 equipos ha sido reemplazado por este sistema. Los scripts del v2 están en `core/` pero no se invocan en el flujo principal.

---

## 1. Entorno Requerido

- **Sistema:** Windows (PowerShell) o Linux/macOS (bash)
- **Python:** 3.10+
- **Librerías:** `pip install pdfplumber pyyaml`
- **API keys:** el `LLMRouter` en `core/llm_router.py` usa variables de entorno. Configurá al menos una de: `CEREBRAS_API_KEY`, `SAMBANOVA_API_KEY`, `MISTRAL_API_KEY`, `GROQ_API_KEY`.

---

## 2. Estructura del Pipeline

```
M0   Cargar voz_autor.yaml + segmentar el PDF por capítulo
M1   Director Editorial → lectura_inicial.md (nota interna)
M2   Oficios especializados emiten sugerencias (YAML):
       - Estructuralista de Ensayo       (bloque por bloque)
       - Editor de Línea (es-MX)         (bloque por bloque)
       - Custodio Doctrinal              (bloque por bloque; solo si habla_de_Dios: true)
M2b  Lector Ideal Simulado              (manuscrito completo → mapa_emocional.md)
M2c  Auditor de Continuidad             (manuscrito completo → continuidad_observaciones.json)
M3   Lector de Voz filtra cada sugerencia (5 filtros deterministas)
M4   Director Editorial arbitra y redacta el dictamen
M5   Salidas en docs/Autores/<Autor>/Proyectos/<Libro>/iteracion_NN/
```

Punto de entrada: `core/editorial/pipeline_editorial.py`

---

## 3. Comandos

### Corrida completa
```powershell
python core/editorial/pipeline_editorial.py --autor <AUTOR> --libro <ID_LIBRO>
```

### Solo capítulos específicos (para pruebas)
```powershell
python core/editorial/pipeline_editorial.py --autor <AUTOR> --libro <ID_LIBRO> --bloques 7 15 16
```

### Solo un oficio
```powershell
python core/editorial/pipeline_editorial.py --autor <AUTOR> --libro <ID_LIBRO> --oficios estructuralista
```

### Oficios disponibles
```
estructuralista    — arco, ritmo, estructura del género
editor_de_linea    — gramática, puntuación, claridad oración a oración
custodio           — coherencia espiritual/doctrinal (condicional)
lector_ideal       — mapa emocional del lector imaginado (manuscrito completo)
auditor            — mantras, promesas, callbacks, contradicciones (manuscrito completo)
```

Por defecto se activan los 5. Usá `--oficios` para limitar:

---

## 4. Salidas por Iteración

Todas en `docs/Autores/<Autor>/Proyectos/<Libro>/iteracion_NN/`:

| Archivo | Destino | Contenido |
|---|---|---|
| `dictamen_editorial.md` | **Al autor** | Carta editorial firmada por el Director |
| `cambios_propuestos.json` | Interno | Todas las sugerencias aprobadas, estructuradas |
| `mapa_emocional.md` | **Al autor** | Experiencia lectora capítulo a capítulo (Lector Ideal) |
| `continuidad_observaciones.json` | Interno | Mantras, promesas y callbacks verificados (Auditor) |
| `bloqueos_voz.json` | Interno | Lo que el Lector de Voz bloqueó, con razón |
| `decisiones_autor.json` | Al autor | Esqueleto para que marque aceptado/rechazado/modificado |
| `lectura_inicial.md` | Interno | Nota del Director antes de que los oficios trabajen |
| `log_iteracion.json` | Interno | Métricas: duración, aprobaciones, proveedor LLM |

---

## 5. Registrar un Nuevo Autor

```
docs/Autores/<NombreAutor>/
├── Libros/
│   └── libro.pdf                ← el manuscrito
└── Proyectos/
    └── <ID_LIBRO>/
        └── voz_autor.yaml       ← la huella vocal del autor (ver el voz_autor.yaml del proyecto piloto como ejemplo)
```

El `voz_autor.yaml` es obligatorio. Sin él, el pipeline no arranca.

---

## 5b. Dashboard Visual

```powershell
# Requiere: pip install streamlit
streamlit run alexandria-writer/dashboard.py
```

Secciones disponibles:
- **Métricas** — gravedad, estabilidad de voz, densidad por capítulo
- **Hallazgos** — filtrado por tipo/severidad, con citas y decisión del autor
- **Backlog** — ítems priorizados por score editorial
- **Riesgos** — estado de los 4 guardianes
- **Benchmark** — percentil y posicionamiento
- **Decisiones** — aceptar/rechazar/modificar + exportar JSON + generar plan Word
- **Entregables** — documentos de M7 + iteraciones del pipeline editorial

## 5c. Exportar Plan de Edición

Genera `plan_edicion_YYYYMMDD.md` y `.docx` con los cambios que el autor aceptó:

```powershell
python core/exportar_plan.py --autor <AUTOR> --libro <ID_LIBRO>
python core/exportar_plan.py --autor <AUTOR> --libro <ID_LIBRO> --formato markdown
```

Requiere `python-docx` para el formato Word: `pip install python-docx`

---

## 6. Pipeline v3 — Sistema de Análisis Profundo (M0→M7)

Pipeline alternativo para análisis editorial completo. Produce entregables profesionales.
Punto de entrada: `core/pipeline_maestro_v3.py`

### Flujo de módulos

```
M0  Ingesta y contexto       → bible_del_libro.json, mapa_chunks.json
M1  Diagnóstico editorial     → hallazgos.json, metricas_editoriales.json, reportes .md
M2  Estrategia de mercado    → comparables, posicionamiento, go-to-market, forecast
M3  Evidencia + trazabilidad → evidencia_store.jsonl, trazabilidad_graph.md
M4  Editor Jefe              → dictamen_editor_jefe.md, backlog_priorizado.json
M5  Control de riesgo        → riesgos_detectados.json, informe_control_riesgo.md
M6  Benchmarking             → benchmark.json, posicionamiento_relativo.md
M7  Output profesional       → brief_final_ejecutivo.md, diagnostico_desarrollo.md,
                                plan_intervencion.md, estrategia_publicacion.md,
                                memo_adquisicion.md
```

### Comandos v3

```powershell
# Pipeline completo M0→M7
python core/pipeline_maestro_v3.py --autor <AUTOR> --libro <ID_LIBRO>

# Solo un módulo específico
python core/pipeline_maestro_v3.py --autor <AUTOR> --libro <ID_LIBRO> --solo m1

# Saltar módulos (skip múltiples)
python core/pipeline_maestro_v3.py --autor <AUTOR> --libro <ID_LIBRO> --skip m2 m6

# Módulos individuales (cada uno tiene CLI propio)
python core/m1_diagnostico.py --autor <AUTOR> --libro <ID_LIBRO>
python core/m7_output_profesional.py --autor <AUTOR> --libro <ID_LIBRO>
```

### Salidas del pipeline v3

Todas en `docs/Autores/<Autor>/Proyectos/<Libro>/`:

| Carpeta | Contenido |
|---|---|
| `m0_ingesta/` | bible_del_libro.json, mapa_chunks.json, contexto_autor.yaml |
| `m1_diagnostico/` | hallazgos.json, metricas_editoriales.json, 5 reportes .md |
| `m2_estrategia/` | analisis_comparables.md, posicionamiento_y_promesa.md, plan_go_to_market.md, forecast_ventas.md |
| `m3_evidencia/` | evidencia_store.jsonl, trazabilidad_graph.md, conflict_log.json |
| `m4_editor_jefe/` | dictamen_editor_jefe.md, backlog_priorizado.json, resumen_ejecutivo_editorial.md |
| `m5_control_riesgo/` | riesgos_detectados.json, informe_control_riesgo.md |
| `m6_benchmarking/` | benchmark.json, posicionamiento_relativo.md |
| `m7_output_profesional/` | **5 entregables para el autor** (brief, diagnóstico, plan, estrategia, memo) |

---

## 7. Archivos del Pipeline v2 (Archivados)

Los scripts del pipeline v2 siguen en `core/` y en `projects/tsbn/_archivado_v2/` como referencia. No se ejecutan en el flujo principal. Si los necesitás por algún motivo:

```powershell
# Pipeline v2 de 4 equipos (OBSOLETO — solo como referencia)
python core/pipeline_maestro.py --modo completo
```

---

*Casa Alexandria — v2 — 2026-05-14*
