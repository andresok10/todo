from flask import Flask, current_app
from datetime import datetime
from calendario import app1
from descargas_android import app2
from descargas_web import app3
import os, urllib.request,zipfile ,tarfile, ssl, certifi, shutil

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.context_processor
def inject_globals():
    return {"hoy": datetime.today()}

app.register_blueprint(app1)
app.register_blueprint(app2)
app.register_blueprint(app3)

#carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "descargas")
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)


'''
quiero que mi app borre los archivos de descarga en render despues de haberlos descargado en mi celular android
Perfecto, si estás usando Render.com para desplegar tu backend y quieres que los archivos se eliminen automáticamente del servidor después de descargarlos en tu celular Android, puedes hacerlo fácilmente.

✅ Objetivo:

Eliminar el archivo en el servidor inmediatamente después de que tu dispositivo haya completado la descarga.

🧠 ¿Cómo hacerlo?

La clave está en modificar tu endpoint que sirve el archivo (/descargax/<path:file>) para que:

Sirva el archivo como descarga (send_from_directory).

Y después de enviarlo, lo elimine del sistema de archivos (os.remove()).

Esto lo puedes lograr usando un after_this_request() de Flask.

✅ Paso a paso: Actualiza tu endpoint /descargax/<file> así:
from flask import send_from_directory, after_this_request

@app2.route("/descargax/<path:file>")
def serve_download(file):
    ruta_archivo = os.path.join(BASE_DIR, "descarga", file)

    if not os.path.exists(ruta_archivo):
        return "Archivo no encontrado", 404

    @after_this_request
    def eliminar_archivo(response):
        try:
            os.remove(ruta_archivo)
            print(f"🗑️ Archivo eliminado: {file}")
        except Exception as e:
            print(f"❌ Error al eliminar {file}: {e}")
        return response

    return send_from_directory(os.path.join(BASE_DIR, "descarga"), file, as_attachment=True)

✅ ¿Qué hace este código?

after_this_request registra una función que se ejecuta después de que la respuesta fue enviada al cliente.

Así garantizas que el archivo se descargó correctamente antes de borrarlo.

Usa os.remove(ruta_archivo) para borrar el archivo.

Imprime en consola si se eliminó o si hubo error.

⚠️ Consideraciones

Esto solo funciona si el archivo se descarga correctamente.

Si la descarga se interrumpe (por mala conexión o cierre), el archivo no se borra — lo cual es bueno.

Puedes limpiar archivos viejos automáticamente con un cron job o script aparte si deseas (p. ej., eliminar archivos con más de X minutos).
##############################
¿Quieres que también lo borre automáticamente si no se descarga después de cierto tiempo (limpieza programada)? Te puedo ayudar con eso también.
Perfecto. Si quieres que los archivos también se eliminen automáticamente si no se descargan en cierto tiempo, por ejemplo después de 5 minutos, entonces puedes implementar una limpieza programada (tipo cron job) directamente dentro de tu aplicación Flask usando un hilo en segundo plano (thread).

✅ Objetivo:

Eliminar archivos de la carpeta descarga/ si tienen más de X minutos de antigüedad (ej: 5 minutos).

🧠 Estrategia:

Crear un hilo de limpieza que se ejecute en segundo plano mientras el servidor está activo.

Este hilo buscará archivos dentro de /descarga y eliminará los que tengan más de X minutos desde su creación.

✅ Paso 1: Agrega esto al final de tu archivo principal (ej. main.py o app.py):
import threading
import time

def limpiar_descargas_antiguas():
    carpeta = os.path.join(BASE_DIR, "descarga")
    tiempo_limite = 5 * 60  # 5 minutos en segundos

    while True:
        if os.path.exists(carpeta):
            ahora = time.time()
            for archivo in os.listdir(carpeta):
                ruta_archivo = os.path.join(carpeta, archivo)
                if os.path.isfile(ruta_archivo):
                    tiempo_modificado = os.path.getmtime(ruta_archivo)
                    if ahora - tiempo_modificado > tiempo_limite:
                        try:
                            os.remove(ruta_archivo)
                            print(f"🧹 Archivo antiguo eliminado: {archivo}")
                        except Exception as e:
                            print(f"❌ Error al eliminar archivo {archivo}: {e}")
        time.sleep(60)  # Ejecutar cada 60 segundos

✅ Paso 2: Inicia el hilo cuando se arranca la app:

Justo al final del archivo, antes de app.run() o cuando se crea app2, añade:

threading.Thread(target=limpiar_descargas_antiguas, daemon=True).start()

🔁 Resultado:

Cada 60 segundos, tu app revisará los archivos en /descarga.

Si alguno tiene más de 5 minutos desde su creación/modificación, se eliminará automáticamente.

Esto funciona en paralelo con tus rutas Flask sin bloquear nada.

⚠️ Recomendaciones en Render.com:

Render reinicia tu instancia si está en modo free y sin uso, así que si quieres que este hilo siempre funcione, asegúrate de estar en un plan que permita procesos duraderos (o que se active constantemente).

Esta solución no usa cron jobs del sistema (no están disponibles en Render), sino hilos dentro de Flask, que es 100% compatible.
'''