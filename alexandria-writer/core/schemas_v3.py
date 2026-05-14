"""
Alexandria Writer v3 — Esquemas de Datos Estructurados
=======================================================
Clases Pydantic (o dataclasses) para garantizar que todos los módulos
hablen el mismo idioma y que la evidencia sea validable.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional, Literal, List
from datetime import datetime
import json


# ─── Taxonomía Editorial v3 ───
TIPO_HALLAZGO = Literal["estructura", "voz", "continuidad", "friccion", "fortaleza"]
CATEGORIA_TAXONOMICA = Literal[
    "arco", "ritmo", "tension", "pico", "valle", "cliffhanger", "resolucion",
    "distancia", "tono", "registro", "estabilidad", "autenticidad",
    "hook", "promesa", "expectativa", "payoff",
    "confusion", "fatiga", "repeticion", "bache", "abandono",
    "continuidad", "callback", "contradiccion", "coherencia tematica",
    "fluidez", "densidad", "claridad", "jerga", "accesibilidad",
    "sobreedicion", "alucinacion", "sesgo", "incompatibilidad",
    "fortaleza", "diferenciador", "ventaja", "potencial"
]
ESTADO_HALLAZGO = Literal[
    "pendiente",
    "aprobado_por_editor_jefe",
    "rechazado_por_editor_jefe",
    "bloqueado_por_riesgo",
    "escalado_a_autor",
    "aceptado_por_autor",
    "rechazado_por_autor",
    "modificado_por_autor"
]


@dataclass
class Hallazgo:
    """
    Unidad mínima de evidencia editorial. Todo hallazgo que viaja
    entre módulos debe cumplir con este esquema.
    """
    id: str                          # Ej: "H-001-EST"
    modulo: str                      # "m1_diagnostico", "m2_estrategia", ...
    agente: str                      # "agente_estructura", "agente_voz", ...
    tipo: TIPO_HALLAZGO
    categoria_taxonomica: CATEGORIA_TAXONOMICA
    chunk_ref: str                   # Ej: "C12-P45"
    capitulo: Optional[int] = None
    pagina_aprox: Optional[int] = None
    cita_textual: str = ""           # Fragmento literal del manuscrito
    descripcion: str = ""
    severidad: int = 1               # 1 (leve) a 5 (crítico)
    confianza: float = 0.0           # 0.0 a 1.0
    intervencion_sugerida: str = ""
    impacto_esperado: str = ""
    conflicto_con: Optional[str] = None   # ID de hallazgo contradictorio
    razon_sobrevivencia: str = ""    # Por qué pasó al consolidado
    estado: ESTADO_HALLAZGO = "pendiente"
    bloqueos_riesgo: List[str] = field(default_factory=list)
    decision_autor: str = "pendiente"      # pendiente / aceptado / rechazado / modificado
    notas_autor: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    @classmethod
    def from_dict(cls, d: dict) -> "Hallazgo":
        return cls(**d)


@dataclass
class MetricasEditoriales:
    """Métricas calculadas sobre el manuscrito (ver Plan v3 sección 6)."""
    libro_id: str
    total_palabras: int = 0
    total_capitulos: int = 0
    total_hallazgos: int = 0
    hallazgos_severidad_alta: int = 0  # severidad >= 3
    densidad_problemas: float = 0.0   # por 1000 palabras
    gravedad_editorial: float = 0.0    # promedio ponderado severidad * confianza
    estabilidad_voz: float = 0.0       # 0.0 a 1.0
    continuidad_tematica: float = 0.0  # callbacks / temas_introducidos
    claridad_promesa: float = 0.0      # 1 a 5
    coherencia_autor_posicionamiento: float = 0.0  # similitud semántica
    probabilidad_ejecucion: float = 0.0  # 1 - (bloqueos / total_generadas)
    percentil_ritmo: Optional[float] = None
    percentil_claridad: Optional[float] = None
    percentil_densidad_problemas: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiesgoDetectado:
    """Registro de un riesgo identificado por los guardianes."""
    id: str
    guardian: str                    # "guardian_alucinaciones", etc.
    tipo: str                        # "alucinacion", "sobreedicion", "sesgo", "voz"
    hallazgo_id: Optional[str] = None
    descripcion: str = ""
    severidad: int = 1               # 1 (baja) a 5 (crítica)
    recomendacion: str = ""          # Qué hacer para mitigar
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Conflicto:
    """Conflicto entre agentes resuelto (o no) por el Editor Jefe."""
    id: str
    hallazgo_a: str
    hallazgo_b: str
    agente_a: str
    agente_b: str
    descripcion: str
    resolucion: Literal["a_gana", "b_gana", "merge", "escalado_a_autor", "pendiente"]
    razon: str = ""                  # Por qué se resolvió así
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DictamenEditorJefe:
    """Salida del Módulo 4: Editor Jefe."""
    libro_id: str
    top10_problemas_criticos: List[str] = field(default_factory=list)
    top10_cambios_alto_retorno: List[str] = field(default_factory=list)
    riesgo_principal_intervencion: dict = field(default_factory=dict)
    coherencia_global: Literal["aprobada", "con_reservas", "rechazada"] = "aprobada"
    alertas_mercado: List[str] = field(default_factory=list)
    notas_direccion: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Helpers de persistencia ───

def guardar_hallazgos(path: str, hallazgos: List[Hallazgo]):
    with open(path, "w", encoding="utf-8") as f:
        json.dump([h.to_dict() for h in hallazgos], f, indent=2, ensure_ascii=False)


def cargar_hallazgos(path: str) -> List[Hallazgo]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Hallazgo.from_dict(d) for d in data]


def append_evidencia_store(path: str, hallazgo: Hallazgo):
    """Escribe un hallazgo en modo append al evidence store (JSON Lines)."""
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(hallazgo.to_dict(), ensure_ascii=False) + "\n")
