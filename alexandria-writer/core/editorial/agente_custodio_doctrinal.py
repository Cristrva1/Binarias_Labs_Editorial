"""Custodio Doctrinal — implementación.

Persona: `agents/editorial/05_custodio_doctrinal.md`.

Solo entra en libros que tocan fe, espiritualidad, conciencia o
doctrina (`voz_autor.yaml > doctrina_y_fe > habla_de_Dios: true`).

No corrige doctrina. Cuida que el libro hable de fe del modo en que
el autor declaró, y protege las sugerencias de otros oficios para que
no introduzcan registro catequético o denominacional que el autor
rechazó.

Trabaja bloque por bloque, como el Estructuralista y el Editor de
Línea, y produce sugerencias en formato YAML estándar.
"""

from __future__ import annotations

from base_agente import BaseAgenteEditorial
from manuscrito import BloqueDelManuscrito


class CustodioDoctrinal(BaseAgenteEditorial):
    nombre_oficio = "Custodio Doctrinal"
    nombre_archivo_md = "05_custodio_doctrinal.md"
    prefijo_id = "CD"
    temperatura = 0.2
    max_tokens = 3500

    @classmethod
    def es_activo(cls, voz) -> bool:
        """Devuelve True solo si el libro toca fe, espiritualidad o doctrina."""
        return voz.habla_de_fe()

    def _encuadre_para_bloque(self, bloque: BloqueDelManuscrito) -> str:
        doctrina = self.voz.doctrina_y_fe

        como_nombra_dios = doctrina.get("como_nombra_a_Dios") or "no especificado"
        evita = doctrina.get("evita") or []
        posicion_no_creyente = (
            doctrina.get("posicion_frente_al_lector_no_creyente") or "no especificado"
        )
        evita_str = (
            ", ".join(f'"{e}"' for e in evita) if evita else "nada declarado explícitamente"
        )

        return (
            f"Sos el Custodio Doctrinal. Aplicá tus tres preguntas a este bloque:\n\n"
            f"MARCO DOCTRINAL DEL AUTOR:\n"
            f"  • Cómo nombra a Dios: {como_nombra_dios}\n"
            f"  • Lenguaje o registro que pidió evitar: {evita_str}\n"
            f"  • Posición frente al lector no creyente: {posicion_no_creyente}\n\n"
            "TUS TRES PREGUNTAS:\n"
            "  1. ¿La voz espiritual de este bloque coincide con la declarada por el autor? "
            "(coincidencia es información valiosa: también se reporta.)\n"
            "  2. ¿Hay frases que asumen fe del lector donde el autor declaró apertura? "
            "(ej: 'como tú sabes, Dios…' cuando el libro está abierto al no creyente.)\n"
            "  3. ¿Hay caída en lenguaje religioso institucional, catequético o denominacional "
            "que el autor pidió evitar?\n\n"
            "Si el bloque no toca temas de fe, espiritualidad o sentido: devolvé exactamente "
            "'Sin observaciones'. No fuerces presencia donde no aplica.\n\n"
            "Si encontrás algo, usá el formato YAML estándar:\n"
            "  • `diagnostico`: qué observás — coincidencia confirmada, desvío del autor, "
            "o riesgo en una sugerencia de otro oficio.\n"
            "  • `propuesta`: acción sugerida. Puede ser 'reconocimiento al autor — sin cambio', "
            "'escalar al Director para decisión del autor', o 'avisar al Lector de Voz'.\n"
            "  • `que_se_pierde`: si no se atiende, qué riesgo corre la coherencia declarada.\n\n"
            "REGLA DURA: No proponés doctrina alternativa. No pedís citas bíblicas ni "
            "referencias a tradiciones. No calificás si un pasaje es 'profundo' o 'superficial'. "
            "Solo verificás coherencia entre la intención declarada y la prosa."
        )
