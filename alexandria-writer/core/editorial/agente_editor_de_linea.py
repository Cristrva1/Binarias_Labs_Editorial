"""Editor de Línea (es-MX) — implementación.

Persona: `agents/editorial/03_editor_de_linea_es_mx.md`.

Cuida gramática, puntuación, ritmo y claridad oración por oración, sin
tocar la voz. Pulido sí, reescritura no.
"""

from __future__ import annotations

from base_agente import BaseAgenteEditorial
from manuscrito import BloqueDelManuscrito


class EditorDeLinea(BaseAgenteEditorial):
    nombre_oficio = "Editor de Línea (es-MX)"
    nombre_archivo_md = "03_editor_de_linea_es_mx.md"
    prefijo_id = "EL"
    temperatura = 0.15
    max_tokens = 3500

    def _encuadre_para_bloque(self, bloque: BloqueDelManuscrito) -> str:
        return (
            "Aplicá tu oficio a este bloque. Buscá únicamente:\n"
            "  • errores de ortografía y acentuación,\n"
            "  • problemas de puntuación que entorpezcan la lectura,\n"
            "  • repeticiones evidentes y no intencionales,\n"
            "  • párrafos con respiración rota por concatenación.\n\n"
            f"Recordá que estás trabajando un libro del autor {self.voz.como_dirigirse} "
            f"escrito en {self.voz.registro_intencional or 'español de México'}. "
            "Los recursos intencionales del autor (mayúsculas en mantra, frases en cascada, "
            "coloquialismos mexicanos, repetición declarativa) NO se marcan como error.\n\n"
            "REGLA DURA SOBRE TILDES (acentuación):\n"
            "Antes de proponer agregar o quitar una tilde, en el campo `diagnostico` "
            "DEBÉS citar la regla RAE específica que aplica. Si no sabés la regla, NO "
            "propongas el cambio. Recordá las reglas básicas:\n"
            "  • Palabras AGUDAS (acento en última sílaba): llevan tilde solo si terminan "
            "en vocal, n o s (canción, jamás, café). 'compartir', 'feliz', 'verdad' NO llevan.\n"
            "  • Palabras GRAVES o LLANAS (acento en penúltima): llevan tilde solo si "
            "NO terminan en vocal, n o s (árbol, lápiz, cráter). 'respeto', 'responsabilidad', "
            "'personal', 'compartida', 'maestro' NO llevan tilde — son llanas terminadas en "
            "vocal o consonante distinta de n/s. NO sugieras tildes en estas palabras.\n"
            "  • Palabras ESDRÚJULAS (acento en antepenúltima): siempre llevan tilde "
            "(música, rápido, pájaro).\n"
            "  • Tildes diacríticas: tú/tu, él/el, sí/si, qué/que, cómo/como, etc., según "
            "función gramatical.\n"
            "  • Hiatos: día, oír, baúl.\n"
            "Si la palabra que querés tildar NO entra claramente en una de estas reglas, "
            "abstené la sugerencia. Vale más callar que sugerir una tilde inventada.\n\n"
            "Si una observación tuya implica reescribir la voz del autor, no la propongas. "
            "Pulido mínimo, no reescritura. Si encontrás varios errores ortográficos del mismo "
            "tipo en el bloque, agrupalos en una sola sugerencia consolidada."
        )
