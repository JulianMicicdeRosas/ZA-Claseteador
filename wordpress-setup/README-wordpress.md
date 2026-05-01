# Instrucciones de configuración para WordPress

Para que la aplicación pueda subir archivos HTML directamente a la biblioteca de medios, debés realizar los siguientes pasos de configuración única en tu sitio `elzorroazul.studio`.

## 1. Habilitar la subida de archivos HTML
WordPress, por seguridad, no permite subir archivos `.html` a la biblioteca de medios por defecto. 

1. Entrá al cPanel de Namecheap de `elzorroazul.studio`.
2. Abrí el **File Manager** (Administrador de Archivos).
3. Navegá hasta la carpeta `public_html/wp-content/`.
4. Buscá una carpeta llamada `mu-plugins`. Si no existe, creala.
5. Subí el archivo `allow-html-uploads.php` (que está en esta misma carpeta) dentro de `mu-plugins`.
   - *Nota: Los "Must-Use Plugins" se activan automáticamente, no tenés que hacer nada más en el panel de WP.*

## 2. Generar Application Password
Para que la app se autentique sin usar tu contraseña principal:

1. Entrá a tu escritorio de WordPress Admin.
2. Navegá a **Usuarios** → **Perfil**.
3. Bajá hasta la sección **Application Passwords**.
4. En "New Application Password Name", escribí: `Transcriptor de Clases`.
5. Clic en **Add New Application Password**.
6. **Copiá el código de 24 caracteres** que aparece.
7. Pegalo en la configuración de esta aplicación (ícono de engranaje → WordPress).

## 3. Verificar conexión
En la app, hacé clic en "Probar conexión". Si ves un tilde verde, ¡estás listo para publicar!
