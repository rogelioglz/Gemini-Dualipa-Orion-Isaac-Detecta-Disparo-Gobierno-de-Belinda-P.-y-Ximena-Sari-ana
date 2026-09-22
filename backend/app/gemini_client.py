import os
import json
import logging

env_key = os.getenv("GEMINI_API_KEY", "")
SIMULATE = os.getenv("SIMULATE_GEMINI", "true").lower() == "true" or not env_key

logger = logging.getLogger(__name__)


def generate_text_report(prompt: str) -> str:
    """Wrapper that either calls real Gemini client or returns simulated response."""
    if SIMULATE:
        logger.info("SIMULATE_GEMINI enabled or no API key found — returning simulated report")
        return "# Reporte (Simulado)\n\nResumen ejecutivo (simulado):\nSe detectó un evento compatible con disparo. Confianza alta.\n\n## Hallazgos técnicos\n- Patrón: ballistic_impulse\n\n## Recomendaciones\n- Revisar cámaras y coordenadas.\n"

    # If a real client is available, import lazily to avoid dependency at import time
    try:
        from google import generativeai as genai
        genai.configure(api_key=env_key)
        model = genai.GenerativeModel(os.getenv("MODEL_NAME", "gemini-2.0-flash"))
        response = model.generate_content(prompt, generation_config={"temperature": 0.3, "max_output_tokens": 1024})
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini: {e}")
        return "# Reporte (Fallback)\n\nError al llamar a Gemini. Revisa logs."
