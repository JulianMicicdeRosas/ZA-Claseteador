# App de Transcripción y Publicación de Clases
## Documento de Especificación Técnica para Antigravity — v2

> Curso: **CAPACITACIÓN MODELADO 3D + IA + ENTORNOS INMERSIVOS — El Zorro Azul**
> 24 clases · Videos no-listados en YouTube · Publicación como media en WP
> Versión 2.0 — Incorpora código 1 como referencia estética

---

## 1. Visión general

App local multiplataforma (macOS / Windows) que toma un link de YouTube no-listado de una clase, la transcribe con Whisper, la reformatea con Gemma 4 respetando la estética de El Zorro Azul, permite editar, y publica automáticamente el HTML resultante como **archivo de medios** en el WordPress del sitio.

Principios:

- **Un solo ejecutable, cero fricción** — doble clic y funciona.
- **Estética encapsulada en una template editable** — no en cada prompt.
- **Gemma 4 solo decide contenido**, no estilos.
- **Portable** entre computadoras vía export/import de configuración.

---

## 2. Arquitectura de dos capas (clave)

Este es el cambio estructural más importante respecto de la v1 del spec:

```
┌──────────────────────────────┐       ┌──────────────────────────────┐
│  templates/base.html         │       │  prompts/default_prompt.md   │
│  ─ Estética completa         │       │  ─ Reglas editoriales        │
│  ─ CSS, fuentes, JS glitch   │       │  ─ Cuándo usar H2            │
│  ─ JS de "Ir al video"       │       │  ─ Cómo marcar timecodes     │
│  ─ Header con placeholders   │       │  ─ Tono, estructura          │
│  ─ Slot {{ content }}        │       │  ─ Qué puede y qué no        │
│  EDITABLE DESDE LA UI        │       │  EDITABLE DESDE LA UI        │
└──────────────┬───────────────┘       └──────────────┬───────────────┘
               │                                      │
               │                                      ▼
               │                     ┌──────────────────────────────┐
               │                     │  Gemma 4 genera:             │
               │                     │  <article>...</article>      │
               │                     │  <article>...</article>      │
               │                     │  (solo los bloques de cont.) │
               │                     └──────────────┬───────────────┘
               │                                    │
               └──────────────┬─────────────────────┘
                              ▼
               ┌──────────────────────────────┐
               │  Template engine (Jinja2)    │
               │  inyecta content en la       │
               │  template → HTML final       │
               └──────────────────────────────┘
```

**Ventajas**:

- Si querés cambiar colores, fuentes o animaciones: editás un archivo, no reentrenás el prompt.
- Gemma 4 se equivoca menos porque su tarea es más acotada.
- Menos tokens por llamada, más barato y más rápido.
- Consistencia visual garantizada entre las 24 clases.

---

## 3. Stack técnico

| Capa | Tecnología | Notas |
|------|------------|-------|
| Runtime | Python 3.11+ via `uv` | `uv` instala Python automáticamente. |
| Backend | FastAPI + Uvicorn | Liviano, async, SSE para progreso. |
| Frontend | HTML + Alpine.js + Tailwind CDN | Sin build step. |
| Transcripción | `faster-whisper` | 4x más rápido que `openai-whisper`. |
| Descarga YouTube | `yt-dlp` | Funciona con no-listados sin auth. |
| Formateo AI | Ollama + Gemma 4 | Local, vía `localhost:11434`. |
| Template engine | Jinja2 | Inyecta content en la template HTML. |
| WordPress | REST API `/wp/v2/media` | Con Application Password. |
| Empaquetado | `launch.command` / `launch.bat` | Ejecutables doble clic. |

---

## 4. Flujo de usuario

**Primera vez** (una vez por computadora):

1. Doble clic en `launch.command` (Mac) o `launch.bat` (Windows).
2. Terminal mínima: `✓ Python · ✓ Whisper · ✓ Ollama · ✓ Gemma 4 · → Abriendo app…`
3. Modal de setup en la UI: URL de `elzorroazul.studio`, usuario, Application Password, y dos nombres por defecto: "Clase dictada por" (default) y "Revisión técnica por" (opcional, puede quedar vacío).
4. Test de conexión → ✓ → Continuar.

**Uso normal**:

1. **Pestaña Inicio**: pegás link de YouTube → clic "Analizar" → muestra título, duración, estimación.
2. Clic **"Transcribir"** → barra de progreso animada.
3. Auto-salta a **Transcripción**: texto con timecodes `[MM:SS]`, editable.
4. Clic **"Dar formato"** → Gemma 4 procesa.
5. **Formato**: preview del HTML final (renderizado) a la izquierda, código editable a la derecha.
6. Clic **"Publicar"** → pestaña **Publicar**:
   - Selector de clase (1–24)
   - Slug auto-sugerido, editable
   - **Clase dictada por** (input, pre-completado con el default, editable por clase)
   - **Revisión técnica por** (input opcional, pre-completado con el default si hay, editable por clase)
   - Dos botones: **Descargar local** · **Subir a WordPress**
7. Al subir: tilde verde + URL del archivo en WP (clickeable).

---

## 5. Detección de sistema y auto-instalación

Script `bootstrap.py` que corre siempre al arrancar:

```python
def bootstrap():
    sistema = detectar_sistema()          # darwin / windows / linux
    arch = detectar_arch()                # arm64 / x86_64
    gpu = detectar_gpu()                  # cuda / metal / cpu
    ram_gb = detectar_ram()

    if not uv_instalado():
        instalar_uv(sistema)

    if not venv_existe():
        run("uv venv")
        run("uv pip install -r requirements.txt")

    if not ollama_corriendo():
        mostrar_instruccion_ollama()

    if not modelo_gemma_descargado():
        run("ollama pull gemma:4b")

    guardar_system_info()
    lanzar_servidor()
```

**Endpoint `/api/system-check`** devuelve:

```json
{
  "python":   { "ok": true, "version": "3.11.8" },
  "whisper":  { "ok": true, "version": "1.0.3" },
  "ollama":   { "ok": true, "running": true },
  "gemma":    { "ok": true, "model": "gemma:4b" },
  "gpu":      { "ok": true, "type": "metal" },
  "ready":    true
}
```

UI: solo muestra tildes verdes. Si algo falla: cruz roja + botón "Reintentar" + nota breve.

---

## 6. Estimación de tiempo de transcripción

```
tiempo_estimado = duracion_video / factor_velocidad(modelo, hardware)
```

Tabla de factores (aproximados):

| Modelo | CPU moderno | Metal (Apple) | CUDA |
|--------|-------------|----------------|------|
| tiny   | 30x         | 50x            | 80x  |
| base   | 16x         | 30x            | 50x  |
| small  | 6x          | 15x            | 30x  |
| medium | 2x          | 6x             | 15x  |
| large-v3 | 0.8x      | 2x             | 8x   |

Selección automática por RAM:

- < 4 GB → `tiny`
- 4–8 GB → `base`
- 8–16 GB → `small`
- > 16 GB → `medium` (o `large-v3` si hay GPU potente, ej. RTX 3070 Ti)

El usuario **no ve** el modelo. Solo "Tiempo estimado: 6 minutos". Panel "Avanzado" en Configuración para forzar modelo específico.

---

## 7. Transcripción con timecodes

`faster-whisper` devuelve segmentos con `start` y `end` en segundos. Formato intermedio:

```
[00:00] Buenos días, hoy vamos a hablar sobre…
[00:12] Como pueden ver acá en pantalla, este gráfico…
[00:34] Si miran este otro ejemplo…
```

`[MM:SS]` al inicio de cada segmento (`[HH:MM:SS]` para videos > 1h).

---

## 8. Formateo con Gemma 4

El endpoint `/api/format` arma la request a Ollama:

```
SYSTEM: [contenido de prompts/default_prompt.md]

USER: Transcripción de la clase:
[transcripción con timecodes]

Generá el HTML de las secciones <article>.
```

**Gemma 4 devuelve solo HTML de articles**, sin `<html>`, sin `<head>`, sin `<body>`. Solo `<article>...</article>` uno tras otro.

Después el backend hace:

```python
from jinja2 import Template

template = Template(open("templates/base.html").read())
html_final = template.render(
    tab_title=f"Apunte: Clase {n:02d} — El Zorro Azul",
    super_label=f"CAPACITACIÓN MODELADO 3D + IA + ENTORNOS INMERSIVOS · CLASE {n:02d}",
    main_title=titulo_clase,
    taught_by=taught_by_input,         # siempre presente
    reviewed_by=reviewed_by_input,     # "" o None → no renderiza la línea
    content=html_de_gemma,
    video_id=youtube_video_id,
    video_url=f"https://www.youtube.com/watch?v={youtube_video_id}"
)

# El logo del Zorro Azul está hardcodeado en la template apuntando a
# https://elzorroazul.studio/wp-content/uploads/2026/04/logo-sin-fondo.png
# Si en algún momento se quiere cambiar, se edita templates/base.html directamente.
```

---

## 9. Timecodes interactivos "Ir al video"

**Paso 1**: Gemma 4 preserva referencias visuales con `[[YT:MM:SS]]` inline:

```html
<p>Como podemos observar en este gráfico [[YT:02:34]], la tendencia…</p>
```

**Paso 2**: el JS de la template busca el patrón y lo reemplaza por un pill estético:

```html
<a href="https://youtube.com/watch?v=VIDEO_ID&t=154s"
   class="yt-jump"
   target="_blank">
  ▶ 02:34
</a>
```

El CSS del pill está en la template: fuente mono, fondo azul translúcido, radio completo, hover que invierte colores. Queda integrado con el estilo del código 1.

---

## 10. Edición inline y personalización

Tres niveles de edición, con auto-save a `workspace/current_session.json`:

1. **Transcripción** — textarea con timecodes editables.
2. **HTML final** — vista dividida: preview en vivo + editor (CodeMirror). Los cambios se reflejan al tipear.
3. **Prompt de Gemma 4** → **pestaña dedicada "Prompt" en Configuración**, con:
   - Editor de texto grande (mínimo 30 líneas visibles, scroll interno).
   - Syntax highlighting de Markdown.
   - Botón **"Restaurar prompt por defecto"** → vuelve a `prompts/default_prompt.md` original.
   - Botón **"Probar con muestra"** → pide una transcripción corta de ejemplo (5-10 líneas con timecodes), la procesa con el prompt actual y muestra el HTML resultante. Útil para iterar sin gastar una clase entera.
   - Toggle **"Aplicar solo a esta sesión / Guardar como default"** → permite hacer pruebas sin romper el prompt que ya funciona.
   - Indicador visual cuando el prompt actual difiere del default (punto azul al lado del tab).

Este editor es **donde se ajusta el nivel de corrección de estilo, el tono editorial, y cualquier regla nueva que quieras sumar** (por ejemplo: "reemplazá toda mención a marcas competidoras por [redacted]", o "agregá glosario al final si aparecen más de 5 términos técnicos nuevos").

Botón flotante "Regenerar desde transcripción" en la pestaña de Formato, por si algo se rompió tras editar el prompt.

---

## 11. WordPress — setup único

### Paso 1: Permitir uploads de HTML (una sola vez)

WordPress bloquea HTML como media por seguridad. La solución limpia es un **mu-plugin** (must-use plugin, se carga automáticamente sin activación).

**Archivo**: `wp-content/mu-plugins/allow-html-uploads.php`

Si la carpeta `mu-plugins` no existe, hay que crearla.

**Qué hace**: agrega `.html` a los mime types permitidos para upload, solo para administradores. No abre endpoints nuevos ni agrega funcionalidad pública.

**Cómo instalarlo**:
1. Por FTP / File Manager de Namecheap → navegar a `wp-content/`.
2. Si no existe, crear carpeta `mu-plugins`.
3. Subir `allow-html-uploads.php` adentro.
4. Listo. No requiere activación.

(Ver archivo `wordpress-setup/allow-html-uploads.php` en este entregable.)

### Paso 2: Generar Application Password

1. WP Admin → **Usuarios → Tu perfil**.
2. Scroll hasta **Application Passwords**.
3. Nombre: "Transcriptor de Clases" → **Add New**.
4. Copiar la password generada (`xxxx xxxx xxxx xxxx xxxx xxxx`) — solo se muestra una vez.
5. Pegarla en la app en el setup inicial.

### Paso 3: La app sube

Endpoint: `POST https://elzorroazul.studio/wp-json/wp/v2/media`

Headers:
```
Authorization: Basic <base64(usuario:app_password)>
Content-Type: text/html
Content-Disposition: attachment; filename="zorroazul_IA_clase_03.html"
```

Body: el archivo HTML.

Respuesta: JSON con la URL final:
`https://elzorroazul.studio/wp-content/uploads/2026/04/zorroazul_IA_clase_03.html`

### Chequeo de duplicados

Antes de subir, la app hace:

```
GET /wp-json/wp/v2/media?search=zorroazul_IA_clase_03
```

Si ya existe un media con ese slug:

- Avisa al usuario.
- Ofrece 3 opciones: **Cancelar** · **Subir con sufijo** (`-v2`) · **Reemplazar** (borra el viejo y sube el nuevo).

---

## 12. Credenciales: dónde viven y cómo se mueven

**Localmente** (por computadora):
`~/.zorroazul-transcriptor/config.json` cifrado con clave derivada del hostname + username del SO:

```json
{
  "wp_url": "https://elzorroazul.studio",
  "wp_user": "julian",
  "wp_app_password": "<cifrada>",
  "default_taught_by": "Julián Micic de Rosas",
  "default_reviewed_by": "",
  "default_super_label": "CAPACITACIÓN MODELADO 3D + IA + ENTORNOS INMERSIVOS"
}
```

**Entre computadoras**:
Botón "Exportar configuración" → archivo `.zorroazul.enc` cifrado con passphrase elegida por el usuario. En otra computadora: "Importar" + passphrase. Listo.

---

## 13. Nomenclatura de archivos

**Esquema elegido**:

```
zorroazul_IA_clase_NN.html
```

Ejemplos:

```
zorroazul_IA_clase_01.html
zorroazul_IA_clase_02.html
zorroazul_IA_clase_03.html
zorroazul_IA_clase_17.html
zorroazul_IA_clase_24.html
```

**Lógica**:

- `zorroazul_` → prefijo de sitio, útil para filtrar en la biblioteca de medios de WP.
- `IA_` → identifica el curso. Si mañana hay un curso de otra temática, se cambia este segmento (por ejemplo `zorroazul_diseño_clase_01.html`).
- `clase_NN` → número de clase con cero a la izquierda (01, no 1), para orden alfabético correcto.
- Separador: guion bajo (`_`) en todos los tramos, consistente.

**Opción con slug descriptivo** (si en algún momento querés agregarlo, la app lo contempla como toggle en la pestaña Publicar):

```
zorroazul_IA_clase_03_tencent-hunyuan-3d.html
```

El slug del tema se auto-genera del título del video de YouTube (minúsculas, sin acentos, guiones medios). Por defecto el toggle está **apagado** y la nomenclatura es la simple.

**URL resultante en WP**:
```
https://elzorroazul.studio/wp-content/uploads/2026/04/zorroazul_IA_clase_03.html
```

El `/2026/04/` es automático de WP.

**Título en el HTML** (`main_title`, con efecto glitch):
```
TENCENT HUNYUAN 3D: PIPELINE GENERATIVO DE MALLAS
```

**Super-label**:
```
CAPACITACIÓN MODELADO 3D + IA + ENTORNOS INMERSIVOS · CLASE 03
```

---

## 14. UI/UX — minimalismo

**Paleta** (alineada al código 1):
- Fondo UI: `#fafafa` (off-white del código 1).
- Texto: `#000` primario, `rgba(0,0,0,0.8)` secundario.
- Acento: `#0044FF` (zorro-blue, único color vibrante).
- Grid overlay opcional en la UI como guiño estético.

**Tipografía**:
- UI headlines: Space Grotesk.
- UI body: Manrope.
- Código/transcripciones: JetBrains Mono.

(Las mismas fuentes del código 1, para que la UI y el output se sientan de la misma familia.)

**Layout**: single page, 4 tabs horizontales. Sin sidebar. Sin menús desplegables innecesarios. Radios 8px. Sombras muy sutiles.

**Animaciones**:
- Barra de progreso con gradiente en transcripción.
- "Pensando" sutil (3 puntitos secuenciales) mientras Gemma procesa.
- Transición entre tabs: 200ms ease.
- Tildes verdes que se dibujan con `stroke-dasharray` al confirmarse cada check del sistema.

**Lo que NO va en la UI**:
- Nombre del modelo de Whisper.
- Parámetros de Gemma (temperature, etc.).
- Logs técnicos.
- Barra de estado del servidor.
- Warnings que no requieren acción.

Todo eso en Configuración → Avanzado para debug.

---

## 15. Estructura del proyecto

```
zorroazul-transcriptor/
├── launch.command              # macOS double-click
├── launch.bat                  # Windows double-click
├── bootstrap.py                # Setup + system checks
├── pyproject.toml              # Deps (uv)
├── README.md
│
├── app/
│   ├── main.py                 # FastAPI entry
│   ├── routes/
│   │   ├── system.py
│   │   ├── youtube.py
│   │   ├── transcribe.py
│   │   ├── format.py
│   │   ├── publish.py
│   │   └── config.py
│   ├── services/
│   │   ├── youtube_service.py
│   │   ├── whisper_service.py
│   │   ├── ollama_service.py
│   │   ├── template_engine.py
│   │   ├── wordpress.py
│   │   └── crypto.py
│   └── ui/
│       ├── index.html
│       ├── app.js
│       └── styles.css
│
├── templates/
│   └── base.html               # ← ESTÉTICA — editable desde UI
│
├── prompts/
│   └── default_prompt.md       # ← REGLAS DE GEMMA — editable desde UI
│
├── wordpress-setup/
│   ├── allow-html-uploads.php  # ← mu-plugin, instalar una vez
│   └── README-wordpress.md
│
└── workspace/                  # gitignored
    ├── current_session.json
    ├── downloads/
    └── audio_cache/
```

---

## 16. Brief compacto para Antigravity

```
Construí una aplicación local multiplataforma (macOS / Windows) que
transcribe clases de YouTube no-listadas, las reformatea con Gemma 4
respetando una estética definida, y las publica como archivos de medios
en un WordPress (Namecheap / El Zorro Azul).

ARQUITECTURA:
- Launcher doble-clic (launch.command / launch.bat) corre bootstrap.py
- bootstrap.py instala uv → crea venv → instala deps → verifica Ollama
  + Gemma 4 → levanta FastAPI en localhost:7860 → abre navegador.
- UI: HTML + Alpine.js + Tailwind CDN. 4 tabs: Inicio, Transcripción,
  Formato, Publicar.
- Backend: FastAPI con SSE para streaming de progreso.

FLUJO:
1. Pegar link YouTube → /api/youtube-info devuelve título + duración.
2. /api/estimate-time calcula demora según modelo Whisper y hardware.
3. /api/transcribe con faster-whisper, streaming de progreso via SSE.
4. Transcripción editable con timecodes [MM:SS].
5. /api/format envía a Gemma 4 vía Ollama con el prompt de
   prompts/default_prompt.md. Gemma devuelve SOLO bloques <article>.
6. Jinja2 inyecta los articles en templates/base.html (que contiene
   TODA la estética: Tailwind, fuentes, glitch, etc.)
7. Preview HTML editable en vivo (CodeMirror).
8. Publicación:
   a. Local: descarga HTML y TXT.
   b. WordPress: POST /wp-json/wp/v2/media con Application Password.
9. Nomenclatura: zorroazul_IA_clase_NN.html (con toggle opcional para sufijo descriptivo)

CLAVES TÉCNICAS:
- Timecodes [[YT:MM:SS]] que Gemma inserta se convierten a pills
  "▶ Ir al video" vía JS en la template (ya incluido).
- Config cifrada en ~/.zorroazul-transcriptor/config.json.
- Export/import portable entre computadoras.
- Chequeo de duplicados antes de subir a WP.
- Videos no-listados: yt-dlp funciona sin auth si tenés la URL.

ARCHIVOS CRÍTICOS DEL PROYECTO:
- templates/base.html           — estética completa
- prompts/default_prompt.md     — reglas editoriales de Gemma
- wordpress-setup/allow-html-uploads.php — mu-plugin para WP

UI PRINCIPIOS:
- Minimalista. Solo tildes verdes y progreso. No mostrar modelos de
  Whisper ni parámetros de Gemma al usuario normal. Panel "Avanzado"
  en Configuración para debug.
- Fuentes Manrope + Space Grotesk. Acento #0044FF. Fondo #fafafa.
```

---

## 17. Checklist del lado humano

1. **Subir `allow-html-uploads.php`** a `wp-content/mu-plugins/` por FTP (una vez).
2. **Generar Application Password** en WP Admin (una vez).
3. **Definir los defaults de autoría**: nombre que va por defecto en "Clase dictada por" y, si corresponde, en "Revisión técnica por". Ambos editables por clase al publicar.
4. **Revisar `prompts/default_prompt.md`** y ajustar tono si hace falta.
5. **Editar `templates/base.html`** si querés tocar estética.

---

## 18. Opcionales para v2

- Cache de transcripciones (no re-transcribir el mismo link).
- Procesamiento por lotes: 24 links en cola.
- Búsqueda full-text entre todas las clases.
- Export a ePub / PDF.
- OAuth de YouTube para videos realmente privados (no-listados no lo requieren).
