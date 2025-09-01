import streamlit as st
import pandas as pd
import os, time, zipfile

from src.firebase_utils import (
    initialize_firebase, 
    get_project_specific_users, 
    get_total_image_count, 
    get_user_images, 
    download_images
)


# ==============================
# ⚙️ CONFIGURACIÓN DE PÁGINA
# ==============================
st.set_page_config(page_title="Observatorio Secreto", layout="wide")


# ==============================
# 🔑 AUTENTICACIÓN BÁSICA
# ==============================
def check_password():
    """Retorna True si la contraseña es correcta."""
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    correct_password = str(st.secrets["admin"]["password"])

    if not st.session_state.password_correct:
        password = st.text_input("Ingresa la clave del Observatorio", type="password")
        if st.button("Acceder"):
            if password.strip() == correct_password.strip():
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.error("Clave incorrecta.")
    return st.session_state.password_correct

if not check_password():
    st.stop()


# ==============================
# 🔥 INICIALIZACIÓN DE FIREBASE
# ==============================
db, bucket = initialize_firebase()


# ==============================
# 📊 MÉTRICAS PRINCIPALES
# ==============================
st.title("🔮 Observatorio Secreto del Akelarre 🔮")

if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

all_users = get_project_specific_users(db)
total_users = len(all_users)
total_images = get_total_image_count(db)

col1, col2 = st.columns(2)
with col1: st.metric("Nº Total de Viajeros", total_users)
with col2: st.metric("Imágenes Totales Generadas", total_images)


# ==============================
# 📂 LISTADO DE USUARIOS
# ==============================
st.header("Listado de Viajeros")

if all_users:
    df_users = pd.DataFrame([{"Usuario": u["nombre"], "UUID": u["user_uuid"]} for u in all_users])
    st.dataframe(df_users, width="stretch")
else:
    st.info("Aún no hay viajeros registrados.")


# ==============================
# 📥 DESCARGA DE IMÁGENES
# ==============================
st.header("📥 Descarga de Imágenes por Usuario")

user_names = [u["nombre"] for u in all_users]
selected_user = st.selectbox("Selecciona un viajero:", [""] + user_names)

if selected_user:
    selected_uuid = next(u["user_uuid"] for u in all_users if u["nombre"] == selected_user)

    if st.button("🔽 Descargar imágenes de este usuario"):
        with st.spinner("Buscando imágenes..."):
            image_paths = get_user_images(bucket, selected_uuid)

        if not image_paths:
            st.warning("Este viajero aún no tiene imágenes.")
        else:
            total = len(image_paths)
            st.info(f"Se encontraron {total} imágenes.")

            # Carpeta destino
            dest_folder = f"downloads/{selected_uuid}"
            os.makedirs(dest_folder, exist_ok=True)

            progress_bar = st.progress(0)
            start_time = time.time()

            for i, path in enumerate(image_paths, start=1):
                blob = bucket.blob(path)
                filename = os.path.join(dest_folder, os.path.basename(path))
                blob.download_to_filename(filename)
                progress_bar.progress(i / total)

            elapsed = time.time() - start_time
            st.success(f"✅ Descarga completa en {elapsed:.2f} segundos.")

            # Empaquetar en ZIP para descargar desde la web
            zip_path = f"{dest_folder}.zip"
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for file in os.listdir(dest_folder):
                    zipf.write(os.path.join(dest_folder, file), arcname=file)

            with open(zip_path, "rb") as f:
                st.download_button("⬇️ Descargar ZIP", f, file_name=f"{selected_user}_imagenes.zip")
