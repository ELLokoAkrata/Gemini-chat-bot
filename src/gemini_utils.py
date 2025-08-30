import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
import io
import traceback
import logging

from src.config import MODEL_ID, SAFETY_CONFIG, MAX_OUTPUT_TOKENS

def initialize_genai_client():
    """
    Inicializa y retorna el cliente de Google Generative AI.
    """
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    return genai.Client(api_key=GOOGLE_API_KEY)

def generate_image_from_prompt(
    client, 
    prompt: str, 
    original_image: Image.Image = None,
    temperature: float = 1.0,
    top_p: float = 0.95,
    top_k: int = 40
):
    """
    Genera una imagen a partir de un prompt, con parámetros de generación dinámicos.
    """
    placeholder = st.empty()
    placeholder.markdown(
        """
        <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(0, 100, 0, 0.2); padding: 10px; border-radius: 5px;">
            🌀 Generando imagen, aguanta la energía del caos...
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    try:
        contents = [prompt, original_image] if original_image else [prompt]
        
        # Construir el objeto de configuración UNIFICADO y PLANO
        dynamic_config = types.GenerateContentConfig(
            # Parámetros de generación directamente en el nivel superior
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            
            # Configuración de seguridad al mismo nivel
            safety_settings=SAFETY_CONFIG.safety_settings,
            response_modalities=SAFETY_CONFIG.response_modalities
        )

        logging.info(f"Enviando petición a Gemini. Temp: {temperature}, Top-P: {top_p}, Top-K: {top_k}")
        logging.info(f"Prompt: '{prompt[:120]}...'")

        # Llamar a la API de la forma correcta, con el config unificado
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents,
            config=dynamic_config
        )
        
        logging.info("Respuesta recibida exitosamente de la API de Gemini.")
        
        placeholder.empty()

        if not response or not response.candidates:
            st.markdown(
                """
                <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                    💀 La respuesta del modelo está vacía. Intenta de nuevo o cambia el prompt.
                </div>
                """, 
                unsafe_allow_html=True
            )
            logging.warning("La respuesta de la API estaba vacía o no contenía candidatos.")
            return None
            
        if not response.candidates[0].content or not response.candidates[0].content.parts:
            st.markdown(
                """
                <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                    💀 No hay contenido en la respuesta del modelo.
                </div>
                """, 
                unsafe_allow_html=True
            )
            logging.warning("La respuesta de la API no contenía 'parts' con datos de imagen.")
            return None
            
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                logging.info("Imagen extraída correctamente de la respuesta.")
                return Image.open(io.BytesIO(image_data))

    except Exception as e:
        placeholder.empty()
        logging.error(f"Error durante la llamada a la API de Gemini: {e}", exc_info=True)
        st.markdown(
            f"""
            <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                💀 ERROR en la generación de imagen: {str(e)}
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.1); padding: 10px; border-radius: 5px; font-size: 0.8em;">
                Detalles del error:<br>{traceback.format_exc().replace(chr(10), '<br>')}
            </div>
            """, 
            unsafe_allow_html=True
        )
    return None
