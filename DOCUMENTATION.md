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

### 5. Arquitectura de Datos (Firebase)

-   **Firestore:** Los datos de imágenes se guardan en `usuarios/{user_uuid}/user_images/{image_id}`.
-   **Storage:** Las imágenes se almacenan en `psycho_generator_images/{user_uuid}/{filename}.png`.

---

### 6. Roadmap

-   [x] **Ingeniería de Prompts y Personalidad del Modelo:** Completado.
-   [x] **Añadir Pestaña de Chatbot:** Completado.

#### Próximos Pasos
-   [ ] **Galería de Creaciones:** Implementar una nueva pestaña donde los usuarios puedan ver un historial de todas las imágenes que han generado.
-   [ ] **Memoria del Chat:** Persistir las conversaciones del Psycho-Bot en Firestore, permitiendo a los usuarios retomar conversaciones pasadas.
-   [ ] **Evolución del Prompting:** Añadir un selector en la UI para que el usuario pueda elegir entre diferentes "personalidades" o "estéticas base" para la generación de imágenes.

---

### 7. Panel de Administración (Observatorio Secreto)

El proyecto incluye un panel de administración local (`admin_dashboard.py`) para monitorear la actividad de la aplicación. Está excluido del repositorio y protegido por contraseña. Para más detalles, ver la sección correspondiente en la documentación anterior.