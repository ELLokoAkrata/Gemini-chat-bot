import streamlit as st
from google import genai
from PIL import Image
import io
import traceback

from src.config import MODEL_ID, SAFETY_CONFIG

def initialize_genai_client():
    """
    Inicializa y retorna el cliente de Google Generative AI.
    """
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    return genai.Client(api_key=GOOGLE_API_KEY)

def generate_image_from_prompt(client, prompt: str, original_image: Image.Image = None):
    """
    Genera una imagen a partir de un prompt y una imagen original opcional.
    Retorna un objeto Image de Pillow o None si falla.
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
        
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents,
            config=SAFETY_CONFIG
        )
        
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
            return None
            
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                image_data = part.inline_data.data
                return Image.open(io.BytesIO(image_data))

    except Exception as e:
        placeholder.empty()
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
