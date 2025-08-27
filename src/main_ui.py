import streamlit as st
from PIL import Image
import os
from datetime import datetime

from src.config import STORAGE_ROOT_FOLDER
from src.firebase_utils import initialize_firebase, upload_image_to_storage, save_image_metadata
from src.gemini_utils import initialize_genai_client, generate_image_from_prompt
from src.prompt_engineering import engineer_prompt, EMOJI_GRIMOIRE
from src.ui_components import (
    display_image_with_expander,
    generate_filename,
    show_login_form,
    show_user_info,
    show_welcome_message
)

def setup_page():
    """Configura la página de Streamlit."""
    st.set_page_config(
        page_title="🧠 Akelarre Generativo",
        page_icon="🔥",
        layout="wide"
    )
    st.markdown("""
        <style>
        .stApp { background-color: black; color: #00ff00; }
        .stTextArea textarea {
            resize: vertical !important;
            min-height: 80px !important;
            overflow-y: auto !important;
        }
        .stButton>button {
            background-color: #111;
            color: #00ff00;
            border: 1px solid #00ff00;
            border-radius: 10px;
            font-size: 1.5em;
            padding: 5px 10px;
            margin: 5px;
            transition: all 0.3s ease;
            width: 100%;
        }
        .stButton>button:hover {
            box-shadow: 0 0 15px #00ff00;
            transform: scale(1.1);
        }
        h1, h2, h3 {
            text-align: center !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title("🔥 Akelarre Generativo with Psycho-Bot 🔥")
    st.markdown("""
    <p style='text-align: center;'>
    Compas, este es un proyecto de desarrollo de código abierto para navegar por el espacio latente.
    Las instrucciones son simples: usen los símbolos, escriban su visión y dejen que el caos haga el resto.
    </p>
    """, unsafe_allow_html=True)


def handle_image_generation(client, user_prompt, user_uuid):
    """Gestiona la lógica de generación y guardado de una nueva imagen."""
    final_prompt = engineer_prompt(user_prompt)
    generated_image = generate_image_from_prompt(client, final_prompt)
    
    if generated_image:
        output_filename = generate_filename(is_modified=False)
        generated_image.save(output_filename)
        
        st.markdown("<h3 style='text-align: center;'>🖼️ Creación Manifestada</h3>", unsafe_allow_html=True)
        display_image_with_expander(image=generated_image, caption=f"Input: {user_prompt}")
        
        db = initialize_firebase()
        remote_path = f"{STORAGE_ROOT_FOLDER}/{user_uuid}/{output_filename}"
        
        metadata = {
            "user_prompt": user_prompt,
            "final_prompt": final_prompt,
            "timestamp": datetime.now(),
            "storage_path": remote_path,
            "is_modified": False
        }
        save_image_metadata(db, user_uuid, metadata)
        
        upload_image_to_storage(output_filename, remote_path)
        
        st.session_state["last_generated_image"] = {
            "filename": output_filename,
            "prompt": user_prompt,
            "image": generated_image
        }
        st.session_state["current_generated_image"] = True

def handle_image_modification(client, user_prompt, user_uuid, original_image):
    """Gestiona la lógica de modificación y guardado de una imagen."""
    final_prompt = engineer_prompt(user_prompt)
    mod_image = generate_image_from_prompt(client, final_prompt, original_image)

    if mod_image:
        output_filename = generate_filename(is_modified=True)
        mod_image.save(output_filename)
        
        st.markdown("<h3 style='text-align: center;'>🖼️ Transmutación Realizada</h3>", unsafe_allow_html=True)
        display_image_with_expander(image=mod_image, caption=f"Input: {user_prompt}")
        
        db = initialize_firebase()
        remote_path = f"{STORAGE_ROOT_FOLDER}/{user_uuid}/{output_filename}"

        metadata = {
            "user_prompt": user_prompt,
            "final_prompt": final_prompt,
            "timestamp": datetime.now(),
            "storage_path": remote_path,
            "is_modified": True
        }
        save_image_metadata(db, user_uuid, metadata)
        
        upload_image_to_storage(output_filename, remote_path)
        
        st.session_state["last_modified_image"] = {
            "filename": output_filename,
            "prompt": user_prompt,
            "image": mod_image
        }

def draw_emoji_interface(text_area_key: str):
    """Dibuja la interfaz de botones de emojis en dos filas."""
    st.markdown("<h3 style='text-align: center;'>🔮 Invoca con Símbolos:</h3>", unsafe_allow_html=True)
    
    # Inicializar el estado del text_area si no existe
    if text_area_key not in st.session_state:
        st.session_state[text_area_key] = ""

    emoji_list = list(EMOJI_GRIMOIRE.keys())
    half_point = len(emoji_list) // 2
    
    # Primera fila
    cols_1 = st.columns(half_point)
    for i, emoji in enumerate(emoji_list[:half_point]):
        if cols_1[i].button(emoji, key=f"{text_area_key}_{emoji}"):
            st.session_state[text_area_key] += emoji
            
    # Segunda fila
    cols_2 = st.columns(len(emoji_list) - half_point)
    for i, emoji in enumerate(emoji_list[half_point:]):
        if cols_2[i].button(emoji, key=f"{text_area_key}_{emoji}_2"):
            st.session_state[text_area_key] += emoji

def run_app():
    """Función principal que ejecuta la aplicación Streamlit."""
    setup_page()
    db = initialize_firebase()
    client = initialize_genai_client()

    if not st.session_state.get("logged_in", False):
        # --- VISTA DE LOGIN ---
        show_welcome_message()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            show_login_form(db)

    else:
        # --- VISTA PRINCIPAL DE LA APP ---
        with st.sidebar:
            st.header("💊 Control Neural")
            st.markdown("---")
            show_user_info()

        user_uuid = st.session_state.get("user_uuid")
        
        tab1, tab2 = st.tabs(["🎨 Generar", "🔄 Transmutar"])

        with tab1:
            draw_emoji_interface("prompt_input_area_gen")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("image_generation_form"):
                    prompt_input = st.text_area("💡 ...o describe tu visión:", 
                                              key="prompt_input_area_gen")
                    submit_gen = st.form_submit_button("🔥 Generar")
                
                if submit_gen:
                    handle_image_generation(client, prompt_input, user_uuid)
                    st.session_state.prompt_input_area_gen = "" # Limpiar

        with tab2:
            st.markdown("<h3 style='text-align: center;'>🌟 Sube una imagen para alterarla</h3>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
            
            original_image = None
            if uploaded_file is not None:
                original_image = Image.open(uploaded_file)
                display_image_with_expander(image=original_image, caption="Imagen a transmutar")
            elif "last_generated_image" in st.session_state:
                original_image = st.session_state["last_generated_image"]["image"]
                st.markdown("<p style='text-align: center;'>Usando la última imagen generada.</p>", unsafe_allow_html=True)
                display_image_with_expander(image=original_image, caption="Última imagen generada")

            draw_emoji_interface("prompt_input_area_mod")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("image_modification_form"):
                    mod_prompt = st.text_area("💡 ...o describe la mutación:", 
                                            key="prompt_input_area_mod")
                    submit_mod = st.form_submit_button("🔥 Modificar")
                
                if submit_mod:
                    if original_image:
                        handle_image_modification(client, mod_prompt, user_uuid, original_image)
                        st.session_state.prompt_input_area_mod = "" # Limpiar
                    else:
                        st.error("💀 No hay imagen disponible. Sube una o genera una nueva.")

        # Lógica de descarga
        d1, d2, d3 = st.columns([1, 2, 1])
        with d2:
            if "last_generated_image" in st.session_state:
                last_image = st.session_state["last_generated_image"]
                if os.path.exists(last_image["filename"]):
                    with open(last_image["filename"], "rb") as file:
                        st.download_button(
                            label="📥 Descargar Creación",
                            data=file,
                            file_name=last_image["filename"],
                            mime="image/png"
                        )
            
            if "last_modified_image" in st.session_state:
                last_mod_image = st.session_state["last_modified_image"]
                if os.path.exists(last_mod_image["filename"]):
                    with open(last_mod_image["filename"], "rb") as file:
                        st.download_button(
                            label="📥 Descargar Transmutación",
                            data=file,
                            file_name=last_mod_image["filename"],
                            mime="image/png"
                        )
    
    st.markdown("---")
    st.caption("Ψ Sistema EsquizoAI v2.5.1 | Glitch Corregido")



