"""
Alexandria Writer v3 — Configuración de Rutas por Autor
========================================================
Maneja la convención de carpetas:
  docs/Autores/<autor>/Libros/<libro>.pdf
  docs/Autores/<autor>/Proyectos/<id_libro>/m{0..7}_*/
  docs/Autores/<autor>/Historial/
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Raíz del proyecto Alexandria Writer
PROJECT_ROOT = Path(__file__).parent.parent

# Raíz de documentos de autores
AUTORES_ROOT = PROJECT_ROOT / "docs" / "Autores"

# Base de datos global de comparables
COMPARABLES_ROOT = PROJECT_ROOT / "data" / "comparables"


@dataclass
class ProyectoPaths:
    """Rutas completas de un ciclo de análisis para un libro específico."""
    autor: str
    libro_id: str

    @property
    def autor_dir(self) -> Path:
        return AUTORES_ROOT / self.autor

    @property
    def libros_dir(self) -> Path:
        return self.autor_dir / "Libros"

    @property
    def proyecto_dir(self) -> Path:
        return self.autor_dir / "Proyectos" / self.libro_id

    @property
    def historial_dir(self) -> Path:
        return self.autor_dir / "Historial"

    # --- Módulos ---

    @property
    def m0_ingesta(self) -> Path:
        return self.proyecto_dir / "m0_ingesta"

    @property
    def m1_diagnostico(self) -> Path:
        return self.proyecto_dir / "m1_diagnostico"

    @property
    def m2_estrategia(self) -> Path:
        return self.proyecto_dir / "m2_estrategia"

    @property
    def m3_evidencia(self) -> Path:
        return self.proyecto_dir / "m3_evidencia"

    @property
    def m4_editor_jefe(self) -> Path:
        return self.proyecto_dir / "m4_editor_jefe"

    @property
    def m5_riesgos(self) -> Path:
        return self.proyecto_dir / "m5_riesgos"

    @property
    def m6_benchmarking(self) -> Path:
        return self.proyecto_dir / "m6_benchmarking"

    @property
    def m7_entregas(self) -> Path:
        return self.proyecto_dir / "m7_entregas"

    # --- Archivos clave ---

    def pdf_path(self, nombre_pdf: Optional[str] = None) -> Path:
        """Devuelve la ruta del PDF. Si no se pasa nombre, busca el único PDF."""
        if nombre_pdf:
            return self.libros_dir / nombre_pdf
        pdfs = list(self.libros_dir.glob("*.pdf"))
        if len(pdfs) == 1:
            return pdfs[0]
        if len(pdfs) == 0:
            raise FileNotFoundError(f"No se encontró PDF en {self.libros_dir}")
        raise ValueError(f"Hay múltiples PDFs en {self.libros_dir}; especifica nombre_pdf")

    def respuestas_autor(self) -> Path:
        return self.proyecto_dir / f"RESPUESTAS_AUTOR_{self.libro_id.upper()}.md"

    def bible_path(self) -> Path:
        return self.m0_ingesta / "bible_del_libro.json"

    def mapa_chunks_path(self) -> Path:
        return self.m0_ingesta / "mapa_chunks.json"

    def contexto_autor_path(self) -> Path:
        return self.m0_ingesta / "contexto_autor.yaml"

    def hallazgos_path(self) -> Path:
        return self.m1_diagnostico / "hallazgos.json"

    def metricas_editoriales_path(self) -> Path:
        return self.m1_diagnostico / "metricas_editoriales.json"

    def evidencia_store_path(self) -> Path:
        return self.m3_evidencia / "evidencia_store.jsonl"

    def conflict_log_path(self) -> Path:
        return self.m3_evidencia / "conflict_log.json"

    def dictamen_editor_jefe_path(self) -> Path:
        return self.m4_editor_jefe / "dictamen_editor_jefe.json"

    def backlog_path(self) -> Path:
        return self.m4_editor_jefe / "backlog_priorizado.json"

    def riesgos_path(self) -> Path:
        return self.m5_riesgos / "riesgos_detectados.json"

    def bloqueos_path(self) -> Path:
        return self.m5_riesgos / "recomendaciones_bloqueadas.json"

    def benchmark_path(self) -> Path:
        return self.m6_benchmarking / "benchmark.json"

    def ensure_dirs(self):
        """Crea todas las carpetas del proyecto si no existen."""
        for attr in dir(self):
            if attr.startswith("m") and "_" in attr:
                path = getattr(self, attr)
                if isinstance(path, Path):
                    path.mkdir(parents=True, exist_ok=True)
        self.historial_dir.mkdir(parents=True, exist_ok=True)


def listar_autores() -> list[str]:
    """Devuelve lista de nombres de autores registrados."""
    if not AUTORES_ROOT.exists():
        return []
    return [d.name for d in AUTORES_ROOT.iterdir() if d.is_dir()]


def listar_libros_de_autor(autor: str) -> list[str]:
    """Devuelve lista de IDs de proyectos/libros de un autor."""
    proyectos_dir = AUTORES_ROOT / autor / "Proyectos"
    if not proyectos_dir.exists():
        return []
    return [d.name for d in proyectos_dir.iterdir() if d.is_dir()]
