#!/usr/bin/env python3
"""
Alexandria Writer — LLM Router Multi-API
Rutea llamadas a través de múltiples proveedores gratuitos con failover automático.
Prioridad: Cerebras -> SambaNova -> Mistral -> Groq -> OpenRouter -> Gemini

Uso:
    from llm_router import LLMRouter
    router = LLMRouter()
    response = router.chat("Analiza este texto...", system="Eres un experto...")
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Cargar .env del proyecto raíz
PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(PROJECT_ROOT.parent / ".env", override=True)


class LLMRouter:
    """
    Router inteligente de APIs LLM con failover automático.
    Prueba proveedores en orden hasta que uno responda correctamente.
    """

    # Configuración de proveedores: (nombre, env_key, url, modelo_default, prioridad)
    PROVIDERS = [
        {
            "name": "CEREBRAS",
            "env_keys": ["CEREBRAS_API_KEY_cristrva", "CEREBRAS_API_KEY_trabajos",
                        "CEREBRAS_API_KEY_cristrva22", "CEREBRAS_API_KEY_ctrisputy",
                        "CEREBRAS_API_KEY_esdata", "CEREBRAS_API_KEY_chtmsputy",
                        "CEREBRAS_API_KEY_juegos", "CEREBRAS_API_KEY_outlcris"],
            "url": "https://api.cerebras.ai/v1/chat/completions",
            "model": "llama-3.3-70b",
            "priority": 1,
            "format": "openai"
        },
        {
            "name": "SAMBANOVA",
            "env_keys": ["SAMBANOVA_API_KEY_cristrva", "SAMBANOVA_API_KEY_trabajos",
                        "SAMBANOVA_API_KEY_cristrva22", "SAMBANOVA_API_KEY_ctrisputy",
                        "SAMBANOVA_API_KEY_esdata", "SAMBANOVA_API_KEY_chtmsputy",
                        "SAMBANOVA_API_KEY_juegos", "SAMBANOVA_API_KEY_outlcris"],
            "url": "https://api.sambanova.ai/v1/chat/completions",
            "model": "Meta-Llama-3.3-70B-Instruct",
            "priority": 2,
            "format": "openai"
        },
        {
            "name": "MISTRAL",
            "env_keys": ["MISTRAL_API_KEY_cristrva"],
            "url": "https://api.mistral.ai/v1/chat/completions",
            "model": "mistral-small-latest",
            "priority": 3,
            "format": "openai"
        },
        {
            "name": "GROQ",
            "env_keys": ["GROQ_API_KEY_cristrva", "GROQ_API_KEY_cristrva22",
                        "GROQ_API_KEY_ctrisputy", "GROQ_API_KEY_esdata",
                        "GROQ_API_KEY_chtmsputy", "GROQ_API_KEY_juegos",
                        "GROQ_API_KEY_outlcris"],
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "model": "llama-3.3-70b-versatile",
            "priority": 4,
            "format": "openai"
        },
        {
            "name": "OPENROUTER",
            "env_keys": ["OPENROUTER_API_KEY_cristrva", "OPENROUTER_API_KEY_trabajos",
                        "OPENROUTER_API_KEY_cristrva22", "OPENROUTER_API_KEY_ctrisputy",
                        "OPENROUTER_API_KEY_esdata", "OPENROUTER_API_KEY_chtmsputy",
                        "OPENROUTER_API_KEY_juegos", "OPENROUTER_API_KEY_outlcris"],
            "url": "https://openrouter.ai/api/v1/chat/completions",
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "priority": 5,
            "format": "openai"
        },
        {
            "name": "GEMINI",
            "env_keys": ["GEMINI_API_KEY_cristrva", "GEMINI_API_KEY_trabajos",
                        "GEMINI_API_KEY_cristrva22", "GEMINI_API_KEY_esdata",
                        "GEMINI_API_KEY_chtmsputy", "GEMINI_API_KEY_juegos",
                        "GEMINI_API_KEY_cris354", "GEMINI_API_KEY_crisputy"],
            "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "model": "gemini-2.0-flash",
            "priority": 6,
            "format": "gemini"
        },
        {
            "name": "NVIDIA",
            "env_keys": ["NVIDIA_API_KEY_cristrva", "NVIDIA_API_KEY_trabajos",
                        "NVIDIA_API_KEY_cristrva22", "NVIDIA_API_KEY_ctrisputy",
                        "NVIDIA_API_KEY_esdata", "NVIDIA_API_KEY_chtmsputy",
                        "NVIDIA_API_KEY_juegos", "NVIDIA_API_KEY_outlcris"],
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "model": "meta/llama-3.3-70b-instruct",
            "priority": 7,
            "format": "openai"
        },
        {
            "name": "VERTEX",
            "env_keys": ["VERTEX_API_KEY_cristrva", "VERTEX_API_KEY_trabajos",
                        "VERTEX_API_KEY_cristrva22", "VERTEX_API_KEY_ctrisputy",
                        "VERTEX_API_KEY_esdata", "VERTEX_API_KEY_chtmsputy",
                        "VERTEX_API_KEY_juegos", "VERTEX_API_KEY_outlcris"],
            "url": "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/publishers/google/models/gemini-2.0-flash-001:generateContent",
            "model": "gemini-2.0-flash-001",
            "priority": 8,
            "format": "vertex"
        },
    ]

    def __init__(self, timeout: int = 120, max_retries: int = 3, delay_between_calls: float = 0.5):
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay_between_calls = delay_between_calls
        self.active_provider: Optional[str] = None
        self._providers = sorted(self.PROVIDERS, key=lambda p: p["priority"])
        # Rate limiting: ultima llamada por proveedor
        self._last_call_time: Dict[str, float] = {}
        # Circuit breaker: contador de fallos seguidos por proveedor
        self._consecutive_failures: Dict[str, int] = {}
        self._circuit_threshold = 5  # Si falla 5 veces seguidas, saltar proveedor
        # Metricas
        self._metrics = {
            "calls": {},
            "errors": {},
            "total_time": {},
        }

    def _get_available_keys(self, provider: Dict) -> List[str]:
        """Obtiene todas las claves válidas de un proveedor."""
        keys = []
        for key_name in provider["env_keys"]:
            val = os.getenv(key_name)
            if val and val.strip() and not val.lower().startswith(("placeholder", "your_", "sk-xxx")):
                # Limpiar comillas si existen
                val = val.strip().strip('"').strip("'")
                if len(val) > 10:
                    keys.append(val)
        return keys

    def _call_openai_format(self, url: str, api_key: str, model: str,
                            messages: List[Dict], temperature: float = 0.3,
                            max_tokens: int = 4096) -> Dict:
        """Llama a una API con formato OpenAI-compatible."""
        payload = json.dumps({
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _call_gemini_format(self, url: str, api_key: str, model: str,
                            messages: List[Dict], temperature: float = 0.3,
                            max_tokens: int = 4096) -> Dict:
        """Llama a la API de Gemini."""
        # Extraer solo el contenido del usuario
        prompt_text = ""
        for m in messages:
            role = "user" if m["role"] == "user" else "model"
            prompt_text += f"{m['content']}\n\n"

        payload = json.dumps({
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }).encode("utf-8")

        full_url = f"{url}?key={api_key}"
        headers = {"Content-Type": "application/json"}

        req = urllib.request.Request(full_url, data=payload, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _call_vertex_format(self, url: str, api_key: str, model: str,
                            messages: List[Dict], temperature: float = 0.3,
                            max_tokens: int = 4096) -> Dict:
        """Llama a la API de Google Cloud Vertex AI."""
        prompt_text = ""
        system_text = ""
        for m in messages:
            if m["role"] == "system":
                system_text += m["content"] + "\n\n"
            else:
                prompt_text += m["content"] + "\n\n"

        payload = json.dumps({
            "contents": [{"role": "user", "parts": [{"text": system_text + prompt_text}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=self.timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    def _extract_content(self, provider_name: str, result: Dict) -> str:
        """Extrae el texto de la respuesta según el formato del proveedor."""
        if provider_name in ("GEMINI", "VERTEX"):
            parts = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])
            return parts[0].get("text", "") if parts else ""
        else:
            # OpenAI-compatible (Cerebras, SambaNova, Mistral, Groq, OpenRouter, NVIDIA)
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")

    def chat(self, user_prompt: str, system: str = "",
             temperature: float = 0.3, max_tokens: int = 4096,
             json_mode: bool = False) -> Dict[str, Any]:
        """
        Envía un prompt y obtiene respuesta con failover automático entre proveedores.

        Args:
            user_prompt: Prompt del usuario
            system: Instrucción de sistema
            temperature: Creatividad (0.0 - 1.0)
            max_tokens: Máximo de tokens de respuesta
            json_mode: Si True, fuerza respuesta JSON

        Returns:
            Dict con: success, content, provider, model, raw_response, error
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": user_prompt})

        last_error = None

        start_time = time.time()

        for provider in self._providers:
            # Circuit breaker: si fallo muchas veces seguidas, saltar proveedor
            if self._consecutive_failures.get(provider["name"], 0) >= self._circuit_threshold:
                print(f"  [CIRCUIT BREAKER] Saltando {provider['name']} ({self._circuit_threshold} fallos seguidos)")
                continue

            keys = self._get_available_keys(provider)
            if not keys:
                continue

            # Rate limiting: esperar entre llamadas al mismo proveedor
            last_call = self._last_call_time.get(provider["name"], 0)
            time_since_last = time.time() - last_call
            if time_since_last < self.delay_between_calls:
                time.sleep(self.delay_between_calls - time_since_last)

            for api_key in keys:
                for attempt in range(self.max_retries):
                    try:
                        if provider["format"] == "gemini":
                            result = self._call_gemini_format(
                                provider["url"], api_key, provider["model"],
                                messages, temperature, max_tokens
                            )
                        elif provider["format"] == "vertex":
                            result = self._call_vertex_format(
                                provider["url"], api_key, provider["model"],
                                messages, temperature, max_tokens
                            )
                        else:
                            result = self._call_openai_format(
                                provider["url"], api_key, provider["model"],
                                messages, temperature, max_tokens
                            )

                        content = self._extract_content(provider["name"], result)
                        self.active_provider = provider["name"]
                        elapsed = time.time() - start_time

                        # Reset circuit breaker al tener exito
                        self._consecutive_failures[provider["name"]] = 0
                        # Registrar metricas
                        self._metrics["calls"][provider["name"]] = self._metrics["calls"].get(provider["name"], 0) + 1
                        self._metrics["total_time"][provider["name"]] = self._metrics["total_time"].get(provider["name"], 0) + elapsed

                        return {
                            "success": True,
                            "content": content,
                            "provider": provider["name"],
                            "model": provider["model"],
                            "elapsed_seconds": round(elapsed, 2),
                            "raw_response": result,
                            "error": None
                        }

                    except urllib.error.HTTPError as e:
                        body = e.read().decode("utf-8") if hasattr(e, 'read') else ""
                        last_error = f"{provider['name']} HTTP {e.code}: {body[:200]}"
                        if e.code in (401, 403):
                            break  # Key inválida, probar siguiente key
                        if e.code == 429:
                            # Rate limit: backoff exponencial
                            wait = min(2 ** attempt, 30)
                            print(f"    [RATE LIMIT {provider['name']}] esperando {wait}s...")
                            time.sleep(wait)
                        else:
                            # Backoff exponencial para otros errores HTTP
                            wait = min(2 ** attempt, 10)
                            time.sleep(wait)
                        # Registrar fallo para circuit breaker
                        self._consecutive_failures[provider["name"]] = self._consecutive_failures.get(provider["name"], 0) + 1

                    except Exception as e:
                        last_error = f"{provider['name']}: {str(e)[:200]}"
                        wait = min(2 ** attempt, 10)
                        time.sleep(wait)
                        self._consecutive_failures[provider["name"]] = self._consecutive_failures.get(provider["name"], 0) + 1

        # Ningún proveedor funcionó
        total_elapsed = time.time() - start_time
        return {
            "success": False,
            "content": "",
            "provider": None,
            "model": None,
            "elapsed_seconds": round(total_elapsed, 2),
            "raw_response": None,
            "error": f"Todos los proveedores fallaron. Último error: {last_error}"
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Devuelve metricas de uso del router."""
        result = {}
        for name in self._metrics["calls"]:
            calls = self._metrics["calls"][name]
            total_time = self._metrics["total_time"][name]
            result[name] = {
                "calls": calls,
                "total_time": round(total_time, 2),
                "avg_time": round(total_time / calls, 2) if calls > 0 else 0,
                "failures": self._consecutive_failures.get(name, 0)
            }
        return result

    def chat_json(self, user_prompt: str, system: str = "",
                  temperature: float = 0.2, max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Envía un prompt y espera respuesta JSON parseable.
        Incluye instrucciones JSON en el system prompt automáticamente.
        """
        json_system = system + "\n\nResponde ÚNICAMENTE con un objeto JSON válido. "
        json_system += "No incluyas markdown, explicaciones ni texto fuera del JSON."

        result = self.chat(user_prompt, json_system, temperature, max_tokens)

        if not result["success"]:
            return result

        content = result["content"].strip()
        # Limpiar markdown de código si existe
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        try:
            parsed = json.loads(content)
            result["parsed_json"] = parsed
        except json.JSONDecodeError as e:
            result["parsed_json"] = None
            result["json_error"] = str(e)

        return result


# --- CLI de prueba ---
if __name__ == "__main__":
    print("=" * 60)
    print("   ALEXANDRIA LLM ROUTER — Test de conectividad")
    print("=" * 60)

    router = LLMRouter()

    # Verificar qué proveedores están disponibles
    print("\nProveedores disponibles:")
    for p in router._providers:
        keys = router._get_available_keys(p)
        status = f"✅ {len(keys)} key(s)" if keys else "❌ Sin claves válidas"
        print(f"  {p['name']:<12} → {status}")

    print("\nPrueba de chat:")
    result = router.chat(
        "Responde en español: ¿Qué es la resiliencia en 2 oraciones?",
        system="Eres un experto en psicología positiva."
    )

    if result["success"]:
        print(f"\n✅ Éxito con {result['provider']} ({result['model']})")
        print(f"Respuesta: {result['content'][:300]}...")
    else:
        print(f"\n❌ Error: {result['error']}")
