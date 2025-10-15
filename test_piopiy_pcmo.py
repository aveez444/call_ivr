# ivrcall.py
from flask import Flask, request, jsonify
import os, json, requests

app = Flask(__name__)

# Fill these env-vars in Render or replace directly (not recommended)
APP_ID = os.environ.get("PIOPIY_APPID", "4222424")
APP_SECRET = os.environ.get("PIOPIY_SECRET", "REPLACE_WITH_SECRET")
FROM_NUMBER = os.environ.get("PIOPIY_FROM", "917943446575")

# Replace these CDN URLs with the exact URLs from TeleCMI CDN
WELCOME_AUDIO = os.environ.get("WELCOME_AUDIO", "https://telecmi-cdn/path/welcome.wav")
OPTION1_AUDIO  = os.environ.get("OPTION1_AUDIO", "https://telecmi-cdn/path/option1.wav")
OPTION2_AUDIO  = os.environ.get("OPTION2_AUDIO", "https://telecmi-cdn/path/option2.wav")

# TeleCMI REST endpoint (India)
TELECMI_CALL_ENDPOINT = "https://rest.telecmi.com/v2/ind_pcmo_make_call"

@app.route("/call", methods=["POST"])
def trigger_call():
    """
    Trigger outbound call via TeleCMI REST API.
    JSON body expected: {"to": "917xxxxxx"}
    """
    req = request.get_json() or {}
    to_number = req.get("to")
    if not to_number:
        return jsonify({"error":"missing 'to' in JSON body"}), 400

    # Build PCMO actions (simple format TeleCMI usually accepts)
    # play welcome -> get single DTMF -> TeleCMI will POST results to /dtmf
    dtmf_callback = f"https://{request.host}/dtmf"  # host will be call-ivr.onrender.com
    pcmo = [
        {"action":"play","type":"audio","url":WELCOME_AUDIO,"loop":1},
        {"action":"get_input","max_digits":1,"timeout":8,"retry":1,"event_url":dtmf_callback}
    ]

    payload = {
        "appid": APP_ID,
        "secret": APP_SECRET,
        "from": FROM_NUMBER,
        "to": to_number,
        "duration": 3600,
        "pcmo": pcmo
    }

    headers = {"Content-Type":"application/json"}
    resp = requests.post(TELECMI_CALL_ENDPOINT, data=json.dumps(payload), headers=headers)
    try:
        body = resp.json()
    except Exception:
        body = {"status_code": resp.status_code, "text": resp.text}

    return jsonify({"telecmi_status": resp.status_code, "telecmi_response": body})


@app.route("/dtmf", methods=["POST"])
def dtmf():
    """TeleCMI will POST user input here. Return next PCMO to play next file and hangup."""
    data = request.get_json() or {}
    print("DTMF webhook payload:", data)

    # Try common fields TeleCMI might send
    digit = data.get("dtmf") or data.get("digits") or (data.get("data") or {}).get("dtmf") or ""
    digit = str(digit)

    if digit == "1":
        pcmo = [
            {"action":"play","type":"audio","url":OPTION1_AUDIO,"loop":1},
            {"action":"hangup"}
        ]
    elif digit == "2":
        pcmo = [
            {"action":"play","type":"audio","url":OPTION2_AUDIO,"loop":1},
            {"action":"hangup"}
        ]
    else:
        # fallback: replay menu
        pcmo = [
            {"action":"play","type":"audio","url":WELCOME_AUDIO,"loop":1},
            {"action":"get_input","max_digits":1,"timeout":8,"retry":1,"event_url":f"https://{request.host}/dtmf"}
        ]

    return jsonify({"pcmo": pcmo})


@app.route("/answer", methods=["POST"])
def answer():
    """Optional: TeleCMI may POST call answer. We can return initial PCMO here."""
    data = request.get_json() or {}
    print("ANSWER webhook payload:", data)
    dtmf_callback = f"https://{request.host}/dtmf"
    pcmo = [
        {"action":"play","type":"audio","url":WELCOME_AUDIO,"loop":1},
        {"action":"get_input","max_digits":1,"timeout":8,"retry":1,"event_url":dtmf_callback}
    ]
    return jsonify({"pcmo": pcmo})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
