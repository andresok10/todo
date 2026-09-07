from flask import Blueprint, request, send_from_directory, jsonify
from yt_dlp import YoutubeDL

import os
import sys
import urllib.request
import zipfile
import tarfile
import ssl
import certifi
import shutil
import platform


app2 = Blueprint("descargas_ok", __name__)


# ============================================================
# RUTAS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARPETA_DESCARGA = os.path.join(BASE_DIR, "descarga")
CARPETA_FFMPEG = os.path.join(BASE_DIR, "ffmpeg")

os.makedirs(CARPETA_DESCARGA, exist_ok=True)
os.makedirs(CARPETA_FFMPEG, exist_ok=True)


# ============================================================
# FFMPEG
# ============================================================

if platform.system() == "Windows":
    FFMPEG_PATH = os.path.join(CARPETA_FFMPEG, "bin", "ffmpeg.exe")

    FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

else:
    FFMPEG_PATH = os.path.join(CARPETA_FFMPEG, "ffmpeg")

    FFMPEG_URL = "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"


# ============================================================
# DESCARGAR FFMPEG SI NO EXISTE
# ============================================================

if not os.path.isfile(FFMPEG_PATH):
    print("FFmpeg no encontrado.")
    print("Descargando FFmpeg...")

    archivo_ffmpeg = os.path.join(CARPETA_FFMPEG, "ffmpeg_download")

    contexto = ssl.create_default_context(cafile=certifi.where())

    try:
        with urllib.request.urlopen(FFMPEG_URL, context=contexto) as respuesta:
            with open(archivo_ffmpeg, "wb") as archivo:
                shutil.copyfileobj(respuesta, archivo)

        print("FFmpeg descargado.")

        # --------------------------------------------------------
        # WINDOWS
        # --------------------------------------------------------

        if platform.system() == "Windows":
            with zipfile.ZipFile(archivo_ffmpeg, "r") as zip_ref:
                zip_ref.extractall(CARPETA_FFMPEG)

            for raiz, carpetas, archivos in os.walk(CARPETA_FFMPEG):
                if "ffmpeg.exe" in archivos:
                    origen = os.path.join(raiz, "ffmpeg.exe")

                    os.makedirs(os.path.dirname(FFMPEG_PATH), exist_ok=True)

                    shutil.copy2(origen, FFMPEG_PATH)

                    break

        # --------------------------------------------------------
        # LINUX
        # --------------------------------------------------------

        else:
            with tarfile.open(archivo_ffmpeg, "r:xz") as tar_ref:
                tar_ref.extractall(CARPETA_FFMPEG)

            for raiz, carpetas, archivos in os.walk(CARPETA_FFMPEG):
                if "ffmpeg" in archivos:
                    origen = os.path.join(raiz, "ffmpeg")

                    os.makedirs(os.path.dirname(FFMPEG_PATH), exist_ok=True)

                    shutil.copy2(origen, FFMPEG_PATH)

                    os.chmod(FFMPEG_PATH, 0o755)

                    break

        # --------------------------------------------------------
        # ELIMINAR ZIP/TAR
        # --------------------------------------------------------

        if os.path.isfile(archivo_ffmpeg):
            os.remove(archivo_ffmpeg)

        print("FFmpeg instalado en:", FFMPEG_PATH)

    except Exception as error:
        print("ERROR INSTALANDO FFMPEG:", error)


# ============================================================
# VERIFICAR FFMPEG
# ============================================================

if os.path.isfile(FFMPEG_PATH):
    print("======================================")
    print("FFmpeg encontrado")
    print("FFmpeg:", FFMPEG_PATH)
    print("======================================")

else:
    print("======================================")
    print("ERROR: FFmpeg NO está disponible")
    print("Ruta:", FFMPEG_PATH)
    print("======================================")


# ============================================================
# INFORMACIÓN DE DIAGNÓSTICO
# ============================================================

import yt_dlp

print("======================================")
print("PYTHON:", sys.executable)
print("YT-DLP:", yt_dlp.version.__version__)
print("YT-DLP PATH:", yt_dlp.__file__)
print("FFMPEG:", FFMPEG_PATH)
print("FFMPEG EXISTE:", os.path.isfile(FFMPEG_PATH))
print("======================================")


# ============================================================
# DESCARGA WEB
# ============================================================


@app2.route("/descarga", methods=["POST"])
def descarga():

    url = request.form.get("url", "").strip()

    download_type = request.form.get("download_type", "video").lower()

    if not url:
        return jsonify({"status": "error", "message": "URL requerida"}), 400

    # ========================================================
    # CONFIGURACIÓN VIDEO
    # ========================================================

    if download_type != "audio":
        download_type = "video"

        extension = "mp4"

        formato = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"

        postprocesadores = []

    # ========================================================
    # CONFIGURACIÓN AUDIO
    # ========================================================

    else:
        download_type = "audio"

        extension = "m4a"

        formato = "bestaudio/best"

        postprocesadores = [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}]

    # ========================================================
    # NÚMERO DEL ARCHIVO
    # ========================================================

    numeros = []

    for archivo in os.listdir(CARPETA_DESCARGA):
        nombre, ext = os.path.splitext(archivo)

        if ext.lower() in [".mp4", ".webm", ".m4a", ".mp3"] and nombre.isdigit():
            numeros.append(int(nombre))

    contador = max(numeros) + 1 if numeros else 1

    # ========================================================
    # ARCHIVO TEMPORAL
    # ========================================================

    temp_template = os.path.join(CARPETA_DESCARGA, f"temp_{contador}.%(ext)s")

    # ========================================================
    # CONFIGURACIÓN YT-DLP
    # ========================================================

    ydl_opts = {
        "outtmpl": temp_template,
        "ffmpeg_location": FFMPEG_PATH,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "restrictfilenames": True,
        "windowsfilenames": True,
        "retries": 3,
        "fragment_retries": 3,
        "continuedl": True,
        "format": formato,
    }

    # ========================================================
    # VIDEO
    # ========================================================

    if download_type == "video":
        ydl_opts["merge_output_format"] = "mp4"

    # ========================================================
    # AUDIO
    # ========================================================

    else:
        ydl_opts["postprocessors"] = postprocesadores

    # ========================================================
    # INFORMACIÓN
    # ========================================================

    print("======================================")
    print("URL:", url)
    print("TIPO:", download_type)
    print("FORMATO:", formato)
    print("FFMPEG:", FFMPEG_PATH)
    print("======================================")

    # ========================================================
    # DESCARGAR
    # ========================================================

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as error:
        print("ERROR:", error)

        return jsonify({"status": "error", "message": str(error)}), 500

    # ========================================================
    # BUSCAR ARCHIVO FINAL
    # ========================================================

    archivo_final = None

    for archivo in os.listdir(CARPETA_DESCARGA):
        if archivo.startswith(f"temp_{contador}."):
            ruta = os.path.join(CARPETA_DESCARGA, archivo)

            if os.path.isfile(ruta):
                archivo_final = archivo

                break

    # ========================================================
    # NO ENCONTRADO
    # ========================================================

    if not archivo_final:
        return jsonify({"status": "error", "message": ("No se encontró el archivo descargado")}), 500

    # ========================================================
    # EXTENSIÓN REAL
    # ========================================================

    extension_real = os.path.splitext(archivo_final)[1].lower()

    # ========================================================
    # NOMBRE FINAL
    # ========================================================

    nombre_final = f"{contador}{extension_real}"

    ruta_origen = os.path.join(CARPETA_DESCARGA, archivo_final)

    ruta_destino = os.path.join(CARPETA_DESCARGA, nombre_final)

    # ========================================================
    # RENOMBRAR
    # ========================================================

    os.replace(ruta_origen, ruta_destino)

    # ========================================================
    # RESPUESTA
    # ========================================================

    return send_from_directory(CARPETA_DESCARGA, nombre_final, as_attachment=True)


# ============================================================
# API PARA ANDROID
# ============================================================


@app2.route("/api/descarga", methods=["POST"])
def api_descarga():

    data = request.get_json(silent=True) or {}

    url = str(data.get("url", "")).strip()

    download_type = str(data.get("download_type", "video")).lower()

    if not url:
        return jsonify({"status": "error", "message": "URL requerida"}), 400

    # ========================================================
    # VIDEO
    # ========================================================

    if download_type != "audio":
        download_type = "video"

        extension = "mp4"

        formato = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"

        postprocesadores = []

    # ========================================================
    # AUDIO
    # ========================================================

    else:
        download_type = "audio"

        extension = "m4a"

        formato = "bestaudio/best"

        postprocesadores = [{"key": "FFmpegExtractAudio", "preferredcodec": "m4a"}]

    # ========================================================
    # NÚMERO DEL ARCHIVO
    # ========================================================

    numeros = []

    for archivo in os.listdir(CARPETA_DESCARGA):
        nombre, ext = os.path.splitext(archivo)

        if ext.lower() in [".mp4", ".webm", ".m4a", ".mp3"] and nombre.isdigit():
            numeros.append(int(nombre))

    contador = max(numeros) + 1 if numeros else 1

    # ========================================================
    # ARCHIVO TEMPORAL
    # ========================================================

    temp_template = os.path.join(CARPETA_DESCARGA, f"temp_{contador}.%(ext)s")

    # ========================================================
    # CONFIGURACIÓN YT-DLP
    # ========================================================

    ydl_opts = {
        "outtmpl": temp_template,
        "ffmpeg_location": FFMPEG_PATH,
        "noplaylist": True,
        "quiet": False,
        "no_warnings": False,
        "restrictfilenames": True,
        "windowsfilenames": True,
        "retries": 3,
        "fragment_retries": 3,
        "continuedl": True,
        "format": formato,
    }

    # ========================================================
    # VIDEO
    # ========================================================

    if download_type == "video":
        ydl_opts["merge_output_format"] = "mp4"

    # ========================================================
    # AUDIO
    # ========================================================

    else:
        ydl_opts["postprocessors"] = postprocesadores

    # ========================================================
    # INFORMACIÓN
    # ========================================================

    print("======================================")
    print("API DESCARGA")
    print("URL:", url)
    print("TIPO:", download_type)
    print("FORMATO:", formato)
    print("FFMPEG:", FFMPEG_PATH)
    print("======================================")

    # ========================================================
    # DESCARGAR
    # ========================================================

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    except Exception as error:
        print("ERROR API:", error)

        return jsonify({"status": "error", "message": str(error)}), 500

    # ========================================================
    # BUSCAR ARCHIVO FINAL
    # ========================================================

    archivo_final = None

    for archivo in os.listdir(CARPETA_DESCARGA):
        if archivo.startswith(f"temp_{contador}."):
            ruta = os.path.join(CARPETA_DESCARGA, archivo)

            if os.path.isfile(ruta):
                archivo_final = archivo

                break

    # ========================================================
    # NO ENCONTRADO
    # ========================================================

    if not archivo_final:
        return jsonify({"status": "error", "message": ("No se encontró el archivo descargado")}), 500

    # ========================================================
    # EXTENSIÓN REAL
    # ========================================================

    extension_real = os.path.splitext(archivo_final)[1].lower()

    # ========================================================
    # NOMBRE FINAL
    # ========================================================

    nombre_final = f"{contador}{extension_real}"

    ruta_origen = os.path.join(CARPETA_DESCARGA, archivo_final)

    ruta_destino = os.path.join(CARPETA_DESCARGA, nombre_final)

    # ========================================================
    # RENOMBRAR
    # ========================================================

    os.replace(ruta_origen, ruta_destino)

    # ========================================================
    # TAMAÑO
    # ========================================================

    tamaño = os.path.getsize(ruta_destino)

    # ========================================================
    # URL DE DESCARGA
    # ========================================================

    download_url = request.host_url.rstrip("/") + "/api/descarga/archivo/" + nombre_final

    # ========================================================
    # RESPUESTA ANDROID
    # ========================================================

    return jsonify({"status": "success", "message": "Descarga completada", "filename": nombre_final, "extension": extension_real.replace(".", ""), "size_mb": round(tamaño / (1024 * 1024), 2), "download_url": download_url})


# ============================================================
# ARCHIVO PARA ANDROID
# ============================================================


@app2.route("/api/descarga/archivo/<path:filename>", methods=["GET"])
def archivo_descarga(filename):

    return send_from_directory(CARPETA_DESCARGA, filename, as_attachment=True)


# ============================================================
# SERVIR ARCHIVOS
# ============================================================


@app2.route("/server/<path:output_file>", methods=["GET"])
def server(output_file):

    return send_from_directory(CARPETA_DESCARGA, output_file, as_attachment=True)
