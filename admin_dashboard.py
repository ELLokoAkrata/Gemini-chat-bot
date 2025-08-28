import streamlit as st
import pandas as pd
from src.firebase_utils import initialize_firebase, get_all_users, get_total_image_count
import altair as alt

# --- Configuración de la página ---
st.set_page_config(page_title="Observatorio Secreto", layout="wide")

# --- Autenticación Simple ---
def check_password():
    """Retorna `True` si el usuario está autenticado."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    # Cargar la contraseña desde los secretos de Streamlit
    correct_password = st.secrets["admin_password"]

    if not st.session_state.password_correct:
        password = st.text_input("Ingresa la clave del Observatorio", type="password")
        if st.button("Acceder"):
            if password == correct_password:
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("La clave es incorrecta. El Akelarre te rechaza.")
    return st.session_state.password_correct

if not check_password():
    st.stop()

# --- Inicialización de Firebase ---
db = initialize_firebase()

# --- Título del Dashboard ---
st.title("🔮 Observatorio Secreto del Akelarre 🔮")
st.markdown("---")

# --- Métricas Principales ---
col1, col2 = st.columns(2)

# Métrica 1: Número total de usuarios
all_users = get_all_users(db)
total_users = len(all_users)
with col1:
    st.metric(label="Nº Total de Viajeros (Usuarios)", value=total_users)

# Métrica 2: Conteo total de imágenes (eficiente)
total_images = get_total_image_count(db)
with col2:
    st.metric(label="Imágenes Totales Generadas", value=total_images)

st.markdown("---")

# --- Visualización de Datos ---
st.header("Listado de Viajeros")

if all_users:
    # Convertir la lista de usuarios a un DataFrame para mostrarlo
    users_data = [{"Usuario": user.get('nombre', 'N/A'), "UUID": user.get('user_uuid', 'N/A')} for user in all_users]
    df_users = pd.DataFrame(users_data)
    
    st.info("El conteo de imágenes por usuario ha sido desactivado para optimizar el rendimiento y los costos de Firebase.")
    st.dataframe(df_users, use_container_width=True)
else:
    st.info("Aún no hay viajeros registrados.")