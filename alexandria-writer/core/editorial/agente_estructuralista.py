"""Estructuralista de Ensayo — implementación.

Persona: `agents/editorial/02_estructuralista_de_ensayo.md`.

Mira el bloque desde la mirada estructural del género real (ensayo,
memoria, devocional, manual). Detecta capítulos de doble corazón,
transiciones secas, promesas no cumplidas, testimonios sin tesis.
"""

from __future__ import annotations

from base_agente import BaseAgenteEditorial
from manuscrito import BloqueDelManuscrito


class Estructuralista(BaseAgenteEditorial):
    nombre_oficio = "Estructuralista de Ensayo"
    nombre_archivo_md = "02_estructuralista_de_ensayo.md"
    prefijo_id = "ES"
    temperatura = 0.25
    max_tokens = 3500

    def _encuadre_para_bloque(self, bloque: BloqueDelManuscrito) -> str:
        capitulos_abiertos = [
            c.get("referencia_capitulo", "")
            for c in self.voz.capitulos_abiertos
        ]
        es_capitulo_abierto = bloque.capitulo and any(
            c.lower() in (bloque.capitulo or "").lower()
            for c in capitulos_abiertos
            if c
        )

        encuadre = (
            f"El género real del libro es: {self.voz.genero_real}.\n"
            "NO uses marcos de ficción comercial (arco de tres actos, hero's journey, "
            "midpoint reversal, save-the-cat). Para ensayo confesional usá: tesis personal "
            "→ testimonios ancla → desarrollo → invitación.\n\n"
            "Mirá el bloque buscando movimientos estructurales: capítulos de doble corazón, "
            "transiciones secas, promesas no cumplidas, testimonios sin tesis, tesis sin "
            "testimonio, sobreposición temática.\n\n"
            "Sé especialmente prudente con capítulos sagrados (los lista la voz del autor): "
            "ahí solo señalás, no proponés movimientos mayores.\n"
        )
        if es_capitulo_abierto:
            encuadre += (
                "\n⚑ Este capítulo está marcado por el autor como ABIERTO — "
                "él pidió ayuda con esta sección. Tenés más libertad de propuesta. "
                "Aun así, no le entregues más de tres sugerencias bien pensadas.\n"
            )
        encuadre += (
            "\nNo proponés reescribir la prosa (eso es del Editor de Línea). "
            "Tu propuesta es del nivel del movimiento estructural.\n\n"
            "REGLA DURA SOBRE VARIEDAD: NO uses la fórmula 'agregar un puente' como "
            "respuesta automática. Si una observación natural fuera 'agregar un puente', "
            "preguntate primero si lo más útil sería en realidad uno de estos otros "
            "movimientos:\n"
            "  • Explicitar la tesis del capítulo en una frase clara cerca del inicio.\n"
            "  • Separar dos hilos confundidos en dos secciones distintas.\n"
            "  • Mover una frase del cierre al inicio (o viceversa).\n"
            "  • Recoger un callback de un capítulo anterior (sostener una promesa).\n"
            "  • Reforzar el remate con un eco de la apertura.\n"
            "  • Cortar una digresión que distrae del corazón del capítulo.\n"
            "  • Pedir un segundo testimonio breve para diversificar el argumento.\n"
            "  • Marcar el viraje emocional con un cambio de párrafo o un silencio.\n"
            "  • Consolidar dos capítulos contiguos que dicen lo mismo.\n"
            "  • Diferir información hasta el momento en que pesa.\n\n"
            "Solo usá 'agregar un puente' cuando sea genuinamente lo único que falta y "
            "ninguno de los otros movimientos sirve mejor. En ese caso, sé específico "
            "sobre qué dos cosas conecta el puente y qué tono debe tener.\n\n"
            "Si la propuesta requiere texto nuevo, pedí al autor que lo escriba — la "
            "casa no inventa anécdotas en su nombre."
        )
        return encuadre
