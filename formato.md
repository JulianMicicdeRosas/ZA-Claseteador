# Formato de salida — Apuntes Académicos

El modelo debe generar **únicamente HTML** con dos partes en este orden exacto. Sin explicaciones, sin bloques markdown, sin `<html>`, `<head>`, `<body>` ni `<main>`.

---

## PARTE 1 — Widget resumen (siempre primero)

```html
<div class="my-4 p-5 md:p-6 bg-black text-white rounded-lg shadow-2xl border-l-4 border-zorro-blue flex flex-col md:flex-row gap-6 items-center">
    <div class="flex-1">
        <h3 class="font-headline font-bold text-xl mb-2 text-zorro-blue uppercase tracking-wide">TEMA PRINCIPAL DE LA CLASE</h3>
        <p class="text-sm text-gray-300 opacity-90 leading-relaxed">Descripción breve de 1-2 oraciones del contenido. Hacé clic en los timecodes para ir directo al video.</p>
    </div>
    <div class="flex gap-2 text-xs font-mono flex-wrap">
        <span class="bg-white/10 px-3 py-2 rounded">Concepto 1</span>
        <span class="bg-white/10 px-3 py-2 rounded">Concepto 2</span>
        <span class="bg-white/10 px-3 py-2 rounded">Concepto 3</span>
        <span class="bg-white/10 px-3 py-2 rounded">Concepto 4</span>
    </div>
</div>
```

**Qué va en cada parte:**
- `h3`: tema principal de la clase en mayúsculas
- `p`: descripción de 1-2 oraciones del contenido
- `span × 4`: los 4 conceptos clave de la clase

---

## PARTE 2 — Secciones de contenido (una por bloque temático)

```html
<article class="bg-white/70 backdrop-blur-xl border border-black/10 shadow-xl rounded-sm p-6 md:p-10 border-l-4 border-l-zorro-blue transition-all hover:bg-white/90">
    <h2 class="glitch-target font-headline text-xl md:text-2xl font-bold text-primary uppercase tracking-wide mb-6">
        TÍTULO DE LA SECCIÓN EN MAYÚSCULAS
    </h2>
    <div class="space-y-2 text-primary/80 font-medium leading-relaxed">
        <p class="clickable-line cursor-pointer hover:bg-black/5 p-2 rounded-lg transition-all group">
            [[YT:MM:SS]] <span class="group-hover:text-zorro-blue transition-colors">Texto de la línea de la transcripción.</span>
        </p>
        <!-- una <p> por cada línea [MM:SS] de la transcripción -->
    </div>
</article>
```

**Reglas de conversión línea por línea:**
- Cada línea `[MM:SS] texto` de la transcripción → una `<p class="clickable-line ...">` 
- El timecode se escribe como `[[YT:MM:SS]]` (doble corchete, sin el texto `YT:` si es solo `MM:SS`)
- El texto de la línea va dentro del `<span class="group-hover:text-zorro-blue transition-colors">`
- **No omitir ni resumir líneas.** Corregir solo errores obvios de reconocimiento de voz.

---

## Reglas generales

1. El widget va siempre primero.
2. Identificar bloques temáticos y agruparlos en un `<article>` con `<h2>` descriptivo.
3. No incluir scripts, estilos, wrappers extra ni comentarios HTML.
4. El output debe empezar directamente con el `<div>` del widget.
