# 🐍 Entorno Virtual y Dependencias

Este documento explica cómo usar el entorno virtual de Python (`.venv`) para este proyecto. Seguir estos pasos es **crucial** para asegurar que la aplicación funcione correctamente y que todos los colaboradores usen las mismas versiones de las librerías.

### ¿Qué es el Entorno Virtual (`.venv`)?

Imagina que es una **caja de herramientas aislada** solo para este proyecto. En lugar de instalar las librerías (como Streamlit, Google GenAI, etc.) en tu sistema global de Python, se instalan dentro de la carpeta `.venv`.

**Beneficios:**
1.  **Evita Conflictos:** Puedes tener diferentes versiones de una misma librería para diferentes proyectos sin que choquen entre sí.
2.  **Reproducibilidad:** Asegura que el entorno de producción y el de todos los desarrolladores sean idénticos, eliminando errores de "en mi máquina sí funciona".
3.  **Limpieza:** Mantiene tu instalación global de Python ordenada.

### El Ritual: Comandos Esenciales

#### 1. Activar el Entorno
Antes de instalar dependencias o ejecutar la aplicación, **siempre** debes activar el entorno.

**Comando (Windows):**
```bash
.venv\Scripts\activate
```
Sabrás que está activo porque el prompt de tu terminal cambiará para mostrar `(.venv)` al principio.

#### 2. Instalar / Actualizar Dependencias
Una vez activado el entorno, puedes instalar todas las librerías listadas en `requirements.txt` con un solo comando.

**Comando:**
```bash
pip install -r requirements.txt
```
Esto leerá el archivo y instalará las versiones exactas de cada herramienta dentro de la "caja" `.venv`.

#### 3. Ejecutar la Aplicación
Con el entorno aún activo, ejecuta la aplicación como de costumbre.

**Comando:**
```bash
python chat_bot.py
```

#### 4. Desactivar el Entorno
Cuando termines de trabajar, puedes desactivar el entorno para volver a tu terminal global.

**Comando:**
```bash
deactivate
```
El prefijo `(.venv)` desaparecerá de tu terminal.
