# Ψ-Psycho Image Generator

*Portal de Imágenes Artificiales creado con la tecnología de EsquizoAI + Google AI*

Este proyecto es una aplicación de generación de imágenes construida con Streamlit y Google Generative AI (Gemini), diseñada para proporcionar una experiencia interactiva-generativa

## 🌀 Demostración
Puedes experimentar el generador de imágenes a través del siguiente portal: [Ψ-Psycho Image Generator](https://gemini-psycho.streamlit.app/)

## 🧠 Características

- **Inicio de Sesión**: Los usuarios pueden acceder con un nombre de poder (máximo 8 caracteres) para mantener un registro de sus creaciones.
- **Generación de Imágenes**: Genera imágenes  a partir de prompts de texto.
- **Modificación de Imágenes**: Transforma imágenes existentes con nuevos prompts, alterando su realidad.
- **Subida de Imágenes**: Permite subir tus propias imágenes para modificarlas (recomendado 1024 x 1024).
- **Almacenamiento en Firebase**: Todas las creaciones se guardan automáticamente para su posterior acceso.
- **Interfaz con Tabs**: Organización intuitiva con pestañas para generación y modificación.
- **Ejemplos de Prompts**: Colección de prompts sugeridos para inspirar tus creaciones.

## 🔮 Tecnologías Utilizadas

- `streamlit`: Para la interfaz de usuario y la ejecución del portal dimensional.
- `firebase_admin`: Para la autenticación y el almacenamiento de datos e imágenes.
- `google.generativeai`: Para la generación y modificación de imágenes utilizando el modelo Gemini.
- `PIL`: Para el procesamiento de imágenes en formato Python.

## ⚙️ Configuración

### Credenciales de Firebase

Las credenciales se almacenan de manera segura como secretos en Streamlit y se utilizan para inicializar y autenticar el acceso a Firestore y Storage.

### Modelo de IA de Google

El proyecto utiliza el modelo `gemini-2.0-flash-exp-image-generation` configurado para maximizar la creatividad y minimizar la restricciones:
- Alta temperatura para aumentar la creatividad
- Configurado para devolver tanto texto como imágenes

## 🚀 Uso

1. Visita el [portal dimensional](https://gemini-psycho.streamlit.app/).
2. Introduce tu nombre de poder (máximo 8 caracteres) para iniciar tu viaje.
3. Genera imágenes escribiendo prompts o seleccionando ejemplos predefinidos.
4. Modifica las imágenes generadas inmediatamente o sube tus propias imágenes para transformarlas.
5. Descarga tus creaciones para guardarlas en tu realidad local.

## 💡 Inspiración para Prompts

- Combina estilos artísticos: "Create a cyberpunk cityscape with art nouveau elements"
- Fusiona conceptos opuestos: "Generate a peaceful war scene with mechanical flowers"
- Experimenta con estados alterados: "Create a psychedelic portrait of consciousness fragmentation"
- Desafía la realidad: "Generate a scene where time flows backwards and gravity is reversed"

## 🔬 Desarrollo y Contribuciones

Si deseas contribuir al proyecto o personalizarlo, puedes clonar el repositorio y seguir las instrucciones de configuración proporcionadas en la documentación.

## 📜 Licencia

Este proyecto está bajo una licencia MIT. Para más detalles, consulta el archivo `LICENSE` en el repositorio.

## 📡 Contacto

Si tienes preguntas o comentarios sobre el generador de imágenes, no dudes en abrir un issue en el repositorio del proyecto.

---

*Ψ Sistema EsquizoAI v2.3.5 | Realidad: Beta*
