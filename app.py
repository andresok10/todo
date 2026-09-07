from flask import Flask
from calendario import app1
from des import app2
import os

app = Flask(__name__)

app.secret_key = "supersecretkey"

app.register_blueprint(app1)
app.register_blueprint(app2)

print("========================================")
print("RUTAS REGISTRADAS:")
print(app.url_map)
print("========================================")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
    )