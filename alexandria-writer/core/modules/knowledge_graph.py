#!/usr/bin/env python3
"""
Alexandria Writer — Knowledge Graph Generator
Integra graphify para mapear el proyecto TSBN en un grafo de conocimiento.
También puede generar grafos desde la memoria persistente.

Uso:
    from modules.knowledge_graph import KnowledgeGraph
    kg = KnowledgeGraph()
    kg.build_from_memory()  # Genera graph.html desde memoria
    kg.build_from_project()  # Usa graphify nativo
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_router import LLMRouter
from modules.memory_manager import MemoryManager


class KnowledgeGraph:
    """
    Generador de Knowledge Graphs para el proyecto TSBN.
    Combina graphify (externo) + generación propia desde memoria.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.memory = MemoryManager(self.project_root)
        self.router = LLMRouter()
        self.graphify_path = self.project_root / "repos" / "graphify"
        self.output_dir = self.project_root / "memory" / "graphify"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_graphify(self) -> bool:
        """Verifica si graphify está instalado."""
        try:
            result = subprocess.run(
                ["graphify", "--version"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def build_from_project(self) -> Dict[str, Any]:
        """
        Usa graphify nativo para mapear todo el proyecto.
        Requiere que graphify esté instalado (`pip install graphifyy`).
        """
        if not self.check_graphify():
            return {
                "success": False,
                "error": "graphify no está instalado. Ejecuta: pip install graphifyy && graphify install",
                "fallback": "Usa build_from_memory() en su lugar"
            }

        try:
            # Ejecutar graphify sobre el proyecto
            result = subprocess.run(
                ["graphify", str(self.project_root), "--output", str(self.output_dir)],
                capture_output=True, text=True, timeout=120
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "output_dir": str(self.output_dir)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def build_from_memory(self, title: str = "TSBN Knowledge Graph") -> Dict[str, Any]:
        """
        Genera un knowledge graph HTML desde la memoria persistente.
        No requiere graphify instalado.
        """
        graph_data = self.memory.get_graph()

        if not graph_data["nodes"]:
            return {
                "success": False,
                "error": "No hay datos en memoria. Usa MemoryManager.store() primero.",
                "hint": "Ejecuta extract_tsbn_context.py para poblar la memoria"
            }

        # Generar HTML interactivo con D3.js
        html = self._generate_d3_html(graph_data, title)

        output_path = self.output_dir / "tsbn_memory_graph.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        # Guardar JSON también
        json_path = self.output_dir / "tsbn_memory_graph.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)

        return {
            "success": True,
            "html_path": str(output_path),
            "json_path": str(json_path),
            "nodes": len(graph_data["nodes"]),
            "edges": len(graph_data["edges"])
        }

    def _generate_d3_html(self, graph_data: Dict, title: str) -> str:
        """Genera un HTML con D3.js para visualización interactiva."""
        nodes_json = json.dumps(graph_data["nodes"])
        edges_json = json.dumps(graph_data["edges"])

        category_colors = {
            "personaje": "#E74C3C",
            "tema": "#2ECC71",
            "trama": "#3498DB",
            "mundo": "#9B59B6",
            "analisis": "#F39C12",
            "research": "#1ABC9C",
            "general": "#95A5A6"
        }

        return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
    body {{ font-family: 'Segoe UI', sans-serif; margin: 0; background: #1a1a2e; color: #eee; }}
    #graph {{ width: 100vw; height: 100vh; }}
    .node {{ cursor: pointer; }}
    .node circle {{ stroke: #fff; stroke-width: 2px; }}
    .node text {{ font-size: 12px; fill: #fff; pointer-events: none; }}
    .link {{ stroke: #aaa; stroke-opacity: 0.6; }}
    #info {{
        position: absolute; top: 20px; left: 20px;
        background: rgba(0,0,0,0.8); padding: 15px;
        border-radius: 8px; max-width: 300px;
    }}
    #legend {{
        position: absolute; bottom: 20px; right: 20px;
        background: rgba(0,0,0,0.8); padding: 10px;
        border-radius: 8px;
    }}
    .legend-item {{ display: flex; align-items: center; margin: 5px 0; }}
    .legend-color {{ width: 15px; height: 15px; border-radius: 50%; margin-right: 8px; }}
</style>
</head>
<body>
<div id="info">
    <h3>{title}</h3>
    <p>Nodos: {len(graph_data['nodes'])} | Aristas: {len(graph_data['edges'])}</p>
    <p id="selection">Haz clic en un nodo para ver detalles</p>
</div>
<div id="legend">
    <h4>Categorías</h4>
    {''.join(f'<div class="legend-item"><div class="legend-color" style="background:{c}"></div>{k}</div>' for k, c in category_colors.items())}
</div>
<div id="graph"></div>

<script>
const nodes = {nodes_json};
const links = {edges_json};
const colors = {json.dumps(category_colors)};

const svg = d3.select("#graph").append("svg")
    .attr("width", window.innerWidth)
    .attr("height", window.innerHeight);

const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(100))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(window.innerWidth/2, window.innerHeight/2))
    .force("collision", d3.forceCollide().radius(30));

const link = svg.append("g").selectAll("line")
    .data(links).enter().append("line")
    .attr("class", "link")
    .attr("stroke-width", d => d.strength * 3 || 2);

const node = svg.append("g").selectAll("g")
    .data(nodes).enter().append("g")
    .attr("class", "node")
    .call(d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

node.append("circle")
    .attr("r", 20)
    .attr("fill", d => colors[d.category] || colors.general);

node.append("text")
    .attr("dx", 25)
    .attr("dy", 5)
    .text(d => d.label || d.id);

node.on("click", (event, d) => {{
    const tags = d.tags && d.tags.length ? d.tags.join(", ") : "N/A";
    document.getElementById("selection").innerHTML = `
        <strong>${{d.id}}</strong><br>
        Categoría: ${{d.category}}<br>
        Tags: ${{tags}}
    `;
}});

simulation.on("tick", () => {{
    link.attr("x1", d => d.source.x).attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});

function dragstarted(event, d) {{ if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }}
function dragged(event, d) {{ d.fx = event.x; d.fy = event.y; }}
function dragended(event, d) {{ if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}

window.addEventListener('resize', () => {{
    svg.attr("width", window.innerWidth).attr("height", window.innerHeight);
    simulation.force("center", d3.forceCenter(window.innerWidth/2, window.innerHeight/2));
    simulation.alpha(0.3).restart();
}});
</script>
</body>
</html>"""

    def generate_report(self) -> str:
        """Genera un reporte textual del knowledge graph."""
        graph = self.memory.get_graph()

        # Análisis del grafo
        categories = {}
        for n in graph["nodes"]:
            cat = n.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1

        # Nodos más conectados
        connection_counts = {}
        for e in graph["edges"]:
            connection_counts[e["source"]] = connection_counts.get(e["source"], 0) + 1
            connection_counts[e["target"]] = connection_counts.get(e["target"], 0) + 1

        top_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        report = f"""# Knowledge Graph Report: TSBN

## Estadísticas
- **Total nodos**: {len(graph['nodes'])}
- **Total aristas**: {len(graph['edges'])}
- **Categorías**: {', '.join(f"{k} ({v})" for k, v in categories.items())}

## Entidades más conectadas (hubs)
{chr(10).join(f"- **{name}**: {count} conexiones" for name, count in top_connected)}

## Cobertura del grafo
"""
        if len(graph["nodes"]) < 5:
            report += "⚠️ El grafo está prácticamente vacío. Se necesita poblar la memoria con personajes, temas, capítulos y relaciones.\n"
        elif len(graph["edges"]) < len(graph["nodes"]):
            report += "⚠️ Hay más nodos que conexiones. El libro puede tener entidades aisladas que no interactúan.\n"
        else:
            report += "✅ El grafo tiene buena conectividad. Las entidades del libro están bien interrelacionadas.\n"

        report += f"""
## Recomendaciones
- Añadir más relaciones entre personajes y temas
- Conectar cada capítulo con los personajes que aparecen
- Vincular temas con capítulos donde se desarrollan

## Archivos generados
- HTML interactivo: `memory/graphify/tsbn_memory_graph.html`
- JSON del grafo: `memory/graphify/tsbn_memory_graph.json`
"""

        report_path = self.output_dir / "GRAPH_REPORT.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)

        return report


# --- CLI de prueba ---
if __name__ == "__main__":
    print("=" * 60)
    print("   ALEXANDRIA KNOWLEDGE GRAPH — Test")
    print("=" * 60)

    kg = KnowledgeGraph()
    print(f"\nGraphify instalado: {kg.check_graphify()}")

    # Construir desde memoria
    result = kg.build_from_memory("TSBN - Red de Conocimiento")
    if result["success"]:
        print(f"✅ Graph generado: {result['html_path']}")
        print(f"   Nodos: {result['nodes']}, Aristas: {result['edges']}")
    else:
        print(f"⚠️  {result['error']}")
        print(f"   Hint: {result.get('hint', '')}")

    # Generar reporte
    report = kg.generate_report()
    print(f"\n📊 Reporte generado en: {kg.output_dir / 'GRAPH_REPORT.md'}")
