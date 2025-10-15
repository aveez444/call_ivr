# ivrcall.py
from flask import Flask, request, jsonify
import os, json, requests

app = Flask(__name__)

# ---------- configuration from environment ----------
APP_ID = os.environ.get("PIOPIY_APP_ID", "4222424")
APP_SECRET = os.environ.get("PIOPIY_SECRET", "REPLACE_WITH_SECRET")
FROM_NUMBER = os.environ.get("PIOPIY_FROM", "917943446575")

# Your public app URL (set in Render): https://call-ivr.onrender.com
APP_URL = os.environ.get("APP_URL", "").rstrip("/")

# Replace these with the exact CDN URLs from TeleCMI (set in Render env)
WELCOME_AUDIO = os.environ.get(
    "WELCOME_AUDIO",
    "https://cdn.telecmi.com/cdn/1760350048331ElevenLabs20251009T151503AnikaSweetLivelyHindiSocialMediaVoicepvcsp99s100sb100se0bm2wav6ca049c0-a81c-11f0-9f7b-3b2ce86cca8b_piopiy.wav"
)
OPTION1_AUDIO = os.environ.get(
    "OPTION1_AUDIO",
    "https://cdn.telecmi.com/cdn/1760362929284ElevenLabs20251009T151214AnikaSweetLivelyHindiSocialMediaVoicepvcsp99s100sb100se0bm2wav6a456e30-a83a-11f0-9f7b-3b2ce86cca8b_piopiy.wav"
)
OPTION2_AUDIO = os.environ.get("OPTION2_AUDIO", OPTION1_AUDIO)

# TeleCMI REST endpoint (India)
TELECMI_CALL_ENDPOINT = "https://rest.telecmi.com/v2/ind_pcmo_make_call"

# ---------- Helpers ----------
def build_callback_path(path="/dtmf"):
    """
    Build full HTTPS callback URL for TeleCMI to call.
    Prefer APP_URL env var. If not set, fallback to request.host (less reliable).
    """
    if APP_URL:
        return f"{APP_URL}{path}"
    else:
        # fallback to request.host
        host = request.host_url.rstrip("/")
        return f"{host}{path}"

# ---------- Endpoints ----------
@app.route("/call", methods=["POST"])
def trigger_call():
    """
    Trigger outbound call via TeleCMI REST API.
    JSON body expected: {"to": "917xxxxxx"}
    """
    req = request.get_json() or {}
    to_number = req.get("to")
    if not to_number:
        return jsonify({"error": "missing 'to' in JSON body"}), 400

    dtmf_callback = build_callback_path("/dtmf")

    pcmo = [
        {"action": "play", "type": "audio", "url": WELCOME_AUDIO, "loop": 1},
        {"action": "get_input", "max_digits": 1, "timeout": 8, "retry": 1, "event_url": dtmf_callback}
    ]

    payload = {
        "appid": APP_ID,
        "secret": APP_SECRET,
        "from": FROM_NUMBER,
        "to": to_number,
        "duration": 3600,
        "pcmo": pcmo
    }

    headers = {"Content-Type": "application/json"}
    resp = requests.post(TELECMI_CALL_ENDPOINT, data=json.dumps(payload), headers=headers)
    try:
        body = resp.json()
    except Exception:
        body = {"status_code": resp.status_code, "text": resp.text}

    return jsonify({"telecmi_status": resp.status_code, "telecmi_response": body})


@app.route("/dtmf", methods=["POST"])
def dtmf():
    """
    TeleCMI will POST user input here. Return next PCMO to play next file and hangup.
    """
    data = request.get_json() or {}
    app.logger.info("DTMF webhook payload: %s", data)

    # Try common keys
    digit = data.get("dtmf") or data.get("digits") or (data.get("data") or {}).get("dtmf") or ""
    digit = str(digit).strip()

    if digit == "1":
        pcmo = [
            {"action": "play", "type": "audio", "url": OPTION1_AUDIO, "loop": 1},
            {"action": "hangup"}
        ]
    elif digit == "2":
        pcmo = [
            {"action": "play", "type": "audio", "url": OPTION2_AUDIO, "loop": 1},
            {"action": "hangup"}
        ]
    else:
        # fallback: replay menu
        fallback_callback = build_callback_path("/dtmf")
        pcmo = [
            {"action": "play", "type": "audio", "url": WELCOME_AUDIO, "loop": 1},
            {"action": "get_input", "max_digits": 1, "timeout": 8, "retry": 1, "event_url": fallback_callback}
        ]

    return jsonify({"pcmo": pcmo})


@app.route("/answer", methods=["POST"])
def answer():
    """
    Optional: TeleCMI may POST call answer. Return initial PCMO here if they call answer webhook.
    """
    data = request.get_json() or {}
    app.logger.info("ANSWER webhook payload: %s", data)

    dtmf_callback = build_callback_path("/dtmf")
    pcmo = [
        {"action": "play", "type": "audio", "url": WELCOME_AUDIO, "loop": 1},
        {"action": "get_input", "max_digits": 1, "timeout": 8, "retry": 1, "event_url": dtmf_callback}
    ]
    return jsonify({"pcmo": pcmo})


if __name__ == "__main__":
    # debug only
    app.run(host="0.0.0.0", port=5000, debug=True)
