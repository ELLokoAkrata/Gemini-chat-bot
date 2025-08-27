## Documentación del Proyecto: Akelarre Generativo

### 1. Resumen General

El proyecto es una aplicación web interactiva construida con **Streamlit**, concebida como un "Akelarre Generativo". Permite a los usuarios generar y modificar imágenes utilizando la API de **Google Generative AI (Gemini)**. La aplicación tiene una estética "hacker" y una temática "psicodélica/anarco-punk", y está diseñada como una herramienta creativa sin filtros de contenido explícitos.

Los usuarios pueden:
- Iniciar sesión con un "Nombre de Poder" único para asociar sus creaciones.
- Generar imágenes a partir de una combinación de texto y símbolos (emojis).
- Modificar imágenes recién generadas o subir sus propias imágenes para alterarlas.
- Descargar sus creaciones.

Toda la infraestructura de backend (autenticación, metadatos y almacenamiento) se gestiona a través de **Google Firebase**.

### 2. Arquitectura y Tecnologías

- **Frontend:** **Streamlit**.
- **Lógica de Backend:** **Python 3**, estructurado en un directorio `src/` para modularidad.
- **IA / Generación de Imágenes:** **Google Generative AI** (`gemini-2.5-flash-image-preview`).
- **Base de Datos (Metadatos):** **Google Firestore**.
- **Almacenamiento de Archivos:** **Google Firebase Storage**.
- **Gestión de Secretos:** A través de `.streamlit/secrets.toml`.

### 3. Flujo de la Aplicación y Experiencia de Usuario

#### Flujo de Inicio de Sesión
Para mejorar la accesibilidad, especialmente en dispositivos móviles, el flujo de inicio de sesión es central y explícito:
1.  **Vista de Bienvenida:** Al entrar, el usuario ve una guía de iniciación y el formulario de login directamente en la página principal.
2.  **Autenticación:** El usuario ingresa un "Nombre de Poder". El sistema verifica en Firestore si el nombre ya existe. Si no, crea un nuevo perfil de usuario con un UUID único.
3.  **Acceso al Akelarre:** Una vez autenticado, la vista principal cambia para mostrar la interfaz de generación de imágenes. La información del usuario y el botón de cierre de sesión se mueven a la barra lateral.

#### Interfaz de Generación
-   **Título y Manifiesto:** La aplicación recibe al usuario con el título "Akelarre Generativo with Psycho-Bot" y un breve manifiesto.
-   **Invocación Directa:** La interfaz se ha purificado a un único campo de texto. Se invita al usuario a escribir su visión directamente, permitiendo el uso de texto, emojis desde su teclado, o una combinación de ambos.
-   **Ingeniería de Prompts:** Cada entrada del usuario es procesada por un sistema de "meta-prompting". Este sistema traduce los emojis conocidos a conceptos textuales y envuelve la solicitud del usuario en una instrucción maestra que dota a la IA de una personalidad y estética base (anarco-punk, ciberpunk, etc.), asegurando resultados coherentes con la temática.

### 4. Estructura del Código Modular

El código fuente está organizado en el directorio `src/` para separar las responsabilidades:
-   **`chat_bot.py`:** Punto de entrada mínimo.
-   **`src/config.py`:** Centraliza constantes y configuraciones.
-   **`src/firebase_utils.py`:** Encapsula la interacción con Firebase.
-   **`src/gemini_utils.py`:** Aísla la lógica de la API de Gemini.
-   **`src/prompt_engineering.py`:** Contiene el meta-prompt, el "grimorio" de traducción de emojis y la lógica para construir el prompt final.
-   **`src/ui_components.py`:** Contiene funciones reutilizables para la UI (formularios, visualizadores de imágenes, etc.).
-   **`src/main_ui.py`:** Orquestador principal que construye la interfaz y gestiona el flujo de la aplicación.

### 5. Arquitectura de Datos (Firebase)

-   **Firestore:** Los datos se guardan en `usuarios/{user_uuid}/user_images/{image_id}`. Cada documento de imagen almacena tanto el `user_prompt` (la entrada original del usuario) como el `final_prompt` (el prompt completo enviado a la IA).
-   **Storage:** Las imágenes se almacenan en `psycho_generator_images/{user_uuid}/{filename}.png`.

---

### 6. Próximos Pasos (Roadmap)

-   [x] **Ingeniería de Prompts y Personalidad del Modelo:**
    -   [x] **Personalidad Base:** Implementado un sistema de "meta-prompting" para una estética coherente.
    -   [x] **Estilos Artísticos:** La personalidad base ya fusiona múltiples estilos.
    -   [x] **Prompts con Emojis:** Implementado un intérprete que traduce emojis a conceptos textuales.

-   [ ] **Añadir Pestaña de Chatbot:**
    -   [ ] Implementar una nueva pestaña en la interfaz que contenga un chatbot conversacional, utilizando un modelo de lenguaje de Gemini para interactuar con el usuario.
