# Publicar Todo en Render

Publica esta carpeta `todo_web` como raíz de un repositorio de GitHub. Las carpetas `todo_android` y `todo_render` son clientes Android y no se suben como backend.

## Despliegue sin Docker

El script `C:\dev\APP_TODO\subir_todo.py` publica el backend y crea o actualiza un servicio Render con runtime nativo de Python. Render instala `requirements.txt`, inicia Flask con Gunicorn y trae FFmpeg en su runtime nativo. `yt-dlp` usa Node para los retos JavaScript de YouTube.

Conecta una vez GitHub a Render para que Render tenga acceso al repositorio. Después ejecuta:

```powershell
python C:\dev\APP_TODO\subir_todo.py
```

También puedes crear el servicio con New > Blueprint; Render usa el `render.yaml` de esta carpeta. No selecciones Docker. Configura `SECRET_KEY` y `TEMPORARY_DOWNLOADS=1` si creas el servicio manualmente.

Usa la URL HTTPS que Render asigne en los clientes Android mediante `flaskBaseUrl` (todo_android) y `webBaseUrl` (todo_render), y vuelve a generar sus APK. El usuario no necesita escribir el servidor en pantalla.

## Archivos y estado

En Render el servidor genera el archivo temporal, lo envía y elimina su copia al cerrar la respuesta. Los temporales abandonados de más de una hora se limpian en la siguiente solicitud temporal. No se provisiona un disco ni un servicio de pago con este Blueprint.

El contador SQLite es pequeño, pero en el disco efímero puede reiniciarse al recrearse o desplegarse el servicio. Para mantener la numeración global entre despliegues hace falta almacenar ese contador en una base persistente; no es necesario conservar los vídeos o audios.

## Diseño compartido

La web sirve static/todo-compacto.css y static/todo-compacto.js. El cliente WebView todo_render incluye una copia para aplicar el mismo diseño cuando termine de cargar la página. Ejecuta el script `../sincronizar_diseno.ps1` después de editar los estilos o la navegación. El cliente nativo todo_android usa la misma paleta y distribución con Compose.