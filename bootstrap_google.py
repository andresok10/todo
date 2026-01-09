import os
import base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token_calendar.pickle")

def bootstrap_calendar_token():
    if os.path.exists(TOKEN_PATH):
        return

    token_b64 = os.environ.get("GOOGLE_CALENDAR_TOKEN_B64")
    if not token_b64:
        raise RuntimeError("GOOGLE_CALENDAR_TOKEN_B64 no definida")

    with open(TOKEN_PATH, "wb") as f:
        f.write(base64.b64decode(token_b64))