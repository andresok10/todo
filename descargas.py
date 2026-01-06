from flask import Blueprint, request, jsonify, url_for, send_from_directory, current_app
from yt_dlp import YoutubeDL  # pip install yt-dlp
import os, urllib.request, zipfile, tarfile, ssl, certifi, shutil
import os, zipfile, tarfile, urllib.request, shutil, ssl, certifi, platform
import glob

app2 = Blueprint("descargas", __name__)

ffmpeg_dir = os.path.dirname(os.path.abspath(__file__))

# Detectar sistema operativo
is_linux = platform.system().lower().startswith("linux")
print(is_linux)
if not os.path.exists(f"{ffmpeg_dir}/ffmpeg"):
    print("FFmpeg no encontrado. Descargando...")
    ssl._create_default_https_context = lambda: ssl.create_default_context(
        cafile=certifi.where()
    )
    if is_linux:
        url = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
        archivo = f"{ffmpeg_dir}/ffmpeg.tar.xz"
        urllib.request.urlretrieve(url, archivo)
        tarfile.open(archivo, "r:xz").extractall(ffmpeg_dir, filter="data")
        print("✅ Extraído")
        old_path = os.path.join(ffmpeg_dir, "ffmpeg-7.0.2-amd64-static")
        new_path = os.path.join(ffmpeg_dir, "ffmpeg")
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print("✅ Carpeta renombrada a ffmpeg")
        else:
            print("ℹ️ Carpeta ffmpeg ya existe, no se renombró.")

        if os.path.isfile(f"{ffmpeg_dir}/ffmpeg.tar.xz"):
            os.remove(f"{ffmpeg_dir}/ffmpeg.tar.xz")
        # if os.path.exists(f"{ffmpeg_dir}/ffmpeg-7.0.2-amd64-static"):
        #    shutil.rmtree(f"{ffmpeg_dir}/ffmpeg-7.0.2-amd64-static")

        # Dar permisos de ejecución al binario
        os.chmod(f"{ffmpeg_dir}/ffmpeg/ffmpeg", 0o755)
        # os.chmod(ffmpeg_bin, 0o755)
        # os.chmod(ffprobe_bin, 0o755)
    else:
        raise Exception("❌ Sistema operativo no soportado")
##################################################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CARPETA_DESCARGA = os.path.join(BASE_DIR, "descarga")
os.makedirs(CARPETA_DESCARGA, exist_ok=True)

FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg/ffmpeg")

@app2.route("/descarga_flutter", methods=["POST"])
def descarga_flutterx():
    try:
        data = request.get_json()
        url = data.get("url").split("?")[0]
        download_type = data.get("download_type", "video")
        extension = "m4a" if download_type == "audio" else "webm"

        if not url:
            return jsonify({"status": "error", "msg": "No se proporcionó URL"}), 400

        # 🔥 Limpiar carpeta antes de descargar
        #for f in glob.glob(os.path.join(CARPETA_DESCARGA, "*")):
        #    try:
        #        os.remove(f)
        #        current_app.logger.info(f"🗑 Eliminado archivo previo: {f}")
        #    except Exception as ex:
        #        current_app.logger.error(f"No se pudo eliminar {f}: {ex}")

        if os.path.exists(CARPETA_DESCARGA):
            current_app.logger.info(f"📂 Contenido actual de {CARPETA_DESCARGA}:")
            for archivo in os.listdir(CARPETA_DESCARGA):
                ruta_completa = os.path.join(CARPETA_DESCARGA, archivo)
                current_app.logger.info(f"   ➜ {ruta_completa}")
                current_app.logger.info(f"{os.remove(os.path.join(CARPETA_DESCARGA, archivo))}")
                #try:
                #if os.remove(os.path.join(CARPETA_DESCARGA, archivo)):
                #    current_app.logger.info(f"archivo antiguo eliminado: {archivo}")
                #else:
                    #except Exception as ex:
                    #current_app.logger.error(f"❌ No se pudo eliminar {archivo}: {ex}")
                #    current_app.logger.error(f"❌ No se pudo eliminar {archivo}")

            current_app.logger.info(f"📂 Contenido actual2 de {CARPETA_DESCARGA}:")
            for archivo in os.listdir(CARPETA_DESCARGA):
                current_app.logger.info(f"   ➜ {archivo}")


        # Archivo final siempre será "1.extension"
        final_file = os.path.join(CARPETA_DESCARGA, f"1.{extension}")

        # Opciones de yt-dlp
        ydl_opts = {
            "outtmpl": final_file,
            "ffmpeg_location": FFMPEG_PATH,
            "noplaylist": True,
            "quiet": False,
        }
        if download_type == "audio":
            ydl_opts["format"] = "bestaudio/best"
        else:
            ydl_opts["format"] = "bestvideo[ext=webm]+bestaudio[ext=webm]/best"
            ydl_opts["merge_output_format"] = extension
            ydl_opts["postprocessor_args"] = ["-strict", "-2"]

        # Descargar
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # URL de descarga
        download_url = url_for(
            "descargas.serve_download",
            file=os.path.basename(final_file),
            _external=True,
            _scheme="https"
        )

        return jsonify({
            "status": "success",
            "msg": f"{download_type.capitalize()} descargado con éxito como 1.{extension}.",
            "download_url": download_url,
            "extension": extension
        })

    except Exception as e:
        current_app.logger.error(f"Error en descarga: {e}")
        return jsonify({"status": "error", "msg": str(e)}), 500


@app2.route("/descargax/<path:file>")
def serve_download(file):
    return send_from_directory(CARPETA_DESCARGA, file, as_attachment=True)

# BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
'''BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)  # /opt/render/project/src/
os.makedirs(f"{BASE_DIR}/descarga", exist_ok=True)

# FFMPEG_PATH = f"{BASE_DIR}/ffmpeg/bin/ffmpeg.exe" # windows
FFMPEG_PATH = f"{BASE_DIR}/ffmpeg/ffmpeg"  # linux
print(FFMPEG_PATH)  # /opt/render/project/src/ffmpeg/ffmpeg

@app2.route("/descarga_flutter", methods=["POST"])
def descarga_flutterx():
    carpeta = os.path.join(BASE_DIR, "descarga")
    # carpeta = "/opt/render/project/src/descarga"
    try:
        data = request.get_json()
        url = data.get("url").split("?")[0]
        download_type = data.get("download_type", "video")
        extension = data.get("extension", "webm")  # ej: mp4, mkv, webm, avi, mp3...

        if not url:
            return jsonify({"status": "error", "msg": "No se proporcionó URL"}), 400

        extension = "m4a" if download_type == "audio" else "webm"

        # Archivo temporal para descargar con yt-dlp
        tmp_file = os.path.join(carpeta, f"temp.%(ext)s")  # siempre fijo, evita conflictos

        # Generar nombre único
        counter = 1
        while True:
            file = f"{BASE_DIR}/descarga/{counter}.{extension}"
            # file = f"{BASE_DIR}/descarga/{counter}"
            if not os.path.exists(file):
                break
            counter += 1
        
        # "format": "bestaudio/best" if download_type == "audio" else "best", "bestvideo+bestaudio/best",
        if download_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                # "outtmpl": file + ".%(ext)s",  # añadir extensión aquí,
                "outtmpl": tmp_file,  # añadir extensión aquí,
                "ffmpeg_location": FFMPEG_PATH,
                "quiet": False,
                "noplaylist": True,
            }
        else:  # video
            ydl_opts = {
                "outtmpl": tmp_file,  # añadir extensión aquí,
                # "outtmpl": f"{counter}.{extension}",  # añadir extensión aquí,
                # "outtmpl": file + ".%(ext)s",  # añadir extensión aquí,
                # "format": "bestvideo+bestaudio/best",
                # "merge_output_format": extension,  # 🔥 esta línea fuerza la extensión
                "format": "bestvideo[ext=webm]+bestaudio[ext=webm]/best",
                #'format': 'best',
                "merge_output_format": extension,
                "ffmpeg_location": FFMPEG_PATH,
                # "quiet": False,
                "noplaylist": True,
                "postprocessor_args": ["-strict", "-2"],  # opcional
                #'postprocessor_args': ['-c', 'copy', '-strict', '-2']
            }

        # Descargar archivo
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Renombrar temporal a archivo final con contador
        #for f in glob.glob(os.path.join(carpeta, "temp.*")):
            #os.rename(f, final_file)
        #    os.rename(f, file)

        # Renombrar temporal a archivo final (solo si existe)
        temp_files = glob.glob(os.path.join(carpeta, "temp.*"))
        if not temp_files:
            raise FileNotFoundError("No se encontró archivo temporal descargado.")
        #os.rename(temp_files[0], final_file)
        os.rename(temp_files[0], file)

        # Después de descargar con yt_dlp  # Generar respuesta
        file_basename = os.path.basename(file)  # ej: 1.webm, 2.m4a, etc.
        real_extension = file_basename.split(".")[-1]  # extrae 'webm', 'mp4', etc.

        # Nombre base del archivo descargado
        # file_basename = os.path.basename(file)
        # file_basename = f"{BASE_DIR}/descarga/{counter}.{extension}"
        # file_basename = f"{counter}.{extension}"

        # ✅ Construir URL con HTTPS para evitar el error CLEARTEXT
        # download_url = url_for("serve_download", file=file_basename, _external=True, _scheme="https")
        # download_url = url_for("descargax", file=file_basename, _external=True, _scheme="https")
        download_url = url_for(
            "descargas.serve_download",
            file=file_basename,
            _external=True,
            _scheme="https",
        )

        msgx = (
            f"{download_type.capitalize()} descargado con éxito como {file_basename}."
        )
        return jsonify(
            {
                "status": "success",
                "msg": msgx,
                "download_url": download_url,
                "extension": real_extension,  # enviamos la extensión real
            }
        )
    except Exception as e:
        print("❌ ERROR:", str(e))
        return (
            jsonify(
                {"status": "error", "msg": f"Error al descargar el archivo: {str(e)}"}
            ),
            500,
        )'''

'''finally:
        if os.path.exists(carpeta):
            try:
                current_app.logger.info(f"📂 Contenido actual de {carpeta}:")
                for archivo in os.listdir(carpeta):
                    ruta_completa = os.path.join(carpeta, archivo)
                    current_app.logger.info(f"   ➜ {ruta_completa}")
                    os.remove(os.path.join(carpeta, archivo))
                    current_app.logger.info(f"🗑 Eliminado temporal residual: {archivo}")
            except Exception as ex:
                current_app.logger.error(f"❌ No se pudo eliminar {archivo}: {ex}")

            current_app.logger.info(f"📂 Contenido actual2 de {carpeta}:")
            for archivo in os.listdir(carpeta):
                current_app.logger.info(f"   ➜ {archivo}")'''
        # else:
        #    current_app.logger.info(f"❌ La carpeta {carpeta} no existe.")

'''@app2.route("/descargax/<path:file>")
def serve_download(file):
    # Ruta completa al archivo temporal
    full_path = os.path.join(BASE_DIR, "descarga", file)
    if not os.path.exists(full_path):
        return "Archivo no encontrado", 404
    # Usamos send_file y luego eliminamos el archivo
    #response = send_file(full_path, as_attachment=True)
    response =  send_from_directory(full_path, as_attachment=True)
    # Borrar el archivo después de servirlo
    try:
        os.remove(full_path)
        current_app.logger.info(f"🗑 Archivo eliminado automáticamente: {full_path}")
    except Exception as e:
        current_app.logger.error(f"❌ Error eliminando archivo: {full_path} | {e}")
    return response'''

# Servir correctamente los archivos desde /downloads/
#@app2.route("/descargax/<path:file>")
#def serve_download(file): # Sirve los archivos descargados directamente
#    return send_from_directory(f"{BASE_DIR}/descarga", file, as_attachment=True)
    # return send_from_directory(f"{BASE_DIR}/downloads", os.path.basename(filename), as_attachment=True)


## Si quieres habilitar descarga directa de archivos:
# @app.route("/downloads/<path:filename>")
# @app.route("/download/<path:output_file>")
# def serve_download(filename):
#    filename = os.path.basename(filename)
# print(filename) # 1.webm
# filename = os.path.join(BASE_DIR, os.path.basename(filename))
# print(filename)
# file_path = os.path.join(BASE_DIR, filename)

# return send_from_directory(file_path, filename, as_attachment=True)
# return send_from_directory("downloads", output_file, as_attachment=True)
#    return send_from_directory(BASE_DIR, filename, as_attachment=True)
