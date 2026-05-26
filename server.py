"""
Flask server — handles incoming Twilio phone calls.
Each call gets its own Receptionist session.

Webhook URLs to set in Twilio:
  Voice → https://YOUR_NGROK_URL/voice/answer
  Status → https://YOUR_NGROK_URL/voice/status
"""

import os
from flask import Flask, request, Response, jsonify, send_file
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from dotenv import load_dotenv
import database
from receptionist import Receptionist

load_dotenv()

app = Flask(__name__)
CORS(app)

# In-memory store: { call_sid: Receptionist }
active_calls = {}

# Map Twilio phone numbers → business IDs
# Set these in .env as: PHONE_MAP=+911234567890:tanuj_dental,+910987654321:barber_001
def load_phone_map():
    raw = os.getenv("PHONE_MAP", "")
    mapping = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if ":" in entry:
            number, biz_id = entry.split(":", 1)
            mapping[number.strip()] = biz_id.strip()
    return mapping


def twiml_say_and_listen(text, action="/voice/gather"):
    """Speak text then wait for caller's voice input."""
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action=action,
        method="POST",
        speech_timeout="auto",
        language="en-IN",
        enhanced=True,
    )
    gather.say(text, voice="alice", language="en-IN")
    resp.append(gather)
    # If caller says nothing, re-prompt
    resp.redirect("/voice/no_input", method="POST")
    return Response(str(resp), mimetype="text/xml")


def twiml_say_and_hangup(text):
    """Speak final message and end the call."""
    resp = VoiceResponse()
    resp.say(text, voice="alice", language="en-IN")
    resp.hangup()
    return Response(str(resp), mimetype="text/xml")


def get_business_for_call(to_number):
    """Find which business this call is for based on the called number."""
    phone_map = load_phone_map()
    if to_number and to_number in phone_map:
        return phone_map[to_number]
    # Fallback: use default business from .env
    default = os.getenv("DEFAULT_BUSINESS_ID", "")
    if default:
        return default
    # Last resort: first business in DB
    businesses = database.get_all_businesses()
    if businesses:
        return businesses[0]["id"]
    return None


# ------------------------------------------------------------------ #
#  Routes                                                             #
# ------------------------------------------------------------------ #

@app.route("/voice/answer", methods=["POST"])
def answer():
    """Twilio calls this when a new call comes in."""
    call_sid = request.form.get("CallSid")
    to_number = request.form.get("To")
    from_number = request.form.get("From")

    print(f"\n📞 Incoming call: {from_number} → {to_number} [{call_sid}]")

    business_id = get_business_for_call(to_number)
    if not business_id:
        return twiml_say_and_hangup(
            "Thank you for calling. We are currently unavailable. Please try again later."
        )

    try:
        receptionist = Receptionist(business_id)
        active_calls[call_sid] = receptionist
        greeting = receptionist.greeting()
        print(f"[{call_sid}] Assistant: {greeting}")
        return twiml_say_and_listen(greeting)
    except Exception as e:
        print(f"Error starting receptionist: {e}")
        return twiml_say_and_hangup(
            "Thank you for calling. We are experiencing technical difficulties. Please call back shortly."
        )


@app.route("/voice/gather", methods=["POST"])
def gather():
    """Twilio calls this after the caller speaks."""
    call_sid = request.form.get("CallSid")
    speech = request.form.get("SpeechResult", "").strip()
    confidence = request.form.get("Confidence", "0")

    receptionist = active_calls.get(call_sid)
    if not receptionist:
        return twiml_say_and_hangup(
            "I'm sorry, your session has expired. Please call back."
        )

    if not speech:
        return twiml_say_and_listen("I didn't quite catch that. Could you please repeat?")

    print(f"[{call_sid}] Customer (conf {confidence}): {speech}")

    # Exit words
    if any(w in speech.lower() for w in ["bye", "goodbye", "hang up", "end call", "disconnect"]):
        del active_calls[call_sid]
        return twiml_say_and_hangup("Thank you for calling. Have a wonderful day. Goodbye!")

    try:
        response = receptionist.process(speech)
        print(f"[{call_sid}] Assistant: {response}")

        if receptionist.is_done:
            del active_calls[call_sid]
            return twiml_say_and_hangup(response)

        return twiml_say_and_listen(response)

    except Exception as e:
        print(f"Error processing input: {e}")
        active_calls.pop(call_sid, None)
        return twiml_say_and_hangup(
            "I'm sorry, something went wrong. Please call back or speak to our team directly."
        )


@app.route("/voice/no_input", methods=["POST"])
def no_input():
    """Called when caller stays silent for too long."""
    call_sid = request.form.get("CallSid")
    receptionist = active_calls.get(call_sid)

    if receptionist:
        return twiml_say_and_listen(
            "Are you still there? Please go ahead and speak, I'm listening."
        )
    return twiml_say_and_hangup("It seems you've disconnected. Thank you for calling. Goodbye!")


@app.route("/voice/status", methods=["POST"])
def call_status():
    """Called when a call ends — cleanup."""
    call_sid = request.form.get("CallSid")
    status = request.form.get("CallStatus")
    print(f"[{call_sid}] Call ended — status: {status}")
    active_calls.pop(call_sid, None)
    return "OK", 200


@app.route("/health", methods=["GET"])
def health():
    businesses = database.get_all_businesses()
    return {
        "status": "running",
        "active_calls": len(active_calls),
        "businesses": len(businesses)
    }


@app.route("/token", methods=["GET"])
def token():
    """Generate Twilio Access Token for browser-based calling."""
    account_sid    = os.getenv("TWILIO_ACCOUNT_SID")
    api_key_sid    = os.getenv("TWILIO_API_KEY_SID")
    api_key_secret = os.getenv("TWILIO_API_KEY_SECRET")
    twiml_app_sid  = os.getenv("TWIML_APP_SID")

    access_token = AccessToken(account_sid, api_key_sid, api_key_secret, identity="browser-user")
    voice_grant = VoiceGrant(outgoing_application_sid=twiml_app_sid, incoming_allow=False)
    access_token.add_grant(voice_grant)

    return jsonify(token=str(access_token.to_jwt()))


@app.route("/phone", methods=["GET"])
def phone():
    """Serve the browser phone UI."""
    return send_file("browser_phone.html")


if __name__ == "__main__":
    database.create_tables()
    port = int(os.getenv("PORT", 5000))
    print(f"\n{'='*50}")
    print(f"  AI Receptionist Server")
    print(f"  Running on http://0.0.0.0:{port}")
    print(f"  Health check: http://localhost:{port}/health")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
