#!/usr/bin/env python3
"""
MÓDULO 0: INGESTA Y CONTEXTO DEL AUTOR (v3)
=============================================
Responsabilidad:
  1. Extraer texto del PDF por páginas.
  2. Dividir en chunks con overlap semántico.
  3. Generar archivos base estructurados:
     - bible_del_libro.json      (metadatos del manuscrito)
     - mapa_chunks.json          (índice navegable de chunks)
     - contexto_autor.yaml       (perfil calibrado del autor)
  4. Validar calidad de extracción (OCR fallido, truncamientos).

Dependencias:
  pip install pdfplumber pyyaml
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# ─── Paths ───
CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from config_v3 import ProyectoPaths
from schemas_v3 import guardar_hallazgos  # Reutilizar helpers de persistencia


class ModuloIngesta:
    """
    Ingesta un manuscrito PDF y prepara todos los artefactos que los
    módulos posteriores necesitan para operar.
    """

    CHUNK_SIZE = 6000          # caracteres por chunk
    CHUNK_OVERLAP = 500        # overlap para no perder contexto en cortes
    MIN_CHARS_PER_PAGE = 50    # Umbral para detectar OCR fallido

    def __init__(self, paths: ProyectoPaths, pdf_nombre: Optional[str] = None):
        self.paths = paths
        self.pdf_path = paths.pdf_path(pdf_nombre)
        self.texto_completo = ""
        self.paginas: List[str] = []
        self.chunks: List[Dict] = []
        self.metadatos: Dict = {}
        self.problemas_extraccion: List[Dict] = []

    def _validar_dependencias(self) -> bool:
        try:
            import pdfplumber
            import yaml
            return True
        except ImportError as e:
            print(f"   [ERROR] Dependencia faltante: {e}. Ejecuta: pip install pdfplumber pyyaml")
            return False

    def extraer_texto(self) -> bool:
        """Extrae texto página por página y detecta problemas de OCR."""
        import pdfplumber

        print(f"   Leyendo PDF: {self.pdf_path}")
        if not self.pdf_path.exists():
            print(f"   [ERROR] No existe el PDF: {self.pdf_path}")
            return False

        with pdfplumber.open(str(self.pdf_path)) as pdf:
            total_paginas = len(pdf.pages)
            print(f"   Páginas detectadas: {total_paginas}")

            for i, page in enumerate(pdf.pages):
                txt = page.extract_text() or ""
                self.paginas.append(txt)
                self.texto_completo += txt + "\n\n"

                # Validación por página
                if len(txt.strip()) < self.MIN_CHARS_PER_PAGE:
                    self.problemas_extraccion.append({
                        "pagina": i + 1,
                        "tipo": "extraccion_baja",
                        "caracteres": len(txt.strip()),
                        "recomendacion": "Revisar si la página es imagen o tiene OCR fallido."
                    })

                if (i + 1) % 20 == 0 or (i + 1) == total_paginas:
                    print(f"      -> {i + 1}/{total_paginas} paginas procesadas")

        print(f"   Total caracteres extraídos: {len(self.texto_completo)}")
        print(f"   Problemas de extracción detectados: {len(self.problemas_extraccion)}")
        return True

    def _chunk_inteligente(self) -> List[Dict]:
        """
        Divide el texto en chunks respetando límites de párrafo cuando sea posible,
        con overlap configurable.
        """
        chunks = []
        texto = self.texto_completo
        start = 0
        idx = 0

        while start < len(texto):
            end = start + self.CHUNK_SIZE
            if end >= len(texto):
                end = len(texto)
            else:
                # Intentar cortar al final de un párrafo (doble salto de línea)
                buscar_desde = max(start, end - 200)
                corte = texto.rfind("\n\n", buscar_desde, end)
                if corte != -1:
                    end = corte + 2

            chunk_text = texto[start:end]

            # Calcular rango de páginas aproximado
            chars_hasta_start = sum(len(p) for p in self.paginas[:])
            # Estimación simple: distribución lineal de caracteres por página
            pagina_inicio = self._approximar_pagina(start)
            pagina_fin = self._approximar_pagina(end)

            chunks.append({
                "id": f"C{idx:03d}",
                "indice": idx,
                "caracteres": len(chunk_text),
                "offset_inicio": start,
                "offset_fin": end,
                "pagina_inicio": pagina_inicio,
                "pagina_fin": pagina_fin,
                "texto_resumen": chunk_text[:300].replace("\n", " ") + "...",
            })

            start = end - self.CHUNK_OVERLAP if end < len(texto) else end
            idx += 1

        return chunks

    def _approximar_pagina(self, offset: int) -> int:
        """Estima la página correspondiente a un offset de caracteres."""
        acum = 0
        for i, pagina in enumerate(self.paginas):
            acum += len(pagina) + 2  # +2 por los \n\n que agregamos
            if offset < acum:
                return i + 1
        return len(self.paginas)

    def generar_chunks(self) -> bool:
        print("   Generando chunks con overlap semántico...")
        self.chunks = self._chunk_inteligente()
        print(f"   Chunks generados: {len(self.chunks)}")
        for c in self.chunks[:3]:
            print(f"      {c['id']}: pág. {c['pagina_inicio']}-{c['pagina_fin']}, {c['caracteres']} chars")
        if len(self.chunks) > 3:
            print(f"      ... y {len(self.chunks) - 3} más")
        return True

    def generar_bible(self) -> bool:
        """Genera bible_del_libro.json con metadatos estructurados."""
        import yaml

        # Contar palabras aproximadas
        palabras = len(self.texto_completo.split())
        capitulos_detectados = self._detectar_capitulos()

        self.metadatos = {
            "libro_id": self.paths.libro_id,
            "autor": self.paths.autor,
            "titulo": self._inferir_titulo(),
            "pdf_fuente": str(self.pdf_path),
            "extraccion": {
                "timestamp": datetime.now().isoformat(),
                "total_paginas": len(self.paginas),
                "total_caracteres": len(self.texto_completo),
                "total_palabras": palabras,
                "total_chunks": len(self.chunks),
                "chunk_size": self.CHUNK_SIZE,
                "chunk_overlap": self.CHUNK_OVERLAP,
            },
            "estructura_detectada": {
                "capitulos_estimados": len(capitulos_detectados),
                "capitulos": capitulos_detectados[:20],  # primeros 20
            },
            "problemas_extraccion": self.problemas_extraccion,
            "version_modulo": "m0_v3.0",
        }

        self.paths.m0_ingesta.mkdir(parents=True, exist_ok=True)
        bible_path = self.paths.bible_path()
        with open(bible_path, "w", encoding="utf-8") as f:
            json.dump(self.metadatos, f, indent=2, ensure_ascii=False)

        print(f"   Bible guardada: {bible_path}")
        return True

    def _detectar_capitulos(self) -> List[Dict]:
        """
        Heurística simple: busca patrones como 'Capítulo X', 'Chapter X', etc.
        """
        patrones = [
            r"Cap[ií]tulo\s+(\d+|\w+)",
            r"Chapter\s+(\d+|\w+)",
            r"^\s*(\d+)\s*[.\-]\s+",
        ]
        encontrados = []
        for i, pagina in enumerate(self.paginas):
            for patron in patrones:
                for match in re.finditer(patron, pagina, re.IGNORECASE | re.MULTILINE):
                    encontrados.append({
                        "tipo": "capitulo",
                        "numero_o_titulo": match.group(1) or match.group(0),
                        "pagina": i + 1,
                        "contexto": pagina[max(0, match.start()-30):match.end()+30].replace("\n", " ")
                    })
        return encontrados

    def _inferir_titulo(self) -> str:
        """Intenta extraer el título de las primeras páginas."""
        primeras_paginas = "\n".join(self.paginas[:3])
        lineas = [l.strip() for l in primeras_paginas.splitlines() if l.strip()]
        if lineas:
            # Típicamente el título está en las primeras 3 líneas no vacías
            candidato = " ".join(lineas[:3])
            return candidato[:120]
        return self.paths.libro_id

    def generar_mapa_chunks(self) -> bool:
        """Genera mapa_chunks.json para navegación."""
        mapa = {
            "libro_id": self.paths.libro_id,
            "total_chunks": len(self.chunks),
            "chunks": self.chunks,
        }
        mapa_path = self.paths.mapa_chunks_path()
        with open(mapa_path, "w", encoding="utf-8") as f:
            json.dump(mapa, f, indent=2, ensure_ascii=False)
        print(f"   Mapa de chunks guardado: {mapa_path}")
        return True

    def generar_contexto_autor(self) -> bool:
        """
        Lee RESPUESTAS_AUTOR_<LIBRO>.md si existe y genera contexto_autor.yaml.
        Si no existe, genera un template para que el autor lo complete.
        """
        import yaml

        respuestas_path = self.paths.respuestas_autor()
        contexto = {
            "libro_id": self.paths.libro_id,
            "autor": self.paths.autor,
            "calibrado": False,
            "timestamp": datetime.now().isoformat(),
            "vision_autor": {
                "intencion": "",
                "mensaje_central": "",
                "lector_ideal": "",
                "genero_esperado": "",
                "tono_deseado": "",
                "dudas_pendientes": [],
            },
            "restricciones": {
                "no_alterar": [],
                "no_recomendar": [],
            },
            "notas_calibracion": "Pendiente: completar con respuestas del cuestionario del autor."
        }

        if respuestas_path.exists():
            print(f"   Respuestas del autor encontradas: {respuestas_path}")
            try:
                contenido = respuestas_path.read_text(encoding="utf-8")
                contexto["fuente_cuestionario"] = str(respuestas_path)
                contexto["raw_respuestas"] = contenido
                contexto["calibrado"] = True
                contexto["notas_calibracion"] = "Cargado desde respuestas del autor."

                # Extracción simple de campos clave (puede mejorarse con LLM en futuro)
                for linea in contenido.splitlines():
                    if "intención" in linea.lower() or "intencion" in linea.lower():
                        contexto["vision_autor"]["intencion"] = linea.split(":", 1)[-1].strip()
                    if "mensaje" in linea.lower():
                        contexto["vision_autor"]["mensaje_central"] = linea.split(":", 1)[-1].strip()
                    if "lector" in linea.lower() or "público" in linea.lower():
                        contexto["vision_autor"]["lector_ideal"] = linea.split(":", 1)[-1].strip()

            except Exception as e:
                print(f"   [ADVERTENCIA] No se pudo leer respuestas: {e}")
        else:
            print(f"   [INFO] No se encontró {respuestas_path}. Se generará template.")

        contexto_path = self.paths.contexto_autor_path()
        with open(contexto_path, "w", encoding="utf-8") as f:
            yaml.dump(contexto, f, allow_unicode=True, sort_keys=False)

        print(f"   Contexto del autor guardado: {contexto_path}")
        return True

    def validar_calidad(self) -> bool:
        """
        Validaciones mínimas antes de declarar la ingesta exitosa.
        """
        print("   Validando calidad de extracción...")
        ok = True

        if len(self.texto_completo) < 1000:
            print("   [ERROR] Extracción demasiado corta (< 1000 caracteres). ¿PDF escaneado?")
            ok = False

        tasa_problemas = len(self.problemas_extraccion) / max(len(self.paginas), 1)
        if tasa_problemas > 0.3:
            print(f"   [ADVERTENCIA] {tasa_problemas:.0%} de páginas con extracción deficiente.")
            ok = False

        if ok:
            print("   ✅ Validación de calidad superada.")
        return ok

    def ejecutar(self) -> bool:
        """Orquesta todo el módulo 0."""
        print("\n   [M0] Iniciando ingesta...")

        if not self._validar_dependencias():
            return False

        if not self.extraer_texto():
            return False

        if not self.generar_chunks():
            return False

        if not self.generar_bible():
            return False

        if not self.generar_mapa_chunks():
            return False

        if not self.generar_contexto_autor():
            return False

        if not self.validar_calidad():
            return False

        print("   [M0] Ingesta completada exitosamente.")
        return True


# ─── CLI standalone ───
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Módulo 0: Ingesta y Contexto del Autor")
    parser.add_argument("--autor", required=True)
    parser.add_argument("--libro", required=True)
    parser.add_argument("--pdf", default=None)
    args = parser.parse_args()

    paths = ProyectoPaths(autor=args.autor, libro_id=args.libro)
    paths.ensure_dirs()
    modulo = ModuloIngesta(paths, pdf_nombre=args.pdf)
    exit(0 if modulo.ejecutar() else 1)
