from flask import Blueprint, request, jsonify, url_for, send_from_directory, current_app
from yt_dlp import YoutubeDL
import os, urllib.request,zipfile ,tarfile, ssl, certifi, shutil
app2 = Blueprint("descargas", __name__)
import os, zipfile, tarfile, urllib.request, shutil, ssl, certifi, platform
ffmpeg_dir = os.path.dirname(os.path.abspath(__file__))
# Detectar sistema operativo
is_windows = platform.system().lower().startswith("win")
print(is_windows)
is_linux = platform.system().lower().startswith("linux")
print(is_linux)
if not os.path.exists(f"{ffmpeg_dir}/ffmpeg"):
    print("FFmpeg no encontrado. Descargando...")
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

    if is_windows:
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        os.system(f"curl -L {url} -o {ffmpeg_dir}/ffmpeg.zip")
        zipfile.ZipFile(f"{ffmpeg_dir}/ffmpeg.zip", 'r').extractall(ffmpeg_dir)
        old_path = f"{ffmpeg_dir}/ffmpeg-8.0-essentials_build"
        new_path = f"{ffmpeg_dir}/ffmpeg"
        if not os.path.exists(new_path):
            os.rename(old_path, new_path)
            print("✅ Carpeta renombrada a ffmpeg")
        else:
            print("ℹ️ Carpeta ffmpeg ya existe, no se renombró.")

        if os.path.isfile(f"{ffmpeg_dir}/ffmpeg.zip"):
            os.remove(f"{ffmpeg_dir}/ffmpeg.zip")

        if os.path.exists(f"{ffmpeg_dir}/ffmpeg-8.0-essentials_build"):
            shutil.rmtree(f"{ffmpeg_dir}/ffmpeg-8.0-essentials_build")
        
    elif is_linux:
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
        #if os.path.exists(f"{ffmpeg_dir}/ffmpeg-7.0.2-amd64-static"):
        #    shutil.rmtree(f"{ffmpeg_dir}/ffmpeg-7.0.2-amd64-static")

        # Dar permisos de ejecución al binario
        os.chmod(f"{ffmpeg_dir}/ffmpeg/ffmpeg", 0o755)
        #os.chmod(ffmpeg_bin, 0o755)
        #os.chmod(ffprobe_bin, 0o755)
    else:
        raise Exception("❌ Sistema operativo no soportado")
##################################################
#BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)
os.makedirs(f"{BASE_DIR}/descarga", exist_ok=True)

#FFMPEG_PATH = f"{BASE_DIR}/ffmpeg/bin/ffmpeg.exe" # windows
FFMPEG_PATH = f"{BASE_DIR}/ffmpeg/ffmpeg" # linux
print(FFMPEG_PATH) #/opt/render/project/src/ffmpeg

#app.config["BASE_DIR"] = BASE_DIR
#app.config["FFMPEG_PATH"] = FFMPEG_PATH

#global BASE_DIR, FFMPEG_PATH

#@app2.before_app_first_request
#def cargar_config():
#    global BASE_DIR, FFMPEG_PATH
#    BASE_DIR = current_app.config["BASE_DIR"]
#    FFMPEG_PATH = current_app.config["FFMPEG_PATH"]

@app2.route("/descarga", methods=["POST"])
def descargaxx():
    url = request.form.get("url").split("?")[0]
    download_type = request.form.get("download_type", "video")

    if not url:
        return jsonify({"status": "error", "msg": "No se proporcionó URL"}), 400

    #extension = "m4a" if download_type == "audio" else "mp4"
    extension = "m4a" if download_type == "audio" else "webm"

    # Generar nombre de archivo único
    counter = 1
    while True:
        file = f"{BASE_DIR}/descarga/{counter}.{extension}"
        if not os.path.exists(file):
            break
        counter += 1

    ydl_opts = {
        "format": "bestaudio/best" if download_type == "audio" else "best",
        "outtmpl": file,
        "ffmpeg_location": FFMPEG_PATH,
        "quiet": True,
        "noplaylist": True,
        #"postprocessor_args": ["-y"],  # evita renombrado duplicado
        #"keepvideo": False,             # elimina el archivo temporal
        #"prefer_ffmpeg": True,          # asegura uso de ffmpeg

        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": extension,  # fuerza la extensión deseada
            "preferredquality": "192",
        }],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        msgx = f"{download_type.capitalize()} descargado con éxito como {os.path.basename(file)}."
        '''return jsonify({
            "status": "success",
            "msg": msgx,
            #"download_url": url_for("serve_download", filename=os.path.basename(filename))
            "download_url": url_for("serve_download")
        })'''
        return jsonify({
            "status": "success",
            "msg": msgx,
            "file_name": os.path.basename(file)
        })

    except Exception as e:
        return jsonify({"status": "error", "msg": f"Error al descargar el archivo: {str(e)}"}), 500
    
@app2.route("/descarga_flutter", methods=["POST"])
def descarga_flutterx():
    try:
        data = request.get_json()
        url = data.get("url").split("?")[0]
        download_type = data.get("download_type", "video")
        #extension = data.get("extension", "webm")  # ej: mp4, mkv, webm, avi, mp3...

        if not url:
            return jsonify({"status": "error", "msg": "No se proporcionó URL"}), 400

        extension = "m4a" if download_type == "audio" else "webm"

        # Generar nombre único
        counter = 1
        while True:
            #file = f"{BASE_DIR}/descarga/{counter}.{extension}"
            file = f"{BASE_DIR}/descarga/{counter}"
            if not os.path.exists(file):
                break
            counter += 1

        #"format": "bestaudio/best" if download_type == "audio" else "best", "bestvideo+bestaudio/best",
        if download_type == "audio":
            ydl_opts = {
                "format": "bestaudio/best",
                #"outtmpl": file + ".%(ext)s",  # añadir extensión aquí,
                "outtmpl": file,  # añadir extensión aquí,
                "ffmpeg_location": FFMPEG_PATH,
                "quiet": False,
                "noplaylist": True,
            }
        else: # video
            ydl_opts = {
                #"outtmpl": f"{counter}.{extension}",  # añadir extensión aquí,
                "outtmpl": file + ".%(ext)s",  # añadir extensión aquí,
                #"format": "bestvideo+bestaudio/best",
                #"merge_output_format": extension,  # 🔥 esta línea fuerza la extensión
                #'format': 'bestvideo[ext=webm]+bestaudio[ext=webm]/best',
                'format': 'best',
                'merge_output_format': 'webm',
                "ffmpeg_location": FFMPEG_PATH,
                "quiet": False,
                "noplaylist": True,
                #'postprocessor_args': ['-strict', '-2'],  # opcional
                'postprocessor_args': ['-c', 'copy', '-strict', '-2']

            }

        # Descargar archivo
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Nombre base del archivo descargado
        #file_basename = os.path.basename(file)
        #file_basename = f"{BASE_DIR}/descarga/{counter}.{extension}"
        file_basename = f"{counter}.{extension}"

        # ✅ Construir URL con HTTPS para evitar el error CLEARTEXT
        #download_url = url_for("serve_download", file=file_basename, _external=True, _scheme="https")
        #download_url = url_for("descargax", file=file_basename, _external=True, _scheme="https")
        download_url = url_for("descargas.serve_download", file=file_basename, _external=True, _scheme="https")


        msgx = f"{download_type.capitalize()} descargado con éxito como {file_basename}."
        return jsonify({
            "status": "success",
            "msg": msgx,
            "download_url": download_url
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({
            "status": "error","msg": f"Error al descargar el archivo: {str(e)}"}), 500

# ✅ Servir correctamente los archivos desde /downloads/
@app2.route("/descargax/<path:file>")
def serve_download(file):
    """Sirve los archivos descargados directamente"""
    return send_from_directory(f"{BASE_DIR}/descarga", file, as_attachment=True)

#@app.route("/downloads/<path:filename>")
#def serve_download(filename):
#    return send_from_directory(f"{BASE_DIR}/downloads", os.path.basename(filename), as_attachment=True)

#@app.route("/downloads/<path:filename>")
#def serve_download(filename):
    #return send_from_directory(f"{BASE_DIR}/downloads", filename, as_attachment=True)
#    return send_from_directory(f"{BASE_DIR}/downloads", os.path.basename(filename), as_attachment=True)

## Si quieres habilitar descarga directa de archivos:
#@app.route("/downloads/<path:filename>")
# @app.route("/download/<path:output_file>")
#def serve_download(filename):
#    filename = os.path.basename(filename)
    # print(filename) # 1.webm
    # filename = os.path.join(BASE_DIR, os.path.basename(filename))
    # print(filename)
    # file_path = os.path.join(BASE_DIR, filename)

    # return send_from_directory(file_path, filename, as_attachment=True)
    # return send_from_directory("downloads", output_file, as_attachment=True)
#    return send_from_directory(BASE_DIR, filename, as_attachment=True)