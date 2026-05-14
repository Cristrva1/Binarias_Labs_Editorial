"""Carga y servidor de la voz del autor.

`voz_autor.yaml` es ley para todo agente del sistema. Este módulo lo carga,
lo valida y lo expone como bloque de texto inyectable en cualquier prompt.

Sin un `voz_autor.yaml` cargado, ningún agente puede trabajar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


@dataclass
class VozAutor:
    """Huella vocal del autor para un libro concreto.

    Se carga una vez por iteración y se inyecta como restricción dura en
    los prompts de los siete oficios y en el filtro del Lector de Voz.
    """

    autor_nombre: str
    libro_titulo: str
    datos: dict[str, Any] = field(default_factory=dict)
    ruta: Optional[Path] = None

    @classmethod
    def cargar(cls, ruta: Path) -> "VozAutor":
        ruta = Path(ruta)
        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontró voz_autor.yaml en {ruta}. "
                "Sin ese archivo el sistema editorial no trabaja."
            )
        with open(ruta, "r", encoding="utf-8") as f:
            datos = yaml.safe_load(f)

        autor_nombre = (datos.get("autor") or {}).get("nombre", "")
        libro_titulo = (datos.get("libro") or {}).get("titulo", "")
        if not autor_nombre or not libro_titulo:
            raise ValueError(
                "voz_autor.yaml requiere `autor.nombre` y `libro.titulo`."
            )

        instancia = cls(
            autor_nombre=autor_nombre,
            libro_titulo=libro_titulo,
            datos=datos,
            ruta=ruta,
        )
        instancia._validar_minimos()
        return instancia

    # ─── Validación ───────────────────────────────────────────────────

    def _validar_minimos(self) -> None:
        """Confirma que el yaml trae los anclajes mínimos para operar.

        Si falta uno, no se aborta — se imprime aviso. Trabajar con voz
        incompleta es válido, pero el operador debe saberlo.
        """
        faltantes: list[str] = []
        for clave in ("intencion", "lector_imaginado", "prohibido", "recursos_intencionales_del_autor"):
            if not self.datos.get(clave):
                faltantes.append(clave)
        if faltantes:
            print(
                f"  [voz_autor] Aviso: faltan secciones en {self.ruta.name}: "
                f"{', '.join(faltantes)}. Los oficios trabajan, pero con menos calibración."
            )

    # ─── Acceso a piezas de la voz ────────────────────────────────────

    @property
    def como_dirigirse(self) -> str:
        return (self.datos.get("autor") or {}).get("forma_de_dirigirse", self.autor_nombre)

    @property
    def registro_intencional(self) -> str:
        return (self.datos.get("autor") or {}).get("registro_intencional", "")

    @property
    def genero_real(self) -> str:
        return (self.datos.get("libro") or {}).get("genero_real", "no especificado")

    @property
    def pasajes_sagrados(self) -> list[dict[str, Any]]:
        return self.datos.get("pasajes_sagrados") or []

    @property
    def palabras_prohibidas(self) -> list[str]:
        prohibido = self.datos.get("prohibido") or {}
        palabras: list[str] = []
        palabras.extend(prohibido.get("vocabulario_corporativo_y_de_coach") or [])
        palabras.extend(prohibido.get("cliches_de_autoayuda") or [])
        return [p.lower() for p in palabras]

    @property
    def movimientos_que_aplanan(self) -> list[str]:
        prohibido = self.datos.get("prohibido") or {}
        return prohibido.get("movimientos_estilisticos_que_aplanan_la_voz") or []

    @property
    def recursos_intencionales(self) -> list[dict[str, Any]]:
        return self.datos.get("recursos_intencionales_del_autor") or []

    @property
    def bloques_de_tercero(self) -> list[dict[str, Any]]:
        return self.datos.get("bloques_no_escritos_por_el_autor") or []

    @property
    def capitulos_abiertos(self) -> list[dict[str, Any]]:
        return self.datos.get("capitulos_abiertos_por_pedido_del_autor") or []

    @property
    def capitulos_dificiles(self) -> list[dict[str, Any]]:
        return self.datos.get("capitulos_dificiles_para_el_autor") or []

    @property
    def banderas_para_escalar(self) -> list[dict[str, Any]]:
        return self.datos.get("escalar_siempre_si") or []

    @property
    def doctrina_y_fe(self) -> dict[str, Any]:
        return self.datos.get("doctrina_y_fe") or {}

    def habla_de_fe(self) -> bool:
        return bool(self.doctrina_y_fe.get("habla_de_Dios"))

    # ─── Inyección en prompts ─────────────────────────────────────────

    def como_bloque_contexto(self) -> str:
        """Devuelve la voz del autor en bloque de texto, listo para
        inyectar como restricción dura al inicio de cualquier prompt.

        Es deliberadamente narrativo, no JSON: los modelos respetan más
        las restricciones cuando vienen redactadas.
        """
        intencion = self.datos.get("intencion") or {}
        lector = self.datos.get("lector_imaginado") or {}

        bloques: list[str] = []

        bloques.append(
            f"VOZ DEL AUTOR — {self.autor_nombre} — Libro: «{self.libro_titulo}»\n"
            f"(Esta sección es ley. Ninguna sugerencia que la contradiga llega al autor.)"
        )

        bloques.append("Intención declarada por el autor:")
        if intencion.get("por_que_lo_escribi"):
            bloques.append(f"  • Por qué lo escribió: {intencion['por_que_lo_escribi'].strip()}")
        if intencion.get("de_que_trata_en_una_frase"):
            bloques.append(f"  • De qué trata en una frase: {intencion['de_que_trata_en_una_frase'].strip()}")
        if intencion.get("prioridad_declarada"):
            bloques.append(f"  • Prioridad del autor: {intencion['prioridad_declarada'].strip()}")
        if intencion.get("como_se_define_a_si_mismo"):
            bloques.append(f"  • Cómo se define el autor: {intencion['como_se_define_a_si_mismo'].strip()}")

        bloques.append("\nEl lector que el autor imaginó:")
        if lector.get("descripcion_textual_del_autor"):
            bloques.append(f"  • {lector['descripcion_textual_del_autor'].strip()}")
        if lector.get("estado_emocional_al_terminar"):
            bloques.append(f"  • Estado emocional buscado al terminar: {lector['estado_emocional_al_terminar'].strip()}")

        if self.pasajes_sagrados:
            bloques.append("\nPasajes sagrados — NO se modifican sin aprobación escrita del autor:")
            for p in self.pasajes_sagrados:
                cita = (p.get("texto_literal") or p.get("referencia_capitulo") or "").strip().replace("\n", " ")
                bloques.append(f"  • [{p.get('id', '?')}] {cita[:200]}")

        prohibido = self.datos.get("prohibido") or {}
        if prohibido.get("vocabulario_corporativo_y_de_coach"):
            bloques.append("\nVocabulario PROHIBIDO en sugerencias (corporativo/coach):")
            bloques.append("  " + " · ".join(prohibido["vocabulario_corporativo_y_de_coach"]))
        if prohibido.get("cliches_de_autoayuda"):
            bloques.append("\nClichés PROHIBIDOS:")
            bloques.append("  " + " · ".join(prohibido["cliches_de_autoayuda"]))
        if self.movimientos_que_aplanan:
            bloques.append("\nMovimientos estilísticos PROHIBIDOS (aplanan la voz):")
            for m in self.movimientos_que_aplanan:
                bloques.append(f"  • {m}")

        if self.recursos_intencionales:
            bloques.append("\nRecursos del autor que NO se marcan como error (son intencionales):")
            for r in self.recursos_intencionales:
                tecnica = r.get("tecnica", "")
                ejemplo = (r.get("ejemplo") or "").strip().replace("\n", " ")
                funcion = (r.get("funcion") or "").strip()
                bloques.append(f"  • {tecnica} — ej.: «{ejemplo}» — función: {funcion}")

        if self.capitulos_abiertos:
            bloques.append("\nCapítulos donde el autor PIDIÓ trabajo (más libertad de propuesta):")
            for c in self.capitulos_abiertos:
                bloques.append(f"  • {c.get('referencia_capitulo', '')}")

        if self.capitulos_dificiles:
            bloques.append("\nCapítulos que al autor le costaron escribir (tratar con sensibilidad):")
            for c in self.capitulos_dificiles:
                bloques.append(f"  • {c.get('referencia_capitulo', '')}")

        if self.bloques_de_tercero:
            bloques.append("\nBloques del libro NO escritos por el autor (no aplicar su voz aquí):")
            for b in self.bloques_de_tercero:
                bloques.append(f"  • {b.get('bloque', '')} — autor real: {b.get('autor_real', 'tercero')}")

        if self.habla_de_fe():
            doctrina = self.doctrina_y_fe
            bloques.append("\nDecisiones doctrinales del autor:")
            bloques.append(f"  • Nombra a lo divino como: {', '.join(doctrina.get('como_lo_nombra') or ['no especificado'])}")
            bloques.append(f"  • Cita escrituras: {doctrina.get('cita_la_Biblia', 'no especificado')}")
            bloques.append(f"  • Denominación: {doctrina.get('denominacion_explicita', 'ninguna')}")

        if self.banderas_para_escalar:
            bloques.append("\nESCALAR AL AUTOR siempre si una sugerencia toca:")
            for b in self.banderas_para_escalar:
                items = ", ".join(f"{k}={v}" for k, v in b.items())
                bloques.append(f"  • {items}")

        return "\n".join(bloques)

    # ─── Helpers para el Lector de Voz ────────────────────────────────

    def es_pasaje_sagrado(self, texto: str) -> Optional[dict[str, Any]]:
        """Si `texto` corresponde a un pasaje sagrado, devuelve el registro."""
        texto_norm = " ".join(texto.lower().split())
        for p in self.pasajes_sagrados:
            literal = (p.get("texto_literal") or "").lower()
            if not literal:
                continue
            literal_norm = " ".join(literal.split())
            # Coincidencia si el pasaje sagrado aparece sustancialmente
            # dentro del texto, o viceversa (toleramos cortes).
            if len(literal_norm) >= 30 and (
                literal_norm in texto_norm or texto_norm in literal_norm
            ):
                return p
        return None

    def palabras_prohibidas_en(self, texto: str) -> list[str]:
        """Devuelve la lista de palabras prohibidas presentes en `texto`."""
        # TODO: la comparación actual es de substring exacto. Una palabra prohibida
        # como "potenciar" no detectará "potenciando", "potenciaste", etc. Para cubrir
        # inflexiones, usar regex con límite de palabra (\b) o un lematizador básico.
        encontradas: list[str] = []
        texto_norm = texto.lower()
        for p in self.palabras_prohibidas:
            if p in texto_norm:
                encontradas.append(p)
        return encontradas
