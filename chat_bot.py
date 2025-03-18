import os
import time
import io
import uuid
import base64
from datetime import datetime
from PIL import Image

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google import genai
from google.genai import types

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
MODEL_ID = 'gemini-2.0-flash-exp-image-generation'  # Volvemos al modelo original
TEMPERATURE = 1.0
TOP_P = 0.95
TOP_K = 40
MAX_OUTPUT_TOKENS = 8192

# Configuración de seguridad sin censura - Ahora se usará en config
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

def save_binary_file(file_name, data):
    """Guarda datos binarios en un archivo."""
    with open(file_name, "wb") as f:
        f.write(data)

def display_image_with_expander(image, caption, key_prefix, is_preview=True):
    """Muestra una imagen centrada en tamaño compacto para ahorrar espacio"""
    # Centrar la imagen con un contenedor y CSS
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(image, caption=caption, width=300)

def generate_and_save_image(prompt: str, username: str, is_modified: bool = False, original_image=None):
    """Genera una imagen a partir de un prompt, la guarda localmente y la sube a Firebase Storage."""
    # Generar nombre de archivo único
    output_filename = generate_filename(username, is_modified)
    
    # Centrar y limitar el ancho del mensaje de información
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(
            """
            <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(0, 100, 0, 0.2); padding: 10px; border-radius: 5px;">
                🌀 Generando imagen, aguanta la energía del caos...
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    try:
        # Preparamos el contenido para la API
        if is_modified and original_image:
            # Para modificación, enviamos la imagen original y el prompt
            contents = [
                prompt,  # Primero el texto según el ejemplo
                original_image  # Luego la imagen
            ]
        else:
            # Para generación, solo enviamos el prompt
            contents = prompt
        
        # Generar imagen con el prompt usando la API correcta
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=contents,
            config=SAFETY_CONFIG  # Usamos la configuración como config
        )
        
        # Verificar si la respuesta es válida
        if not response or not response.candidates:
            # Centrar y limitar el ancho del mensaje de error
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown(
                    """
                    <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                        💀 La respuesta del modelo está vacía
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            return None
            
        # Verificar si hay contenido en la respuesta
        if not response.candidates[0].content:
            # Centrar y limitar el ancho del mensaje de error
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                st.markdown(
                    """
                    <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                        💀 No hay contenido en la respuesta del modelo
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
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
                
                # Usar la función simplificada para mostrar la imagen
                display_image_with_expander(
                    image=image, 
                    caption=f"Prompt: {prompt}", 
                    key_prefix=f"img_{output_filename}"
                )
                
                # Guardar información en Firestore
                image_data = {
                    "username": username,
                    "prompt": prompt,
                    "timestamp": datetime.now(),
                    "filename": output_filename,
                    "is_modified": is_modified,
                    "original_prompt": None if is_modified else prompt
                }
                
                # Procesar y mostrar el texto generado si existe
                generated_text = []
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        generated_text.append(part.text)
                
                if generated_text:
                    # Container para reducir el ancho del texto
                    with st.container():
                        st.markdown("### 📝 Texto generado")
                        for text in generated_text:
                            # Limitar el ancho del texto usando CSS más restrictivo
                            st.markdown(
                                f"""
                                <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto;">
                                    <em>{text}</em>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                    
                    # Agregar el texto generado a los datos de Firestore
                    image_data["generated_text"] = generated_text
                
                db.collection("imagenes").document(output_filename).set(image_data)
                
                # Subir a Firebase Storage en la carpeta "gemini images"
                remote_path = f"gemini images/{output_filename}"
                upload_image_to_storage(output_filename, remote_path)
                
                # Guardar la imagen en memoria en session_state
                if not is_modified:
                    st.session_state["last_generated_image"] = {
                        "filename": output_filename,
                        "prompt": prompt,
                        "image": image  # Guardamos la imagen en memoria
                    }
                else:
                    st.session_state["last_modified_image"] = {
                        "filename": output_filename,
                        "prompt": prompt,
                        "image": image  # Guardamos la imagen en memoria
                    }
                
                return image
            elif hasattr(part, 'text') and part.text:
                st.write(part.text)
    except Exception as e:
        # Centrar y limitar el ancho del mensaje de error
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown(
                f"""
                <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                    💀 ERROR en la generación de imagen: {str(e)}
                </div>
                """, 
                unsafe_allow_html=True
            )
            import traceback
            st.markdown(
                f"""
                <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.1); padding: 10px; border-radius: 5px; font-size: 0.8em;">
                    Detalles del error:<br>{traceback.format_exc().replace(chr(10), '<br>')}
                </div>
                """, 
                unsafe_allow_html=True
            )
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
    /* Estilo para limitar el ancho de los inputs */
    .stTextInput input, .stTextArea textarea {
        max-width: 500px !important;
        margin: 0 auto;
    }
    /* Ajustar el área de texto para que crezca verticalmente */
    .stTextArea textarea {
        resize: vertical !important;
        min-height: 100px !important;
        overflow-y: auto !important;
    }
    /* Estilo para centrar los botones */
    .stButton button {
        margin: 0 auto;
        display: block;
    }
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
    
    # Tabs para diferentes funcionalidades
    tab1, tab2 = st.tabs(["🎨 Generar Imagen", "🔄 Modificar Imagen"])
    
    with tab1:
        # Mostrar ejemplos de prompts
        st.markdown("<h3 style='text-align: center;'>🌟 Ejemplos de Prompts:</h3>", unsafe_allow_html=True)
        
        # Centrar y ajustar los botones de ejemplo
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            for prompt in EXAMPLE_PROMPTS:
                if st.button(f"Usar: {prompt}"):
                    st.session_state["selected_prompt"] = prompt
        
        # Centrar el formulario
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            with st.form("image_generation_form"):
                prompt_input = st.text_area("💡 Ingresa el prompt para generar imagen:", 
                                          value=st.session_state.get("selected_prompt", ""),
                                          height=100)
                submit_gen = st.form_submit_button("Generar Imagen")
        
        # Generación de imagen (FUERA del formulario)
        if submit_gen and prompt_input:
            generated_image = generate_and_save_image(prompt_input, username)
            
            # Guardar en session_state para poder modificarla después
            if generated_image:
                st.session_state["current_generated_image"] = True
        
        # Mostrar opción de modificación inmediata (FUERA del formulario)
        if st.session_state.get("current_generated_image", False) and "last_generated_image" in st.session_state:
            st.markdown("---")
            st.markdown("<h3 style='text-align: center;'>🔄 ¿Quieres modificar esta imagen?</h3>", unsafe_allow_html=True)
            
            # Formulario de modificación separado y centrado
            col1, col2, col3 = st.columns([1, 3, 1])
            with col2:
                with st.form("immediate_modification_form"):
                    mod_prompt = st.text_area("💡 Ingresa el prompt para modificar:", 
                                            value=st.session_state.get("selected_mod_prompt", ""),
                                            height=100)
                    submit_immediate_mod = st.form_submit_button("Modificar Imagen")
            
            # Procesamiento de la modificación (FUERA del formulario)
            if submit_immediate_mod:
                try:
                    last_image = st.session_state["last_generated_image"]
                    if "image" not in last_image:
                        # Centrar y limitar el ancho del mensaje de error
                        col1, col2, col3 = st.columns([1, 3, 1])
                        with col2:
                            st.markdown(
                                """
                                <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                                    💀 Error: La imagen original no está disponible en memoria
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        st.stop()
                    
                    original_image = last_image["image"]
                    
                    # Generar imagen modificada
                    mod_image = generate_and_save_image(
                        prompt=mod_prompt,
                        username=username,
                        is_modified=True,
                        original_image=original_image
                    )
                    
                except Exception as e:
                    # Centrar y limitar el ancho del mensaje de error
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        st.markdown(
                            f"""
                            <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                                💀 ERROR al modificar la imagen: {str(e)}
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        import traceback
                        st.markdown(
                            f"""
                            <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.1); padding: 10px; border-radius: 5px; font-size: 0.8em;">
                                Detalles del error:<br>{traceback.format_exc().replace(chr(10), '<br>')}
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
    
    with tab2:
        st.markdown("<h3 style='text-align: center;'>🌟 Sube tu imagen para modificarla</h3>", unsafe_allow_html=True)
        
        # Centrar el uploader
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            uploaded_file = st.file_uploader("Sube una imagen para modificarla", type=["png", "jpg", "jpeg"])
        
        if uploaded_file is not None:
            # Convertir el archivo subido a imagen PIL
            image = Image.open(uploaded_file)
            
            # Usar la función para mostrar la imagen centrada
            display_image_with_expander(
                image=image, 
                caption="Imagen subida", 
                key_prefix="uploaded_img"
            )
            
            # Guardar la imagen en session_state para modificaciones
            st.session_state["uploaded_image"] = image
        
        # Mostrar ejemplos de prompts de modificación
        st.markdown("<h3 style='text-align: center;'>🌟 Ejemplos de Modificación:</h3>", unsafe_allow_html=True)
        
        # Centrar los botones de ejemplos de modificación
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            for prompt in EXAMPLE_MOD_PROMPTS:
                if st.button(f"Usar: {prompt}", key=f"mod_{prompt}"):
                    st.session_state["selected_mod_prompt"] = prompt
        
        # Centrar el formulario de modificación
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            with st.form("image_modification_form"):
                mod_prompt = st.text_area("💡 Ingresa el prompt para modificar la imagen:", 
                                        value=st.session_state.get("selected_mod_prompt", ""),
                                        height=100)
                submit_mod = st.form_submit_button("Modificar Imagen")
        
        # Procesamiento de la modificación (FUERA del formulario)
        if submit_mod:
            try:
                # Usar la imagen subida o la última generada
                if "uploaded_image" in st.session_state:
                    original_image = st.session_state["uploaded_image"]
                elif "last_generated_image" in st.session_state:
                    last_image = st.session_state["last_generated_image"]
                    if "image" not in last_image:
                        # Centrar y limitar el ancho del mensaje de error
                        col1, col2, col3 = st.columns([1, 3, 1])
                        with col2:
                            st.markdown(
                                """
                                <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                                    💀 Error: La imagen original no está disponible en memoria
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        st.stop()
                    original_image = last_image["image"]
                else:
                    # Centrar y limitar el ancho del mensaje de error
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col2:
                        st.markdown(
                            """
                            <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                                💀 No hay imagen disponible para modificar. Sube una imagen o genera una nueva.
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    st.stop()
                
                # Generar imagen modificada
                mod_image = generate_and_save_image(
                    prompt=mod_prompt,
                    username=username,
                    is_modified=True,
                    original_image=original_image
                )
                
            except Exception as e:
                # Centrar y limitar el ancho del mensaje de error
                col1, col2, col3 = st.columns([1, 3, 1])
                with col2:
                    st.markdown(
                        f"""
                        <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.2); padding: 10px; border-radius: 5px;">
                            💀 ERROR al modificar la imagen: {str(e)}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                    import traceback
                    st.markdown(
                        f"""
                        <div style="max-width: 450px; word-wrap: break-word; white-space: normal; margin: 0 auto; text-align: center; background-color: rgba(180, 0, 0, 0.1); padding: 10px; border-radius: 5px; font-size: 0.8em;">
                            Detalles del error:<br>{traceback.format_exc().replace(chr(10), '<br>')}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
    
    # Botones de descarga (fuera de los tabs)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.write("")  # Espaciador
        
    with col2:
        # Centrar los botones de descarga
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
    
    with col3:
        st.write("")  # Espaciador
else:
    st.markdown("""
    ## 🌌 GUÍA DE INICIACIÓN
    1. Ingresa tu nombre de poder en la barra lateral (máximo 8 caracteres).
    2. Una vez dentro, escribe un prompt para generar una imagen o usa uno de los ejemplos.
    3. (Opcional) Modifica la imagen con un nuevo prompt o usa uno de los ejemplos.
    4. Tambien puedes subir una imagen y editarla (de preferencia que sea de 1024 * 1024)
    
    ⚠️ ADVERTENCIA: Este generador funciona en el plan free de GoogleAI por lo cual el uso está bastante limitado.
                
    Código:https://github.com/Ellokoakarata/Gemini-chat-bot 
    """)
    
st.markdown("---")
st.caption("Ψ Sistema EsquizoAI v2.3.5 | Realidad: Beta")
