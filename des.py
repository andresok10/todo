from flask import Blueprint, request, send_from_directory, jsonify
from yt_dlp import YoutubeDL
import yt_dlp

import os
import sys
import shutil
import platform


app2 = Blueprint("descargas_ok", __name__)


# ============================================================
# RUTAS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CARPETA_DESCARGA = os.path.join(BASE_DIR, "descarga")

CARPETA_FFMPEG = os.path.join(BASE_DIR, "ffmpeg")


# ============================================================
# FFMPEG
# ============================================================

if platform.system() == "Windows":
    FFMPEG_PATH = os.path.join(
        CARPETA_FFMPEG,
        "bin",
        "ffmpeg.exe",
    )

else:
    FFMPEG_PATH = os.path.join(
        CARPETA_FFMPEG,
        "ffmpeg",
    )


os.makedirs(CARPETA_DESCARGA, exist_ok=True)


# ============================================================
# BUSCAR FFMPEG
# ============================================================

if not os.path.isfile(FFMPEG_PATH):
    ffmpeg_sistema = shutil.which("ffmpeg")

    if ffmpeg_sistema:
        FFMPEG_PATH = ffmpeg_sistema


if not os.path.isfile(FFMPEG_PATH):
    raise FileNotFoundError(f"FFmpeg no está disponible en: {FFMPEG_PATH}")


# ============================================================
# BUSCAR DENO
# ============================================================

DENO_PATH = shutil.which("deno")


if not DENO_PATH:
    rutas_deno = [
        "/opt/render/.deno/bin/deno",
        "/opt/render/project/.deno/bin/deno",
        "/root/.deno/bin/deno",
        os.path.expanduser("~/.deno/bin/deno"),
    ]

    for ruta in rutas_deno:
        if os.path.isfile(ruta):
            DENO_PATH = ruta

            break


# ============================================================
# CONFIGURACIÓN JS
# ============================================================

JS_RUNTIMES = {}

REMOTE_COMPONENTS = {"ejs:npm"}


if DENO_PATH:
    JS_RUNTIMES = {"deno": {"path": DENO_PATH}}


# ============================================================
# DIAGNÓSTICO
# ============================================================

print("======================================")
print("DIAGNÓSTICO")
print("PYTHON:", sys.executable)
print("YT-DLP:", yt_dlp.version.__version__)
print("YT-DLP PATH:", yt_dlp.__file__)
print("FFMPEG:", FFMPEG_PATH)
print("FFMPEG EXISTE:", os.path.isfile(FFMPEG_PATH))
print("DENO:", DENO_PATH)
print("DENO EXISTE:", bool(DENO_PATH and os.path.isfile(DENO_PATH)))
print("JS RUNTIMES:", JS_RUNTIMES)
print("======================================")


# ============================================================
# CREAR NÚMERO DE ARCHIVO
# ============================================================


def obtener_contador():

    numeros = []

    for archivo in os.listdir(CARPETA_DESCARGA):
        nombre, ext = os.path.splitext(archivo)

        if ext.lower() in [".mp4", ".webm", ".m4a", ".mp3"] and nombre.isdigit():
            numeros.append(int(nombre))

    return max(numeros) + 1 if numeros else 1


# ============================================================
# CONFIGURAR YT-DLP
# ============================================================


def crear_opciones(contador, download_type):

    if download_type == "audio":
        formato = "bestaudio/best"

        opciones = {
            "outtmpl": os.path.join(CARPETA_DESCARGA, f"temp_{contador}.%(ext)s"),
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
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
        }

    else:
        formato = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"

        opciones = {
            "outtmpl": os.path.join(CARPETA_DESCARGA, f"temp_{contador}.%(ext)s"),
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
            "merge_output_format": "mp4",
        }

    # ========================================================
    # DENO / EJS
    # ========================================================

    if DENO_PATH:
        opciones["js_runtimes"] = JS_RUNTIMES

        opciones["remote_components"] = REMOTE_COMPONENTS

    else:
        print("ADVERTENCIA: Deno no está instalado.")

    return opciones, formato


# ============================================================
# BUSCAR ARCHIVO TEMPORAL
# ============================================================


def buscar_archivo(contador):

    prefijo = f"temp_{contador}."

    for archivo in os.listdir(CARPETA_DESCARGA):
        if archivo.startswith(prefijo):
            ruta = os.path.join(
                CARPETA_DESCARGA,
                archivo,
            )

            if os.path.isfile(ruta):
                return archivo

    return None


# ============================================================
# RENOMBRAR ARCHIVO
# ============================================================


def renombrar_archivo(archivo, contador):

    extension = os.path.splitext(archivo)[1].lower()

    nombre_final = f"{contador}{extension}"

    ruta_origen = os.path.join(
        CARPETA_DESCARGA,
        archivo,
    )

    ruta_destino = os.path.join(
        CARPETA_DESCARGA,
        nombre_final,
    )

    os.replace(
        ruta_origen,
        ruta_destino,
    )

    return nombre_final, ruta_destino, extension


# ============================================================
# DESCARGAR
# ============================================================


def ejecutar_descarga(url, download_type):

    contador = obtener_contador()

    opciones, formato = crear_opciones(
        contador,
        download_type,
    )

    print("======================================")
    print("DESCARGA WEB")
    print("URL:", url)
    print("TIPO:", download_type)
    print("FORMATO:", formato)
    print("FFMPEG:", FFMPEG_PATH)
    print("DENO:", DENO_PATH)
    print("======================================")

    try:
        with YoutubeDL(opciones) as ydl:
            ydl.download([url])

    except Exception as error:
        print("======================================")
        print("ERROR YT-DLP")
        print(error)
        print("======================================")

        return None, str(error)

    archivo = buscar_archivo(contador)

    if not archivo:
        return None, ("yt-dlp terminó la ejecución, pero no se encontró el archivo descargado.")

    try:
        nombre_final, ruta_final, extension = renombrar_archivo(
            archivo,
            contador,
        )

    except Exception as error:
        return None, (f"Error renombrando el archivo: {error}")

    return {
        "filename": nombre_final,
        "path": ruta_final,
        "extension": extension,
        "contador": contador,
    }, None


# ============================================================
# MENSAJE DE ERROR YOUTUBE
# ============================================================


def mensaje_error(error):

    texto = str(error)

    if "Sign in to confirm" in texto:
        return "YouTube rechazó la solicitud porque la IP o sesión del servidor fue identificada como tráfico automatizado. Deno/EJS está configurado, pero este bloqueo requiere autenticación mediante cookies u otro mecanismo compatible con YouTube."

    if "No supported JavaScript runtime" in texto:
        return "No se encontró un runtime JavaScript compatible. Comprueba que Deno esté instalado en Render."

    return texto


# ============================================================
# DESCARGA WEB
# ============================================================


@app2.route("/descarga", methods=["POST"])
def descarga():

    url = request.form.get("url", "").strip()

    download_type = request.form.get("download_type", "video").lower()

    if not url:
        return jsonify({
            "status": "error",
            "message": "URL requerida",
        }), 400

    if download_type not in (
        "video",
        "audio",
    ):
        download_type = "video"

    resultado, error = ejecutar_descarga(
        url,
        download_type,
    )

    if error:
        return jsonify({
            "status": "error",
            "message": mensaje_error(error),
        }), 500

    return send_from_directory(
        CARPETA_DESCARGA,
        resultado["filename"],
        as_attachment=True,
    )


# ============================================================
# API PARA ANDROID
# ============================================================


@app2.route("/api/descarga", methods=["POST"])
def api_descarga():

    data = request.get_json(silent=True) or {}

    url = str(data.get("url", "")).strip()

    download_type = str(data.get("download_type", "video")).lower()

    if not url:
        return jsonify({
            "status": "error",
            "message": "URL requerida",
        }), 400

    if download_type not in (
        "video",
        "audio",
    ):
        download_type = "video"

    resultado, error = ejecutar_descarga(
        url,
        download_type,
    )

    if error:
        return jsonify({
            "status": "error",
            "message": mensaje_error(error),
        }), 500

    tamaño = os.path.getsize(resultado["path"])

    download_url = request.host_url.rstrip("/") + "/api/descarga/archivo/" + resultado["filename"]

    return jsonify({
        "status": "success",
        "message": "Descarga completada",
        "filename": resultado["filename"],
        "extension": (resultado["extension"].replace(".", "")),
        "size_mb": round(
            tamaño / (1024 * 1024),
            2,
        ),
        "download_url": download_url,
    })


# ============================================================
# ARCHIVO PARA ANDROID
# ============================================================


@app2.route("/api/descarga/archivo/<path:filename>", methods=["GET"])
def archivo_descarga(filename):

    return send_from_directory(
        CARPETA_DESCARGA,
        filename,
        as_attachment=True,
    )


# ============================================================
# SERVIR ARCHIVOS
# ============================================================


@app2.route("/server/<path:output_file>", methods=["GET"])
def server(output_file):

    return send_from_directory(
        CARPETA_DESCARGA,
        output_file,
        as_attachment=True,
    )
