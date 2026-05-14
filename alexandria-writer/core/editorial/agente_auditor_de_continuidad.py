"""Auditor de Continuidad — implementación.

Persona: `agents/editorial/06_auditor_de_continuidad.md`.

Último oficio en ejecutarse por iteración. Lee el manuscrito completo
y verifica cinco cosas:
  1. Mantras — ¿aparecen donde deben? ¿hay alguno abandonado?
  2. Promesas — ¿el libro cumple lo que prometió?
  3. Callbacks — ¿las ideas introducidas temprano se recogen después?
  4. Contradicciones internas — ¿el autor afirma X y luego no-X sin
     que medie una transformación visible?
  5. Quiebres de tono no justificados.

No reescribe. No propone cambios estructurales. Produce observaciones
con cita literal; el Director decide qué hacer con cada una.

Las observaciones se mapean al esquema SugerenciaEditorial para que
el Lector de Voz y el Director puedan procesarlas en el flujo normal.
El campo `metadata["tipo_continuidad"]` distingue de qué tipo es cada
observación.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from base_agente import BaseAgenteEditorial, SugerenciaEditorial

if TYPE_CHECKING:
    from manuscrito import BloqueDelManuscrito, Manuscrito


class AuditorDeContinuidad(BaseAgenteEditorial):
    nombre_oficio = "Auditor de Continuidad"
    nombre_archivo_md = "06_auditor_de_continuidad.md"
    prefijo_id = "AC"
    temperatura = 0.2
    max_tokens = 5000

    def _encuadre_para_bloque(self, bloque: "BloqueDelManuscrito") -> str:
        """No se usa en este oficio (trabaja sobre el manuscrito completo)."""
        return ""

    def analizar_manuscrito(
        self,
        manuscrito: "Manuscrito",
        lectura_inicial: str = "",
        sugerencias_previas: list[SugerenciaEditorial] | None = None,
    ) -> list[SugerenciaEditorial]:
        """Audita el manuscrito completo y devuelve observaciones estructuradas.

        Args:
            manuscrito: El manuscrito completo.
            lectura_inicial: Texto de la lectura inicial del Director (M1).
            sugerencias_previas: Sugerencias ya generadas en esta iteración,
                para evitar repetir lo que otros oficios ya marcaron.

        Returns:
            Lista de SugerenciaEditorial con tipo_continuidad en metadata.
        """
        self._bloque_actual = 0
        self._contador_id = 0

        intencion = self.voz.datos.get("intencion") or {}
        promesa_central = (
            intencion.get("de_que_trata_en_una_frase") or "no declarada"
        )
        lector = self.voz.datos.get("lector_imaginado") or {}
        estado_esperado = lector.get("estado_emocional_al_terminar") or "no declarado"

        mantras_str = self._resumir_mantras()
        temas_previos = self._resumir_temas_previos(sugerencias_previas)
        texto_manuscrito = self._resumir_manuscrito(manuscrito)

        system = self.system_prompt()
        user = (
            f"Sos el Auditor de Continuidad. Acabás de leer «{self.voz.libro_titulo}» completo.\n\n"
            f"PROMESA CENTRAL DEL LIBRO: {promesa_central}\n"
            f"ESTADO EMOCIONAL QUE EL AUTOR QUIERE DESPERTAR AL TERMINAR: {estado_esperado}\n\n"
            f"MANTRAS Y PASAJES SAGRADOS (a verificar):\n{mantras_str}\n\n"
            f"TEMAS YA MARCADOS POR OTROS OFICIOS EN ESTA ITERACIÓN (no repetir):\n"
            f"{temas_previos}\n\n"
            "Aplicá tus cinco verificaciones:\n"
            "  1. MANTRAS: ¿aparecen en los momentos pivote del libro? ¿hay alguno introducido "
            "y luego abandonado? ¿hay variaciones involuntarias que confunden?\n"
            "  2. PROMESAS: ¿el libro cumple lo que prometió al lector (explícita o "
            "implícitamente en el prólogo o primer capítulo)?\n"
            "  3. CALLBACKS: ¿las ideas, imágenes o frases introducidas temprano se recogen "
            "más adelante? ¿hay callbacks rotos?\n"
            "  4. CONTRADICCIONES: ¿el autor afirma X en un capítulo y no-X en otro sin que "
            "medie una transformación visible y marcada?\n"
            "  5. QUIEBRES DE TONO: ¿hay capítulos que cambian de registro sin que el "
            "contenido lo justifique?\n\n"
            "Devolvé tus observaciones como YAML dentro de ```yaml ... ```. "
            "Cada observación tiene EXACTAMENTE estos campos:\n"
            "  - tipo: (mantra_abandonado | promesa_no_cumplida | callback_roto | "
            "contradiccion_interna | quiebre_de_tono)\n"
            "  - capitulo_origen: string (capítulo donde se introduce o promete el elemento)\n"
            "  - cita_origen: string (cita literal del manuscrito — obligatoria)\n"
            "  - capitulo_observado: string (capítulo donde se verifica el problema)\n"
            "  - observacion: string (qué encontraste, en tres frases máximo)\n"
            "  - decisiones_posibles: string (opciones para el autor, sin imponer cuál tomar)\n\n"
            "Si el libro es internamente coherente en todas las verificaciones, devolvé "
            "exactamente: 'Sin observaciones'.\n"
            "Producí solo las observaciones que de verdad importen. Tres buenas "
            "valen más que diez ruidosas.\n\n"
            "=== MANUSCRITO (capítulo por capítulo) ===\n\n"
            f"{texto_manuscrito}\n\n"
            "=== LECTURA INICIAL DEL DIRECTOR ===\n\n"
            f"{lectura_inicial[:3000] if lectura_inicial else '(no disponible)'}\n\n"
            "=== FIN ==="
        )

        resultado = self.router.chat(
            user_prompt=user,
            system=system,
            temperature=self.temperatura,
            max_tokens=self.max_tokens,
        )

        if not resultado.get("success"):
            print(f"      [Auditor] error: {resultado.get('error', 'desconocido')}")
            return []

        return self._parsear_observaciones(resultado.get("content", ""))

    def guardar_observaciones_json(
        self, sugerencias: list[SugerenciaEditorial], ruta_salida: Path
    ) -> None:
        """Escribe las observaciones del auditor en continuidad_observaciones.json."""
        datos = [s.to_dict() for s in sugerencias]
        ruta_salida.write_text(
            json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ─── Helpers privados ─────────────────────────────────────────────

    def _resumir_mantras(self) -> str:
        pasajes = self.voz.pasajes_sagrados
        if not pasajes:
            return "  (no declarados en voz_autor.yaml)"
        lineas: list[str] = []
        for p in pasajes[:10]:
            desc = p.get("descripcion") or p.get("texto") or ""
            cap = p.get("referencia_capitulo") or ""
            entrada = f"  - {desc}"
            if cap:
                entrada += f" (cap: {cap})"
            lineas.append(entrada)
        return "\n".join(lineas)

    def _resumir_temas_previos(
        self, sugerencias: list[SugerenciaEditorial] | None
    ) -> str:
        if not sugerencias:
            return "  (ninguno aún)"
        resumen: list[str] = []
        for s in sugerencias[:30]:
            texto = s.diagnostico[:80].replace("\n", " ")
            resumen.append(f"  - [{s.oficio}] {texto}")
        return "\n".join(resumen)

    def _resumir_manuscrito(self, manuscrito: "Manuscrito") -> str:
        partes: list[str] = []
        for bloque in manuscrito.bloques:
            if bloque.es_bloque_de_tercero:
                continue
            cap = bloque.capitulo or f"Bloque {bloque.indice}"
            partes.append(f"### {cap}\n\n{bloque.texto[:2500]}")
        return "\n\n---\n\n".join(partes)

    def _parsear_observaciones(self, contenido: str) -> list[SugerenciaEditorial]:
        if "sin observaciones" in contenido.lower()[:200]:
            return []

        bloques_yaml = re.findall(r"```yaml\s*\n(.*?)\n```", contenido, re.DOTALL)
        if not bloques_yaml:
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

                tipo = str(entrada.get("tipo") or "continuidad")
                cita = str(entrada.get("cita_origen") or "").strip()
                cap_origen = str(
                    entrada.get("capitulo_origen") or entrada.get("capitulo") or ""
                ).strip()
                observacion = str(entrada.get("observacion") or "").strip()

                if not observacion or not (cita or cap_origen):
                    continue

                sug = SugerenciaEditorial(
                    id=self._siguiente_id(),
                    oficio=self.nombre_oficio,
                    capitulo=cap_origen,
                    ubicacion=cita[:80] if cita else cap_origen,
                    cita_completa=cita,
                    diagnostico=observacion,
                    propuesta=str(entrada.get("decisiones_posibles") or "").strip(),
                    que_se_gana="Coherencia interna del libro.",
                    que_se_pierde=(
                        "El lector puede notar la incoherencia y perder confianza en el texto."
                    ),
                    metadata={
                        "tipo_continuidad": tipo,
                        "capitulo_observado": str(
                            entrada.get("capitulo_observado") or ""
                        ),
                    },
                )
                sugerencias.append(sug)

        return sugerencias
