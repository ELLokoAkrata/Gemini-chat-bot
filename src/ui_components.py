import streamlit as st
from datetime import datetime

def get_timestamp():
    """Retorna un timestamp formateado para nombres de archivo."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_filename(is_modified: bool = False):
    """Genera un nombre de archivo único basado en el timestamp."""
    timestamp = get_timestamp()
    prefix = "mod_" if is_modified else "gen_"
    return f"{prefix}{timestamp}.png"

def display_image_with_expander(image, caption):
    """
    Muestra una imagen centrada con un expander para verla en tamaño completo.
    """
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(
            image=image,
            caption=caption,
            width='stretch',
            output_format="PNG"
        )
        st.caption("🔍 Haz clic en el cuadrito de full screen para ver la imagen en tamaño original")

def show_login_form(db):
    """
    Muestra el formulario de login en la barra lateral y gestiona la lógica de autenticación.
    """
    with st.form("login"):
        user_name = st.text_input("🌀 Tu Nombre de Poder (máx 8 caracteres)")
        if st.form_submit_button("🎯 Iniciar Viaje"):
            if user_name:
                if len(user_name) > 8:
                    st.error("💀 El nombre no puede tener más de 8 caracteres")
                else:
                    from src.firebase_utils import get_or_create_user
                    user_uuid = get_or_create_user(db, user_name)
                    st.session_state["user_uuid"] = user_uuid
                    st.session_state["user_name"] = user_name
                    st.session_state["logged_in"] = True
                    st.rerun()

def show_user_info():
    """
    Muestra la información del usuario logueado y el botón de logout.
    """
    st.write(f"🎭 Viajero: {st.session_state.get('user_name', 'Anónimo')}")
    st.write(f"🔮 ID: {st.session_state.get('user_uuid', '')[:8]}...")
    if st.button("⚡ Cerrar Portal"):
        st.session_state.logged_in = False
        st.rerun()

def show_welcome_message():
    """
    Muestra el mensaje de bienvenida y las instrucciones para usuarios no logueados.
    """
    st.markdown("""
    <div style="text-align: center;">
        <h2>🌌 GUÍA DE INICIACIÓN 🌌</h2>
        <p>1. Ingresa tu <b>Nombre de Poder</b> abajo para entrar al Akelarre.</p>
        <p>2. Una vez dentro, <b>invoca tu visión</b> en el campo de texto.</p>
        <p>3. Puedes usar <b>texto, emojis de tu teclado 💀🔥🤖, o una mezcla de ambos</b>.</p>
        <p>4. <b>Transmuta</b> la imagen generada o sube una propia para alterarla.</p>
        <br>
        <p>Este portal se alimenta de la energía del caos y de los créditos personales del desarrollador. Si quieres mantener la llama encendida, considera ofrendar una donación.</p>
        <p><a href="https://www.paypal.com/paypalme/rdvibe?country.x=PE&locale.x=es_XC" target="_blank" style="color: #00ff00; text-decoration: underline;"><b>>> Donar para mantener vivo el Akelarre <<</b></a></p>
        <br>
        <p><a href="https://github.com/Ellokoakarata/Gemini-chat-bot" target="_blank">Código Fuente del Ritual</a></p>
    </div>
    """, unsafe_allow_html=True)
