# 🌀 Guía para Subir Cambios al Void Digital

## Pre-requisitos
- Tener Git instalado
- Tener acceso al repositorio
- Terminal PowerShell abierta

## 🧠 Comandos Paso a Paso

### 1. Verificar el Estado
```powershell
git status
```
Este comando te mostrará qué archivos han sido modificados.

### 2. Navegar al Directorio
```powershell
cd Gemini-chat-bot
```
Asegúrate de estar en el directorio correcto.

### 3. Agregar Cambios
Para un archivo específico:
```powershell
git add chat_bot.py
```

Para todos los cambios:
```powershell
git add .
```

### 4. Crear el Commit
```powershell
git commit -m "🌀 Descripción de los cambios locos que hiciste"
```
Usa emojis para hacer más psycho tus commits:
- 🌀 Para cambios generales
- 🧠 Para cambios en la lógica
- 💊 Para fixes
- 🎭 Para cambios en la interfaz
- ⚡ Para optimizaciones

### 5. Subir al Repositorio
```powershell
git push origin main
```

## ⚠️ Solución de Problemas

### Si hay conflictos:
```powershell
git pull origin main
# Resolver conflictos
git add .
git commit -m "💊 Resolviendo conflictos en la matrix"
git push origin main
```

### Si necesitas deshacer cambios:
```powershell
# Deshacer último commit (manteniendo cambios)
git reset --soft HEAD~1

# Deshacer cambios en un archivo
git checkout -- chat_bot.py
```

## 🎭 Flujo Completo de Ejemplo

```powershell
# 1. Verificar estado
git status

# 2. Ir al directorio
cd Gemini-chat-bot

# 3. Agregar cambios
git add chat_bot.py

# 4. Crear commit
git commit -m "🧠 Mejoras en el system prompt y optimización de la interfaz"

# 5. Subir cambios
git push origin main
```

## 🌌 Notas Importantes
- Siempre verifica el estado antes de hacer cambios
- Usa mensajes descriptivos en tus commits
- Si algo sale mal, no entres en pánico, todo se puede resolver
- Mantén la coherencia en el caos

## 💀 Advertencias
- No hagas force push a menos que sea absolutamente necesario
- Siempre haz pull antes de empezar a trabajar
- Mantén backups de tus cambios importantes
- No temas al void, él es tu amigo 