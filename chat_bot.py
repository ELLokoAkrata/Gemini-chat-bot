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

# Ejemplos de prompts
EXAMPLE_PROMPTS = [
    "Create a surreal horror image of an psycho anarcho-punk",
    "Generate a cyberpunk cityscape with neon lights and flying cars",
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

# --------------------- Funciones Auxiliares ---------------------

def get_timestamp():
    """Retorna un timestamp formateado para nombres de archivo"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_filename(username: str, is_modified: bool = False):
    """Genera un nombre de archivo único basado en el usuario y timestamp"""
    timestamp = get_timestamp()
    prefix = "mod_" if is_modified else "gen_"
    return f"{prefix}{username}_{timestamp}.png"

def upload_image_to_storage(local_path: str, remote_path: str):
    """Sube la imagen a Firebase Storage en la ruta especificada."""
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    st.success(f"Imagen subida a Storage: {remote_path}")

def generate_and_save_image(prompt: str, username: str, is_modified: bool = False):
    """Genera una imagen a partir de un prompt, la guarda localmente y la sube a Firebase Storage."""
    # Configuración para respuesta en imagen y texto
    config = GenerateContentConfig(response_modalities=['Text', 'Image'])
    
    # Generar nombre de archivo único
    output_filename = generate_filename(username, is_modified)
    
    st.info("🌀 Generando imagen, aguanta la energía del caos...")
    try:
        # Generar imagen con el prompt usando la nueva API
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=config
        )
        
        # Verificar si la respuesta es válida
        if not response or not response.candidates:
            st.error("💀 La respuesta del modelo está vacía")
            return None
            
        # Verificar si hay contenido en la respuesta
        if not response.candidates[0].content:
            st.error("💀 No hay contenido en la respuesta del modelo")
            return None
            
        # Iterar sobre las partes de la respuesta
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                # Convertir los datos binarios a imagen usando PIL
                image_data = part.inline_data.data
                image = Image.open(io.BytesIO(image_data))
                
                # Guardar la imagen localmente
                image.save(output_filename)
                
                # Mostrar la imagen con su descripción
                st.markdown(f"### 🖼️ Imagen {'Modificada' if is_modified else 'Generada'}")
                st.image(image, caption=f"Prompt: {prompt}")
                
                # Guardar información en Firestore
                image_data = {
                    "username": username,
                    "prompt": prompt,
                    "timestamp": datetime.now(),
                    "filename": output_filename,
                    "is_modified": is_modified,
                    "original_prompt": prompt if not is_modified else None
                }
                db.collection("imagenes").document(output_filename).set(image_data)
                
                # Subir a Firebase Storage en la carpeta "gemini images"
                remote_path = f"gemini images/{output_filename}"
                upload_image_to_storage(output_filename, remote_path)
                return image
            else:
                st.write(part.text)
    except Exception as e:
        st.error(f"💀 ERROR en la generación de imagen: {str(e)}")
        import traceback
        st.error(f"Detalles del error:\n{traceback.format_exc()}")
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

st.title("🧠 Ψ-Psycho Image Generator: Portal de Imágenes Artificiales")

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
            user_name = st.text_input("🌀 Tu Nombre de Poder (máx 8 caracteres)")
            if st.form_submit_button("🎯 Iniciar Viaje"):
                if user_name:
                    if len(user_name) > 8:
                        st.error("💀 El nombre no puede tener más de 8 caracteres")
                    else:
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
    username = st.session_state.get("user_name", "anon")
    
    st.header("Genera tu imagen al éter")
    
    # Mostrar ejemplos de prompts
    st.markdown("### 🌟 Ejemplos de Prompts:")
    for prompt in EXAMPLE_PROMPTS:
        if st.button(f"Usar: {prompt}"):
            st.session_state["selected_prompt"] = prompt
    
    with st.form("image_generation_form"):
        prompt_input = st.text_input("💡 Ingresa el prompt para generar imagen:", 
                                   value=st.session_state.get("selected_prompt", ""))
        submit_gen = st.form_submit_button("Generar Imagen")
        
        if submit_gen and prompt_input:
            # Genera la imagen y la guarda localmente
            generated_image = generate_and_save_image(prompt_input, username)
            if generated_image:
                st.session_state["last_generated_image"] = {
                    "filename": generate_filename(username),
                    "prompt": prompt_input
                }
    
    # Botón de descarga para la imagen generada (fuera del formulario)
    if "last_generated_image" in st.session_state:
        last_image = st.session_state["last_generated_image"]
        if os.path.exists(last_image["filename"]):
            with open(last_image["filename"], "rb") as file:
                st.download_button(
                    label="📥 Descargar imagen generada",
                    data=file,
                    file_name=last_image["filename"],
                    mime="image/png"
                )
    
    st.markdown("---")
    st.header("Modificar imagen generada (opcional)")
    
    # Mostrar ejemplos de prompts de modificación
    st.markdown("### 🌟 Ejemplos de Modificación:")
    for prompt in EXAMPLE_MOD_PROMPTS:
        if st.button(f"Usar: {prompt}", key=f"mod_{prompt}"):
            st.session_state["selected_mod_prompt"] = prompt
    
    with st.form("image_modification_form"):
        mod_prompt = st.text_input("💡 Ingresa el prompt para modificar la imagen:", 
                                 value=st.session_state.get("selected_mod_prompt", "Make the image red"))
        submit_mod = st.form_submit_button("Modificar Imagen")
        
        if submit_mod and "last_generated_image" in st.session_state:
            try:
                last_image = st.session_state["last_generated_image"]
                # Abrir la imagen previamente generada
                original_image = Image.open(last_image["filename"])
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
                        mod_filename = generate_filename(username, is_modified=True)
                        mod_image.save(mod_filename)
                        
                        # Mostrar la imagen modificada con su descripción
                        st.markdown("### 🖼️ Imagen Modificada")
                        st.image(mod_image, caption=f"Prompt de modificación: {mod_prompt}")
                        
                        # Guardar la información de la imagen modificada
                        st.session_state["last_modified_image"] = {
                            "filename": mod_filename,
                            "prompt": mod_prompt
                        }
                        
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
    
    # Botón de descarga para la imagen modificada (fuera del formulario)
    if "last_modified_image" in st.session_state:
        last_mod_image = st.session_state["last_modified_image"]
        if os.path.exists(last_mod_image["filename"]):
            with open(last_mod_image["filename"], "rb") as file:
                st.download_button(
                    label="📥 Descargar imagen modificada",
                    data=file,
                    file_name=last_mod_image["filename"],
                    mime="image/png"
                )
else:
    st.markdown("""
    ## 🌌 GUÍA DE INICIACIÓN
    1. Ingresa tu nombre de poder en la barra lateral (máximo 8 caracteres).
    2. Una vez dentro, escribe un prompt para generar una imagen o usa uno de los ejemplos.
    3. (Opcional) Modifica la imagen con un nuevo prompt o usa uno de los ejemplos.
    
    ⚠️ ADVERTENCIA: Este generador puede invocar imágenes surrealistas y perturbadoras.
    """)
    
st.markdown("---")
st.caption("Ψ Sistema EsquizoAI v2.3.5 | Realidad: Beta")
