"""Lector del manuscrito y atribución de voces.

Lee un PDF y devuelve una secuencia de bloques. Cada bloque sabe:
  - quién lo firma (el autor del libro, o un tercero declarado en
    `voz_autor.yaml > bloques_no_escritos_por_el_autor`);
  - a qué capítulo pertenece, si lo detectamos;
  - su rango de páginas.

La detección de capítulos es heurística — busca títulos en mayúsculas y
saltos de página. Si falla, el bloque queda como `capitulo: None` y el
flujo trabaja con segmentos de N páginas como respaldo.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from voz_autor import VozAutor


# Páginas por chunk cuando no se detectan capítulos limpios.
PAGINAS_POR_CHUNK_FALLBACK = 8

# Páginas iniciales reservadas para secciones preliminares
# (créditos, dedicatoria, prólogo, etc.)
PAGINAS_PRELIMINARES_DEFECTO = 6

# Patrón heurístico para detectar un título de capítulo.
PATRON_TITULO_CAP = re.compile(
    r"^\s*(?:CAP[IÍ]TULO\s+\d+\s*[-:.\s]*\s*)?([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s,;:.'·…\"\-—¡!¿?]{4,80})\s*$",
    re.MULTILINE,
)


@dataclass
class BloqueDelManuscrito:
    """Una pieza del manuscrito con su atribución de voz."""

    indice: int
    pagina_inicio: int
    pagina_fin: int
    texto: str
    capitulo: Optional[str] = None
    autor_real: str = "autor_del_libro"
    es_bloque_de_tercero: bool = False
    tratamiento_especial: str = ""
    metadata: dict = field(default_factory=dict)

    @property
    def caracteres(self) -> int:
        return len(self.texto)

    @property
    def palabras(self) -> int:
        return len(self.texto.split())

    @property
    def paginas_str(self) -> str:
        if self.pagina_inicio == self.pagina_fin:
            return f"p. {self.pagina_inicio}"
        return f"pp. {self.pagina_inicio}–{self.pagina_fin}"

    @property
    def encabezado_corto(self) -> str:
        if self.capitulo:
            return f"«{self.capitulo}» — {self.paginas_str}"
        return f"Bloque {self.indice} — {self.paginas_str}"


class Manuscrito:
    """Manuscrito leído en bloques, con voz atribuida por bloque."""

    def __init__(self, ruta_pdf: Path, voz: VozAutor):
        self.ruta_pdf = Path(ruta_pdf)
        self.voz = voz
        self.bloques: list[BloqueDelManuscrito] = []
        self.paginas_totales: int = 0

    @classmethod
    def cargar(cls, ruta_pdf: Path, voz: VozAutor) -> "Manuscrito":
        instancia = cls(ruta_pdf, voz)
        instancia._extraer_y_segmentar()
        instancia._atribuir_voces()
        return instancia

    # ─── Extracción ────────────────────────────────────────────────────

    def _extraer_y_segmentar(self) -> None:
        try:
            import pdfplumber
        except ImportError:
            raise RuntimeError(
                "Falta la dependencia `pdfplumber`. Instalá con: pip install pdfplumber"
            )

        with pdfplumber.open(str(self.ruta_pdf)) as pdf:
            paginas: list[tuple[int, str]] = []
            for i, page in enumerate(pdf.pages, start=1):
                texto = page.extract_text() or ""
                paginas.append((i, texto.strip()))
            self.paginas_totales = len(paginas)

        # Estrategia de segmentación, en este orden:
        # 1) Buscar el índice del libro y mapear cada capítulo a su rango
        #    real de páginas. Esta es la única segmentación confiable.
        # 2) Heurística de líneas en mayúsculas (ruidosa con libros como TSBN
        #    que usan mayúsculas como recurso poético).
        # 3) Respaldo: chunks de N páginas.
        bloques_via_toc = self._detectar_capitulos_via_toc(paginas)
        if bloques_via_toc:
            print(
                f"  [manuscrito] segmentado vía índice: {len(bloques_via_toc)} secciones."
            )
            self.bloques = bloques_via_toc
        else:
            bloques_heuristica = self._detectar_capitulos(paginas)
            if bloques_heuristica:
                print(
                    f"  [manuscrito] segmentado vía heurística de mayúsculas: "
                    f"{len(bloques_heuristica)} secciones."
                )
                self.bloques = bloques_heuristica
            else:
                self.bloques = self._dividir_por_paginas(paginas)
                print(
                    f"  [manuscrito] sin TOC ni títulos detectables — chunks de "
                    f"{PAGINAS_POR_CHUNK_FALLBACK} páginas."
                )

    # ─── Detección vía índice del libro (preferida) ───────────────────

    # Líneas que en el índice marcan tipo de sección sin ser título.
    _MARCADORES_TIPO_INDICE = {
        "introducción", "introduccion", "prólogo", "prologo",
        "epílogo", "epilogo", "anexo", "apéndice", "apendice",
        "índice", "indice", "contenido",
    }

    def _detectar_capitulos_via_toc(
        self, paginas: list[tuple[int, str]]
    ) -> list[BloqueDelManuscrito]:
        """Estrategia precisa: localizar el índice del libro, sacar los
        títulos en orden, y luego buscar cada título en el cuerpo para
        marcar su página de inicio. Devuelve [] si no logra parsear un
        índice creíble.
        """
        toc_paginas = self._localizar_paginas_toc(paginas)
        if not toc_paginas:
            return []

        titulos_en_orden = self._extraer_titulos_del_toc(toc_paginas, paginas)
        if len(titulos_en_orden) < 6:
            return []

        # Páginas posteriores al TOC = cuerpo del libro.
        ultima_pagina_toc = toc_paginas[-1]
        cuerpo = [(p, t) for p, t in paginas if p > ultima_pagina_toc]

        # Para cada título, encontrar su primera aparición en el cuerpo
        # después del título previo.
        ubicaciones: list[tuple[str, int]] = []  # (titulo, pagina_inicio)
        ultima_pag_encontrada = ultima_pagina_toc
        for titulo in titulos_en_orden:
            pag = self._buscar_titulo_en_cuerpo(
                titulo, cuerpo, desde_pagina=ultima_pag_encontrada
            )
            if pag is None:
                # Título no encontrado: lo saltamos y avisamos. La segmentación
                # sigue siendo válida con los demás.
                continue
            ubicaciones.append((titulo, pag))
            ultima_pag_encontrada = pag

        if len(ubicaciones) < 6:
            return []

        # Construimos los bloques.
        bloques: list[BloqueDelManuscrito] = []

        # Bloque 1: preliminares (todo lo anterior al primer capítulo, incluye TOC).
        primera_pag_cap = ubicaciones[0][1]
        if primera_pag_cap > 1:
            texto_prelim = "\n\n".join(
                t for p, t in paginas if p < primera_pag_cap and t
            )
            if texto_prelim:
                bloques.append(
                    BloqueDelManuscrito(
                        indice=len(bloques) + 1,
                        pagina_inicio=1,
                        pagina_fin=primera_pag_cap - 1,
                        texto=texto_prelim,
                        capitulo="Preliminares (créditos, dedicatoria, prólogo, índice)",
                    )
                )

        # Bloques: un capítulo por título.
        for i, (titulo, pag_inicio) in enumerate(ubicaciones):
            pag_fin = (
                ubicaciones[i + 1][1] - 1
                if i + 1 < len(ubicaciones)
                else self.paginas_totales
            )
            texto = "\n\n".join(
                t for p, t in paginas if pag_inicio <= p <= pag_fin and t
            )
            if not texto:
                continue
            bloques.append(
                BloqueDelManuscrito(
                    indice=len(bloques) + 1,
                    pagina_inicio=pag_inicio,
                    pagina_fin=pag_fin,
                    texto=texto,
                    capitulo=titulo,
                )
            )
        return bloques

    def _localizar_paginas_toc(
        self, paginas: list[tuple[int, str]]
    ) -> list[int]:
        """Devuelve los números de página que forman parte del índice.
        Heurística: páginas con la palabra 'ÍNDICE' arriba y muchas líneas
        cortas, o con muchos marcadores tipo 'Capítulo N' / 'Introducción'.
        """
        candidatos: list[int] = []
        for p, texto in paginas:
            if not texto:
                continue
            primeras_lineas = texto.splitlines()[:3]
            tiene_titulo_indice = any(
                "índice" in l.lower() or "indice" in l.lower() or "contenido" in l.lower()
                for l in primeras_lineas
            )
            cuenta_capitulos = len(re.findall(r"\bCap[ií]tulo\s+\d+\b", texto))
            cuenta_intro = len(re.findall(r"\bIntroducci[oó]n\b", texto))
            es_corto = len(texto.split()) < 350
            if tiene_titulo_indice and cuenta_capitulos + cuenta_intro >= 4 and es_corto:
                candidatos.append(p)
                continue
            if cuenta_capitulos >= 8 and es_corto:
                candidatos.append(p)
        # Solo aceptamos páginas TOC contiguas, una vez encontrada la primera.
        if not candidatos:
            return []
        contiguas: list[int] = [candidatos[0]]
        for c in candidatos[1:]:
            if c - contiguas[-1] <= 2:
                contiguas.append(c)
        return contiguas

    def _extraer_titulos_del_toc(
        self,
        toc_paginas: list[int],
        paginas: list[tuple[int, str]],
    ) -> list[str]:
        """Saca, en orden, los títulos de capítulo del bloque TOC.

        Convención observada en TSBN: cada par del índice es
            <Título del capítulo>
            <Capítulo N | Introducción | …>
        Aceptamos esa forma y también la inversa (Capítulo N en línea previa).
        """
        textos = [t for p, t in paginas if p in toc_paginas]
        toc = "\n".join(textos)

        lineas = [l.strip() for l in toc.splitlines() if l.strip()]
        # Quitamos cabeceras genéricas del propio índice.
        lineas = [
            l for l in lineas
            if l.lower() not in {"índice", "indice", "contenido"}
            and not re.match(r"^\d+$", l)            # números sueltos (paginación)
            and not re.match(r"^[ivxlcd]+$", l.lower())  # numeración romana
        ]

        titulos: list[str] = []
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            siguiente = lineas[i + 1] if i + 1 < len(lineas) else ""
            anterior = lineas[i - 1] if i > 0 else ""

            es_marcador_capitulo = bool(re.match(r"^Cap[ií]tulo\s+\d+\s*$", linea))
            es_marcador_intro = linea.lower().strip(":.,") in self._MARCADORES_TIPO_INDICE

            if es_marcador_capitulo or es_marcador_intro:
                # El título suele estar en la línea ANTERIOR.
                if anterior and anterior not in titulos and not (
                    re.match(r"^Cap[ií]tulo\s+\d+\s*$", anterior)
                    or anterior.lower().strip(":.,") in self._MARCADORES_TIPO_INDICE
                ):
                    titulos.append(anterior)
                i += 1
                continue
            i += 1
        return titulos

    def _buscar_titulo_en_cuerpo(
        self,
        titulo: str,
        cuerpo: list[tuple[int, str]],
        desde_pagina: int,
    ) -> Optional[int]:
        """Busca la primera aparición del `titulo` en el cuerpo del libro
        a partir de `desde_pagina` (exclusive). Devuelve la página.
        """
        # Normalizamos: comparamos sin distinción de caso, sin acentos en
        # los espacios extra, y permitimos cortes de línea.
        titulo_norm = re.sub(r"\s+", " ", titulo).strip().lower()
        if not titulo_norm:
            return None
        for pagina, texto in cuerpo:
            if pagina <= desde_pagina:
                continue
            if not texto:
                continue
            texto_norm = re.sub(r"\s+", " ", texto).lower()
            if titulo_norm in texto_norm:
                return pagina
            # Tolerancia: algunos títulos llegan partidos por línea con
            # ellipsis (…). Probamos también sin los puntos suspensivos.
            if "…" in titulo_norm:
                titulo_sin_ellipsis = titulo_norm.replace("…", " ").replace("  ", " ").strip()
                if titulo_sin_ellipsis in texto_norm:
                    return pagina
            # Tolerancia adicional: comparamos primeras 6 palabras del título.
            primeras_6 = " ".join(titulo_norm.split()[:6])
            if len(primeras_6) >= 18 and primeras_6 in texto_norm:
                return pagina
        # TODO: en TSBN, los capítulos 30 ("Validando que TODAS sean BUENAS NOTICIAS")
        # y 31 ("Cuando todo se ilumina y dios te recibe") no se encuentran porque el
        # PDF los renderiza con saltos de línea en el título. Posible fix: intentar
        # la búsqueda con las primeras 4 palabras cuando las 6 palabras no dan resultado.
        return None

    # ─── Detección heurística por líneas en mayúsculas (respaldo) ─────

    def _detectar_capitulos(
        self, paginas: list[tuple[int, str]]
    ) -> list[BloqueDelManuscrito]:
        """Heurística simple: busca líneas en mayúsculas que parezcan
        títulos de capítulo. Si encuentra al menos 4, segmenta por ahí.
        """
        candidatos: list[tuple[int, str, int]] = []  # (pagina, titulo, pos_en_pagina)
        for pagina, texto in paginas:
            if not texto:
                continue
            for match in PATRON_TITULO_CAP.finditer(texto):
                titulo = match.group(1).strip()
                # Heurísticas de descarte para evitar capturar texto en mayúsculas
                # accidental dentro de párrafos.
                if len(titulo) > 80 or len(titulo.split()) > 12:
                    continue
                if titulo in {"DIOS", "ARTURITO", "TODAS", "AMOR", "FE"}:
                    # Palabras sueltas en mayúsculas — probablemente énfasis, no títulos.
                    continue
                candidatos.append((pagina, titulo, match.start()))

        # Filtrar candidatos que estén demasiado cerca uno del otro.
        candidatos_filtrados: list[tuple[int, str, int]] = []
        for cand in candidatos:
            if not candidatos_filtrados:
                candidatos_filtrados.append(cand)
                continue
            ult_pag = candidatos_filtrados[-1][0]
            if cand[0] - ult_pag < 1:
                continue
            candidatos_filtrados.append(cand)

        if len(candidatos_filtrados) < 4:
            return []

        # Segmentar.
        bloques: list[BloqueDelManuscrito] = []
        # Añadir bloque "preliminares" si el primer capítulo no empieza en p. 1.
        primera_pag_cap = candidatos_filtrados[0][0]
        if primera_pag_cap > 1:
            texto_prelim = "\n\n".join(
                t for p, t in paginas if p < primera_pag_cap and t
            )
            bloques.append(
                BloqueDelManuscrito(
                    indice=len(bloques) + 1,
                    pagina_inicio=1,
                    pagina_fin=primera_pag_cap - 1,
                    texto=texto_prelim,
                    capitulo="Preliminares (créditos, dedicatoria, prólogo)",
                )
            )

        for i, (pag_inicio, titulo, _) in enumerate(candidatos_filtrados):
            pag_fin = (
                candidatos_filtrados[i + 1][0] - 1
                if i + 1 < len(candidatos_filtrados)
                else self.paginas_totales
            )
            texto_cap = "\n\n".join(
                t for p, t in paginas if pag_inicio <= p <= pag_fin and t
            )
            if not texto_cap:
                continue
            bloques.append(
                BloqueDelManuscrito(
                    indice=len(bloques) + 1,
                    pagina_inicio=pag_inicio,
                    pagina_fin=pag_fin,
                    texto=texto_cap,
                    capitulo=titulo,
                )
            )
        return bloques

    def _dividir_por_paginas(
        self, paginas: list[tuple[int, str]]
    ) -> list[BloqueDelManuscrito]:
        bloques: list[BloqueDelManuscrito] = []
        # Bloque preliminar fijo (créditos, prólogo, etc.).
        prelim_fin = min(PAGINAS_PRELIMINARES_DEFECTO, self.paginas_totales)
        texto_prelim = "\n\n".join(
            t for p, t in paginas if p <= prelim_fin and t
        )
        if texto_prelim:
            bloques.append(
                BloqueDelManuscrito(
                    indice=1,
                    pagina_inicio=1,
                    pagina_fin=prelim_fin,
                    texto=texto_prelim,
                    capitulo="Preliminares (créditos, dedicatoria, prólogo)",
                )
            )

        # Resto en chunks de N páginas.
        for inicio in range(prelim_fin + 1, self.paginas_totales + 1, PAGINAS_POR_CHUNK_FALLBACK):
            fin = min(inicio + PAGINAS_POR_CHUNK_FALLBACK - 1, self.paginas_totales)
            texto = "\n\n".join(t for p, t in paginas if inicio <= p <= fin and t)
            if not texto:
                continue
            bloques.append(
                BloqueDelManuscrito(
                    indice=len(bloques) + 1,
                    pagina_inicio=inicio,
                    pagina_fin=fin,
                    texto=texto,
                )
            )
        return bloques

    # ─── Atribución de voces ───────────────────────────────────────────

    def _atribuir_voces(self) -> None:
        bloques_de_tercero = self.voz.bloques_de_tercero
        if not bloques_de_tercero:
            return

        for bloque in self.bloques:
            for declaracion in bloques_de_tercero:
                nombre_bloque = declaracion.get("bloque", "").lower()
                if not nombre_bloque:
                    continue
                # Coincidencia textual sencilla: "prólogo" en el nombre del
                # capítulo detectado, o "preliminares" para créditos.
                if (
                    bloque.capitulo
                    and (
                        nombre_bloque in bloque.capitulo.lower()
                        or (
                            "prólogo" in nombre_bloque
                            and "preliminar" in bloque.capitulo.lower()
                        )
                        or (
                            "créditos" in nombre_bloque
                            and "preliminar" in bloque.capitulo.lower()
                        )
                    )
                ):
                    bloque.es_bloque_de_tercero = True
                    bloque.autor_real = declaracion.get("autor_real", "tercero")
                    bloque.tratamiento_especial = (
                        declaracion.get("tratamiento", "").strip()
                    )

    # ─── Acceso conveniente ────────────────────────────────────────────

    def bloques_del_autor(self) -> list[BloqueDelManuscrito]:
        """Devuelve solo los bloques escritos por el autor del libro."""
        return [b for b in self.bloques if not b.es_bloque_de_tercero]

    def resumen(self) -> str:
        """Una línea por bloque, para imprimir al iniciar la corrida."""
        lineas = [
            f"  Manuscrito: {self.ruta_pdf.name}",
            f"  Páginas totales: {self.paginas_totales}",
            f"  Bloques detectados: {len(self.bloques)}",
        ]
        for b in self.bloques:
            firma = "[autor]" if not b.es_bloque_de_tercero else "[3ro] "
            lineas.append(
                f"    {firma} {b.indice:>2}. {b.encabezado_corto}  ({b.palabras} palabras)"
            )
        return "\n".join(lineas)
