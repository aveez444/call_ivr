# ivrcall_fixed.py
from flask import Flask, request, jsonify
import os
from piopiy.action import Action
from piopiy.underscore import isNumber
import requests

app = Flask(__name__)

# ---------- configuration ----------
APP_ID = int(os.environ.get("PIOPIY_APP_ID", 4222424))
APP_SECRET = os.environ.get("PIOPIY_SECRET", "REPLACE_WITH_SECRET")
FROM_NUMBER = int(os.environ.get("PIOPIY_FROM", 917943446575))
APP_URL = os.environ.get("APP_URL", "").rstrip("/")

WELCOME_AUDIO = os.environ.get("WELCOME_AUDIO", "")
OPTION1_AUDIO = os.environ.get("OPTION1_AUDIO", "")
OPTION2_AUDIO = os.environ.get("OPTION2_AUDIO", OPTION1_AUDIO)

# ---------- Helpers ----------
def build_callback_path(path="/dtmf"):
    if APP_URL:
        return f"{APP_URL}{path}"
    else:
        return f"http://localhost:5000{path}"  # fallback

# ---------- Endpoints ----------
@app.route("/call", methods=["POST"])
def trigger_call():
    """
    Trigger outbound call via TeleCMI REST API using Action class to build PCMO.
    """
    req = request.get_json() or {}
    to_number = req.get("to")
    if not to_number or not isNumber(to_number):
        return jsonify({"error": "missing or invalid 'to' number"}), 400

    dtmf_callback = build_callback_path("/dtmf")

    # Use Action class to build schema-compliant PCMO
    pcmo = Action()
    pcmo.play(WELCOME_AUDIO, loop=1)
    pcmo.get_input(max_digits=1, timeout=8, retry=1, event_url=dtmf_callback)

    payload = {
        "appid": APP_ID,
        "secret": APP_SECRET,
        "from": FROM_NUMBER,
        "to": int(to_number),
        "duration": 3600,
        "pcmo": pcmo.PCMO()
    }

    resp = requests.post("https://rest.telecmi.com/v2/ind_pcmo_make_call",
                         json=payload,
                         headers={"Content-Type": "application/json"})
    try:
        body = resp.json()
    except Exception:
        body = {"status_code": resp.status_code, "text": resp.text}

    return jsonify({"telecmi_status": resp.status_code, "telecmi_response": body})


@app.route("/dtmf", methods=["POST"])
def dtmf():
    """
    Handle DTMF input and respond with next PCMO using Action.
    """
    data = request.get_json() or {}
    digit = str(data.get("dtmf") or data.get("digits") or "").strip()
    dtmf_callback = build_callback_path("/dtmf")

    pcmo = Action()
    if digit == "1":
        pcmo.play(OPTION1_AUDIO, loop=1)
        pcmo.hangup()
    elif digit == "2":
        pcmo.play(OPTION2_AUDIO, loop=1)
        pcmo.hangup()
    else:
        # fallback: replay menu
        pcmo.play(WELCOME_AUDIO, loop=1)
        pcmo.get_input(max_digits=1, timeout=8, retry=1, event_url=dtmf_callback)

    return jsonify({"pcmo": pcmo.PCMO()})


@app.route("/answer", methods=["POST"])
def answer():
    """
    Optional: TeleCMI may POST call answer. Return initial PCMO.
    """
    dtmf_callback = build_callback_path("/dtmf")
    pcmo = Action()
    pcmo.play(WELCOME_AUDIO, loop=1)
    pcmo.get_input(max_digits=1, timeout=8, retry=1, event_url=dtmf_callback)
    return jsonify({"pcmo": pcmo.PCMO()})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
