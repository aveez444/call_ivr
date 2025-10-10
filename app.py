# app.py
import os
import requests
from flask import Flask, request, Response, jsonify
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)

# PIOPIY Configuration
PIOPIY_SECRET = os.getenv("PIOPIY_SECRET", "ccf0a102-ea6a-4f26-8d1c-7a1732eb0780")
PIOPIY_APP_ID = os.getenv("PIOPIY_APP_ID", "4222424")
PIOPIY_BASE_URL = "https://api.telecmi.com/v1/call"

# Language texts (same as your Twilio version)
LANGUAGES = {
    "en": {
        "welcome": "Welcome to HealthyCare Clinic. For English, press 1. For Hindi, press 2. For Marathi, press 3. To repeat this menu press 9.",
        "no_input": "We did not receive any input. Goodbye.",
        "invalid_selection": "Invalid selection. ",
        "return_main": "No input received. Returning to main menu.",
        "main_menu": "For appointment booking press 1. For emergency help press 2. For pathology tests press 3. To repeat this menu press 9.",
        "appointment_menu": "For appointment booking. For Dental press 1. For General Doctor press 2. For Orthopaedic press 3. To repeat this menu press 9.",
        "pathology_menu": "Pathology tests. For regular blood test press 1. For full body profile press 2. For heart check up press 3. To repeat this menu press 9.",
        "emergency_connect": "Connecting you to emergency services. Please hold.",
        "emergency_fail": "Unable to connect to emergency number. Goodbye.",
        "appointment_thanks": "Thank you. You selected {}. Our team will call you soon to schedule a convenient time.",
        "appointment_record": "If you would like to leave a short message with your preferred time or details, please record after the tone. Press hash when finished. To repeat the previous menu press 9.",
        "pathology_thanks": "Thank you. You selected {}. Our staff will call you shortly to arrange an appointment and share instructions.",
        "pathology_record": "If you want to leave a message for preferred timing, record after the tone. Press hash when finished. To repeat the previous menu press 9.",
        "thankyou_goodbye": "Thank you. Goodbye.",
        "recording_saved": "Your message has been recorded. We will contact you soon. Goodbye."
    },
    "hi": {
        "welcome": "स्वागत है हेल्थीकेयर क्लिनिक में। अंग्रेजी के लिए, 1 दबाएं। हिंदी के लिए, 2 दबाएं। मराठी के लिए 3 दबाएं। इस मेनू को दोहराने के लिए 9 दबाएं।",
        "no_input": "हमें कोई इनपुट प्राप्त नहीं हुआ। अलविदा।",
        "invalid_selection": "अमान्य चयन। ",
        "return_main": "कोई इनपुट प्राप्त नहीं हुआ। मुख्य मेनू पर वापस जा रहे हैं।",
        "main_menu": "अपॉइंटमेंट बुकिंग के लिए 1 दबाएं। इमरजेंसी हेल्प के लिए 2 दबाएं। पैथोलॉजी टेस्ट के लिए 3 दबाएं। इस मेनू को दोहराने के लिए 9 दबाएं।",
        "appointment_menu": "अपॉइंटमेंट बुकिंग के लिए। डेंटल के लिए 1 दबाएं। जनरल डॉक्टर के लिए 2 दबाएं। ऑर्थोपेडिक के लिए 3 दबाएं। इस मेनू को दोहराने के लिए 9 दबाएं।",
        "pathology_menu": "पैथोलॉजी टेस्ट। रेगुलर ब्लड टेस्ट के लिए 1 दबाएं। फुल बॉडी प्रोफाइल के लिए 2 दबाएं। हार्ट चेक अप के लिए 3 दबाएं। इस मेनू को दोहराने के लिए 9 दबाएं।",
        "emergency_connect": "आपको इमरजेंसी सर्विसेज से कनेक्ट किया जा रहा है। कृपया प्रतीक्षा करें।",
        "emergency_fail": "इमरजेंसी नंबर से कनेक्ट नहीं हो पा रहे हैं। अलविदा।",
        "appointment_thanks": "धन्यवाद। आपने {} चुना है। हमारी टीम जल्द ही आपको एक सुविधाजनक समय निर्धारित करने के लिए कॉल करेगी।",
        "appointment_record": "यदि आप अपने पसंदीदा समय या विवरण के साथ एक छोटा संदेश छोड़ना चाहते हैं, कृपया टोन के बाद रिकॉर्ड करें। समाप्त करने पर हैश दबाएं। पिछले मेनू को दोहराने के लिए 9 दबाएं।",
        "pathology_thanks": "धन्यवाद। आपने {} चुना है। हमारा स्टाफ जल्द ही आपके साथ एक अपॉइंटमेंट व्यवस्थित करने और निर्देश साझा करने के लिए कॉल करेगा।",
        "pathology_record": "यदि आप पसंदीदा समय के लिए कोई संदेश छोड़ना चाहते हैं, टोन के बाद रिकॉर्ड करें। समाप्त करने पर हैश दबाएं। पिछले मेनू को दोहराने के लिए 9 दबाएं।",
        "thankyou_goodbye": "धन्यवाद। अलविदा।",
        "recording_saved": "आपका संदेश रिकॉर्ड कर लिया गया है। हम जल्द ही आपसे संपर्क करेंगे। अलविदा।"
    },
    "mr": {
        "welcome": "हेल्थीकेअर क्लिनिकमध्ये आपले स्वागत आहे. इंग्रजीसाठी 1 दाबा. हिंदीसाठी 2 दाबा. मराठीसाठी 3 दाबा. हा मेनू पुन्हा ऐकण्यासाठी 9 दाबा.",
        "no_input": "आपला इनपुट मिळाला नाही. अलविदा.",
        "invalid_selection": "अवैध निवड. ",
        "return_main": "कोणताही इनपुट मिळाला नाही. मुख्य मेन्यूकडे परत जात आहोत.",
        "main_menu": "अपॉइंटमेंट बुक करण्यासाठी 1 दाबा. आपत्कालीन मदतीसाठी 2 दाबा. पॅथॉलॉजी चाचणीसाठी 3 दाबा. हा मेनू पुन्हा ऐकण्यासाठी 9 दाबा.",
        "appointment_menu": "अपॉइंटमेंट बुकिंगसाठी. डेन्टल साठी 1 दाबा. जनरल डॉक्टर साठी 2 दाबा. अर्थोपेडिक साठी 3 दाबा. हा मेनू पुन्हा ऐकण्यासाठी 9 दाबा.",
        "pathology_menu": "पॅथॉलॉजी टेस्ट. नियमित रक्त तपासणीसाठी 1 दाबा. फुल बॉडी प्रोफाइलसाठी 2 दाबा. हार्ट चेकअपसाठी 3 दाबा. हा मेनू पुन्हा ऐकण्यासाठी 9 दाबा.",
        "emergency_connect": "आपल्याला आपत्कालीन सेवांशी जोडले जात आहे. कृपया थांबा.",
        "emergency_fail": "आपत्कालीन नंबरशी कनेक्ट करता येत नाही. अलविदा.",
        "appointment_thanks": "धन्यवाद. आपण {} निवडले. आमची टीम लवकरच आपल्याला कॉल करून वेळ ठरवेल.",
        "appointment_record": "आपण आपला पसंतीचा वेळ किंवा तपशील सांगणारा छोटा संदेश ठेवू इच्छित असल्यास, टोननंतर रेकॉर्ड करा. पूर्ण झाल्यावर हैश दाबा. मागील मेनू पुन्हा ऐकण्यासाठी 9 दाबा.",
        "pathology_thanks": "धन्यवाद. आपण {} निवडले. आमचे कर्मचारी लवकरच आपल्याशी संपर्क करेल.",
        "pathology_record": "पसंत वेळेकरता संदेश ठेवायचा असल्यास, टोननंतर रेकॉर्ड करा. पूर्ण झाल्यावर हैश दाबा. मागील मेनू पुन्हा ऐकण्यासाठी 9 दाबा.",
        "thankyou_goodbye": "धन्यवाद. अलविदा.",
        "recording_saved": "आपला संदेश रेकॉर्ड केला गेला आहे. आम्ही लवकरच संपर्क करू. अलविदा."
    }
}

DOCTOR_MAP = {
    "en": {"1": "Dental", "2": "General Doctor", "3": "Orthopaedic"},
    "hi": {"1": "डेंटल", "2": "जनरल डॉक्टर", "3": "ऑर्थोपेडिक"},
    "mr": {"1": "डेन्टल", "2": "जनरल डॉक्टर", "3": "ऑर्थोपेडिक"}
}

TEST_MAP = {
    "en": {"1": "regular blood test", "2": "full body profile", "3": "heart check up"},
    "hi": {"1": "रेगुलर ब्लड टेस्ट", "2": "फुल बॉडी प्रोफाइल", "3": "हार्ट चेक अप"},
    "mr": {"1": "नियमित रक्त तपासणी", "2": "फुल बॉडी प्रोफाइल", "3": "हार्ट चेकअप"}
}

def generate_piopiy_xml(action_elements):
    """Generate PIOPIY XML response"""
    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?><Response>']
    xml_parts.extend(action_elements)
    xml_parts.append('</Response>')
    return ''.join(xml_parts)

def get_language(digits):
    if digits == "1":
        return "en"
    elif digits == "2":
        return "hi"
    elif digits == "3":
        return "mr"
    return None

# Answer URL - This is where PIOPIY sends the call
@app.route("/call", methods=["POST"])
def handle_call():
    """This is the Answer URL that PIOPIY will call when a call is answered"""
    caller = request.form.get('caller')
    called = request.form.get('called')
    callid = request.form.get('callid')
    
    print(f"PIOPIY Call Received - From: {caller}, To: {called}, CallID: {callid}")
    
    # Start with language selection
    actions = [
        '<Speak>'+LANGUAGES["en"]["welcome"]+'</Speak>',
        '<Gather numDigits="1" timeout="8" action="/handle-language" method="POST"/>'
    ]
    
    return Response(generate_piopiy_xml(actions), mimetype='text/xml')

@app.route("/handle-language", methods=["POST"])
def handle_language():
    digits = request.form.get('digits', '')
    actions = []
    
    if digits == "9":  # Repeat
        actions = [
            '<Speak>'+LANGUAGES["en"]["welcome"]+'</Speak>',
            '<Gather numDigits="1" timeout="8" action="/handle-language" method="POST"/>'
        ]
    else:
        lang = get_language(digits)
        if lang:
            actions = [
                '<Speak>'+LANGUAGES[lang]["main_menu"]+'</Speak>',
                '<Gather numDigits="1" timeout="8" action="/handle-main?lang='+lang+'" method="POST"/>'
            ]
        else:
            actions = [
                '<Speak>'+LANGUAGES["en"]["invalid_selection"]+' Please choose a language.</Speak>',
                '<Speak>'+LANGUAGES["en"]["welcome"]+'</Speak>',
                '<Gather numDigits="1" timeout="8" action="/handle-language" method="POST"/>'
            ]
    
    return Response(generate_piopiy_xml(actions), mimetype='text/xml')

@app.route("/handle-main", methods=["POST"])
def handle_main():
    digits = request.form.get('digits', '')
    lang = request.args.get('lang', 'en')
    actions = []
    
    if digits == "9" or digits == "":
        actions = [
            '<Speak>'+LANGUAGES[lang]["main_menu"]+'</Speak>',
            '<Gather numDigits="1" timeout="8" action="/handle-main?lang='+lang+'" method="POST"/>'
        ]
    elif digits == "1":
        actions = [
            '<Speak>'+LANGUAGES[lang]["appointment_menu"]+'</Speak>',
            '<Gather numDigits="1" timeout="8" action="/handle-appointment-doctor?lang='+lang+'" method="POST"/>'
        ]
    elif digits == "2":
        # For emergency, dial out to another number
        actions = [
            '<Speak>'+LANGUAGES[lang]["emergency_connect"]+'</Speak>',
            '<Dial>+919999999999</Dial>',  # Replace with actual emergency number
            '<Speak>'+LANGUAGES[lang]["emergency_fail"]+'</Speak>',
            '<Hangup/>'
        ]
    elif digits == "3":
        actions = [
            '<Speak>'+LANGUAGES[lang]["pathology_menu"]+'</Speak>',
            '<Gather numDigits="1" timeout="8" action="/handle-pathology?lang='+lang+'" method="POST"/>'
        ]
    else:
        actions = [
            '<Speak>'+LANGUAGES[lang]["invalid_selection"]+LANGUAGES[lang]["main_menu"]+'</Speak>',
            '<Gather numDigits="1" timeout="8" action="/handle-main?lang='+lang+'" method="POST"/>'
        ]
    
    return Response(generate_piopiy_xml(actions), mimetype='text/xml')

# Add appointment and pathology handlers
@app.route("/handle-appointment-doctor", methods=["POST"])
def handle_appointment_doctor():
    digits = request.form.get('digits', '')
    lang = request.args.get('lang', 'en')
    actions = []
    
    if digits == "9" or digits == "":
        actions = [
            '<Speak>'+LANGUAGES[lang]["appointment_menu"]+'</Speak>',
            '<Gather numDigits="1" timeout="8" action="/handle-appointment-doctor?lang='+lang+'" method="POST"/>'
        ]
    else:
        doc = DOCTOR_MAP[lang].get(digits)
        if doc:
            actions = [
                '<Speak>'+LANGUAGES[lang]["appointment_thanks"].format(doc)+'</Speak>',
                '<Speak>'+LANGUAGES[lang]["thankyou_goodbye"]+'</Speak>',
                '<Hangup/>'
            ]
        else:
            actions = [
                '<Speak>'+LANGUAGES[lang]["invalid_selection"]+LANGUAGES[lang]["appointment_menu"]+'</Speak>',
                '<Gather numDigits="1" timeout="8" action="/handle-appointment-doctor?lang='+lang+'" method="POST"/>'
            ]
    
    return Response(generate_piopiy_xml(actions), mimetype='text/xml')

@app.route("/handle-pathology", methods=["POST"])
def handle_pathology():
    digits = request.form.get('digits', '')
    lang = request.args.get('lang', 'en')
    actions = []
    
    if digits == "9" or digits == "":
        actions = [
            '<Speak>'+LANGUAGES[lang]["pathology_menu"]+'</Speak>',
            '<Gather numDigits="1" timeout="8" action="/handle-pathology?lang='+lang+'" method="POST"/>'
        ]
    else:
        test = TEST_MAP[lang].get(digits)
        if test:
            actions = [
                '<Speak>'+LANGUAGES[lang]["pathology_thanks"].format(test)+'</Speak>',
                '<Speak>'+LANGUAGES[lang]["thankyou_goodbye"]+'</Speak>',
                '<Hangup/>'
            ]
        else:
            actions = [
                '<Speak>'+LANGUAGES[lang]["invalid_selection"]+LANGUAGES[lang]["pathology_menu"]+'</Speak>',
                '<Gather numDigits="1" timeout="8" action="/handle-pathology?lang='+lang+'" method="POST"/>'
            ]
    
    return Response(generate_piopiy_xml(actions), mimetype='text/xml')

@app.route("/make-call", methods=["POST"])
def make_call():
    """Endpoint to trigger outgoing calls using PIOPIY REST API"""
    body = request.get_json(force=True, silent=True) or {}
    to_number = body.get("to")
    
    if not to_number:
        return jsonify({"error": "missing 'to' field"}), 400
    
    try:
        # Prepare the API request
        headers = {
            'Content-Type': 'application/json'
        }
        
        payload = {
            'app_id': PIOPIY_APP_ID,
            'secret': PIOPIY_SECRET,
            'from': '917943446575',  # Your PIOPIY number
            'to': to_number,
            'answer_url': f"{request.url_root.rstrip('/')}/call"  # Your answer URL
        }
        
        # Make API call to PIOPIY
        response = requests.post(PIOPIY_BASE_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                "status": "queued", 
                "to": to_number,
                "piopiy_response": result
            })
        else:
            return jsonify({
                "error": f"PIOPIY API error: {response.status_code}",
                "details": response.text
            }), 500
            
    except Exception as e:  
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return jsonify({"status": "PIOPIY IVR Server is running"})

@app.route("/test", methods=["GET"])
def test():
    """Test endpoint to verify server is working"""
    return jsonify({
        "message": "Server is running",
        "app_id": PIOPIY_APP_ID,
        "has_secret": bool(PIOPIY_SECRET)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)