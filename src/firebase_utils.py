import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid
from datetime import timedelta, datetime, timezone
import os

from src.config import STORAGE_ROOT_FOLDER, MAX_IMAGES_PER_DAY


# ==============================
# 🔥 INICIALIZACIÓN DE FIREBASE
# ==============================
def initialize_firebase():
    """
    Inicializa Firebase con credenciales guardadas en Streamlit secrets.
    Retorna: (cliente Firestore, bucket Storage).
    """
    if not firebase_admin._apps:
        firebase_secrets = st.secrets["firebase"]
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
        firebase_admin.initialize_app(cred, {
            "storageBucket": firebase_secrets.get("storageBucket")
        })
    return firestore.client(), storage.bucket()


# ==============================
# 📊 CONTROL DE LÍMITE DIARIO
# ==============================
def check_daily_limit(db):
    """Verifica si se alcanzó el límite diario de generación de imágenes."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    limit_ref = db.collection("daily_limits").document(today_str)
    limit_doc = limit_ref.get()

    if limit_doc.exists:
        count = limit_doc.to_dict().get("image_count", 0)
        return count >= MAX_IMAGES_PER_DAY
    return False


def increment_daily_count(db):
    """Incrementa el contador de imágenes del día actual (atómico con transacción)."""
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    limit_ref = db.collection("daily_limits").document(today_str)

    @firestore.transactional
    def update_in_transaction(transaction, doc_ref):
        snapshot = doc_ref.get(transaction=transaction)
        if snapshot.exists:
            new_count = snapshot.to_dict().get("image_count", 0) + 1
            transaction.update(doc_ref, {"image_count": new_count})
        else:
            transaction.set(doc_ref, {"image_count": 1})

    transaction = db.transaction()
    update_in_transaction(transaction, limit_ref)


# ==============================
# ☁️ STORAGE (SUBIDA / BAJADA)
# ==============================
def upload_image_to_storage(local_path: str, remote_path: str):
    """Sube una imagen al bucket de Firebase Storage."""
    bucket = storage.bucket()
    blob = bucket.blob(remote_path)
    blob.upload_from_filename(local_path)
    st.success(f"Imagen subida a Storage: {remote_path}")


def get_user_images(bucket, user_uuid: str):
    """
    Lista las imágenes de un usuario dentro de Firebase Storage.
    Supone que las imágenes están bajo 'images/<user_uuid>/'.
    """
    prefix = f"{STORAGE_ROOT_FOLDER}/{user_uuid}/"
    blobs = bucket.list_blobs(prefix=prefix)
    return [blob.name for blob in blobs if blob.name.lower().endswith((".png", ".jpg", ".jpeg"))]


def download_images(bucket, image_paths, dest_folder="downloads"):
    """
    Descarga una lista de imágenes desde Firebase Storage a una carpeta local.
    Retorna la carpeta de destino.
    """
    os.makedirs(dest_folder, exist_ok=True)

    for path in image_paths:
        blob = bucket.blob(path)
        filename = os.path.join(dest_folder, os.path.basename(path))
        blob.download_to_filename(filename)

    return dest_folder


def get_image_public_url(storage_path: str):
    """Genera una URL firmada (1h) para visualizar un archivo en Storage."""
    bucket = storage.bucket()
    blob = bucket.blob(storage_path)
    return blob.generate_signed_url(version="v4", expiration=timedelta(minutes=60))


# ==============================
# 📂 METADATOS Y USUARIOS
# ==============================
def save_image_metadata(db, user_uuid: str, metadata: dict):
    """Guarda metadatos de una imagen en la subcolección 'user_images'."""
    db.collection("usuarios").document(user_uuid).collection("user_images").add(metadata)


def get_or_create_user(db, user_name: str):
    """Busca un usuario por nombre o lo crea si no existe. Retorna su UUID."""
    user_query = db.collection("usuarios").where(filter=FieldFilter("nombre", "==", user_name)).get()
    if user_query:
        return user_query[0].to_dict()["user_uuid"]
    else:
        new_uuid = str(uuid.uuid4())
        db.collection("usuarios").document(new_uuid).set({
            "nombre": user_name,
            "user_uuid": new_uuid
        })
        return new_uuid


def get_project_specific_users(db):
    """Obtiene los usuarios que tienen imágenes en este proyecto específico."""
    images_group_ref = db.collection_group('user_images')

    start_at = f"{STORAGE_ROOT_FOLDER}/"
    end_at = start_at + "\uf8ff"

    query = images_group_ref.where(filter=FieldFilter("storage_path", ">=", start_at)) \
                            .where(filter=FieldFilter("storage_path", "<", end_at))

    user_uuids = {doc.reference.parent.parent.id for doc in query.stream()}

    users_data = []
    for uuid in user_uuids:
        user_doc = db.collection("usuarios").document(uuid).get()
        if user_doc.exists:
            users_data.append(user_doc.to_dict())

    return users_data


def get_total_image_count(db):
    """Cuenta total de imágenes generadas en el proyecto (consulta de agregación eficiente)."""
    images_group_ref = db.collection_group('user_images')

    start_at = f"{STORAGE_ROOT_FOLDER}/"
    end_at = start_at + "\uf8ff"

    query = images_group_ref.where(filter=FieldFilter("storage_path", ">=", start_at)) \
                            .where(filter=FieldFilter("storage_path", "<", end_at))

    aggregate_query = query.count()
    result = aggregate_query.get()

    if result and result[0] and hasattr(result[0][0], 'value'):
        return result[0][0].value
    return 0
