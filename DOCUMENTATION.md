## Documentación del Proyecto: Akelarre Generativo

### 1. Resumen General

El proyecto es una aplicación web interactiva construida con **Streamlit**, concebida como un "Akelarre Generativo". Permite a los usuarios generar imágenes y conversar con una IA de personalidad definida. La aplicación tiene una estética "hacker" y una temática "psicodélica/anarco-punk", y está diseñada como una herramienta creativa sin filtros de contenido explícitos.

Los usuarios pueden:
- Iniciar sesión con un "Nombre de Poder" único.
- Generar imágenes a partir de una combinación de texto y emojis.
- Modificar imágenes existentes.
- Conversar con el "Psycho-Bot", una IA con una personalidad anarco-punk definida.
- Descargar sus creaciones.

Toda la infraestructura de backend se gestiona a través de **Google Firebase**.

### 2. Arquitectura y Tecnologías

- **Frontend:** **Streamlit**.
- **Lógica de Backend:** **Python 3**, estructurado en un directorio `src/`.
- **IA:** **Google Generative AI** (modelos `gemini-2.5-flash` para imágenes y chat).
- **Base de Datos (Metadatos):** **Google Firestore**.
- **Almacenamiento de Archivos:** **Google Firebase Storage**.
- **Gestión de Secretos:** A través de `.streamlit/secrets.toml`.

### 3. Flujo de la Aplicación y Experiencia de Usuario

#### Flujo de Inicio de Sesión
El flujo de inicio de sesión es central y explícito para mejorar la accesibilidad. El usuario ingresa un "Nombre de Poder" en la página principal para acceder a la aplicación.

#### Pestañas de Funcionalidad
Una vez dentro, la interfaz se divide en tres pestañas:
1.  **🎨 Generar:** Permite la creación de imágenes. La interfaz se centra en un campo de texto donde el usuario puede escribir su visión, combinando texto y emojis. Cada prompt es procesado por un sistema de "meta-prompting" que dota a la IA de una estética base coherente.
2.  **🔄 Transmutar:** Permite al usuario subir una imagen propia o usar la última generada para modificarla con un nuevo prompt.
3.  **🔥 Psycho-Chat:** Abre una interfaz de chat para conversar directamente con el Psycho-Bot. La IA está configurada con un `system_prompt` detallado que le confiere una personalidad única, rebelde y filosófica. El historial de la conversación es efímero y se mantiene solo durante la sesión actual.

### 4. Estructura del Código Modular

-   **`chat_bot.py`:** Punto de entrada mínimo.
-   **`src/config.py`:** Centraliza constantes y configuraciones.
-   **`src/firebase_utils.py`:** Encapsula la interacción con Firebase.
-   **`src/gemini_utils.py`:** Aísla la lógica de la API de Gemini para la generación de imágenes.
-   **`src/chat_logic.py`:** Contiene el `SYSTEM_PROMPT` del Psycho-Bot y la lógica para la conversación.
-   **`src/prompt_engineering.py`:** Contiene el meta-prompt para la generación de imágenes.
-   **`src/ui_components.py`:** Contiene funciones reutilizables para la UI.
-   **`src/main_ui.py`:** Orquestador principal que construye la interfaz.

### 5. Depuración y Monitoreo

Para facilitar la depuración y observar el comportamiento de la aplicación en tiempo real, se ha implementado un sistema de logging centralizado utilizando el módulo `logging` de Python.

-   **Configuración:** La configuración del logger se define en la función `setup_logging()` dentro de `src/config.py`. Establece el nivel de log en `INFO` y formatea los mensajes para incluir timestamp, nivel y nombre del logger, imprimiendo todo en la salida estándar (terminal).
-   **Inicialización:** El logging se activa al inicio de la aplicación mediante una llamada a `setup_logging()` en `chat_bot.py`.
-   **Puntos de Log Clave:**
    -   En `src/gemini_utils.py`, se registran logs `INFO`, `WARNING` y `ERROR` para monitorear las interacciones con la API de Google.
    -   En `src/main_ui.py`, se registran logs de `WARNING` cada vez que un usuario es bloqueado por el cooldown o por el límite diario global, permitiendo monitorear la frecuencia de estas restricciones.

### 6. Control de Costos y Límites de Uso (Rate Limiting)

Para garantizar la sostenibilidad del proyecto y prevenir abusos, se han implementado dos mecanismos de control de uso:

-   **Límite Diario Global:** La aplicación permite un número máximo de generaciones de imágenes por día para todos los usuarios combinados.
    -   **Implementación:** Se utiliza una colección `daily_limits` en Firestore para llevar un conteo atómico de las imágenes generadas cada día (identificado por `YYYY-MM-DD`).
    -   **Configuración:** El límite se define en `src/config.py` con la constante `MAX_IMAGES_PER_DAY`.

-   **Enfriamiento (Cooldown) por Usuario:** Se ha establecido un período de espera obligatorio para cada usuario entre solicitudes de generación o modificación de imágenes.
    -   **Implementación:** Se utiliza `st.session_state` para almacenar la marca de tiempo de la última solicitud del usuario, validando el tiempo transcurrido en cada nueva petición.
    -   **Configuración:** El tiempo de espera se define en `src/config.py` con la constante `USER_COOLDOWN_SECONDS`.

### 7. Arquitectura de Datos (Firebase)

-   **Firestore:**
    -   `usuarios/{user_uuid}/user_images/{image_id}`: Guarda los metadatos de cada imagen.
    -   `daily_limits/{YYYY-MM-DD}`: Documento que actúa como contador para el límite diario global.
-   **Storage:** Las imágenes se almacenan en `psycho_generator_images/{user_uuid}/{filename}.png`.

---

### 8. Roadmap

-   [x] **Ingeniería de Prompts y Personalidad del Modelo:** Completado.
-   [x] **Añadir Pestaña de Chatbot:** Completado.

#### Próximos Pasos
-   [ ] **Galería de Creaciones:** Implementar una nueva pestaña donde los usuarios puedan ver un historial de todas las imágenes que han generado.
-   [ ] **Memoria del Chat:** Persistir las conversaciones del Psycho-Bot en Firestore, permitiendo a los usuarios retomar conversaciones pasadas.
-   [ ] **Evolución del Prompting:** Añadir un selector en la UI para que el usuario pueda elegir entre diferentes "personalidades" o "estéticas base" para la generación de imágenes.

---

### 9. Panel de Administración (Observatorio Secreto)

El proyecto incluye un panel de administración local (`admin_dashboard.py`) que ha sido optimizado para reducir costos de lectura en Firebase. Ahora muestra métricas globales (total de usuarios e imágenes) y una lista de usuarios registrados. Está excluido del repositorio y protegido por contraseña.