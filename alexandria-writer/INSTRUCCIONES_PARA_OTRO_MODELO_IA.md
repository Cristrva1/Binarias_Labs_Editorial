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
M0  Cargar voz_autor.yaml + segmentar el PDF por capítulo (TOC-based)
M1  Director Editorial → lectura_inicial.md (nota interna)
M2  Oficios especializados leen cada capítulo y emiten sugerencias (YAML)
      - Estructuralista de Ensayo
      - Editor de Línea (es-MX)
M3  Lector de Voz filtra cada sugerencia (5 filtros deterministas)
M4  Director Editorial arbitra y redacta el dictamen
M5  Salidas en docs/Autores/<Autor>/Proyectos/<Libro>/iteracion_NN/
```

Punto de entrada: `core/editorial/pipeline_editorial.py`

---

## 3. Comandos

### Corrida completa
```powershell
python core/editorial/pipeline_editorial.py --autor Arturo_Ledezma --libro TSBN
```

### Solo capítulos específicos (para pruebas)
```powershell
python core/editorial/pipeline_editorial.py --autor Arturo_Ledezma --libro TSBN --bloques 7 15 16
```

### Solo un oficio
```powershell
python core/editorial/pipeline_editorial.py --autor Arturo_Ledezma --libro TSBN --oficios estructuralista
```

---

## 4. Salidas por Iteración

Todas en `docs/Autores/<Autor>/Proyectos/<Libro>/iteracion_NN/`:

| Archivo | Destino | Contenido |
|---|---|---|
| `dictamen_editorial.md` | **Al autor** | Carta editorial firmada por el Director |
| `cambios_propuestos.json` | Interno | Todas las sugerencias aprobadas, estructuradas |
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
        └── voz_autor.yaml       ← la huella vocal del autor (ver voz_autor.yaml de TSBN como ejemplo)
```

El `voz_autor.yaml` es obligatorio. Sin él, el pipeline no arranca.

---

## 6. Archivos del Pipeline v2 (Archivados)

Los scripts del pipeline v2 siguen en `core/` y en `projects/tsbn/_archivado_v2/` como referencia. No se ejecutan en el flujo principal. Si los necesitás por algún motivo:

```powershell
# Pipeline v2 de 4 equipos (OBSOLETO — solo como referencia)
python core/pipeline_maestro_v3.py
```

---

*Casa Alexandria — v1 — 2026-05-13*
