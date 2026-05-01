# Manual de Usuario - Claseteador 🦊

Esta guía te explica paso a paso cómo configurar y utilizar la aplicación para transcribir y publicar tus clases.

## 1. Configuración Inicial (Una sola vez)

Antes de poder publicar en WordPress, necesitás configurar la conexión entre la App y tu sitio web.

### A. Preparar WordPress
1. **Habilitar subida de HTML**: Copiá el archivo `wordpress-setup/allow-html-uploads.php` a la carpeta `wp-content/mu-plugins/` de tu servidor (vía FTP o Administrador de Archivos de Namecheap).
2. **Obtener Contraseña de Aplicación**:
   - Entrá a tu WP Admin -> Usuarios -> Tu Perfil.
   - Buscá "Application Passwords".
   - Creá una nueva llamada "Claseteador" y copiá el código generado.

### B. Configurar la App
1. Abrí la aplicación (usando `launch.command` o `launch.bat`).
2. Hacé clic en el **ícono de engranaje (Configuración)**.
3. Completá los campos:
   - **URL de WordPress**: `https://elzorroazul.studio`
   - **Usuario**: Tu nombre de usuario en WordPress.
   - **Contraseña de Aplicación**: La que generaste en el paso anterior.
   - **Defaults**: Podés definir quién dicta la clase y quién hace la revisión técnica por defecto.
4. Hacé clic en **"Probar conexión"**. Si aparece un tilde verde, la configuración es correcta.

---

## 2. Flujo de Trabajo: De YouTube a WordPress

La aplicación se divide en 4 pestañas principales:

### Paso 1: Inicio (Carga del Video)
1. **Link de YouTube**: Pegalo siempre. Es obligatorio porque la app lo usa para generar los botones interactivos **"▶ Ir al video"** y obtener el título de la clase.
2. **Video Local (Opcional)**: Si ya tenés el video descargado, seleccionalo en el área de "Cargar video local". Esto hará que la transcripción sea mucho más rápida.
3. **Analizar**: Hacé clic en este botón. Si cargaste un video local pero olvidaste el link de YouTube, la app te lo recordará.
4. **Transcribir**: Una vez que veas la miniatura del video, hacé clic para comenzar.

### Paso 2: Transcripción
- La app descargará el audio y comenzará a transcribir usando Whisper.
- Verás el progreso en tiempo real.
- Al terminar, verás el texto con marcas de tiempo (timecodes) como `[05:23]`.
- **Podés editar el texto manualmente** si detectás errores de nombres propios o términos técnicos antes de pasar al siguiente paso.
- Hacé clic en **"Dar formato"**.

### Paso 3: Formato (IA Gemma 4)
- La IA procesará el texto para convertirlo en un apunte estructurado.
- **Preview**: A la izquierda verás cómo quedará el apunte final con la estética de El Zorro Azul.
- **Editor**: A la derecha verás el código HTML generado. Si sabés un poco de HTML, podés hacer ajustes finales aquí.
- Los timecodes se convierten automáticamente en botones de **"▶ Ir al video"** que abren YouTube en el segundo exacto.

### Paso 4: Publicar
- **Nomenclatura**: Definí el prefijo del curso (ej: `ZA_IA`).
- **Clase #**: Seleccioná el número de clase.
- **Estilo de Nombre**: Elegí entre el nombre simple (`Prefijo_ClaseX.html`) o descriptivo (`Prefijo_ClaseX_Apuntes.html`).
- Tenés dos opciones:
  1. **Guardar Archivo Local**: Descarga el archivo `.html` en tu computadora con el nombre generado.
  2. **Subir a WordPress**: Envía el archivo directamente a tu sitio.

---

## 3. Personalización Avanzada

### Editar la Estética (Template)
Si querés cambiar colores, fuentes o el logo, podés editar el archivo `templates/base.html`. Los cambios se verán reflejados inmediatamente en la pestaña de "Formato".

### Editar las Reglas de la IA (Prompt)
Si sentís que la IA está resumiendo demasiado o querés que use un tono diferente, podés ajustar las instrucciones en la pestaña de **Configuración -> Prompt**. Allí podés restaurar el original si cometés algún error.

---

## 4. Solución de Problemas

- **La App no arranca**: Asegurate de tener instalada la última versión de Python (o dejá que `uv` lo haga por vos) y que no haya otra app usando el puerto 7860.
- **Error en Ollama**: Asegurate de que la aplicación Ollama esté abierta y corriendo en tu computadora.
- **Falla la subida a WordPress**: Verificá que el archivo `allow-html-uploads.php` esté correctamente subido al servidor. Sin él, WordPress rechazará el archivo por ser formato HTML.
