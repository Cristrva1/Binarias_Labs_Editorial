"""Lector de Voz — implementación.

Persona: `agents/editorial/00_lector_de_voz.md`.

A diferencia de los demás oficios, este es mayormente determinista. Aplica
los cinco filtros descritos en su `.md` sobre cada `SugerenciaEditorial`
producida por los demás oficios. Devuelve una decisión por sugerencia y
deja registro en `bloqueos_voz.json`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from base_agente import SugerenciaEditorial
from voz_autor import VozAutor


Decision = Literal["aprobada", "modificada", "rechazada", "escalada_al_autor"]


@dataclass
class ResultadoFiltro:
    """Resultado del paso de una sugerencia por el Lector de Voz."""

    sugerencia: SugerenciaEditorial
    decision: Decision
    filtro_que_aplico: int = 0
    razon: str = ""
    propuesta_alternativa: str = ""
    sugerencia_modificada: SugerenciaEditorial | None = None

    def to_dict(self) -> dict:
        out = {
            "id_sugerencia": self.sugerencia.id,
            "oficio_origen": self.sugerencia.oficio,
            "decision": self.decision,
            "filtro_que_aplico": self.filtro_que_aplico,
            "razon": self.razon,
            "cita": self.sugerencia.cita_completa,
            "propuesta_original": self.sugerencia.propuesta,
        }
        if self.propuesta_alternativa:
            out["propuesta_alternativa"] = self.propuesta_alternativa
        return out


class LectorDeVoz:
    """Filtro de voz determinista. Cinco filtros, en orden."""

    nombre_oficio = "Lector de Voz"

    def __init__(self, voz: VozAutor):
        self.voz = voz
        self.contador_bv = 0

    # ─── API principal ────────────────────────────────────────────────

    def filtrar(self, sugerencias: list[SugerenciaEditorial]) -> list[ResultadoFiltro]:
        """Pasa cada sugerencia por los cinco filtros y devuelve la decisión."""
        resultados: list[ResultadoFiltro] = []
        for sug in sugerencias:
            resultado = self._aplicar_filtros(sug)
            resultados.append(resultado)
            self.contador_bv += 1
        return resultados

    def _aplicar_filtros(self, sug: SugerenciaEditorial) -> ResultadoFiltro:
        # Filtro 1 — pasaje sagrado.
        sagrado = self.voz.es_pasaje_sagrado(sug.cita_completa)
        if sagrado is not None:
            return ResultadoFiltro(
                sugerencia=sug,
                decision="escalada_al_autor",
                filtro_que_aplico=1,
                razon=(
                    f"La cita coincide con un pasaje sagrado declarado en voz_autor.yaml "
                    f"(id «{sagrado.get('id', '?')}»). El autor pidió que ningún oficio "
                    "intervenga aquí sin su aprobación escrita. Escalada."
                ),
            )

        # Filtro 2 — vocabulario prohibido en la propuesta.
        prohibidas = self.voz.palabras_prohibidas_en(sug.propuesta)
        if prohibidas:
            # Si la propuesta entera depende de la palabra prohibida (clichés
            # de coach, de autoayuda), la rechazamos. Si solo aparece una vez
            # y se puede reescribir, marcamos como rechazo con alternativa.
            return ResultadoFiltro(
                sugerencia=sug,
                decision="rechazada",
                filtro_que_aplico=2,
                razon=(
                    "La propuesta introduce vocabulario que el autor pidió evitar "
                    f"({', '.join(repr(p) for p in prohibidas)}). El autor declaró "
                    "«profundidad espiritual sin caer en clichés ni religiones» "
                    "(o equivalente). Rechazada."
                ),
                propuesta_alternativa=(
                    "Si el oficio considera que la observación de fondo era válida, "
                    "que la formule sin usar el vocabulario prohibido y la presente "
                    "de nuevo en la siguiente iteración."
                ),
            )

        # Filtro 3 — movimiento estilístico que aplana.
        riesgo, descripcion = self._detectar_aplanamiento(sug)
        if riesgo:
            return ResultadoFiltro(
                sugerencia=sug,
                decision="rechazada",
                filtro_que_aplico=3,
                razon=descripcion,
            )

        # Filtro 4 — recurso intencional marcado como debilidad.
        recurso = self._detecta_recurso_intencional_marcado(sug)
        if recurso:
            return ResultadoFiltro(
                sugerencia=sug,
                decision="rechazada",
                filtro_que_aplico=4,
                razon=(
                    f"La sugerencia trata como problema un recurso que el autor declaró "
                    f"intencional: {recurso}. No es debilidad; es voz."
                ),
            )

        # Filtro 5 — bloque de tercero.
        bloque_tercero = self._detecta_bloque_de_tercero(sug)
        if bloque_tercero:
            return ResultadoFiltro(
                sugerencia=sug,
                decision="escalada_al_autor",
                filtro_que_aplico=5,
                razon=(
                    f"Este capítulo lo escribió un tercero ({bloque_tercero}). La sugerencia "
                    "afecta a un autor distinto del autor del libro y requiere consulta antes "
                    "de aplicarse."
                ),
            )

        # Si pasó los cinco filtros — aprobada.
        return ResultadoFiltro(
            sugerencia=sug,
            decision="aprobada",
            filtro_que_aplico=0,
            razon="",
        )

    # ─── Detectores ───────────────────────────────────────────────────

    # Verbos típicos de meta-instrucción editorial (no son reescritura).
    _VERBOS_META_INSTRUCCION: set[str] = {
        "revisar", "revisa", "considerar", "considera", "agregar", "agrega",
        "añadir", "añade", "evaluar", "evalua", "dividir", "divide",
        "fusionar", "fusiona", "separar", "separa", "señalar", "señala",
        "pulir", "pule", "ajustar", "ajusta", "verificar", "verifica",
        "expandir", "expande", "acortar", "acorta", "reordenar", "reordena",
        "explorar", "explora", "trabajar", "trabaja", "incluir", "incluye",
        "proponer", "propone", "marcar", "marca", "cambiar", "cambia",
        # Verbos del catálogo de movimientos estructurales que ahora damos
        # al Estructuralista en su prompt:
        "pedir", "pide", "sugerir", "sugiere", "explicitar", "explicita",
        "reforzar", "refuerza", "consolidar", "consolida", "diferir", "difiere",
        "mover", "mueve", "cortar", "corta", "recoger", "recoge",
        "sostener", "sostiene", "remarcar", "remarca", "reemplazar", "reemplaza",
        "reorganizar", "reorganiza", "reestructurar", "reestructura",
        "alinear", "alinea", "delimitar", "delimita", "introducir", "introduce",
        "destacar", "destaca", "abrir", "cerrar", "cierra",
    }

    def _es_meta_instruccion(self, propuesta: str, original: str) -> bool:
        """Una propuesta es meta-instrucción cuando NO es texto reescrito
        sino una instrucción al autor sobre qué hacer.
        Heurísticas:
          • la propuesta es notablemente más corta que el original; y
          • empieza con (o contiene cerca del inicio) un verbo de instrucción.
        """
        prop = propuesta.strip()
        orig = original.strip()
        if not prop:
            return True
        # Si la propuesta es mucho más corta que el original, casi siempre es instrucción.
        if len(prop.split()) < max(20, len(orig.split()) * 0.5):
            primeras = prop.lower().split()[:6]
            if any(p.strip(".,;:") in self._VERBOS_META_INSTRUCCION for p in primeras):
                return True
        # Caso adicional: empieza directamente con verbo de instrucción.
        primera_palabra = prop.lower().split()[0].strip(".,;:") if prop else ""
        if primera_palabra in self._VERBOS_META_INSTRUCCION:
            return True
        return False

    def _detectar_aplanamiento(
        self, sug: SugerenciaEditorial
    ) -> tuple[bool, str]:
        """Heurísticas para detectar si la propuesta aplana la voz del original.

        Solo aplica cuando la propuesta es una REESCRITURA del original.
        Las meta-instrucciones ('revisá', 'considerá', 'agregá un párrafo')
        no se evalúan con estas heurísticas — están permitidas, son el
        oficio normal del editor.
        """
        original = sug.cita_completa.strip()
        propuesta = sug.propuesta.strip()
        if not original or not propuesta:
            return False, ""

        # Si la propuesta es meta-instrucción y no reescritura, no es aplanamiento.
        if self._es_meta_instruccion(propuesta, original):
            return False, ""

        razones: list[str] = []

        # Heurística 1: el original tiene cascada con ellipsis y la propuesta no.
        if original.count("…") >= 2 and propuesta.count("…") == 0:
            razones.append(
                "el original usa cascadas con puntos suspensivos (recurso poético del autor) "
                "y la propuesta los elimina."
            )

        # Heurística 2: el original tiene mayúsculas completas (mantra) y la propuesta no.
        palabras_mayus_orig = sum(
            1 for w in original.split() if len(w) > 3 and w.isupper()
        )
        palabras_mayus_prop = sum(
            1 for w in propuesta.split() if len(w) > 3 and w.isupper()
        )
        if palabras_mayus_orig >= 2 and palabras_mayus_prop == 0:
            razones.append(
                "el original usa mayúsculas completas como recurso de énfasis (mantra) "
                "y la propuesta las elimina."
            )

        # Heurística 3: la propuesta introduce cuantificadores genéricos que no estaban.
        cuantificadores = [
            "según estudios", "se sabe que", "muchas personas",
            "todos sabemos", "la mayoría de", "está demostrado",
        ]
        for cuant in cuantificadores:
            if cuant in propuesta.lower() and cuant not in original.lower():
                razones.append(
                    f"la propuesta introduce el cuantificador genérico «{cuant}» que no "
                    "estaba en el original; convierte una experiencia personal en un argumento."
                )
                break

        # Heurística 4: la propuesta cambia primera persona por tercera/impersonal.
        primera_orig = self._densidad_primera_persona(original)
        primera_prop = self._densidad_primera_persona(propuesta)
        if primera_orig >= 0.02 and primera_prop < 0.005:
            razones.append(
                "el original está claramente en primera persona y la propuesta la borra. "
                "El autor habla desde la vivencia: la primera persona es voz."
            )

        # Heurística 5: la propuesta es mucho más larga que el original (típico
        # de paráfrasis explicativa que aplana).
        if len(propuesta.split()) > len(original.split()) * 1.6 and len(original.split()) > 10:
            razones.append(
                "la propuesta es mucho más larga que el original (paráfrasis explicativa). "
                "El autor escribe ajustado; agregar prosa explicativa diluye la fuerza."
            )

        if not razones:
            return False, ""

        descripcion = (
            "La propuesta aplana la voz del autor. Razones detectadas: "
            + "; ".join(razones)
            + ". Rechazada por el filtro 3 (movimientos estilísticos que aplanan la voz)."
        )
        return True, descripcion

    def _densidad_primera_persona(self, texto: str) -> float:
        if not texto:
            return 0.0
        palabras = texto.lower().split()
        marcadores = {
            "yo", "me", "mi", "mis", "mío", "mía", "míos", "mías",
            "conmigo", "vivimos", "mi", "soy", "estoy", "tengo", "decidí",
            "decidi", "viví", "vivi", "creí", "crei",
        }
        if not palabras:
            return 0.0
        return sum(1 for p in palabras if p.strip(".,;:¿?¡!") in marcadores) / len(palabras)

    # Verbos que indican ATAQUE a un recurso (no mera mención).
    _VERBOS_DE_ATAQUE: set[str] = {
        "reemplazar", "reemplaza", "reemplazo",
        "quitar", "quita", "quitarlas", "quitarlos",
        "eliminar", "elimina", "eliminarlas", "eliminarlos",
        "evitar", "evita", "evitarse",
        "cambiar", "cambia", "cambiarlas", "cambiarlos",
        "sustituir", "sustituye",
        "convertir", "convierte",
        "borrar", "borra",
        "suprimir", "suprime",
        "corregir", "corrige",  # solo en contexto de recurso intencional
        "reducir", "reduce",
        "minimizar", "minimiza",
        "no usar", "no use",
        "abandonar", "abandona",
    }

    def _detecta_recurso_intencional_marcado(
        self, sug: SugerenciaEditorial
    ) -> str:
        """Devuelve el recurso atacado si la sugerencia lo trata como debilidad.

        El filtro solo dispara cuando se cumplen DOS condiciones:
          1. La sugerencia menciona el recurso (mayúsculas, puntos suspensivos,
             repetición, anécdota+reflexión, coloquialismos).
          2. La sugerencia propone una acción de ATAQUE sobre ese recurso
             (reemplazar, quitar, eliminar, etc.).

        Si solo se menciona sin atacar, no es problema — pasa.

        # TODO (edge case): si la cita muestra texto claramente garbled (artefacto
        # de OCR / extracción de PDF — eg. palabras duplicadas, fragmentos sin sentido),
        # la "repetición" es accidental y no debe bloquear una corrección legítima del
        # Editor de Línea. Heurística posible: si la misma secuencia de 4+ palabras
        # aparece más de una vez en la cita en un radio de 10 palabras, es probable
        # artefacto de extracción, no repetición intencional del autor.
        """
        texto_sug = (sug.diagnostico + " " + sug.propuesta).lower()
        for recurso in self.voz.recursos_intencionales:
            tecnica = (recurso.get("tecnica") or "").lower()
            if not tecnica:
                continue
            palabras_clave = {
                "mayúscula": ["mayúscula", "mayuscula", "all caps"],
                "puntos suspensivos": ["puntos suspensivos", "ellipsis", "…"],
                "repetición": ["repetic", "repeti"],
                "anécdota": ["anécdota", "anecdota"],
                "coloquial": ["coloquial", "regional", "neutro"],
            }
            for clave, sinonimos in palabras_clave.items():
                if clave not in tecnica:
                    continue
                # Encontró que esta sugerencia toca este recurso.
                menciona = any(syn in texto_sug for syn in sinonimos)
                if not menciona:
                    continue
                # ¿Hay además un verbo de ataque cerca?
                ataca = self._hay_verbo_de_ataque(texto_sug)
                if ataca:
                    return recurso.get("tecnica", "recurso del autor")
        return ""

    def _hay_verbo_de_ataque(self, texto: str) -> bool:
        for verbo in self._VERBOS_DE_ATAQUE:
            if verbo in texto:
                return True
        return False

    def _detecta_bloque_de_tercero(self, sug: SugerenciaEditorial) -> str:
        capitulo = (sug.capitulo or "").lower()
        if not capitulo:
            return ""
        for declaracion in self.voz.bloques_de_tercero:
            nombre_bloque = (declaracion.get("bloque") or "").lower()
            if not nombre_bloque:
                continue
            if (
                nombre_bloque in capitulo
                or ("prólogo" in nombre_bloque and "prólogo" in capitulo)
                or ("preliminar" in capitulo and ("prólogo" in nombre_bloque or "créditos" in nombre_bloque))
            ):
                return declaracion.get("autor_real", "tercero")
        return ""

    # ─── Persistencia ─────────────────────────────────────────────────

    def escribir_bloqueos(
        self, resultados: list[ResultadoFiltro], destino: Path
    ) -> None:
        bloqueos = [
            r.to_dict()
            for r in resultados
            if r.decision in ("rechazada", "escalada_al_autor", "modificada")
        ]
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(
            json.dumps(bloqueos, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ─── Resumen para consola ─────────────────────────────────────────

    def resumen_resultados(self, resultados: list[ResultadoFiltro]) -> str:
        conteo = {"aprobada": 0, "modificada": 0, "rechazada": 0, "escalada_al_autor": 0}
        por_oficio: dict[str, dict[str, int]] = {}
        for r in resultados:
            conteo[r.decision] = conteo.get(r.decision, 0) + 1
            of = r.sugerencia.oficio
            por_oficio.setdefault(of, {}).setdefault(r.decision, 0)
            por_oficio[of][r.decision] = por_oficio[of].get(r.decision, 0) + 1

        lineas = [
            f"  Lector de Voz revisó {len(resultados)} sugerencias.",
            f"    Aprobadas:  {conteo['aprobada']}",
            f"    Rechazadas: {conteo['rechazada']}",
            f"    Escaladas al autor: {conteo['escalada_al_autor']}",
            f"    Modificadas: {conteo['modificada']}",
        ]
        for of, c in por_oficio.items():
            partes = ", ".join(f"{k}={v}" for k, v in c.items())
            lineas.append(f"      · {of}: {partes}")
        return "\n".join(lineas)
