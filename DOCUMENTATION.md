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

### 2. Configuración del Entorno de Desarrollo

Para asegurar la consistencia y evitar conflictos de dependencias, el proyecto utiliza un entorno virtual de Python. Toda la información sobre cómo configurar y gestionar este entorno se encuentra en un documento dedicado.

### [**>> Guía del Entorno Virtual <<**](./VIRTUAL_ENV.md)

### 3. Arquitectura y Tecnologías

- **Frontend:** **Streamlit**.
- **Lógica de Backend:** **Python 3**, estructurado en un directorio `src/`.
- **IA:** **Google Generative AI** (modelos `gemini-2.5-flash` para imágenes y chat).
- **Base de Datos (Metadatos):** **Google Firestore**.
- **Almacenamiento de Archivos:** **Google Firebase Storage**.
- **Gestión de Secretos:** A través de `.streamlit/secrets.toml`.

### 4. Flujo de la Aplicación y Experiencia de Usuario

#### Flujo de Inicio de Sesión
El flujo de inicio de sesión es central y explícito para mejorar la accesibilidad. El usuario ingresa un "Nombre de Poder" en la página principal para acceder a la aplicación.

#### Pestañas de Funcionalidad
Una vez dentro, la interfaz se divide en tres pestañas:
1.  **🎨 Generar:** Permite la creación de imágenes. La interfaz se centra en un campo de texto donde el usuario puede escribir su visión. A través de los controles de la barra lateral, puede fusionar su idea con una estética central y un estilo artístico específico.
2.  **🔄 Transmutar:** Permite al usuario subir una imagen propia o usar la última generada para modificarla con un nuevo prompt y los mismos controles creativos.
3.  **🔥 Psycho-Chat:** Abre una interfaz de chat para conversar directamente con el Psycho-Bot. La IA está configurada con un `system_prompt` detallado que le confiere una personalidad única. **Ahora también puede ayudar a los usuarios a crear y refinar prompts** para la generación de imágenes.

### 5. Estructura del Código Modular

-   **`chat_bot.py`:** Punto de entrada mínimo.
-   **`src/config.py`:** Centraliza constantes y configuraciones.
-   **`src/firebase_utils.py`:** Encapsula la interacción con Firebase.
-   **`src/gemini_utils.py`:** Aísla la lógica de la API de Gemini para la generación de imágenes.
-   **`src/chat_logic.py`:** Contiene el `SYSTEM_PROMPT` del Psycho-Bot y la lógica para la conversación.
-   **`src/prompt_engineering.py`:** Contiene los diccionarios de estilos y la lógica para construir dinámicamente los prompts.
-   **`src/ui_components.py`:** Contiene funciones reutilizables para la UI.
-   **`src/main_ui.py`:** Orquestador principal que construye la interfaz.

### 6. Depuración y Monitoreo

Para facilitar la depuración y observar el comportamiento de la aplicación en tiempo real, se ha implementado un sistema de logging centralizado utilizando el módulo `logging` de Python.

-   **Configuración:** La configuración del logger se define en la función `setup_logging()` dentro de `src/config.py`.
-   **Inicialización:** El logging se activa al inicio de la aplicación en `chat_bot.py`.
-   **Puntos de Log Clave:** Se registran interacciones con la API de Google, así como eventos de limitación de usuarios (cooldown, límite diario).

### 7. Control de Costos y Límites de Uso (Rate Limiting)

Para garantizar la sostenibilidad del proyecto, se han implementado dos mecanismos de control:

-   **Límite Diario Global:** Un número máximo de generaciones de imágenes por día para todos los usuarios.
-   **Enfriamiento (Cooldown) por Usuario:** Un período de espera obligatorio para cada usuario entre solicitudes.

### 8. Parámetros de Creación

La interfaz ofrece un control granular sobre el proceso creativo a través de una serie de controles en la barra lateral.

#### Jerarquía de Control

1.  **Modo RAW (Sin Estilos):** Un `checkbox` que actúa como un interruptor maestro. Si está activado, **ignora todas las demás opciones creativas** y utiliza únicamente el texto del prompt del usuario. Es la forma más pura de interactuar con el modelo.

2.  **🧠 Estética Central:** Un menú desplegable para seleccionar la **temática filosófica y visual** de la imagen. Define el "qué" se está representando (ej. `anarcho_punk`, `chaos_magick`, `cypherpunk`). Si se selecciona `none`, no se aplica ninguna temática.

3.  **🎨 Estilo Artístico:** Un menú desplegable para seleccionar la **técnica visual** de la imagen. Define el "cómo" se representa (ej. `photorealistic`, `sketch`, `anime_fusion`). Si se selecciona `none`, no se aplica ninguna técnica específica.

#### Parámetros de Modulación

-   **🌀 Nivel de Glitch:** Slider que controla la intensidad de los artefactos visuales y la estética "glitch".
-   **🔥 Nivel de Caos:** Slider que define el nivel de desorden y energía en la composición.

#### Parámetros de la IA

-   **🤖 Temperatura, Top-P, Top-K:** Sliders que ajustan el comportamiento interno del modelo de IA (creatividad, coherencia, diversidad).

### 9. Arquitectura de Datos (Firebase)

-   **Firestore:**
    -   `usuarios/{user_uuid}/user_images/{image_id}`: Guarda los metadatos de cada imagen.
    -   `daily_limits/{YYYY-MM-DD}`: Documento que actúa como contador para el límite diario global.
-   **Storage:** Las imágenes se almacenan en `psycho_generator_images/{user_uuid}/{filename}.png`.

---

### 10. Roadmap

-   [x] **Ingeniería de Prompts y Personalidad del Modelo:** Completado.
-   [x] **Añadir Pestaña de Chatbot:** Completado.
-   [x] **Evolución del Prompting:** Completado.

#### Próximos Pasos
-   [ ] **Galería de Creaciones:** Implementar una nueva pestaña donde los usuarios puedan ver un historial de todas las imágenes que han generado.
-   [ ] **Memoria del Chat:** Persistir las conversaciones del Psycho-Bot en Firestore.

---

### 11. Panel de Administración (Observatorio Secreto)

El proyecto incluye un panel de administración local (`admin_dashboard.py`) optimizado para reducir costos de lectura en Firebase.