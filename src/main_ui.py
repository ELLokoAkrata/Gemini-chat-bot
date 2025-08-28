import streamlit as st
from PIL import Image
import os
from datetime import datetime, timedelta
import logging

from src.config import STORAGE_ROOT_FOLDER, USER_COOLDOWN_SECONDS
from src.firebase_utils import (
    initialize_firebase, 
    upload_image_to_storage, 
    save_image_metadata,
    check_daily_limit,
    increment_daily_count
)
from src.gemini_utils import initialize_genai_client, generate_image_from_prompt
from src.prompt_engineering import engineer_prompt
from src.chat_logic import initialize_chat_client, stream_chat_response
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
        .st-emotion-cache-1f2d094 { /* Contenedor del chat */
            border: 1px solid #00ff00;
            border-radius: 10px;
            box-shadow: 0 0 10px #00ff00;
        }
        h1, h2, h3 {
            text-align: center !important;
        }
        /* Estilo para el contenedor del chat */
        [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
            border: 1px solid #00ff00;
            border-radius: 10px;
            box-shadow: 0 0 10px #00ff00;
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
    db = initialize_firebase()

    # --- 1. Verificación de Cooldown del Usuario ---
    now = datetime.now()
    if "last_request_time" in st.session_state:
        time_since_last_request = now - st.session_state["last_request_time"]
        if time_since_last_request < timedelta(seconds=USER_COOLDOWN_SECONDS):
            remaining_time = USER_COOLDOWN_SECONDS - time_since_last_request.total_seconds()
            st.error(f"⏳ Energía del caos baja. Espera {remaining_time:.0f} segundos antes de generar otra imagen.")
            logging.warning(f"Usuario {user_uuid} limitado por cooldown. Tiempo restante: {remaining_time:.0f}s")
            return

    # --- 2. Verificación del Límite Diario Global ---
    if check_daily_limit(db):
        st.error("🚫 El Akelarre ha alcanzado su límite de energía por hoy. Vuelve mañana para seguir creando.")
        logging.warning(f"Generación bloqueada para {user_uuid}. Límite diario global alcanzado.")
        return

    # Si las validaciones pasan, actualizamos el tiempo de la última petición
    st.session_state["last_request_time"] = now

    # --- Proceso de Generación ---
    final_prompt = engineer_prompt(user_prompt)
    generated_image = generate_image_from_prompt(client, final_prompt)
    
    if generated_image:
        # --- 3. Incrementar el contador solo si la imagen se generó con éxito ---
        increment_daily_count(db)

        output_filename = generate_filename(is_modified=False)
        generated_image.save(output_filename)
        
        st.markdown("<h3 style='text-align: center;'>🖼️ Creación Manifestada</h3>", unsafe_allow_html=True)
        display_image_with_expander(image=generated_image, caption=f"Input: {user_prompt}")
        
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
    db = initialize_firebase()

    # --- 1. Verificación de Cooldown del Usuario ---
    now = datetime.now()
    if "last_request_time" in st.session_state:
        time_since_last_request = now - st.session_state["last_request_time"]
        if time_since_last_request < timedelta(seconds=USER_COOLDOWN_SECONDS):
            remaining_time = USER_COOLDOWN_SECONDS - time_since_last_request.total_seconds()
            st.error(f"⏳ Energía del caos baja. Espera {remaining_time:.0f} segundos antes de transmutar de nuevo.")
            logging.warning(f"Usuario {user_uuid} limitado por cooldown. Tiempo restante: {remaining_time:.0f}s")
            return

    # --- 2. Verificación del Límite Diario Global ---
    if check_daily_limit(db):
        st.error("🚫 El Akelarre ha alcanzado su límite de energía por hoy. Vuelve mañana para seguir creando.")
        logging.warning(f"Generación bloqueada para {user_uuid}. Límite diario global alcanzado.")
        return
        
    # Si las validaciones pasan, actualizamos el tiempo de la última petición
    st.session_state["last_request_time"] = now

    # --- Proceso de Modificación ---
    final_prompt = engineer_prompt(user_prompt)
    mod_image = generate_image_from_prompt(client, final_prompt, original_image)

    if mod_image:
        # --- 3. Incrementar el contador solo si la imagen se generó con éxito ---
        increment_daily_count(db)

        output_filename = generate_filename(is_modified=True)
        mod_image.save(output_filename)
        
        st.markdown("<h3 style='text-align: center;'>🖼️ Transmutación Realizada</h3>", unsafe_allow_html=True)
        display_image_with_expander(image=mod_image, caption=f"Input: {user_prompt}")
        
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

def run_app():
    """Función principal que ejecuta la aplicación Streamlit."""
    setup_page()
    db = initialize_firebase()
    # El cliente de GenAI para imágenes se inicializa aquí
    image_client = initialize_genai_client()

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
        
        tab1, tab2, tab3 = st.tabs(["🎨 Generar", "🔄 Transmutar", "🔥 Psycho-Chat"])

        with tab1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("image_generation_form"):
                    prompt_input = st.text_area("💡 Invoca tu visión (puedes usar texto y emojis):", 
                                              key="prompt_input_area_gen")
                    submit_gen = st.form_submit_button("🔥 Generar")
                
                if submit_gen:
                    handle_image_generation(image_client, prompt_input, user_uuid)

            # Lógica de descarga para la imagen generada
            if "last_generated_image" in st.session_state:
                d1, d2, d3 = st.columns([1, 2, 1])
                with d2:
                    last_image = st.session_state["last_generated_image"]
                    if os.path.exists(last_image["filename"]):
                        with open(last_image["filename"], "rb") as file:
                            st.download_button(
                                label="📥 Descargar Creación",
                                data=file,
                                file_name=last_image["filename"],
                                mime="image/png"
                            )

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

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("image_modification_form"):
                    mod_prompt = st.text_area("💡 Describe la mutación (puedes usar texto y emojis):", 
                                            key="prompt_input_area_mod")
                    submit_mod = st.form_submit_button("🔥 Modificar")
                
                if submit_mod:
                    if original_image:
                        handle_image_modification(image_client, mod_prompt, user_uuid, original_image)
                    else:
                        st.error("💀 No hay imagen disponible. Sube una o genera una nueva.")
            
            # Lógica de descarga para la imagen modificada
            if "last_modified_image" in st.session_state:
                d1, d2, d3 = st.columns([1, 2, 1])
                with d2:
                    last_mod_image = st.session_state["last_modified_image"]
                    if os.path.exists(last_mod_image["filename"]):
                        with open(last_mod_image["filename"], "rb") as file:
                            st.download_button(
                                label="📥 Descargar Transmutación",
                                data=file,
                                file_name=last_mod_image["filename"],
                                mime="image/png"
                            )
        
        with tab3:
            st.header("Conversación con el Abismo")

            # Inicializar el cliente de chat y el historial en el estado de la sesión
            if "chat_client" not in st.session_state:
                st.session_state.chat_client = initialize_chat_client()
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Mostrar mensajes del historial
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Generar respuesta del asistente si el último mensaje es del usuario
            if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    with st.spinner("El abismo está susurrando..."):
                        response_stream = stream_chat_response(
                            st.session_state.chat_client, 
                            st.session_state.messages
                        )
                        full_response = st.write_stream(response_stream)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Aceptar entrada del usuario. Esto siempre se ejecuta al final.
            if prompt := st.chat_input("ESCÚPEME TU VENENO..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
    
    st.markdown("---")
    st.caption("Ψ Sistema EsquizoAI 3.3.3 | Akelarre Generativo") # no cambiar nunca este pie de página (psychobot)