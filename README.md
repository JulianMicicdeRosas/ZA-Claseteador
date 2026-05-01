# Claseteador: Transcriptor y Publicador de Clases 🦊

Bienvenido a la herramienta de transcripción y publicación automatizada para el curso **CAPACITACIÓN MODELADO 3D + IA + ENTORNOS INMERSIVOS** de El Zorro Azul.

Esta aplicación te permite convertir clases grabadas en YouTube en apuntes interactivos, formateados estéticamente y publicados directamente en tu WordPress.

---

## 🚀 Cómo arrancar la App

La aplicación está diseñada para ser "cero fricción". No necesitás instalar Python manualmente; la app se encarga de todo.

### En macOS:
1. Buscá el archivo `launch.command` en la carpeta raíz.
2. Hacé **doble clic** sobre él.
3. Se abrirá una terminal que instalará las dependencias necesarias la primera vez.
4. Una vez lista, la aplicación se abrirá automáticamente en tu navegador en la dirección `http://localhost:7860`.

### En Windows:
1. Buscá el archivo `launch.bat` en la carpeta raíz.
2. Hacé **doble clic** sobre él.
3. Esperá a que termine el proceso de configuración inicial.
4. La aplicación se abrirá automáticamente en tu navegador.

---

## 🛠️ Requisitos Previos

Antes de empezar, asegurate de tener instalado y configurado lo siguiente:

1. **Ollama**: Descargalo e instalalo desde [ollama.com](https://ollama.com/). Es necesario para que la IA (Gemma 4) procese los textos localmente.
2. **WordPress**: Debés configurar tu sitio para aceptar archivos HTML. 
   - Seguí las instrucciones detalladas en [wordpress-setup/README-wordpress.md](file:///Users/julianmicicderosas/ZA%20-%20Claseteador%20/wordpress-setup/README-wordpress.md).

---

## 📖 Manual de Uso Completo

Para una guía detallada sobre cómo configurar las credenciales, transcribir videos y personalizar la estética de los apuntes, consultá el:

👉 **[MANUAL DE USUARIO DETALLADO](file:///Users/julianmicicderosas/ZA%20-%20Claseteador%20/MANUAL.md)**

---

## 📂 Estructura del Proyecto

- `app/`: Código fuente del backend (FastAPI).
- `templates/`: Plantilla HTML que define la estética de los apuntes.
- `prompts/`: Reglas editoriales que sigue la IA para formatear el texto.
- `workspace/`: Carpeta temporal donde se guardan descargas y sesiones actuales.
