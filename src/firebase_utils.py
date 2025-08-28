import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
from google.cloud.firestore_v1.base_query import FieldFilter
import uuid
from datetime import timedelta, datetime, timezone
from src.config import STORAGE_ROOT_FOLDER, MAX_IMAGES_PER_DAY

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

def check_daily_limit(db):
    """
    Verifica si se ha alcanzado el límite diario de generación de imágenes.
    Retorna True si el límite fue alcanzado, False en caso contrario.
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    limit_ref = db.collection("daily_limits").document(today_str)
    limit_doc = limit_ref.get()

    if limit_doc.exists:
        count = limit_doc.to_dict().get("image_count", 0)
        if count >= MAX_IMAGES_PER_DAY:
            return True  # Límite alcanzado
    return False # Límite no alcanzado

def increment_daily_count(db):
    """
    Incrementa el contador de imágenes para el día actual.
    Usa una transacción para seguridad en concurrencia.
    """
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    limit_ref = db.collection("daily_limits").document(today_str)
    
    # Usamos una transacción para asegurar que el incremento sea atómico
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

# --- Funciones para el Dashboard de Administración ---

def get_project_specific_users(db):
    """
    Recupera solo los usuarios que han generado imágenes para el proyecto
    'psycho_generator_images'.
    """
    images_group_ref = db.collection_group('user_images')
    
    start_at = f"{STORAGE_ROOT_FOLDER}/"
    end_at = start_at + "\uf8ff"

    query = images_group_ref.where(filter=FieldFilter("storage_path", ">=", start_at)) \
                            .where(filter=FieldFilter("storage_path", "<", end_at))
    
    user_uuids = set()
    for doc in query.stream():
        # Extraemos el UUID del usuario del path del documento
        user_uuid = doc.reference.parent.parent.id
        user_uuids.add(user_uuid)
        
    # Ahora, obtenemos los datos de los usuarios únicos que encontramos
    users_data = []
    for uuid in user_uuids:
        user_ref = db.collection("usuarios").document(uuid)
        user_doc = user_ref.get()
        if user_doc.exists:
            users_data.append(user_doc.to_dict())
            
    return users_data


def get_total_image_count(db):
    """
    Realiza una consulta de agregación para obtener el número total de imágenes
    del proyecto 'psycho_generator_images'.
    Esta operación es muy eficiente en costes (1 lectura).
    Retorna un número entero.
    """
    images_group_ref = db.collection_group('user_images')
    
    start_at = f"{STORAGE_ROOT_FOLDER}/"
    end_at = start_at + "\uf8ff"

    query = images_group_ref.where(filter=FieldFilter("storage_path", ">=", start_at)) \
                            .where(filter=FieldFilter("storage_path", "<", end_at))
    
    # Realizamos la consulta de agregación para contar los documentos
    aggregate_query = query.count()
    result = aggregate_query.get()
    
    # El resultado es una lista que contiene otra lista con el resultado.
    if result and result[0] and hasattr(result[0][0], 'value'):
        return result[0][0].value
    return 0



def get_image_public_url(storage_path: str):
    """Genera una URL pública y firmada para un archivo en Firebase Storage."""
    bucket = storage.bucket()
    blob = bucket.blob(storage_path)
    # La URL expira en 1 hora, suficiente para la visualización en el dashboard
    return blob.generate_signed_url(version="v4", expiration=timedelta(minutes=60))