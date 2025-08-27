import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid

def initialize_firebase():
    """
    Inicializa la conexión con Firebase usando las credenciales de Streamlit secrets.
    Retorna el cliente de Firestore.
    """
    if not firebase_admin._apps:
        firebase_secrets = st.secrets["firebase"]
        cred = credentials.Certificate({
            "type": firebase_secrets["type"],
            "project_id": firebase_secrets["project_id"],
            "private_key_id": firebase_secrets["private_key_id"],
            "private_key": firebase_secrets["private_key"].replace('\n', '\n'),
            "client_email": firebase_secrets["client_email"],
            "client_id": firebase_secrets["client_id"],
            "auth_uri": firebase_secrets["auth_uri"],
            "token_uri": firebase_secrets["token_uri"],
            "auth_provider_x509_cert_url": firebase_secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": firebase_secrets["client_x509_cert_url"]
        })
        firebase_admin.initialize_app(cred, {
            "storageBucket": firebase_secrets.get("storageBucket")
        })
    return firestore.client()

def upload_image_to_storage(local_path: str, remote_path: str):
    """
    Sube una imagen a Firebase Storage.
    """
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    st.success(f"Imagen subida a Storage: {remote_path}")

def save_image_metadata(db, user_uuid: str, metadata: dict):
    """
    Guarda los metadatos de una imagen en la subcolección 'user_images'
    del usuario correspondiente.
    """
    db.collection("usuarios").document(user_uuid).collection("user_images").add(metadata)

def get_or_create_user(db, user_name: str):
    """
    Busca un usuario por nombre en Firestore. Si no existe, lo crea.
    Retorna el UUID del usuario.
    """
    user_query = db.collection("usuarios").where(filter=FieldFilter("nombre", "==", user_name)).get()
    if user_query:
        user_data = user_query[0].to_dict()
        return user_data["user_uuid"]
    else:
        new_uuid = str(uuid.uuid4())
        db.collection("usuarios").document(new_uuid).set({
            "nombre": user_name,
            "user_uuid": new_uuid
        })
        return new_uuid
