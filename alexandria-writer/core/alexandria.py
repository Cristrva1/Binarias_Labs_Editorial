#!/usr/bin/env python3
"""
Alexandria Writer — Core Orchestrator
Sistema de orquestación principal que coordina todos los módulos
para el análisis, edición y mejora de TSBN.

Uso:
    python alexandria.py --mode analyze --input "path/to/manuscript.pdf"
    python alexandria.py --mode research --topic "resiliencia laboral"
    python alexandria.py --mode memory --action store --key "personaje_x" --content "..."
    python alexandria.py --mode graph
    python alexandria.py --mode full

Modos:
    analyze   → Análisis multi-dimensional del manuscrito
    research  → Investigación profunda sobre un tema
    memory    → Gestión de memoria persistente
    graph     → Generación de knowledge graph
    full      → Pipeline completo: research + analyze + graph
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Añadir paths
CORE_DIR = Path(__file__).parent
sys.path.insert(0, str(CORE_DIR))

from llm_router import LLMRouter
from modules.research_engine import ResearchEngine
from modules.memory_manager import MemoryManager
from modules.knowledge_graph import KnowledgeGraph
from modules.tsbn_analyzer import TSBNAnalyzer

PROJECT_ROOT = CORE_DIR.parent


class AlexandriaOrchestrator:
    """
    Orquestador central del sistema Alexandria Writer.
    Coordina LLM Router, Research, Memory, Knowledge Graph y Analysis.
    """

    def __init__(self):
        print("=" * 65)
        print("   ALEXANDRIA WRITER — Core Orchestrator v1.0")
        print("=" * 65)

        self.router = LLMRouter()
        self.research = ResearchEngine(PROJECT_ROOT)
        self.memory = MemoryManager(PROJECT_ROOT)
        self.kgraph = KnowledgeGraph(PROJECT_ROOT)
        self.analyzer = TSBNAnalyzer(PROJECT_ROOT)

        self._print_status()

    def _print_status(self):
        """Muestra estado de los componentes."""
        print("\n📦 Componentes cargados:")
        print(f"   ✓ LLM Router      → 6 proveedores, failover automático")
        print(f"   ✓ Research Engine → GPT-Researcher + LLM Router fallback")
        print(f"   ✓ Memory Manager  → SQLite + FTS5 + Knowledge Graph")
        print(f"   ✓ Knowledge Graph → D3.js visual + graphify nativo")
        print(f"   ✓ TSBN Analyzer   → 5 dimensiones, score global ponderado")
        print(f"\n📁 Directorio raíz: {PROJECT_ROOT}")

    def extract_pdf_text(self, pdf_path: str, max_pages: int = 50) -> str:
        """Extrae texto de un PDF para análisis."""
        try:
            import pdfplumber
        except ImportError:
            print("❌ pdfplumber no instalado. Ejecuta: pip install pdfplumber")
            sys.exit(1)

        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            total = min(max_pages, len(pdf.pages))
            print(f"\n📄 Extrayendo PDF: {len(pdf.pages)} páginas totales, analizando {total}...")
            for i, page in enumerate(pdf.pages[:total], 1):
                txt = page.extract_text()
                if txt:
                    text_parts.append(txt)
                if i % 10 == 0:
                    print(f"   → Página {i}/{total}")

        full = "\n\n".join(text_parts)
        print(f"   ✅ {len(full)} caracteres extraídos")
        return full

    def cmd_analyze(self, input_path: str, dimensions: Optional[str] = None):
        """Ejecuta análisis multi-dimensional."""
        print("\n🔬 MODO: Análisis Multi-Dimensional de TSBN")
        print("-" * 65)

        # Extraer texto
        if input_path.endswith(".pdf"):
            text = self.extract_pdf_text(input_path)
        else:
            with open(input_path, "r", encoding="utf-8") as f:
                text = f.read()
            print(f"\n📄 Texto cargado: {len(text)} caracteres")

        # Determinar dimensiones
        dims = None
        if dimensions:
            dims = [d.strip() for d in dimensions.split(",")]
            valid = set(self.analyzer.DIMENSIONS.keys())
            dims = [d for d in dims if d in valid]

        # Ejecutar análisis
        report = self.analyzer.full_analysis(
            text,
            context="TSBN - Todas Son Buenas Noticias. Libro de autoayuda espiritual.",
            dimensions=dims
        )

        # Guardar en memoria
        self.memory.store(
            "ultimo_analisis_tsbn",
            f"Análisis completo de TSBN. Score global: {report['score_global']}/10",
            category="analisis",
            data={"score": report["score_global"], "dimensiones": list(report["dimensiones"].keys())},
            tags=["analisis", "tsbn", "completo"],
            importance=10.0
        )

        print(f"\n{'='*65}")
        print(f"🏆 SCORE GLOBAL TSBN: {report['score_global']}/10")
        print(f"   Evaluación: {report['evaluacion_global']}")
        print(f"{'='*65}")

        return report

    def cmd_research(self, topic: str, depth: str = "medium", context: str = ""):
        """Ejecuta investigación profunda."""
        print(f"\n🔍 MODO: Investigación Profunda")
        print(f"   Tema: {topic}")
        print(f"   Profundidad: {depth}")
        print("-" * 65)

        result = self.research.research(
            topic,
            depth=depth,
            context=context or "para un libro de autoayuda espiritual dirigido a trabajadores en México"
        )

        if result["success"]:
            print(f"\n✅ Research completado")
            print(f"   Proveedor: {result.get('provider', 'N/A')}")
            print(f"   Archivo: {result['file_path']}")
            print(f"\n📋 Resumen:")
            print(result["report"][:800])
            print("\n   [...] Ver archivo completo para el reporte total.")
        else:
            print(f"\n❌ Error: {result.get('error', 'Desconocido')}")

        return result

    def cmd_memory(self, action: str, key: Optional[str] = None,
                   content: Optional[str] = None, category: str = "general",
                   tags: Optional[str] = None):
        """Gestiona memoria persistente."""
        print(f"\n💾 MODO: Memory Manager ({action})")
        print("-" * 65)

        if action == "store":
            if not key or not content:
                print("❌ Requiere --key y --content para store")
                return
            tag_list = [t.strip() for t in tags.split(",")] if tags else []
            success = self.memory.store(key, content, category, tags=tag_list)
            status = "Almacenado" if success else "Error"
            print(f"   {'✅' if success else '❌'} {status}: {key}")

        elif action == "retrieve":
            if not key:
                print("❌ Requiere --key para retrieve")
                return
            data = self.memory.retrieve(key)
            if data:
                print(f"   ✅ Encontrado: {key}")
                print(f"   Categoría: {data['category']}")
                print(f"   Contenido: {data['content'][:200]}...")
            else:
                print(f"   ❌ No encontrado: {key}")

        elif action == "search":
            if not key:  # key aquí es el query de búsqueda
                print("❌ Requiere --key como término de búsqueda")
                return
            results = self.memory.search(key, limit=10)
            print(f"   🔍 {len(results)} resultados para '{key}':")
            for r in results:
                print(f"      [{r['category']}] {r['key']}: {r['content'][:80]}...")

        elif action == "graph":
            graph = self.memory.get_graph()
            print(f"   📊 Knowledge Graph en memoria:")
            print(f"      Nodos: {len(graph['nodes'])}")
            print(f"      Aristas: {len(graph['edges'])}")
            for n in graph['nodes'][:5]:
                print(f"      • {n['id']} ({n['category']})")

        elif action == "export":
            path = self.memory.export_to_json()
            print(f"   💾 Exportado a: {path}")

        else:
            print(f"   ❌ Acción desconocida: {action}")
            print(f"   Acciones válidas: store, retrieve, search, graph, export")

    def cmd_graph(self):
        """Genera knowledge graph."""
        print("\n🕸️  MODO: Knowledge Graph Generator")
        print("-" * 65)

        # Intentar graphify nativo primero
        if self.kgraph.check_graphify():
            print("   Usando graphify nativo...")
            result = self.kgraph.build_from_project()
        else:
            print("   Graphify no instalado. Usando generador propio...")
            result = self.kgraph.build_from_memory("TSBN Knowledge Graph")

        if result["success"]:
            print(f"\n✅ Knowledge Graph generado")
            if "html_path" in result:
                print(f"   HTML: {result['html_path']}")
            if "output_dir" in result:
                print(f"   Dir: {result['output_dir']}")

            # Generar reporte
            report = self.kgraph.generate_report()
            print(f"\n📊 Reporte guardado")
        else:
            print(f"\n❌ Error: {result.get('error', 'Desconocido')}")
            if "fallback" in result:
                print(f"   Fallback: {result['fallback']}")

    def cmd_full(self, input_path: str):
        """Ejecuta pipeline completo."""
        print("\n🚀 MODO: Pipeline Completo (Full)")
        print("=" * 65)
        print("Este modo ejecuta TODO el análisis en secuencia:")
        print("  1. Extraer texto del manuscrito")
        print("  2. Análisis multi-dimensional (5 dimensiones)")
        print("  3. Investigación de temas identificados")
        print("  4. Generar knowledge graph")
        print("  5. Compilar reporte ejecutivo final")
        print("=" * 65)

        # 1. Análisis principal
        analysis = self.cmd_analyze(input_path)

        # 2. Research sobre temas débiles
        print("\n" + "=" * 65)
        print("FASE 2: Investigación de temas identificados")
        print("=" * 65)

        for dim_name, dim_data in analysis.get("dimensiones", {}).items():
            debilidades = dim_data.get("debilidades_dimension", [])
            if debilidades:
                topic = debilidades[0][:50]  # Primera debilidad como tema de research
                print(f"\n🔍 Investigando debilidad en {dim_name}: {topic}...")
                self.cmd_research(topic, depth="quick")

        # 3. Knowledge Graph
        print("\n" + "=" * 65)
        print("FASE 3: Generación de Knowledge Graph")
        print("=" * 65)
        self.cmd_graph()

        # 4. Reporte final
        print("\n" + "=" * 65)
        print("✅ PIPELINE COMPLETO FINALIZADO")
        print("=" * 65)
        print(f"\n📁 Archivos generados en: {PROJECT_ROOT / 'projects' / 'tsbn'}")
        print(f"   • research/tsbn_analisis_multidimensional.md")
        print(f"   • research/research_*.md")
        print(f"   • memory/graphify/tsbn_memory_graph.html")
        print(f"\n🎯 Próximo paso: Revisa el análisis y ejecuta correcciones.")

        return analysis


def main():
    parser = argparse.ArgumentParser(
        description="Alexandria Writer — Sistema de Orquestación para TSBN",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python alexandria.py --mode analyze --input "manuscrito.pdf"
  python alexandria.py --mode research --topic "resiliencia espiritual" --depth deep
  python alexandria.py --mode memory --action store --key "tema_fe" --content "..."
  python alexandria.py --mode graph
  python alexandria.py --mode full --input "manuscrito.pdf"
        """
    )

    parser.add_argument("--mode", required=True,
                        choices=["analyze", "research", "memory", "graph", "full", "status"],
                        help="Modo de operación")
    parser.add_argument("--input", help="Ruta al archivo de entrada (PDF o texto)")
    parser.add_argument("--topic", help="Tema para investigación")
    parser.add_argument("--depth", default="medium",
                        choices=["quick", "medium", "deep"],
                        help="Profundidad de investigación")
    parser.add_argument("--dimensions",
                        help="Dimensiones a analizar (separadas por coma: literario,espiritual,mercadologico,tecnico,impacto)")
    parser.add_argument("--action", default="store",
                        choices=["store", "retrieve", "search", "graph", "export"],
                        help="Acción de memoria")
    parser.add_argument("--key", help="Clave para operaciones de memoria")
    parser.add_argument("--content", help="Contenido para store")
    parser.add_argument("--category", default="general",
                        help="Categoría para store")
    parser.add_argument("--tags", help="Tags separados por coma")
    parser.add_argument("--context", help="Contexto adicional para research")

    args = parser.parse_args()

    orch = AlexandriaOrchestrator()

    if args.mode == "status":
        print("\n✅ Todos los sistemas operativos.")
        return

    elif args.mode == "analyze":
        if not args.input:
            print("❌ --input requerido para modo analyze")
            sys.exit(1)
        orch.cmd_analyze(args.input, args.dimensions)

    elif args.mode == "research":
        if not args.topic:
            print("❌ --topic requerido para modo research")
            sys.exit(1)
        orch.cmd_research(args.topic, args.depth, args.context)

    elif args.mode == "memory":
        orch.cmd_memory(args.action, args.key, args.content, args.category, args.tags)

    elif args.mode == "graph":
        orch.cmd_graph()

    elif args.mode == "full":
        if not args.input:
            print("❌ --input requerido para modo full")
            sys.exit(1)
        orch.cmd_full(args.input)

    print("\n" + "=" * 65)
    print("   Alexandria Writer — Sesión finalizada")
    print("=" * 65)


if __name__ == "__main__":
    main()
