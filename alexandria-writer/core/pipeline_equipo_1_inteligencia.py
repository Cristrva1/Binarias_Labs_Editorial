#!/usr/bin/env python3
"""
EQUIPO 1: INTELIGENCIA Y PREPARACION
=====================================
Mision: Comprender TODO el libro TSBN y generar los documentos maestros
que los equipos 2 y 3 usaran como base de trabajo.

Agentes:
  - Extractor: Extrae texto completo del PDF
  - Sintetizador: Crea sinopsis y resumen ejecutivo
  - Cartografo: Mapea capitulos, secciones, arcos
  - Tematologo: Identifica temas, simbolos, mensajes clave
  - Vocero: Analiza la voz, tono, estilo del autor
  - Demografo: Identifica publico objetivo inicial

Salidas (en projects/tsbn/equipo1/):
  - 01_BIBLE_DEL_LIBRO.md         → Documento maestro del proyecto
  - 02_MAPA_CAPITULOS.md          → Estructura detallada por capitulo
  - 03_ANALISIS_TEMATICO.md       → Temas, simbolos, mensajes
  - 04_VOZ_TONO_ESTILO.md         → Caracteristicas de la escritura
  - 05_PUBLICO_OBJETIVO.md        → Perfil inicial de lector ideal
  - 06_RESUMEN_EJECUTIVO.md       → One-pager para stakeholders
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))
from llm_router import LLMRouter

PROJECT = CORE_DIR.parent
OUTPUT = PROJECT / "projects" / "tsbn" / "equipo1"
PDF = PROJECT / "projects" / "tsbn" / "TSBN-digital-A4.pdf"
os.makedirs(OUTPUT, exist_ok=True)


class Equipo1Inteligencia:
    def __init__(self):
        self.router = LLMRouter()
        self.texto_completo = ""
        self.chunks = []
        print("=" * 65)
        print("  EQUIPO 1: INTELIGENCIA Y PREPARACION")
        print("=" * 65)

    def extraer_texto(self):
        print("\n[FASE 1/6] Extrayendo texto completo del PDF...")
        try:
            import pdfplumber
        except ImportError:
            print("ERROR: pip install pdfplumber")
            return False

        with pdfplumber.open(str(PDF)) as pdf:
            total = len(pdf.pages)
            print(f"  Paginas: {total}")
            for i, page in enumerate(pdf.pages):
                txt = page.extract_text()
                if txt:
                    self.texto_completo += txt + "\n\n"
                if (i + 1) % 20 == 0:
                    print(f"    -> {i+1}/{total}")

        # Dividir en chunks de ~8000 chars para analisis
        chunk_size = 8000
        for i in range(0, len(self.texto_completo), chunk_size):
            self.chunks.append(self.texto_completo[i:i+chunk_size])

        print(f"  Total caracteres: {len(self.texto_completo)}")
        print(f"  Chunks para analisis: {len(self.chunks)}")
        return True

    def _llamar(self, prompt, system, temp=0.2, max_tok=4000):
        """Wrapper con retry y log de proveedor."""
        result = self.router.chat(prompt, system=system, temperature=temp, max_tokens=max_tok)
        if result["success"]:
            return result["content"], result["provider"]
        return f"ERROR: {result['error']}", "FAIL"

    def sintetizador(self):
        print("\n[FASE 2/6] Sintetizador: Creando sinopsis y resumen...")

        # Analizar primeros 3 chunks para estructura general
        muestra = "\n\n".join(self.chunks[:3])[:15000]

        prompt = f"""Analiza este texto y genera un DOCUMENTO DE INTELIGENCIA EDITORIAL completo:

## 1. SINOPSIS (max 300 palabras)
De que trata el libro, quien es el protagonista/autor, cual es el viaje central.

## 2. MENSAJE CENTRAL (max 100 palabras)
La idea unica que el lector debe llevarse.

## 3. GENERO Y SUBGENERO
Clasificacion precisa con justificacion.

## 4. FORMATO
Numero de capitulos, extension, tipo de narrativa (ensayo, memoria, devotional, etc).

## 5. HOOK PUBLICITARIO (max 50 palabras)
Frase para contraportada. Variante A (emocional) y Variante B (practica).

## 6. PALABRAS CLAVE SEO
10 terminos ordenados por volumen de busqueda estimado.

## 7. PREGUNTA CENTRAL DEL LIBRO
La pregunta que el libro responde.

## 8. PROMESA AL LECTOR
Que transformacion ofrece.

## 9. DOLOR DEL LECTOR
Que problema resuelve.

## 10. CATEGORIAS DE AMAZON
3 categorias KDP donde posicionaria mejor.

TEXTO:
{muestra}"""

        system = "Eres un editor de desarrollo con 15 anos de experiencia en best sellers de no ficcion espiritual. Generas documentos de inteligencia editorial."
        content, provider = self._llamar(prompt, system, temp=0.2, max_tok=4000)
        print(f"  OK [{provider}]")
        return content

    def cartografo(self):
        print("\n[FASE 3/6] Cartografo: Mapeando capitulos y estructura...")

        muestra = self.texto_completo[:20000]

        prompt = f"""Analiza el texto e identifica la ESTRUCTURA NARRATIVA PROFUNDA del libro:

## MAPA DE CAPITULOS
Para cada CAPITULO o SECCION encontrada:
- Titulo / Primeras palabras identificadoras
- Pagina/aproximacion de inicio
- Tema central
- Tipo de contenido (narrativa, reflexion, ejercicio, introduccion)
- Emocion dominante
- Funcion estructural (setup, desarrollo, climax, resolucion?)
- Conexion con el mensaje global

## ARQUITECTURA NARRATIVA
- ARCO GENERAL: Como evoluciona del inicio al final (3-act structure aplicada)
- PUNTOS DE GIRO (Plot Points):
  * Punto de no retorno (inciting incident)
  * Punto medio (midpoint reversal)
  * Crisis/Peor momento (all is lost)
  * Climax emocional
- ESTADO INICIAL DEL LECTOR vs ESTADO FINAL: Como cambia quien lee

## DINAMICA DE TENSION
- Donde sube la tension
- Donde baja (respiros)
- Momentos de revelacion
- Patron ritmico (intenso/calmado)

TEXTO:
{muestra}"""

        system = "Eres un editor estructural especializado en arquitectura narrativa de libros de desarrollo personal. Mapeas la estructura interna de manuscritos."
        content, provider = self._llamar(prompt, system, temp=0.2, max_tok=4000)
        print(f"  OK [{provider}]")
        return content

    def tematologo(self):
        print("\n[FASE 4/6] Tematologo: Identificando temas y simbolos...")

        # Usar muestras distribuidas del libro (inicio, medio, final)
        tercio = len(self.texto_completo) // 3
        muestra = (
            self.texto_completo[:5000] + "\n\n[...]\n\n" +
            self.texto_completo[tercio:tercio+5000] + "\n\n[...]\n\n" +
            self.texto_completo[-5000:]
        )

        prompt = f"""Analiza el texto e identifica:

1. TEMAS PRINCIPALES (max 10): Lista con prioridad
2. TEMAS SECUNDARIOS (max 10): Ideas recurrentes
3. SIMBOLOS Y METAFORAS: Imagenes repetitivas o potentes
4. CONCEPTOS CLAVE: Terminos que el autor define o usa tecnicamente
5. MENSAJES IMPLICITOS: Lo que el autor dice sin decirlo explicitamente
6. CONTRADICCIONES: Ideas que se contradicen o evolucionan
7. UNIVERSALIDAD: Que temas son universales y cuales son muy personales

TEXTO:
{muestra}"""

        system = "Eres un academico especializado en analisis tematico de literatura espiritual. Identificas patrones, simbolos y arquetipos en textos."
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"  OK [{provider}]")
        return content

    def vocero(self):
        print("\n[FASE 5/6] Vocero: Analizando voz, tono y estilo...")

        muestra = self.texto_completo[:15000]

        prompt = f"""Analiza el ESTILO DE ESCRITURA del autor:

1. VOZ: Como se presenta el autor (autoridad, amigo, mentor, companero de viaje?)
2. TONO: Cual es el tono predominante (inspirador, confesional, didactico, poetico?)
3. REGISTRO: Nivel de lenguaje (coloquial, estandar, academico, poetico?)
4. TECNICAS NARRATIVAS: Usa dialogo? Flashbacks? Metaroras? Anécdotas?
5. PATRONES: Frases o estructuras que repite frecuentemente
6. FORTALEZAS DE ESTILO: Lo que hace unico al autor
7. DEBILIDADES DE ESTILO: Lo que podria mejorar sin perder su esencia
8. COMPARABLES CON: A que autores se parece en voz/tono (max 3)
9. FIRMA DEL AUTOR: Que hace que este texto sea reconocible como de Arturo Ledezma

TEXTO:
{muestra}"""

        system = "Eres un critico literario especializado en voz y estilo de autores de no ficcion. Analizas la prosa a nivel micro y macro."
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"  OK [{provider}]")
        return content

    def demografo(self):
        print("\n[FASE 6/6] Demografo: Identificando publico objetivo...")

        muestra = self.texto_completo[:12000]

        prompt = f"""Basandote en el texto, genera un PERFIL DE LECTOR IDEAL detallado:

1. DEMOGRAFICO:
   - Edad aproximada
   - Genero (si aplica)
   - Ubicacion geografica (el libro menciona Mexico? LATAM?)
   - Nivel educativo
   - Ocupacion

2. PSICOGRAFICO:
   - Estado emocional cuando busca este libro
   - Motivacion para leer (problema que quiere resolver)
   - Valores principales
   - Creencias religiosas/espirituales
   - Situacion vital (crisis, transicion, busqueda)

3. COMPORTAMIENTO:
   - Donde compra libros
   - Como descubre libros nuevos
   - Que otros autores lee
   - Cuando lee (manana, noche, transporte)
   - Formato preferido (fisico, digital, audio)

4. OBJECIONES: Por que podria NO comprar este libro
5. GANCHOS: Que frase o promesa lo convenceria

TEXTO:
{muestra}"""

        system = "Eres un estratega de marketing editorial con experiencia en segmentacion de audiencias para libros de autoayuda espiritual. Creas buyer personas detalladas."
        content, provider = self._llamar(prompt, system, temp=0.3, max_tok=4000)
        print(f"  OK [{provider}]")
        return content

    def compilar_documentos(self, sinopsis, mapa, temas, voz, publico):
        print("\n[COMPILACION] Generando documentos maestros...")

        # 01_BIBLE_DEL_LIBRO.md
        bible = f"""# Bible del Libro — Todas Son Buenas Noticias
# Documento Maestro del Proyecto Editorial

> **Fecha de generacion:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **Generado por:** Equipo 1 de Inteligencia (Alexandria Writer)
> **Estado:** Listo para Equipos 2 y 3

---

## 1. Datos Fundamentales

| Campo | Valor |
|-------|-------|
| **Titulo** | Todas Son Buenas Noticias |
| **Autor** | Arturo Ledezma Ruan |
| **Genero** | Autoayuda espiritual / Desarrollo personal |
| **Subgenero** | *(completar tras analisis)* |
| **Extension** | 91 paginas |
| **Publico objetivo primario** | *(ver seccion 5)* |
| **Mensaje central** | *(ver seccion 2)* |
| **Score inicial** | 8.4/10 (Alexandria Analyzer) |

---

## 2. Sinopsis y Mensaje Central

{sinopsis}

---

## 3. Estructura y Mapa del Libro

{mapa}

---

## 4. Analisis Tematico

{temas}

---

## 5. Voz, Tono y Estilo del Autor

{voz}

---

## 6. Perfil del Lector Ideal (Buyer Persona Inicial)

{publico}

---

## 7. Pipeline Editorial

Este documento es la base para:
- **Equipo 2** → Analisis editorial profundo + recomendaciones de cambios
- **Equipo 3** → Estrategia de mercado, Go-to-Market, marketing plan

---

## 8. Notas para el Equipo 2 (Analisis)

Al analizar el libro, considerar:
- La voz del autor es: *(resumir de seccion 5)*
- El lector ideal es: *(resumir de seccion 6)*
- Los temas centrales son: *(resumir de seccion 4)*
- La estructura actual tiene estos puntos de giro: *(resumir de seccion 3)*

## 9. Notas para el Equipo 3 (Estrategia)

Al planificar mercado, considerar:
- El nicho espiritual en Mexico/LATAM es: *(resumir de seccion 6)*
- Los comparables son: *(resumir de seccion 5)*
- El hook publicitario es: *(resumir de seccion 2)*
- Las palabras clave de SEO son: *(resumir de seccion 2)*

---

*Documento maestro. No editar manualmente. Generado automaticamente.*
"""
        with open(OUTPUT / "01_BIBLE_DEL_LIBRO.md", "w", encoding="utf-8") as f:
            f.write(bible)
        print(f"  -> 01_BIBLE_DEL_LIBRO.md")

        # Documentos individuales para facil acceso
        docs = [
            ("02_MAPA_CAPITULOS.md", "# Mapa de Capitulos\n\n" + mapa),
            ("03_ANALISIS_TEMATICO.md", "# Analisis Tematico\n\n" + temas),
            ("04_VOZ_TONO_ESTILO.md", "# Voz, Tono y Estilo\n\n" + voz),
            ("05_PUBLICO_OBJETIVO.md", "# Publico Objetivo\n\n" + publico),
            ("06_RESUMEN_EJECUTIVO.md", "# Resumen Ejecutivo\n\n" + sinopsis),
        ]
        for fname, content in docs:
            with open(OUTPUT / fname, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  -> {fname}")

    def ejecutar(self):
        if not self.extraer_texto():
            return False

        sinopsis = self.sintetizador()
        mapa = self.cartografo()
        temas = self.tematologo()
        voz = self.vocero()
        publico = self.demografo()

        self.compilar_documentos(sinopsis, mapa, temas, voz, publico)

        print("\n" + "=" * 65)
        print("  EQUIPO 1 COMPLETADO")
        print("=" * 65)
        print(f"\n  Documentos generados en: {OUTPUT}")
        print("  Listo para pasar al Equipo 2 (Analisis Editorial)")
        return True


def main():
    equipo = Equipo1Inteligencia()
    equipo.ejecutar()


if __name__ == "__main__":
    main()
