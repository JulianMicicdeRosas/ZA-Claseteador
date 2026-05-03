# Historial de cambios — ZA-Claseteador

---

## 2026-05-03

### feat: Abrir navegador automáticamente al iniciar
**Archivo:** `launch.command`

`launch.command` ahora lanza en background un proceso que hace polling a `127.0.0.1:7860` cada segundo (hasta 60 intentos). En cuanto el servidor responde, abre el browser automáticamente (`open` en macOS, `xdg-open` en Linux). El bootstrap continúa en primer plano como siempre.

---

### feat: Historial de sesiones, versión anterior, nombre de modelo en nav
**Archivos:** `app/ui/app.js`, `app/ui/index.html`, `prompts/default_prompt.md`

- **Historial de sesiones:** cada vez que se completa un formateo, la sesión se guarda automáticamente en `localStorage`. La pestaña Publicar muestra un repositorio de sesiones anteriores con botones Cargar y Borrar por entrada. Máximo 30 entradas guardadas.
- **Versión anterior:** al hacer Re-formatear, el formato previo se conserva. Un botón "Versión Anterior" en la pestaña Formato permite alternar entre la versión actual y la anterior (ámbar cuando está mostrando la versión anterior).
- **Modelo visible en nav:** el nombre del modelo activo aparece como badge en la barra de navegación (`qwen2.5:0.5b` por defecto).
- **Botón Re-formatear:** permite regenerar el formato con el LLM sin necesidad de volver a transcribir el video.
- **Prompt actualizado:** estructura de dos partes (widget resumen + artículos clickeables) según plantilla canónica. Ver `formato.md`.

---

## 2026-05-02

### fix: Reemplaza Gemma 4 por Qwen 2.5 0.5B en todo el proyecto
**Archivos:** `bootstrap.py`, `app/routes/system.py`, `app/ui/app.js`

Se reemplaza el modelo `gemma4:latest` por `qwen2.5:0.5b` en todos los archivos. El bootstrap ya no muestra "Gemma disponible" sino "Modelo disponible". El system check reporta el modelo correcto. El default de configuración en el frontend refleja el nuevo modelo.

---

### feat: Actualiza prompt y estructura HTML al formato clickable-line
**Archivo:** `prompts/default_prompt.md`

Se reescribe el prompt del sistema para generar HTML con estructura de dos partes: widget resumen (fondo negro, borde azul) + artículos con párrafos `clickable-line` con timecodes en doble corchete `[[YT:MM:SS]]`. Cada línea de la transcripción se convierte en un `<p>` individual con hover interactivo.

---

### feat: Redirección automática en plugin Redirection al publicar en WordPress
**Archivo:** `app/routes/publish.py`

Al subir una clase a WordPress, se crea automáticamente una entrada en el plugin Redirection que mapea `/video-clase-{N}` → URL del video de YouTube original. Usa la API REST del plugin (`POST /wp-json/redirection/v1/redirect`) con autenticación Basic (Application Password). La operación es best-effort: si falla no interrumpe la publicación.

---

### fix: Preview del resultado final muestra contenido completo
**Archivo:** `app/ui/index.html`

El iframe de preview tenía altura fija (`65vh`) que cortaba el contenido largo. Ahora se auto-ajusta al `scrollHeight` del documento interno al cargar, mostrando el HTML completo sin scroll interno.

---

### fix: Restaura el proceso de formateo con LLM en la pestaña Apuntes
**Archivos:** `app/ui/app.js`, `app/ui/index.html`

Se había eliminado por error el proceso de Gemma 4 al renombrar la pestaña. Se restaura `articlesHtml` y la función `formatWithGemma()` con el SSE buffer fix. El resultado en la pestaña Formato ahora muestra los apuntes generados por el LLM.

---

### feat: Rediseño de pestañas y mejoras de UX
**Archivos:** `app/ui/app.js`, `app/ui/index.html`

- Renombra la pestaña `Transcripción` → `Apuntes`
- Estimación de tiempo de formateo basada en conteo de palabras (~2 min por cada 2500 palabras)
- Botón `Descargar TXT` en la pestaña Apuntes para bajar la transcripción cruda
- Pestaña Resultado Final: preview arriba + editor de código abajo; botón `Modificar` aparece al detectar cambios en el código
- Pestaña Publicar: preview del nombre del archivo final (ej. `IA_Clase1.html`)
- Auto-guardado del prompt personalizado desde la pestaña de configuración

---

### fix: Buffer SSE para evitar spinner infinito en formateo
**Archivo:** `app/ui/app.js`

El parser SSE dividía cada chunk de red por `\n` asumiendo JSON completo por línea. Cuando el LLM genera HTML extenso, el mensaje final `"completado"` se parte entre varios chunks, `JSON.parse` falla en silencio y `formatting` nunca vuelve a `false` → spinner infinito.

**Solución:** buffer acumulador. Cada chunk se anexa al buffer, se extraen las líneas completas (el último fragmento incompleto se reinserta), y al cerrar el stream se flushea lo que quede. Patrón con loop `outer:` etiquetado para break desde el callback de stream.

---

## 2026-05-01

### Initial commit
**Archivos:** todos

Commit inicial del proyecto con el workspace limpio. Estructura base con FastAPI, faster-whisper, Alpine.js, Tailwind CSS. Integración con Ollama para formateo local con LLM.
