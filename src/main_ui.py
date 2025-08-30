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
from src.prompt_engineering import engineer_prompt, ART_STYLES
from src.chat_logic import initialize_chat_client, stream_chat_response
from src.ui_components import (
    display_image_with_expander,
    generate_filename,
    show_login_form,
    show_user_info,
    show_welcome_message
)

def show_generation_controls():
    """Muestra los sliders de control en la barra lateral y devuelve sus valores."""
    st.sidebar.header("🌀 Parámetros de Creación 🌀")
    
    use_core_aesthetic = st.sidebar.checkbox(
        "Mantener Estética Central", 
        value=True, 
        help="Actívalo para fusionar tu estilo con la temática anarco-punk. Desactívalo para un estilo puro."
    )

    art_style = st.sidebar.selectbox(
        "Estilo Artístico 🎨",
        options=list(ART_STYLES.keys()),
        index=0, # 'fusion' por defecto
        help="Elige el estilo visual principal para la imagen."
    )

    glitch_value = st.sidebar.slider(
        "Nivel de Glitch 藝術", 0.0, 1.0, 0.4, 0.05,
        help="Controla la intensidad de los artefactos visuales y la estética 'glitch'."
    )
    chaos_value = st.sidebar.slider(
        "Nivel de Caos 🔥", 0.0, 1.0, 0.6, 0.05,
        help="Define el nivel de desorden, energía y crudeza en la composición."
    )

    st.sidebar.header("🤖 Parámetros de la IA 🤖")
    temperature = st.sidebar.slider(
        "Temperatura (Creatividad)", 0.0, 1.0, 1.0, 0.05,
        help="Valores más altos (ej. 1.0) generan resultados más inesperados y creativos. Valores bajos (ej. 0.1) son más conservadores."
    )
    top_p = st.sidebar.slider(
        "Top-P (Coherencia)", 0.0, 1.0, 0.95, 0.05,
        help="Filtra las opciones menos probables. No suele ser necesario cambiarlo."
    )
    top_k = st.sidebar.slider(
        "Top-K (Diversidad)", 1, 50, 40, 1,
        help="Limita la selección de tokens a los K más probables. Ajusta la diversidad de la salida."
    )
    return use_core_aesthetic, art_style, glitch_value, chaos_value, temperature, top_p, top_k

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


def handle_image_processing(
    client, user_prompt, user_uuid,
    use_core_aesthetic, art_style, glitch_value, chaos_value, temperature, top_p, top_k,
    original_image: Image.Image = None
):
    """
    Gestiona la lógica unificada para generar o modificar una imagen,
    incluyendo validaciones y guardado.
    """
    db = initialize_firebase()
    is_modification = original_image is not None

    # --- 1. Verificación de Cooldown del Usuario ---
    now = datetime.now()
    if "last_request_time" in st.session_state:
        time_since_last_request = now - st.session_state["last_request_time"]
        if time_since_last_request < timedelta(seconds=USER_COOLDOWN_SECONDS):
            remaining_time = USER_COOLDOWN_SECONDS - time_since_last_request.total_seconds()
            st.error(f"⏳ Energía del caos baja. Espera {remaining_time:.0f} segundos.")
            logging.warning(f"Usuario {user_uuid} limitado por cooldown.")
            return

    # --- 2. Verificación del Límite Diario Global ---
    if check_daily_limit(db):
        st.error("🚫 El Akelarre ha alcanzado su límite de energía por hoy. Vuelve mañana.")
        logging.warning(f"Generación bloqueada para {user_uuid}. Límite diario alcanzado.")
        return

    st.session_state["last_request_time"] = now

    # --- Proceso de Generación / Modificación ---
    final_prompt = engineer_prompt(
        user_input=user_prompt,
        style=art_style,
        glitch_value=glitch_value,
        chaos_value=chaos_value,
        use_core_aesthetic=use_core_aesthetic
    )
    processed_image = generate_image_from_prompt(
        client=client,
        prompt=final_prompt,
        original_image=original_image,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k
    )

    if processed_image:
        increment_daily_count(db)
        output_filename = generate_filename(is_modified=is_modification)
        processed_image.save(output_filename)

        title = "🖼️ Transmutación Realizada" if is_modification else "🖼️ Creación Manifestada"
        st.markdown(f"<h3 style='text-align: center;'>{title}</h3>", unsafe_allow_html=True)
        display_image_with_expander(image=processed_image, caption=f"Input: {user_prompt}")

        remote_path = f"{STORAGE_ROOT_FOLDER}/{user_uuid}/{output_filename}"
        metadata = {
            "user_prompt": user_prompt, "final_prompt": final_prompt,
            "timestamp": datetime.now(), "storage_path": remote_path,
            "is_modified": is_modification,
            "params": {
                "glitch": glitch_value, "chaos": chaos_value, "temp": temperature,
                "top_p": top_p, "top_k": top_k
            }
        }
        save_image_metadata(db, user_uuid, metadata)
        upload_image_to_storage(output_filename, remote_path)

        session_key = "last_modified_image" if is_modification else "last_generated_image"
        st.session_state[session_key] = {
            "filename": output_filename,
            "prompt": user_prompt,
            "image": processed_image
        }
        if not is_modification:
            st.session_state["current_generated_image"] = True


def run_app():
    """Función principal que ejecuta la aplicación Streamlit."""
    setup_page()
    db = initialize_firebase()
    image_client = initialize_genai_client()

    if not st.session_state.get("logged_in", False):
        show_welcome_message()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            show_login_form(db)
    else:
        with st.sidebar:
            st.header("💊 Control Neural")
            st.markdown("---")
            show_user_info()
            st.markdown("---")
            # Obtener los valores de los sliders
            use_core, art_style, glitch, chaos, temp, top_p, top_k = show_generation_controls()

        user_uuid = st.session_state.get("user_uuid")
        tab1, tab2, tab3 = st.tabs(["🎨 Generar", "🔄 Transmutar", "🔥 Psycho-Chat"])

        with tab1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("image_generation_form"):
                    prompt_input = st.text_area("💡 Invoca tu visión (puedes usar texto y emojis):", key="prompt_input_area_gen")
                    submit_gen = st.form_submit_button("🔥 Generar")

                if submit_gen:
                    handle_image_processing(
                        image_client, prompt_input, user_uuid,
                        use_core, art_style, glitch, chaos, temp, top_p, top_k
                    )

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
                    mod_prompt = st.text_area("💡 Describe la mutación (puedes usar texto y emojis):", key="prompt_input_area_mod")
                    submit_mod = st.form_submit_button("🔥 Modificar")

                if submit_mod:
                    if original_image:
                        handle_image_processing(
                            image_client, mod_prompt, user_uuid,
                            use_core, art_style, glitch, chaos, temp, top_p, top_k,
                            original_image=original_image
                        )
                    else:
                        st.error("💀 No hay imagen disponible. Sube una o genera una nueva.")

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
            if "chat_client" not in st.session_state:
                st.session_state.chat_client = initialize_chat_client()
            if "messages" not in st.session_state:
                st.session_state.messages = []
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    with st.spinner("El abismo está susurrando..."):
                        response_stream = stream_chat_response(
                            st.session_state.chat_client,
                            st.session_state.messages
                        )
                        full_response = st.write_stream(response_stream)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            if prompt := st.chat_input("ESCÚPEME TU VENENO..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()

    st.markdown("---")
    st.caption("Ψ Sistema EsquizoAI 3.3.3 | Akelarre Generativo")
