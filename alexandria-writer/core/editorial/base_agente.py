"""Base para los oficios editoriales.

Cada oficio (Editor de Línea, Estructuralista, etc.) hereda de
`BaseAgenteEditorial`. La base se encarga de:
  - cargar el `.md` del oficio (su persona y reglas);
  - construir el prompt completo con la voz del autor inyectada;
  - llamar al LLM vía LLMRouter;
  - parsear la salida YAML de sugerencias.

Los oficios concretos solo definen cómo construyen su prompt operativo
para un bloque del manuscrito y, opcionalmente, cómo procesan la salida.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


from manuscrito import BloqueDelManuscrito
from voz_autor import VozAutor


CORE_DIR = Path(__file__).parent.parent
AGENTS_EDITORIAL_DIR = CORE_DIR.parent / "agents" / "editorial"


@dataclass
class SugerenciaEditorial:
    """Una sugerencia formal de un oficio editorial."""

    id: str
    oficio: str
    capitulo: str
    ubicacion: str
    cita_completa: str
    diagnostico: str
    propuesta: str
    que_se_gana: str = ""
    que_se_pierde: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "oficio": self.oficio,
            "capitulo": self.capitulo,
            "ubicacion": self.ubicacion,
            "cita_completa": self.cita_completa,
            "diagnostico": self.diagnostico,
            "propuesta": self.propuesta,
            "que_se_gana": self.que_se_gana,
            "que_se_pierde": self.que_se_pierde,
            "metadata": self.metadata,
        }


class BaseAgenteEditorial:
    """Padre de todos los oficios."""

    nombre_oficio: str = "Oficio sin nombre"
    nombre_archivo_md: str = ""  # ej. "00_lector_de_voz.md"
    prefijo_id: str = "ED"        # ED para edición; otros usan CD, AC, BV
    temperatura: float = 0.2
    max_tokens: int = 4096

    def __init__(self, voz: VozAutor, router):
        self.voz = voz
        self.router = router
        self.persona_md = self._cargar_persona_md()
        self._contador_id = 0
        self._bloque_actual: Optional[int] = None

    # ─── Carga de persona ─────────────────────────────────────────────

    def _cargar_persona_md(self) -> str:
        if not self.nombre_archivo_md:
            return ""
        ruta = AGENTS_EDITORIAL_DIR / self.nombre_archivo_md
        if not ruta.exists():
            return ""
        contenido = ruta.read_text(encoding="utf-8")
        # Quitamos el frontmatter YAML para no duplicar metadata en el prompt.
        if contenido.startswith("---"):
            partes = contenido.split("---", 2)
            if len(partes) >= 3:
                contenido = partes[2].strip()
        return contenido

    # ─── Identificadores ──────────────────────────────────────────────

    def _siguiente_id(self) -> str:
        """ID único por construcción: prefijo + bloque + secuencia.
        Ejemplo: ES-B14-001. Garantiza unicidad sin depender del modelo.
        """
        self._contador_id += 1
        bloque = self._bloque_actual if self._bloque_actual is not None else 0
        return f"{self.prefijo_id}-B{bloque:02d}-{self._contador_id:03d}"

    # ─── Construcción del system prompt ───────────────────────────────

    def system_prompt(self) -> str:
        """System prompt = manifiesto del oficio + voz del autor inyectada
        + reglas de salida.
        """
        encabezado = (
            f"Sos un agente editorial de Casa Alexandria. Trabajás en español. "
            f"Tu oficio es: {self.nombre_oficio}.\n\n"
            f"Antes de proponer una sola sugerencia, leé y respetá los dos bloques "
            f"que vienen abajo. La voz del autor es ley dura. "
            f"Si una sugerencia tuya entrara en conflicto con esa voz, no la propongas — "
            f"o márcala explícitamente como duda para escalar.\n"
        )

        bloque_voz = "\n=== VOZ DEL AUTOR (LEY) ===\n" + self.voz.como_bloque_contexto()

        bloque_persona = ""
        if self.persona_md:
            bloque_persona = (
                "\n\n=== TU OFICIO Y TU MÉTODO ===\n"
                + self.persona_md
            )

        instruccion_salida = (
            "\n\n=== FORMATO DE SALIDA ===\n"
            "Devolvé tus sugerencias como una lista YAML dentro de un bloque ```yaml ... ```. "
            "Cada sugerencia tiene EXACTAMENTE estos campos:\n"
            "  - capitulo: string (nombre del capítulo, no número)\n"
            "  - ubicacion: string (las primeras 15-20 palabras del párrafo, entre comillas)\n"
            "  - cita_completa: string (el párrafo completo tal cual aparece, entre comillas)\n"
            "  - diagnostico: string (qué observás, en una a tres frases, sin censura)\n"
            "  - propuesta: string (la sugerencia concreta — pulido o señal; no reescribas voz)\n"
            "  - que_se_gana: string\n"
            "  - que_se_pierde: string (si no se pierde nada, escribí exactamente: 'nada' — nunca escribas 'se pierde nada')\n\n"
            "Si no encontrás nada digno de sugerencia en este bloque, devolvé exactamente: 'Sin observaciones'. "
            "No inventes hallazgos para llenar espacio. Tres sugerencias buenas valen más que doce ruidosas."
        )

        return encabezado + bloque_voz + bloque_persona + instruccion_salida

    # ─── Construcción del user prompt ─────────────────────────────────

    def user_prompt_para_bloque(self, bloque: BloqueDelManuscrito) -> str:
        """Cada oficio puede sobrescribir esto si necesita un encuadre
        distinto. Por defecto pasa el bloque entero del manuscrito y
        recuerda al modelo qué oficio es.
        """
        encuadre = self._encuadre_para_bloque(bloque)
        cuerpo = (
            f"Bloque del manuscrito a leer.\n"
            f"Capítulo: {bloque.capitulo or 'sin título detectado'}\n"
            f"Páginas: {bloque.paginas_str}\n"
            f"Palabras: {bloque.palabras}\n"
        )
        if bloque.es_bloque_de_tercero:
            cuerpo += (
                f"\n⚠ Este bloque NO lo escribió el autor del libro. "
                f"Lo firma: {bloque.autor_real}. Tratalo como tal: tu oficio "
                f"normalmente NO interviene aquí. Si tenés algo que decir, "
                f"marcalo como 'afecta a tercero — requiere consulta'.\n"
            )
        if bloque.tratamiento_especial:
            cuerpo += f"Tratamiento especial declarado: {bloque.tratamiento_especial}\n"

        cuerpo += (
            f"\n--- TEXTO DEL BLOQUE (entre líneas) ---\n"
            f"{bloque.texto[:14000]}\n"
            f"--- FIN DEL BLOQUE ---\n\n"
            f"{encuadre}\n"
        )
        return cuerpo

    def _encuadre_para_bloque(self, bloque: BloqueDelManuscrito) -> str:
        """Pregunta concreta para el oficio. Las subclases la definen."""
        return "Aplicá tu oficio al bloque y devolvé tus sugerencias."

    # ─── Llamada al LLM ───────────────────────────────────────────────

    def analizar_bloque(self, bloque: BloqueDelManuscrito) -> list[SugerenciaEditorial]:
        # Reseteamos el contador para que cada bloque empiece en 001 dentro
        # de su prefijo BNN. Garantiza unicidad combinada con el bloque.
        self._bloque_actual = bloque.indice
        self._contador_id = 0
        system = self.system_prompt()
        user = self.user_prompt_para_bloque(bloque)
        resultado = self.router.chat(
            user_prompt=user,
            system=system,
            temperature=self.temperatura,
            max_tokens=self.max_tokens,
        )
        if not resultado.get("success"):
            print(
                f"      [{self.nombre_oficio}] error: {resultado.get('error', 'desconocido')}"
            )
            return []
        contenido = resultado.get("content", "")
        return self._parsear_salida(contenido, bloque)

    # ─── Parser ───────────────────────────────────────────────────────

    def _parsear_salida(
        self, contenido: str, bloque: BloqueDelManuscrito
    ) -> list[SugerenciaEditorial]:
        if "sin observaciones" in contenido.lower()[:200]:
            return []

        bloques_yaml = re.findall(r"```yaml\s*\n(.*?)\n```", contenido, re.DOTALL)
        if not bloques_yaml:
            # fallback: intentar parsear todo como yaml
            bloques_yaml = [contenido]

        sugerencias: list[SugerenciaEditorial] = []
        for bloque_yaml in bloques_yaml:
            try:
                datos = yaml.safe_load(bloque_yaml)
            except Exception:
                continue
            if datos is None:
                continue
            if isinstance(datos, dict):
                datos = [datos]
            if not isinstance(datos, list):
                continue
            for entrada in datos:
                if not isinstance(entrada, dict):
                    continue
                sug = SugerenciaEditorial(
                    id=self._siguiente_id(),
                    oficio=self.nombre_oficio,
                    capitulo=str(entrada.get("capitulo") or bloque.capitulo or ""),
                    ubicacion=str(entrada.get("ubicacion") or "").strip(),
                    cita_completa=str(entrada.get("cita_completa") or "").strip(),
                    diagnostico=str(entrada.get("diagnostico") or "").strip(),
                    propuesta=str(entrada.get("propuesta") or "").strip(),
                    que_se_gana=str(entrada.get("que_se_gana") or "").strip(),
                    que_se_pierde=str(entrada.get("que_se_pierde") or "").strip(),
                    metadata={
                        "bloque_indice": bloque.indice,
                        "paginas": bloque.paginas_str,
                    },
                )
                if not (sug.cita_completa or sug.ubicacion):
                    continue
                # Descartar entradas vacías o de "no hay nada que cambiar".
                if self._es_propuesta_vacia(sug.propuesta):
                    continue
                sugerencias.append(sug)
        return sugerencias

    @staticmethod
    def _es_propuesta_vacia(propuesta: str) -> bool:
        if not propuesta:
            return True
        p = propuesta.strip().lower()
        if len(p) < 6:
            return True
        marcadores_vacios = (
            "no se necesitan cambios",
            "no hay cambios",
            "ningún cambio",
            "ningun cambio",
            "no se requieren cambios",
            "no se requiere",
            "no se sugiere",
            "no se propone",
            "no aplica",
            "n/a",
            "sin cambios",
            "sin sugerencia",
            "ninguna sugerencia",
            "no hay nada que",
            "todo está bien",
            "todo esta bien",
        )
        return any(m in p for m in marcadores_vacios)
