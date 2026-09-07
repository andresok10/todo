from flask import Blueprint, request, jsonify, send_file, render_template
import yt_dlp
import os
import re
import base64
import tempfile
import shutil
from pathlib import Path


app2 = Blueprint("app2", __name__)


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# DETECTAR DENO
# ============================================================


def buscar_deno():
    """
    Busca Deno en las ubicaciones habituales.

    Funciona tanto en Windows como en Render/Linux.
    """

    # 1. PATH del sistema
    deno = shutil.which("deno")

    if deno and os.path.isfile(deno):
        return deno

    # 2. Ubicaciones habituales en Windows
    rutas_windows = [
        Path.home() / ".deno" / "bin" / "deno.exe",
        Path(os.environ.get("USERPROFILE", "")) / ".deno" / "bin" / "deno.exe",
    ]

    # 3. Ubicaciones habituales en Render/Linux
    rutas_linux = [
        Path("/opt/render/.deno/bin/deno"),
        Path("/opt/render/project/.deno/bin/deno"),
        Path("/root/.deno/bin/deno"),
        Path.home() / ".deno" / "bin" / "deno",
    ]

    for ruta in rutas_windows + rutas_linux:
        if ruta.is_file():
            return str(ruta)

    return None


DENO_PATH = buscar_deno()


if DENO_PATH:
    print("========================================")
    print("DENO ENCONTRADO:")
    print(DENO_PATH)
    print("========================================")
else:
    print("========================================")
    print("ADVERTENCIA: DENO NO ENCONTRADO")
    print("========================================")


# ============================================================
# DETECTAR FFMPEG
# ============================================================


def buscar_ffmpeg():
    """
    Busca FFmpeg en el PATH o en algunas ubicaciones habituales.
    """

    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg and os.path.isfile(ffmpeg):
        return ffmpeg

    rutas = [
        Path("/usr/bin/ffmpeg"),
        Path("/usr/local/bin/ffmpeg"),
        Path("C:/ffmpeg/bin/ffmpeg.exe"),
        Path("C:/Program Files/ffmpeg/bin/ffmpeg.exe"),
    ]

    for ruta in rutas:
        if ruta.is_file():
            return str(ruta)

    return None


FFMPEG_PATH = buscar_ffmpeg()


if FFMPEG_PATH:
    print("FFMPEG ENCONTRADO:")
    print(FFMPEG_PATH)
else:
    print("ADVERTENCIA: FFMPEG NO ENCONTRADO")


# ============================================================
# COOKIES DE YOUTUBE
# ============================================================


def preparar_cookies():
    """
    Lee YOUTUBE_COOKIES_B64, si existe, y crea temporalmente
    un archivo cookies.txt para yt-dlp.

    No es obligatorio para todas las descargas.
    """

    cookies_b64 = os.environ.get("YOUTUBE_COOKIES_B64")

    if not cookies_b64:
        print("COOKIES YOUTUBE: no configuradas")
        return None

    try:
        contenido = base64.b64decode(cookies_b64)

        archivo = tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False)

        archivo.write(contenido)
        archivo.close()

        try:
            os.chmod(archivo.name, 0o600)
        except Exception:
            pass

        print("COOKIES YOUTUBE: configuradas correctamente")

        return archivo.name

    except Exception as e:
        print("ERROR AL PREPARAR COOKIES:", e)
        return None


# ============================================================
# CONTADOR
# ============================================================


def obtener_contador():
    """
    Obtiene el siguiente número disponible:

    1.mp4
    2.mp4
    3.mp4
    ...
    """

    numeros = []

    for archivo in DOWNLOAD_DIR.iterdir():
        if not archivo.is_file():
            continue

        coincidencia = re.fullmatch(r"(\d+)(?:\.[^.]+)?", archivo.name)

        if coincidencia:
            numeros.append(int(coincidencia.group(1)))

    if not numeros:
        return 1

    return max(numeros) + 1


# ============================================================
# CREAR OPCIONES YT-DLP
# ============================================================


def crear_opciones(download_type, contador, cookies_file=None):
    """
    Configuración de yt-dlp.
    """

    # --------------------------------------------------------
    # DENO
    # --------------------------------------------------------

    opciones = {
        "quiet": False,
        "no_warnings": False,
        "noplaylist": True,
        "outtmpl": str(DOWNLOAD_DIR / f"temp_{contador}.%(ext)s"),
        "overwrites": True,
        "retries": 3,
        "fragment_retries": 3,
        "continuedl": True,
        "noprogress": False,
        "merge_output_format": "mp4",
        "postprocessors": [],
        "http_headers": {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"),
        },
    }

    # --------------------------------------------------------
    # DENO
    # --------------------------------------------------------

    if DENO_PATH:
        opciones["js_runtimes"] = {"deno": {"path": DENO_PATH}}

    # --------------------------------------------------------
    # FFMPEG
    # --------------------------------------------------------

    if FFMPEG_PATH:
        opciones["ffmpeg_location"] = str(Path(FFMPEG_PATH).parent)

    # --------------------------------------------------------
    # COOKIES
    # --------------------------------------------------------

    if cookies_file:
        opciones["cookiefile"] = cookies_file

    # --------------------------------------------------------
    # VIDEO
    # --------------------------------------------------------

    if download_type == "video":
        opciones["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"

        opciones["postprocessors"] = []

    # --------------------------------------------------------
    # AUDIO
    # --------------------------------------------------------

    elif download_type == "audio":
        opciones["format"] = "bestaudio/best"

        opciones["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "m4a",
                "preferredquality": "0",
            }
        ]

    return opciones


# ============================================================
# BUSCAR ARCHIVO DESCARGADO
# ============================================================


def buscar_archivo(contador, download_type):
    """
    Busca el archivo generado por yt-dlp.
    """

    prefijo = f"temp_{contador}."

    archivos = [archivo for archivo in DOWNLOAD_DIR.iterdir() if archivo.is_file() and archivo.name.startswith(prefijo)]

    if not archivos:
        return None

    # Preferencias para video
    if download_type == "video":
        extensiones = [
            ".mp4",
            ".mkv",
            ".webm",
            ".mov",
        ]

    else:
        extensiones = [
            ".m4a",
            ".mp3",
            ".opus",
            ".webm",
            ".aac",
        ]

    for extension in extensiones:
        for archivo in archivos:
            if archivo.suffix.lower() == extension:
                return archivo

    return archivos[0]


# ============================================================
# RENOMBRAR ARCHIVO
# ============================================================


def renombrar_archivo(archivo, contador):
    """
    Convierte:

        temp_1.mp4

    en:

        1.mp4
    """

    if not archivo:
        return None

    extension = archivo.suffix

    destino = DOWNLOAD_DIR / f"{contador}{extension}"

    # Si por alguna razón ya existe
    if destino.exists():
        destino.unlink()

    archivo.rename(destino)

    return destino


# ============================================================
# EJECUTAR DESCARGA
# ============================================================


def ejecutar_descarga(url, download_type):
    """
    Ejecuta yt-dlp y devuelve el archivo final.
    """

    contador = obtener_contador()

    cookies_file = None
    archivo_temporal = None

    try:
        cookies_file = preparar_cookies()

        opciones = crear_opciones(download_type, contador, cookies_file)

        print("========================================")
        print("INICIANDO DESCARGA")
        print("URL:", url)
        print("TIPO:", download_type)
        print("DENO:", DENO_PATH or "NO DISPONIBLE")
        print("FFMPEG:", FFMPEG_PATH or "NO DISPONIBLE")
        print("CONTADOR:", contador)
        print("========================================")

        with yt_dlp.YoutubeDL(opciones) as ydl:
            ydl.download([url])

        archivo_temporal = buscar_archivo(contador, download_type)

        if not archivo_temporal:
            raise FileNotFoundError("yt-dlp terminó pero no se encontró el archivo descargado.")

        archivo_final = renombrar_archivo(archivo_temporal, contador)

        if not archivo_final:
            raise FileNotFoundError("No fue posible renombrar el archivo.")

        print("========================================")
        print("DESCARGA COMPLETADA")
        print("ARCHIVO:", archivo_final)
        print("========================================")

        return archivo_final

    finally:
        # Eliminar cookies temporales
        if cookies_file:
            try:
                os.remove(cookies_file)
            except Exception:
                pass

        # Eliminar posibles temporales restantes
        if archivo_temporal:
            try:
                if archivo_temporal.exists():
                    archivo_temporal.unlink()
            except Exception:
                pass


# ============================================================
# MENSAJES DE ERROR
# ============================================================


def mensaje_error(error):
    """
    Convierte errores técnicos de yt-dlp en mensajes
    más comprensibles.
    """

    texto = str(error)

    texto_lower = texto.lower()

    if "sign in to confirm you're not a bot" in texto_lower:
        return "YouTube requiere autenticación para esta solicitud. Configura YOUTUBE_COOKIES_B64 si es necesario."

    if "no supported javascript runtime" in texto_lower:
        return "No se encontró un runtime JavaScript compatible. Verifica que Deno esté instalado y disponible."

    if "ffmpeg" in texto_lower:
        return "FFmpeg no está disponible o no pudo procesar el archivo."

    if "unsupported url" in texto_lower:
        return "La URL proporcionada no es compatible."

    if "private video" in texto_lower:
        return "El video es privado y no puede descargarse."

    if "video unavailable" in texto_lower:
        return "El video no está disponible."

    return texto


# ============================================================
# RUTA WEB /descarga
# ============================================================


@app2.route("/descarga", methods=["POST"])
def descarga():

    url = request.form.get("url", "").strip()

    download_type = request.form.get("download_type", "video").strip().lower()

    if not url:
        return ("Debes proporcionar una URL.", 400)

    if download_type not in ("video", "audio"):
        return ("Tipo de descarga inválido.", 400)

    try:
        archivo = ejecutar_descarga(url, download_type)

        return send_file(archivo, as_attachment=True, download_name=archivo.name)

    except Exception as e:
        print("ERROR DURANTE LA DESCARGA:")
        print(e)

        return (f"Error durante la descarga: {mensaje_error(e)}", 500)


# ============================================================
# API /api/descarga
# ============================================================


@app2.route("/api/descarga", methods=["POST"])
def api_descarga():

    datos = request.get_json(silent=True) or {}

    # También acepta form-data por compatibilidad
    url = (datos.get("url") or request.form.get("url") or "").strip()

    download_type = (datos.get("download_type") or request.form.get("download_type") or "video").strip().lower()

    if not url:
        return jsonify({"success": False, "message": "Debes proporcionar una URL."}), 400

    if download_type not in ("video", "audio"):
        return jsonify({"success": False, "message": "Tipo de descarga inválido."}), 400

    try:
        archivo = ejecutar_descarga(url, download_type)

        tamaño = archivo.stat().st_size

        tamaño_mb = round(tamaño / (1024 * 1024), 2)

        return jsonify({"success": True, "filename": archivo.name, "extension": archivo.suffix.lstrip("."), "size_mb": tamaño_mb, "download_url": (f"/api/descarga/archivo/{archivo.name}")})

    except Exception as e:
        print("ERROR API DURANTE LA DESCARGA:")
        print(e)

        return jsonify({"success": False, "message": mensaje_error(e)}), 500


# ============================================================
# DESCARGAR ARCHIVO DE LA API
# ============================================================


@app2.route("/api/descarga/archivo/<filename>", methods=["GET"])
def api_descarga_archivo(filename):

    # Evita rutas como ../../archivo
    nombre = Path(filename).name

    archivo = DOWNLOAD_DIR / nombre

    if not archivo.is_file():
        return jsonify({"success": False, "message": "Archivo no encontrado."}), 404

    return send_file(archivo, as_attachment=True, download_name=archivo.name)


# ============================================================
# RUTA /server/<path:output_file>
# ============================================================


@app2.route("/server/<path:output_file>", methods=["GET"])
def server_file(output_file):

    # Seguridad: evita salir de DOWNLOAD_DIR
    nombre = Path(output_file).name

    archivo = DOWNLOAD_DIR / nombre

    if not archivo.is_file():
        return ("Archivo no encontrado.", 404)

    return send_file(archivo, as_attachment=True, download_name=archivo.name)


# ============================================================
# INFORMACIÓN DEL SISTEMA
# ============================================================


@app2.route("/api/descarga/status", methods=["GET"])
def descarga_status():

    return jsonify({"success": True, "yt_dlp": yt_dlp.version.__version__, "deno": DENO_PATH is not None, "deno_path": DENO_PATH, "ffmpeg": FFMPEG_PATH is not None, "ffmpeg_path": FFMPEG_PATH, "cookies": bool(os.environ.get("YOUTUBE_COOKIES_B64"))})
