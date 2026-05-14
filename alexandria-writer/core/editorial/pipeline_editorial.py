#!/usr/bin/env python3
"""Casa Alexandria — orquestador editorial.

Implementa el flujo descrito en el `MANIFIESTO_EDITORIAL.md`:

    M0  Cargar voz_autor.yaml + manuscrito (con atribución de voces)
    M1  Director Editorial → lectura_inicial.md
    M2  Oficios especializados leen el manuscrito y emiten sugerencias:
          - Estructuralista de Ensayo
          - Editor de Línea (es-MX)
          - (otros oficios — Lector Ideal, Custodio, Auditor — pendientes
             de implementación; corren como stubs en esta versión)
    M3  Lector de Voz filtra cada sugerencia (5 filtros)
    M4  Director Editorial arbitra y redacta el dictamen
    M5  Salidas en docs/Autores/<Autor>/Proyectos/<Libro>/iteracion_NN/

Uso:
    python core/editorial/pipeline_editorial.py \
        --autor <AUTOR> --libro <ID_LIBRO> --pdf <libro>.pdf

    python core/editorial/pipeline_editorial.py \
        --autor <AUTOR> --libro <ID_LIBRO> --bloques 1 2  # solo bloques 1 y 2
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Hacemos importables los módulos de core/ y core/editorial/
HERE = Path(__file__).parent
CORE_DIR = HERE.parent
PROJECT_ROOT = CORE_DIR.parent
sys.path.insert(0, str(CORE_DIR))
sys.path.insert(0, str(HERE))

from llm_router import LLMRouter

from agente_auditor_de_continuidad import AuditorDeContinuidad
from agente_custodio_doctrinal import CustodioDoctrinal
from agente_director_editorial import DirectorEditorial
from agente_editor_de_linea import EditorDeLinea
from agente_estructuralista import Estructuralista
from agente_lector_de_voz import LectorDeVoz
from agente_lector_ideal_simulado import LectorIdealSimulado
from base_agente import SugerenciaEditorial
from manuscrito import Manuscrito
from voz_autor import VozAutor


AUTORES_ROOT = PROJECT_ROOT / "docs" / "Autores"


class PipelineEditorial:
    def __init__(
        self,
        autor: str,
        libro_id: str,
        pdf_nombre: str | None = None,
        bloques_a_correr: list[int] | None = None,
        oficios: list[str] | None = None,
    ):
        self.autor = autor
        self.libro_id = libro_id
        self.pdf_nombre = pdf_nombre
        self.bloques_a_correr = bloques_a_correr
        self.oficios = oficios or ["estructuralista", "editor_de_linea", "custodio", "lector_ideal", "auditor"]
        self.t0 = time.time()

        # Rutas
        self.autor_dir = AUTORES_ROOT / autor
        self.proyecto_dir = self.autor_dir / "Proyectos" / libro_id
        self.libros_dir = self.autor_dir / "Libros"

        if not self.proyecto_dir.exists():
            raise FileNotFoundError(
                f"No existe el proyecto {self.proyecto_dir}. "
                "Creá la carpeta y colocá ahí el voz_autor.yaml."
            )

        # PDF: el primero del directorio si no se especifica.
        if pdf_nombre:
            self.pdf_ruta = self.libros_dir / pdf_nombre
        else:
            pdfs = sorted(self.libros_dir.glob("*.pdf"))
            if not pdfs:
                # caer al lugar viejo, projects/<libro_id>/
                pdfs = sorted(
                    (PROJECT_ROOT / "projects" / libro_id.lower()).glob("*.pdf")
                )
            if not pdfs:
                raise FileNotFoundError(
                    f"No encontré ningún PDF en {self.libros_dir} ni en projects/{libro_id.lower()}/"
                )
            self.pdf_ruta = pdfs[0]

        # Voz del autor
        self.voz_ruta = self.proyecto_dir / "voz_autor.yaml"
        self.voz: VozAutor = VozAutor.cargar(self.voz_ruta)

        # Iteración: la siguiente disponible.
        self.numero_iteracion = self._siguiente_iteracion()
        self.iter_dir = self.proyecto_dir / f"iteracion_{self.numero_iteracion:02d}"
        self.iter_dir.mkdir(parents=True, exist_ok=True)

        # Router LLM
        self.router = LLMRouter()

    def _siguiente_iteracion(self) -> int:
        existentes = sorted(self.proyecto_dir.glob("iteracion_*"))
        nums = []
        for d in existentes:
            try:
                nums.append(int(d.name.split("_")[1]))
            except (IndexError, ValueError):
                continue
        return (max(nums) + 1) if nums else 1

    # ─── Banner ───────────────────────────────────────────────────────

    def banner(self) -> None:
        print("\n" + "=" * 72)
        print("  CASA ALEXANDRIA — Pipeline editorial")
        print("=" * 72)
        print(f"  Autor: {self.voz.autor_nombre}  ·  Libro: «{self.voz.libro_titulo}»")
        print(f"  Género real declarado: {self.voz.genero_real}")
        print(f"  PDF fuente: {self.pdf_ruta}")
        print(f"  voz_autor.yaml: {self.voz_ruta}")
        print(f"  Iteración: {self.numero_iteracion:02d}")
        print(f"  Salida: {self.iter_dir}")
        print(f"  Oficios activos: {', '.join(self.oficios)}")
        print("=" * 72 + "\n")

    # ─── Ejecución ────────────────────────────────────────────────────

    def ejecutar(self) -> dict:
        self.banner()

        # M0 — Manuscrito
        print("[M0] Leyendo manuscrito y atribuyendo voces…")
        manuscrito = Manuscrito.cargar(self.pdf_ruta, self.voz)
        print(manuscrito.resumen())

        # Si el operador pidió bloques específicos, filtramos.
        bloques = manuscrito.bloques
        if self.bloques_a_correr:
            bloques = [b for b in bloques if b.indice in self.bloques_a_correr]
            print(f"\n  Filtrando a {len(bloques)} bloques: {self.bloques_a_correr}")

        # M1 — Lectura inicial del Director
        print("\n[M1] Director Editorial — lectura inicial…")
        director = DirectorEditorial(self.voz, self.router)
        lectura_inicial = director.lectura_inicial(manuscrito)
        (self.iter_dir / "lectura_inicial.md").write_text(
            lectura_inicial, encoding="utf-8"
        )
        print(f"  → {self.iter_dir / 'lectura_inicial.md'}")

        # M2 — Oficios
        agentes = self._instanciar_oficios()
        todas_sugerencias: list[SugerenciaEditorial] = []
        print(f"\n[M2] Oficios trabajando sobre {len(bloques)} bloques…")
        for i, bloque in enumerate(bloques, start=1):
            print(f"\n  Bloque {bloque.indice}: {bloque.encabezado_corto}")
            if bloque.es_bloque_de_tercero:
                print(
                    f"    [3ro] Bloque de tercero ({bloque.autor_real}) — los "
                    "oficios especializados no intervienen aquí."
                )
                continue
            for nombre, agente in agentes.items():
                print(f"    · {nombre} leyendo…", end=" ", flush=True)
                t = time.time()
                sugs = agente.analizar_bloque(bloque)
                print(f"{len(sugs)} sugerencia(s) en {time.time()-t:.1f}s")
                todas_sugerencias.extend(sugs)

        # M2b — Lector Ideal Simulado (lectura completa, mapa emocional)
        if "lector_ideal" in self.oficios:
            print("\n[M2b] Lector Ideal Simulado — mapa emocional del manuscrito…")
            lector_ideal = LectorIdealSimulado(self.voz, self.router)
            mapa_emocional = lector_ideal.analizar_manuscrito(manuscrito)
            (self.iter_dir / "mapa_emocional.md").write_text(
                mapa_emocional, encoding="utf-8"
            )
            print(f"  → {self.iter_dir / 'mapa_emocional.md'}")

        # M2c — Auditor de Continuidad (revisión global, entra al final de los oficios)
        if "auditor" in self.oficios:
            print("\n[M2c] Auditor de Continuidad — verificando coherencia del libro…")
            auditor = AuditorDeContinuidad(self.voz, self.router)
            obs_auditoria = auditor.analizar_manuscrito(
                manuscrito,
                lectura_inicial=lectura_inicial,
                sugerencias_previas=todas_sugerencias,
            )
            print(f"  {len(obs_auditoria)} observación(es) de continuidad.")
            if obs_auditoria:
                auditor.guardar_observaciones_json(
                    obs_auditoria, self.iter_dir / "continuidad_observaciones.json"
                )
                print(f"  → {self.iter_dir / 'continuidad_observaciones.json'}")
                todas_sugerencias.extend(obs_auditoria)

        # M3 — Lector de Voz (filtro)
        print("\n[M3] Lector de Voz — filtrando sugerencias…")
        lector_de_voz = LectorDeVoz(self.voz)
        resultados = lector_de_voz.filtrar(todas_sugerencias)
        print(lector_de_voz.resumen_resultados(resultados))
        lector_de_voz.escribir_bloqueos(
            resultados, self.iter_dir / "bloqueos_voz.json"
        )

        # M4 — Director arbitra y redacta dictamen
        print("\n[M4] Director Editorial — arbitraje y dictamen…")
        dictamen_md, datos = director.producir_dictamen(
            manuscrito,
            resultados,
            lectura_inicial,
            numero_iteracion=self.numero_iteracion,
        )

        # M5 — Salidas
        (self.iter_dir / "dictamen_editorial.md").write_text(
            dictamen_md, encoding="utf-8"
        )
        (self.iter_dir / "cambios_propuestos.json").write_text(
            json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (self.iter_dir / "decisiones_autor.json").write_text(
            json.dumps(
                {
                    "iteracion": self.numero_iteracion,
                    "instrucciones": (
                        "Por cada sugerencia, marcá su 'estado' como uno de: "
                        "'aceptada', 'rechazada', 'modificada' o 'pendiente'. "
                        "Si modificás, agregá el campo 'modificacion_del_autor'. "
                        "La casa lee este archivo al inicio de la siguiente iteración."
                    ),
                    "decisiones": [
                        {
                            "id": s.id,
                            "oficio": s.oficio,
                            "capitulo": s.capitulo,
                            "estado": "pendiente",
                            "comentario_autor": "",
                        }
                        for s in (
                            r.sugerencia
                            for r in resultados
                            if r.decision in ("aprobada", "modificada")
                        )
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        # Log
        self._guardar_log(datos, lector_de_voz.resumen_resultados(resultados))

        # Cierre
        duracion = (time.time() - self.t0) / 60
        print("\n" + "=" * 72)
        print(f"  Iteración {self.numero_iteracion:02d} completada en {duracion:.1f} min.")
        print("=" * 72)
        print("\n  Entregables:")
        for nombre in [
            "lectura_inicial.md",
            "dictamen_editorial.md",
            "cambios_propuestos.json",
            "mapa_emocional.md",
            "continuidad_observaciones.json",
            "bloqueos_voz.json",
            "decisiones_autor.json",
            "log_iteracion.json",
        ]:
            ruta = self.iter_dir / nombre
            if ruta.exists():
                print(f"    · {ruta}")

        return datos

    # ─── Instanciación de oficios ─────────────────────────────────────

    def _instanciar_oficios(self) -> dict:
        disponibles = {
            "estructuralista": Estructuralista,
            "editor_de_linea": EditorDeLinea,
        }
        instancias: dict[str, object] = {}
        for nombre in self.oficios:
            if nombre in ("lector_ideal", "auditor"):
                continue
            if nombre == "custodio":
                if CustodioDoctrinal.es_activo(self.voz):
                    instancias[nombre] = CustodioDoctrinal(self.voz, self.router)
                else:
                    print(
                        "  [custodio] El libro no declara habla_de_Dios: true. "
                        "Custodio Doctrinal no entra en esta iteración."
                    )
                continue
            cls = disponibles.get(nombre)
            if cls is None:
                print(f"  [aviso] Oficio '{nombre}' no reconocido; se omite.")
                continue
            instancias[nombre] = cls(self.voz, self.router)
        return instancias

    # ─── Log ──────────────────────────────────────────────────────────

    def _guardar_log(self, datos: dict, resumen_lector_de_voz: str) -> None:
        log = {
            "iteracion": self.numero_iteracion,
            "autor": self.autor,
            "libro": self.libro_id,
            "fecha": datetime.now().isoformat(),
            "duracion_minutos": round((time.time() - self.t0) / 60, 2),
            "oficios_activos": self.oficios,
            "bloques_corridos": (
                self.bloques_a_correr if self.bloques_a_correr else "todos"
            ),
            "total_sugerencias_aprobadas": datos["total_sugerencias_aprobadas"],
            "total_escaladas": datos["total_escaladas"],
            "provider_dictamen": datos.get("provider_dictamen", ""),
            "resumen_lector_de_voz": resumen_lector_de_voz,
        }
        (self.iter_dir / "log_iteracion.json").write_text(
            json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Casa Alexandria — pipeline editorial",
    )
    parser.add_argument("--autor", required=True, help="Carpeta del autor (ej: Juan_Perez)")
    parser.add_argument("--libro", required=True, help="ID del libro (ej: MI_LIBRO)")
    parser.add_argument("--pdf", default=None, help="Nombre específico del PDF (opcional)")
    parser.add_argument(
        "--bloques",
        nargs="+",
        type=int,
        default=None,
        help="Lista de índices de bloque a correr (para pruebas rápidas).",
    )
    parser.add_argument(
        "--oficios",
        nargs="+",
        default=None,
        help="Lista de oficios a activar (default: estructuralista editor_de_linea).",
    )
    args = parser.parse_args()

    pipeline = PipelineEditorial(
        autor=args.autor,
        libro_id=args.libro,
        pdf_nombre=args.pdf,
        bloques_a_correr=args.bloques,
        oficios=args.oficios,
    )
    pipeline.ejecutar()


if __name__ == "__main__":
    main()
