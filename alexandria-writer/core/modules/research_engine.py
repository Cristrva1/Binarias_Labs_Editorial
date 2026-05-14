#!/usr/bin/env python3
"""
Alexandria Writer — Research Engine
Integra gpt-researcher para investigación profunda sobre temas del libro.
También puede usar el LLM Router para research rápido cuando gpt-researcher
no esté instalado.

Uso:
    from modules.research_engine import ResearchEngine
    engine = ResearchEngine()
    result = engine.research("resiliencia psicológica en el trabajo", depth="deep")
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, List

# Añadir el core al path
sys.path.insert(0, str(Path(__file__).parent.parent))
from llm_router import LLMRouter


class ResearchEngine:
    """
    Motor de investigación que integra múltiples fuentes:
    1. GPT Researcher (deep research con web scraping)
    2. LLM Router (research rápido vía APIs gratuitas)
    3. Scrapling/Crawlee (web scraping local)
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.router = LLMRouter()
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.gptr_path = self.project_root / "repos" / "gpt-researcher"
        self.results_dir = self.project_root / "projects" / "tsbn" / "research"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _check_gpt_researcher(self) -> bool:
        """Verifica si gpt-researcher está instalado y funcional."""
        if not self.gptr_path.exists():
            return False
        main_py = self.gptr_path / "main.py"
        return main_py.exists()

    def research(self, query: str, depth: str = "medium",
                 context: str = "", sources: int = 10) -> Dict[str, Any]:
        """
        Realiza investigación profunda sobre un tema.

        Args:
            query: Tema a investigar
            depth: "quick" (resumen), "medium" (reporte detallado), "deep" (investigación exhaustiva)
            context: Contexto adicional (ej: "para un libro de autoayuda espiritual")
            sources: Número de fuentes a consultar

        Returns:
            Dict con: success, report, sources, provider, file_path
        """
        if depth == "quick":
            return self._quick_research(query, context)

        # Para medium/deep, usar gpt-researcher si está disponible
        if self._check_gpt_researcher():
            return self._gptr_research(query, depth, context)
        else:
            return self._deep_research_via_router(query, context, sources)

    def _quick_research(self, query: str, context: str = "") -> Dict[str, Any]:
        """Research rápido usando el LLM Router directamente."""
        system = (
            "Eres un investigador experto. Proporciona un resumen estructurado "
            "con puntos clave, datos relevantes y fuentes sugeridas."
        )
        prompt = f"Investiga sobre: {query}"
        if context:
            prompt += f"\n\nContexto: {context}"
        prompt += (
            "\n\nProporciona:\n"
            "1. Resumen ejecutivo (3-5 puntos)\n"
            "2. Datos clave con estadísticas si aplica\n"
            "3. Perspectivas/contraste de opiniones\n"
            "4. Fuentes recomendadas (libros, estudios, expertos)\n"
            "5. Aplicación práctica al contexto dado"
        )

        result = self.router.chat(prompt, system=system, temperature=0.3)

        if result["success"]:
            filename = f"research_{query.replace(' ', '_')[:30]}_quick.md"
            filepath = self.results_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Research: {query}\n\n")
                f.write(f"**Fecha**: auto-generated\n")
                f.write(f"**Profundidad**: quick\n")
                f.write(f"**Proveedor**: {result['provider']}\n\n")
                f.write(result["content"])

            return {
                "success": True,
                "report": result["content"],
                "sources": [],
                "provider": result["provider"],
                "file_path": str(filepath)
            }
        else:
            return {"success": False, "error": result["error"]}

    def _deep_research_via_router(self, query: str, context: str = "",
                                   num_sources: int = 10) -> Dict[str, Any]:
        """
        Research profundo simulado vía LLM Router.
        Genera preguntas de investigación, las responde una a una,
        y compila un reporte completo.
        """
        system = (
            "Eres un investigador académico riguroso. Tu trabajo es producir "
            "reportes de investigación detallados, objetivos y bien estructurados."
        )

        # Paso 1: Generar preguntas de investigación
        step1_prompt = (
            f"Tema de investigación: '{query}'\n"
            f"Contexto: {context or 'Investigación general'}\n\n"
            "Genera exactamente 5 preguntas de investigación específicas que "
            "permitan construir un reporte exhaustivo sobre este tema. "
            "Responde SOLO con un array JSON de strings."
        )

        step1 = self.router.chat_json(step1_prompt, system=system)
        if not step1["success"]:
            return {"success": False, "error": step1["error"]}

        questions = step1.get("parsed_json", [])
        if not isinstance(questions, list):
            questions = [query]  # fallback

        # Paso 2: Investigar cada pregunta
        findings = []
        for i, q in enumerate(questions[:5], 1):
            q_prompt = (
                f"Investiga esta pregunta a fondo (pregunta {i}/5): {q}\n\n"
                f"Contexto general: {context or query}\n\n"
                "Proporciona:\n"
                "- Respuesta detallada\n"
                "- Datos/conceptos clave\n"
                "- Citas o referencias implícitas\n"
                "- Conexión con el tema principal"
            )
            q_result = self.router.chat(q_prompt, system=system, temperature=0.3)
            if q_result["success"]:
                findings.append({"question": q, "answer": q_result["content"]})

        # Paso 3: Compilar reporte final
        compile_prompt = (
            f"Compila el siguiente research en un reporte profesional sobre: {query}\n\n"
            f"Contexto: {context or 'Libro de autoayuda espiritual'}\n\n"
        )
        for f in findings:
            compile_prompt += f"## Pregunta: {f['question']}\n{f['answer']}\n\n"

        compile_prompt += (
            "\n\nGenera ahora el REPORTE FINAL con esta estructura:\n"
            "# Executive Summary\n"
            "# Key Findings (5-7 puntos)\n"
            "# Detailed Analysis\n"
            "# Contrasting Perspectives\n"
            "# Practical Applications\n"
            "# Recommended Sources\n"
            "# Conclusion"
        )

        final = self.router.chat(compile_prompt, system=system, temperature=0.3)

        if final["success"]:
            filename = f"research_{query.replace(' ', '_')[:30]}_deep.md"
            filepath = self.results_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Deep Research Report: {query}\n\n")
                f.write(f"**Fecha**: auto-generated\n")
                f.write(f"**Profundidad**: deep (simulada vía LLM Router)\n")
                f.write(f"**Proveedor**: {final['provider']}\n")
                f.write(f"**Preguntas investigadas**: {len(findings)}\n\n")
                f.write(final["content"])

            return {
                "success": True,
                "report": final["content"],
                "questions": [f["question"] for f in findings],
                "findings": findings,
                "provider": final["provider"],
                "file_path": str(filepath)
            }
        else:
            return {"success": False, "error": final["error"]}

    def _gptr_research(self, query: str, depth: str, context: str) -> Dict[str, Any]:
        """Usa gpt-researcher nativo si está disponible."""
        # Implementación futura: ejecutar gpt-researcher como subproceso
        # o importar como módulo Python
        return self._deep_research_via_router(query, context)


# --- CLI de prueba ---
if __name__ == "__main__":
    print("=" * 60)
    print("   ALEXANDRIA RESEARCH ENGINE — Test")
    print("=" * 60)

    engine = ResearchEngine()
    print(f"\nGPT Researcher disponible: {engine._check_gpt_researcher()}")
    print(f"Resultados se guardarán en: {engine.results_dir}")

    # Prueba rápida
    print("\n📝 Prueba de research rápido...")
    result = engine.research(
        "resiliencia en adversidades laborales",
        depth="quick",
        context="para un libro de autoayuda espiritual dirigido a trabajadores en México"
    )

    if result["success"]:
        print(f"✅ Research completado con {result['provider']}")
        print(f"📄 Guardado en: {result['file_path']}")
        print(f"\nPrimeras líneas del reporte:")
        print(result["report"][:500])
    else:
        print(f"❌ Error: {result.get('error', 'Desconocido')}")
