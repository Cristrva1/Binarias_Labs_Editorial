"""Lector Ideal Simulado — implementación.

Persona: `agents/editorial/04_lector_ideal_simulado.md`.

Simula la lectura completa del libro desde la piel del lector que el
autor imaginó. Produce un mapa emocional en Markdown por capítulo —
no sugerencias YAML. El Director convierte sus observaciones en
dictamen si lo decide.

A diferencia del resto de oficios, este no trabaja bloque por bloque:
lee el manuscrito completo en una sola pasada para que la simulación
de la experiencia lectora sea coherente.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from base_agente import BaseAgenteEditorial

if TYPE_CHECKING:
    from manuscrito import BloqueDelManuscrito, Manuscrito


class LectorIdealSimulado(BaseAgenteEditorial):
    nombre_oficio = "Lector Ideal Simulado"
    nombre_archivo_md = "04_lector_ideal_simulado.md"
    prefijo_id = "LI"
    temperatura = 0.35
    max_tokens = 5000

    def _encuadre_para_bloque(self, bloque: "BloqueDelManuscrito") -> str:
        """No se usa en este oficio (trabaja sobre el manuscrito completo)."""
        return ""

    def analizar_manuscrito(self, manuscrito: "Manuscrito") -> str:
        """Lee el manuscrito completo y devuelve un mapa emocional en Markdown.

        Returns:
            Texto en Markdown con la nota por capítulo y la nota de cierre.
        """
        lector = self.voz.datos.get("lector_imaginado") or {}
        descripcion_lector = (
            lector.get("descripcion")
            or lector.get("quien_es")
            or "el lector que el autor imaginó"
        )
        estado_esperado = lector.get("estado_emocional_al_terminar") or "no declarado"

        capitulos_str = self._resumir_capitulos(manuscrito)

        system = self.system_prompt()
        user = (
            f"Sos el Lector Ideal Simulado. Acabás de leer «{self.voz.libro_titulo}» completo.\n\n"
            f"Antes de empezar, te pusiste en la piel de este lector:\n"
            f"  {descripcion_lector}\n\n"
            f"El estado emocional que el autor quería despertar al terminar:\n"
            f"  {estado_esperado}\n\n"
            "Devolvé tu mapa emocional capítulo por capítulo, con exactamente este formato:\n\n"
            "### Capítulo: \"[nombre]\"\n\n"
            "Lo que me llegó. [cita literal si la hay, o declarar que no la hubo]\n\n"
            "Dónde me detuve. [imagen, frase o idea que me hizo cerrar el libro; o 'en ningún momento']\n\n"
            "Dónde me distraje. [párrafo o sección donde mi atención se fue; o 'en ningún momento']\n\n"
            "Lo que me preguntaría. [la pregunta que me queda como lector]\n\n"
            "Si seguiría leyendo. [honestidad bruta; si no, en qué frase exacta soltaría el libro]\n\n"
            "---\n\n"
            "Después de todos los capítulos, agregá una NOTA DE CIERRE de una página:\n"
            "  - Cómo te sentís como lector al terminar el libro.\n"
            "  - Si lo que sentiste coincide con lo que el autor declaró querer despertar.\n"
            "  - Si no coincide, dónde se fue la brecha — con cuidado, sin dramatismo.\n\n"
            "RECORDÁ: No proponés cambios. No hacés marketing. "
            "No comparás al autor con otros. Solo describís la experiencia.\n\n"
            "=== MANUSCRITO (capítulo por capítulo) ===\n\n"
            f"{capitulos_str}\n"
            "=== FIN DEL MANUSCRITO ==="
        )

        resultado = self.router.chat(
            user_prompt=user,
            system=system,
            temperature=self.temperatura,
            max_tokens=self.max_tokens,
        )

        if not resultado.get("success"):
            error = resultado.get("error", "desconocido")
            return (
                f"# Mapa Emocional — ERROR\n\n"
                f"No fue posible generar el mapa emocional.\n"
                f"Error: {error}\n"
            )

        encabezado = (
            f"# Mapa Emocional — {self.voz.libro_titulo}\n\n"
            f"*Oficio: Lector Ideal Simulado | Lector imaginado: {descripcion_lector}*\n\n"
            "---\n\n"
        )
        return encabezado + resultado.get("content", "")

    def _resumir_capitulos(self, manuscrito: "Manuscrito") -> str:
        """Construye un texto compacto del manuscrito para el prompt."""
        partes: list[str] = []
        for bloque in manuscrito.bloques:
            if bloque.es_bloque_de_tercero:
                continue
            cap = bloque.capitulo or f"Bloque {bloque.indice}"
            partes.append(f"### {cap}\n\n{bloque.texto[:3000]}")
        return "\n\n---\n\n".join(partes)
