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
from src.prompt_engineering import engineer_prompt, ART_STYLES, CORE_AESTHETICS
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
    
    use_raw_mode = st.sidebar.checkbox(
        "Modo RAW (Sin Estilos)", 
        value=False, 
        help="Actívalo para ignorar la Estética Central y el Estilo Artístico, usando solo tu prompt."
    )

    # Nuevo selectbox para elegir la estética central
    selected_core_aesthetic = st.sidebar.selectbox(
        "Estética Central 🧠",
        options=list(CORE_AESTHETICS.keys()),
        index=0, # Dejar que 'none' sea el default
        help="Elige la estética filosófica y visual principal para la generación.",
        disabled=use_raw_mode
    )

    art_style = st.sidebar.selectbox(
        "Estilo Artístico 🎨",
        options=list(ART_STYLES.keys()),
        index=0, # Dejar que 'none' sea el default
        help="Elige el estilo visual principal para la imagen.",
        disabled=use_raw_mode
    )

    # Si el modo RAW está activo, forzamos los valores a 'none'
    if use_raw_mode:
        selected_core_aesthetic = "none"
        art_style = "none"

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
    return selected_core_aesthetic, art_style, glitch_value, chaos_value, temperature, top_p, top_k

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
        .st-emotion-cache-1f2d094 {
            border: 1px solid #00ff00;
            border-radius: 10px;
            box-shadow: 0 0 10px #00ff00;
        }
        h1, h2, h3 {
            text-align: center !important;
        }
        [data-testid="stVerticalBlock"] > [data-testid="stContainer"] {
            border: 1px solid #00ff00;
            border-radius: 10px;
            box-shadow: 0 0 10px #00ff00;
        }
        .stChatMessage > div > div > div { font-size: 18px !important; line-height: 1.6 !important; }
        .stChatMessage[data-testid="user"] > div > div > div { font-size: 20px !important; font-weight: 600 !important; color: #ff6b6b !important; }
        .stChatMessage[data-testid="assistant"] > div > div > div { font-size: 19px !important; font-weight: 500 !important; color: #00ff00 !important; }
        .stChatInput > div > div > div > div > div > div > div { font-size: 18px !important; padding: 15px !important; }
        .stChatInput input::placeholder { font-size: 18px !important; color: #666 !important; }
        .stChatMessage { margin-bottom: 20px !important; }
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
    selected_core_aesthetic, art_style, glitch_value, chaos_value, temperature, top_p, top_k,
    original_image: Image.Image = None
):
    """
    Gestiona la lógica unificada para generar o modificar una imagen,
    incluyendo validaciones y guardado.
    """
    db, _ = initialize_firebase()
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
        selected_core_aesthetic=selected_core_aesthetic
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
            st.session_state["image_ready"] = True  # Marcar que la imagen está lista

def run_app():
    """Función principal que ejecuta la aplicación Streamlit."""
    setup_page()
    db, _ = initialize_firebase()
    image_client = initialize_genai_client()

    # ---- Estado por defecto para controlar visibilidad del botón de descarga en "Generar"
    if "image_ready" not in st.session_state:
        st.session_state["image_ready"] = False  # No mostrar hasta que se genere algo en esta sesión

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
            core_aesthetic, art_style, glitch, chaos, temp, top_p, top_k = show_generation_controls()

        user_uuid = st.session_state.get("user_uuid")
        tab1, tab2, tab3 = st.tabs(["🎨 Generar", "🔄 Transmutar", "🔥 Psycho-Chat"])

        # ---------------- TAB 1: GENERAR ----------------
        with tab1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("image_generation_form"):
                    prompt_input = st.text_area(
                        "💡 Invoca tu visión (puedes usar texto y emojis):",
                        key="prompt_input_area_gen"
                    )
                    submit_gen = st.form_submit_button("🔥 Generar")

                if submit_gen:
                    # FIX: ocultar el botón de descarga previo al iniciar una nueva generación
                    st.session_state["image_ready"] = False

                    if not (prompt_input or "").strip():
                        st.warning("Escribe un prompt para invocar la imagen.")
                    else:
                        handle_image_processing(
                            image_client, prompt_input, user_uuid,
                            core_aesthetic, art_style, glitch, chaos, temp, top_p, top_k
                        )

            # Botón de descarga solo si una generación RECIENTE está lista
            if (
                st.session_state.get("image_ready", False) and
                "last_generated_image" in st.session_state and
                "filename" in st.session_state["last_generated_image"] and
                os.path.exists(st.session_state["last_generated_image"]["filename"])
            ):
                d1, d2, d3 = st.columns([1, 2, 1])
                with d2:
                    last_image = st.session_state["last_generated_image"]
                    try:
                        with open(last_image["filename"], "rb") as file:
                            # Usar un callback para ocultar el botón después de la descarga
                            if st.download_button(
                                label="📥 Descargar Creación",
                                data=file,
                                file_name=last_image["filename"],
                                mime="image/png",
                                key="download_generated_image"
                            ):
                                # Este bloque se ejecuta cuando se hace click
                                st.session_state["image_ready"] = False
                                st.rerun()  # Forzar re-render para ocultar el botón
                    except FileNotFoundError:
                        # Si el archivo fue movido/borrado, ocultar botón
                        st.session_state["image_ready"] = False

        # ---------------- TAB 2: TRANSMUTAR ----------------
        with tab2:
            st.markdown(
                "<h3 style='text-align: center;'>🌟 Sube una imagen para alterarla</h3>",
                unsafe_allow_html=True
            )
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                uploaded_file = st.file_uploader(
                    "Sube una imagen", type=["png", "jpg", "jpeg"], label_visibility="collapsed"
                )

            original_image = None
            if uploaded_file is not None:
                original_image = Image.open(uploaded_file)
                display_image_with_expander(image=original_image, caption="Imagen a transmutar")
            elif "last_generated_image" in st.session_state:
                original_image = st.session_state["last_generated_image"]["image"]
                st.markdown(
                    "<p style='text-align: center;'>Usando la última imagen generada.</p>",
                    unsafe_allow_html=True
                )
                display_image_with_expander(image=original_image, caption="Última imagen generada")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                with st.form("image_modification_form"):
                    mod_prompt = st.text_area(
                        "💡 Describe la mutación (puedes usar texto y emojis):",
                        key="prompt_input_area_mod"
                    )
                    submit_mod = st.form_submit_button("🔥 Modificar")

                if submit_mod:
                    if original_image:
                        handle_image_processing(
                            image_client, mod_prompt, user_uuid,
                            core_aesthetic, art_style, glitch, chaos, temp, top_p, top_k,
                            original_image=original_image
                        )
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
                    else:
                        st.error("💀 No hay imagen disponible. Sube una o genera una nueva.")

        # ---------------- TAB 3: PSYCHO-CHAT ----------------
        with tab3:
            st.header("Conversación con el Abismo")

            if "chat_client" not in st.session_state:
                st.session_state.chat_client = initialize_chat_client()
            if "messages" not in st.session_state:
                st.session_state.messages = []

            # Mostrar historial de mensajes
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Respuesta del bot si el último no fue del asistente
            if st.session_state.messages and st.session_state.messages[-1]["role"] != "assistant":
                with st.chat_message("assistant"):
                    processing_placeholder = st.empty()
                    processing_placeholder.markdown("🧠 *El abismo está procesando su demencia interna...*")

                    response_stream = stream_chat_response(
                        st.session_state.chat_client,
                        st.session_state.messages
                    )

                    full_response_text = ""
                    response_area = st.empty()

                    for chunk in response_stream:
                        if hasattr(chunk, "text") and chunk.text:
                            full_response_text += chunk.text
                            response_area.markdown(full_response_text)

                    processing_placeholder.empty()

                # Guardar respuesta en historial
                st.session_state.messages.append(
                    {"role": "assistant", "content": full_response_text}
                )

            # Input del chat
            if prompt := st.chat_input("ESCÚPEME TU VENENO...", key="psycho_chat_input"):
                if prompt.strip():
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.rerun()

    st.markdown("---")
    st.caption("Ψ Sistema EsquizoAI 3.3.3 | Akelarre Generativo")


