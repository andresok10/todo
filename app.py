from flask import Flask, current_app
from datetime import datetime
from calendario import app1
from descargas import app2
import os, urllib.request,zipfile ,tarfile, ssl, certifi, shutil

app = Flask(__name__)
app.secret_key = "supersecretkey"

@app.context_processor
def inject_globals():
    return {"hoy": datetime.today()}

app.register_blueprint(app1)
app.register_blueprint(app2)

#carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "descargas")
    
if __name__ == "__main__":
    # Mostrar contenido de la carpeta descarga
    '''carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "descarga")
    if os.path.exists(carpeta):
        print(f"📂 Contenido de: {carpeta}\n")
        for nombre in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, nombre)
            print(ruta_completa)
    else:
        print(f"❌ La carpeta {carpeta} no existe.")'''
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)