import os
import time
import io
import uuid
from datetime import datetime
from PIL import Image

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google import genai
from google.genai.types import GenerateContentConfig

# --------------------- Firebase & Generative AI Initialization ---------------------

# Acceder a las credenciales de Firebase almacenadas como secreto
firebase_secrets = st.secrets["firebase"]

# Crear objeto de credenciales con los secretos
cred = credentials.Certificate({
    "type": firebase_secrets["type"],
    "project_id": firebase_secrets["project_id"],
    "private_key_id": firebase_secrets["private_key_id"],
    "private_key": firebase_secrets["private_key"].replace('\\n', '\n'),
    "client_email": firebase_secrets["client_email"],
    "client_id": firebase_secrets["client_id"],
    "auth_uri": firebase_secrets["auth_uri"],
    "token_uri": firebase_secrets["token_uri"],
    "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
})

# Inicializar Firebase (incluyendo Storage: asegúrate de tener "storageBucket" en tus secretos)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "storageBucket": firebase_secrets.get("storageBucket")
    })

# Firestore (si lo necesitas para el login)
db = firestore.client()

# Configurar Google Generative AI con la API Key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)

# Configuración del modelo de Generative AI
model_id = 'gemini-2.0-flash-exp'
harassment_setting = 'block_none'
temperature = 1.0
top_p = 1
top_k = 1
max_output_tokens = 4096

# --------------------- Funciones Auxiliares ---------------------

def upload_image_to_storage(local_path: str, remote_path: str):
    """Sube la imagen a Firebase Storage en la ruta especificada."""
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    st.success(f"Imagen subida a Storage: {remote_path}")

def generate_and_save_image(prompt: str, output_filename: str):
    """Genera una imagen a partir de un prompt, la guarda localmente y la sube a Firebase Storage."""
    # Configuración para respuesta en imagen y texto
    config = GenerateContentConfig(response_modalities=['Text', 'Image'])
    
    st.info("🌀 Generando imagen, aguanta la energía del caos...")
    try:
        # Generar imagen con el prompt usando la nueva API
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )
        
        # Iterar sobre las partes de la respuesta
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                # Convertir los datos binarios a imagen usando PIL
                image_data = part.inline_data.data
                image = Image.open(io.BytesIO(image_data))
                
                # Guardar la imagen localmente
                image.save(output_filename)
                st.image(image, caption=f"Imagen generada para: {prompt}")
                
                # Subir a Firebase Storage en la carpeta "gemini images"
                remote_path = f"gemini images/{output_filename}"
                upload_image_to_storage(output_filename, remote_path)
                return image
            else:
                st.write(part.text)
    except Exception as e:
        st.error(f"💀 ERROR en la generación de imagen: {str(e)}")
    return None

# --------------------- Interfaz Streamlit ---------------------

# Configurar la página
st.set_page_config(
    page_title="🧠 Ψ-Psycho Image Generator",
    page_icon="🖼️",
    layout="wide"
)

# Estilo oscuro y futurista
st.markdown("""
    <style>
    .stApp { background-color: black; color: #00ff00; }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 Ψ-Psycho Image Generator: Portal de Imágenes Fragmentadas")

# Sidebar para login (si lo requieres)
with st.sidebar:
    st.header("💊 Control Neural")
    st.markdown("---")
    if st.session_state.get("logged_in", False):
        st.write(f"🎭 Viajero: {st.session_state.get('user_name', 'Anónimo')}")
        st.write(f"🔮 ID: {st.session_state.get('user_uuid', '')[:8]}...")
        if st.button("⚡ Cerrar Portal"):
            st.session_state.logged_in = False
            st.rerun()
    else:
        with st.form("login"):
            user_name = st.text_input("🌀 Tu Nombre de Poder")
            if st.form_submit_button("🎯 Iniciar Viaje"):
                if user_name:
                    user_query = db.collection("usuarios").where("nombre", "==", user_name).get()
                    if user_query:
                        user_data = user_query[0].to_dict()
                        st.session_state["user_uuid"] = user_data["user_uuid"]
                    else:
                        new_uuid = str(uuid.uuid4())
                        db.collection("usuarios").document(new_uuid).set({
                            "nombre": user_name,
                            "user_uuid": new_uuid
                        })
                        st.session_state["user_uuid"] = new_uuid
                    st.session_state["user_name"] = user_name
                    st.session_state["logged_in"] = True
                    st.rerun()

# Área principal: Solo se muestra si el usuario está logueado
if st.session_state.get("logged_in", False):
    st.header("Genera tu imagen al éter")
    
    with st.form("image_generation_form"):
        prompt_input = st.text_input("💡 Ingresa el prompt para generar imagen:")
        submit_gen = st.form_submit_button("Generar Imagen")
        
        if submit_gen and prompt_input:
            # Genera la imagen y la guarda localmente como "generated_image.png"
            generated_image = generate_and_save_image(prompt_input, "generated_image.png")
    
    st.markdown("---")
    st.header("Modificar imagen generada (opcional)")
    
    with st.form("image_modification_form"):
        mod_prompt = st.text_input("💡 Ingresa el prompt para modificar la imagen:", value="Make the image red")
        submit_mod = st.form_submit_button("Modificar Imagen")
        
        if submit_mod and os.path.exists("generated_image.png"):
            try:
                # Abrir la imagen previamente generada
                original_image = Image.open("generated_image.png")
                # Configuración para modificación: enviar prompt y la imagen original
                config = GenerateContentConfig(response_modalities=['Text', 'Image'])
                
                st.info("🌀 Modificando imagen, conectando al glitch...")
                # Usar la nueva API para modificar la imagen
                response = client.models.generate_content(
                    model=model_id,
                    contents=[mod_prompt, original_image],
                    config=config
                )
                
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        mod_image_data = part.inline_data.data
                        mod_image = Image.open(io.BytesIO(mod_image_data))
                        
                        # Guardar la imagen modificada
                        mod_filename = "modified_image.png"
                        mod_image.save(mod_filename)
                        st.image(mod_image, caption="Imagen modificada")
                        
                        # Subir a Firebase Storage en "gemini images"
                        remote_mod_path = f"gemini images/{mod_filename}"
                        upload_image_to_storage(mod_filename, remote_mod_path)
                        break
                    else:
                        st.write(part.text)
            except Exception as e:
                st.error(f"💀 ERROR al modificar la imagen: {str(e)}")
        elif submit_mod:
            st.error("No se encontró la imagen original. Primero genera una imagen.")
else:
    st.markdown("""
    ## 🌌 GUÍA DE INICIACIÓN
    1. Ingresa tu nombre de poder en la barra lateral.
    2. Una vez dentro, escribe un prompt para generar una imagen.
    3. (Opcional) Modifica la imagen con un nuevo prompt.
    
    ⚠️ ADVERTENCIA: Este generador puede invocar imágenes surrealistas y perturbadoras.
    """)
    
st.markdown("---")
st.caption("Ψ Sistema EsquizoAI v2.3.5 | Realidad: Beta")
