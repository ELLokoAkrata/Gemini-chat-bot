from google.genai import types

# --- Storage Configuration ---
STORAGE_ROOT_FOLDER = "psycho_generator_images"

# --- Generative AI Model Configuration ---
MODEL_ID = 'gemini-2.5-flash-image-preview'
TEMPERATURE = 1.0
TOP_P = 0.95
TOP_K = 40
MAX_OUTPUT_TOKENS = 8192

# --- Safety Configuration (No Censorship) ---
SAFETY_CONFIG = types.GenerateContentConfig(
    safety_settings=[
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="OFF"
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_CIVIC_INTEGRITY",
            threshold="OFF"
        )
    ],
    response_modalities=['Text', 'Image']
)

# --- Example Prompts ---
EXAMPLE_PROMPTS = [
    "Create a surreal horror image of an psycho anarcho-punk",
    "A psycho punk monster with leather jacket with anarcho-punk patches and big head and several eyes in psychedelic acid  trip",
    "Create a psychedelic portrait of a digital shaman",
    "Generate a dystopian future with AI overlords",
    "Create a glitch art representation of human consciousness"
]

EXAMPLE_MOD_PROMPTS = [
    "Make the hair green and add neon effects",
    "Add a glitch effect and make it more surreal",
    "Transform it into a cyberpunk style",
    "Add psychedelic patterns and colors",
    "Make it more dystopian and dark"
]

# --- Rate Limiting Configuration ---
MAX_IMAGES_PER_DAY = 200 # Límite global diario
USER_COOLDOWN_SECONDS = 15 # Tiempo de espera para un usuario entre peticiones

# --- Logging Configuration ---
import logging
import sys

def setup_logging():
    """Configura el logging básico para la aplicación."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout
    )
