"""Director Editorial — implementación.

Persona: `agents/editorial/01_director_editorial.md`.

Hace dos cosas en una iteración:
  1. Antes de los demás oficios: produce la `lectura_inicial.md` —
     una nota interna corta sobre la promesa, la curva, los pasajes que
     respiran y los pasajes sagrados nuevos detectados.
  2. Después de los demás oficios y del Lector de Voz: arbitra,
     deduplica, prioriza y escribe el `dictamen_editorial.md` —
     única salida para el autor.

Las dos llamadas son al LLM. El Director es quien redacta la prosa final.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from agente_lector_de_voz import ResultadoFiltro
from base_agente import BaseAgenteEditorial, SugerenciaEditorial
from manuscrito import Manuscrito


class DirectorEditorial(BaseAgenteEditorial):
    nombre_oficio = "Director Editorial"
    nombre_archivo_md = "01_director_editorial.md"
    prefijo_id = "DE"
    temperatura = 0.35   # un poco más cálido para la prosa de la carta
    max_tokens = 8000

    # ─── Lectura inicial ──────────────────────────────────────────────

    # TODO: cargar el decisiones_autor.json de la iteración anterior (si existe) e
    # inyectarlo en ambas llamadas al LLM. El Director debe saber qué decidió el autor
    # la vuelta pasada para no repetir las mismas preguntas y para confirmar si los
    # cambios aceptados ya aparecen en el manuscrito actualizado.
    def lectura_inicial(self, manuscrito: Manuscrito) -> str:
        bloques_del_autor = manuscrito.bloques_del_autor()
        if not bloques_del_autor:
            return "Sin bloques del autor para leer."

        # Resumimos cada bloque del autor en su primer y último párrafo
        # para que el Director vea estructura sin reventar tokens.
        resumen_bloques: list[str] = []
        # TODO: el tope de 14 bloques puede silenciar los últimos capítulos del libro
        # en libros largos (TSBN tiene 32). Alternativa: resumir por tercios (primero,
        # mitad y final) en vez de solo los primeros 14.
        for b in bloques_del_autor[:14]:  # tope para no exceder contexto
            partes = [p.strip() for p in b.texto.split("\n\n") if p.strip()]
            primero = partes[0][:600] if partes else ""
            ultimo = partes[-1][:600] if len(partes) > 1 else ""
            resumen_bloques.append(
                f"--- {b.encabezado_corto} ({b.palabras} palabras) ---\n"
                f"Apertura: {primero}\n"
                + (f"Cierre: {ultimo}\n" if ultimo else "")
            )

        cuerpo = "Bloques del manuscrito (apertura y cierre de cada uno):\n\n" + "\n".join(
            resumen_bloques
        )
        cuerpo += (
            "\n\nTu tarea ahora: producí una `lectura_inicial.md` corta. Tres a cinco "
            "párrafos. Es nota interna para los demás oficios — no es para el autor.\n\n"
            "Incluí, sin numerar:\n"
            "  • La promesa que el libro le hace al lector, en una sola frase.\n"
            "  • La curva interna que percibís (no marco de tres actos — usá el marco "
            "    apropiado al género real declarado en la voz del autor).\n"
            "  • Tres pasajes que respiran y tres que no, citados literalmente.\n"
            "  • Cualquier pasaje nuevo que merezca protección y aún no esté en "
            "    voz_autor.yaml > pasajes_sagrados (los proponés agregar).\n\n"
            "No uses bullets. Prosa. Castellano editorial. No firmes con tu nombre — "
            "este documento es interno."
        )

        # System: usamos el system_prompt heredado pero con persona ya cargada.
        system = self.system_prompt() + (
            "\n\n=== AHORA: LECTURA INICIAL ===\n"
            "Esta NO es la fase de arbitraje. No proponés sugerencias. Solo dejás "
            "tu impresión inicial para que los demás oficios trabajen con tu marco."
        )

        resultado = self.router.chat(
            user_prompt=cuerpo,
            system=system,
            temperature=0.3,
            max_tokens=2500,
        )
        if not resultado.get("success"):
            return f"[error en lectura inicial: {resultado.get('error', '?')}]"
        return resultado.get("content", "").strip()

    # ─── Arbitraje y dictamen ─────────────────────────────────────────

    def producir_dictamen(
        self,
        manuscrito: Manuscrito,
        resultados_lector_de_voz: list[ResultadoFiltro],
        lectura_inicial: str,
        numero_iteracion: int = 1,
    ) -> tuple[str, dict]:
        """Devuelve (dictamen_md, datos_estructurados)."""

        # 1. Solo trabajamos con sugerencias aprobadas o modificadas.
        aprobadas: list[SugerenciaEditorial] = [
            r.sugerencia for r in resultados_lector_de_voz
            if r.decision in ("aprobada", "modificada")
        ]
        escaladas: list[ResultadoFiltro] = [
            r for r in resultados_lector_de_voz
            if r.decision == "escalada_al_autor"
        ]

        # 2. Ordenamos por capítulo para que el dictamen lea limpio.
        aprobadas_por_cap: dict[str, list[SugerenciaEditorial]] = {}
        for s in aprobadas:
            aprobadas_por_cap.setdefault(s.capitulo or "Sin capítulo", []).append(s)

        # 3. Preparamos el bloque resumen para el LLM.
        resumen_aprobadas = self._formatear_sugerencias_para_prompt(aprobadas_por_cap)
        resumen_escaladas = self._formatear_escaladas_para_prompt(escaladas)

        autor = self.voz.como_dirigirse
        titulo = self.voz.libro_titulo
        prioridad_autor = (
            (self.voz.datos.get("intencion") or {}).get("prioridad_declarada", "")
        ).strip()
        capitulos_abiertos = ", ".join(
            c.get("referencia_capitulo", "")
            for c in self.voz.capitulos_abiertos
        ) or "ninguno declarado"

        cuerpo = (
            f"Iteración: {numero_iteracion:02d}\n"
            f"Autor: {autor}\n"
            f"Libro: {titulo}\n"
            f"Prioridad declarada del autor: {prioridad_autor or 'no especificada'}\n"
            f"Capítulos abiertos por pedido del autor: {capitulos_abiertos}\n\n"
            "TU LECTURA INICIAL DEL MANUSCRITO (lo que vos mismo dejaste antes "
            "de que los demás oficios trabajaran):\n"
            f"{lectura_inicial}\n\n"
            "SUGERENCIAS QUE PASARON EL FILTRO DEL LECTOR DE VOZ "
            f"({len(aprobadas)} en total):\n"
            f"{resumen_aprobadas}\n\n"
            "ESCALADAS AL AUTOR (no decidís vos; las presentás):\n"
            f"{resumen_escaladas}\n\n"
            "TU TAREA: redactá el `dictamen_editorial.md` completo, dirigido al autor "
            "por su nombre, en castellano cálido y editorial. Seguí EXACTAMENTE este "
            "orden y estos encabezados:\n\n"
            f"# Dictamen editorial — «{titulo}» — Iteración {numero_iteracion:02d}\n\n"
            f"## Querido {autor},\n"
            "(carta de apertura corta — tres a cinco párrafos. Lo que la lectura completa "
            "te dejó. Sin 'estimado autor'. Sin lugares comunes. Cita una frase del "
            "manuscrito que te haya marcado.)\n\n"
            "## Lo que ya está funcionando\n"
            "(PROSA CORRIDA — absolutamente sin bullets ni asteriscos ni guiones de lista. "
            "Al menos tres cosas concretas que ya funcionan, citadas literalmente del "
            "manuscrito, integradas en párrafos de prosa. Antes de pedir cambios, "
            "reconocemos lo logrado.)\n\n"
            "## Decisiones que te pedimos esta vuelta\n"
            "(numeradas, no más de cinco. Cada decisión: qué te pedimos decidir, por qué "
            "importa, qué pasa si decidís A, qué pasa si decidís B. "
            "RECORDÁ: revisar puntuación, ortografía o gramática en el manuscrito NO "
            "es una decisión del autor — es trabajo del Editor de Línea. Eso nunca va aquí.)\n\n"
            "## Sugerencias por capítulo\n"
            "(las sugerencias aprobadas, agrupadas por capítulo, en prosa — no en bullets. "
            "Cada sugerencia: cita literal, qué observamos, qué proponemos, qué se gana, "
            "qué se pierde. Firmá cada bloque con el oficio que la propuso, "
            "entre paréntesis.)\n\n"
            "## Lo que necesita tu palabra\n"
            "(las escaladas — pasajes sagrados que algún oficio quiso tocar, conflictos "
            "donde no decidimos. Sección corta y delicada. Vos decidís.)\n\n"
            "## La próxima conversación\n"
            "(una sola pregunta concreta para vos, la que más nos importa que respondas "
            "antes de la siguiente iteración. No 'esperamos que esto sea de utilidad'.)\n\n"
            "Reglas duras de redacción:\n"
            "  • Dirigite al autor por su nombre, no como 'el autor' o 'usted'.\n"
            "  • Nada de marketing, ROI, precio, subgénero, buyer persona, comparables.\n"
            "  • Nada de 'score global' ni 'puntaje'.\n"
            "  • CERO bullets, asteriscos o guiones de lista en TODO el dictamen. "
            "Prosa corrida siempre, incluso en 'Lo que ya está funcionando'.\n"
            "  • Citá literalmente antes de comentar.\n"
            "  • Reconocé antes de pedir.\n"
            "  • Castellano de México coloquial cuando el autor escribe así.\n"
            "  • Si una sugerencia se repite por capítulo, agrupala en una sola observación.\n\n"
            "REGLA DURA SOBRE IDS:\n"
            "Cada sugerencia que recibiste arriba viene con un ID único entre corchetes "
            "(por ejemplo [ES-049] o [EL-115]). Cuando cites una sugerencia en el "
            "dictamen, usá EXACTAMENTE ese ID. NO inventes IDs. NO repitas el mismo ID "
            "en dos capítulos distintos. Si dudás del ID, mejor no lo escribas.\n\n"
            "FRASES PROHIBIDAS (no las uses jamás en el dictamen):\n"
            "  • 'podrías considerar contratar a un editor de línea' (vos sos quien dirige al editor)\n"
            "  • 'podrías considerar revisar el manuscrito tú mismo' (no es nuestro lugar empujar trabajo al autor)\n"
            "  • 'esperamos que estas observaciones sean de utilidad'\n"
            "  • 'esto es una decisión menor' (si es menor, no es decisión)\n"
            "  • 'salir de la zona de confort'\n"
            "  • 'viaje de descubrimiento'\n"
            "  • 'alcanzar tu mejor versión'\n"
            "  • 'mindset', 'paradigma', 'potenciar', 'empoderamiento'\n\n"
            "DECISIONES VS TAREAS:\n"
            "Una decisión que pedimos al autor es una disyuntiva real (A vs B), no una "
            "tarea evidente. 'Revisar puntuación en todo el manuscrito' NO es una "
            "decisión — es trabajo del Editor de Línea, no preguntamos. Si una sugerencia "
            "no requiere que el autor decida nada nuevo, va a 'Sugerencias por capítulo', "
            "no a 'Decisiones que te pedimos esta vuelta'.\n"
        )

        system = self.system_prompt() + (
            "\n\n=== AHORA: ARBITRAJE Y DICTAMEN ===\n"
            "Tu salida en este turno es UN ÚNICO archivo Markdown completo. Empezá con "
            f"`# Dictamen editorial — «{titulo}» — Iteración {numero_iteracion:02d}` y "
            "respetá los encabezados pedidos. No envuelvas la salida en bloques de código."
        )

        resultado = self.router.chat(
            user_prompt=cuerpo,
            system=system,
            temperature=0.4,
            max_tokens=8000,
        )

        if not resultado.get("success"):
            dictamen_md = (
                f"# Dictamen editorial — «{titulo}» — Iteración {numero_iteracion:02d}\n\n"
                f"⚠ El Director Editorial no pudo redactar el dictamen en esta corrida.\n"
                f"Error: {resultado.get('error', 'desconocido')}\n\n"
                f"Sugerencias aprobadas en bruto:\n\n"
            )
            for s in aprobadas:
                dictamen_md += (
                    f"- [{s.id}] ({s.oficio}) {s.capitulo} — {s.diagnostico}\n"
                )
        else:
            dictamen_md = resultado.get("content", "").strip()

        datos = {
            "iteracion": numero_iteracion,
            "autor": autor,
            "libro": titulo,
            "total_sugerencias_aprobadas": len(aprobadas),
            "total_escaladas": len(escaladas),
            "sugerencias_aprobadas": [s.to_dict() for s in aprobadas],
            "escaladas": [r.to_dict() for r in escaladas],
            "lectura_inicial": lectura_inicial,
            "provider_dictamen": resultado.get("provider", ""),
        }
        return dictamen_md, datos

    # ─── Helpers de formato ───────────────────────────────────────────

    def _formatear_sugerencias_para_prompt(
        self, por_capitulo: dict[str, list[SugerenciaEditorial]]
    ) -> str:
        if not por_capitulo:
            return "(ninguna sugerencia aprobada en esta iteración)"

        lineas: list[str] = []
        for cap, sugs in por_capitulo.items():
            lineas.append(f"\n### Capítulo: {cap}\n")
            for s in sugs:
                cita = (s.cita_completa or "").strip().replace("\n", " ")
                lineas.append(
                    f"- [{s.id}] ({s.oficio})\n"
                    f"  cita: «{cita[:280]}»\n"
                    f"  observamos: {s.diagnostico}\n"
                    f"  proponemos: {s.propuesta}\n"
                    f"  se gana: {s.que_se_gana}\n"
                    f"  se pierde: {s.que_se_pierde}\n"
                )
        return "\n".join(lineas)

    def _formatear_escaladas_para_prompt(
        self, escaladas: list[ResultadoFiltro]
    ) -> str:
        if not escaladas:
            return "(ninguna escalada en esta iteración)"
        lineas: list[str] = []
        for r in escaladas:
            cita = (r.sugerencia.cita_completa or "").strip().replace("\n", " ")
            lineas.append(
                f"- [{r.sugerencia.id}] ({r.sugerencia.oficio})\n"
                f"  cita: «{cita[:240]}»\n"
                f"  por qué se escala: {r.razon}\n"
                f"  propuesta original: {r.sugerencia.propuesta}\n"
            )
        return "\n".join(lineas)
