"""
Flask server — handles incoming Twilio phone calls.
Each call gets its own Receptionist session.

Webhook URLs to set in Twilio:
  Voice → https://YOUR_NGROK_URL/voice/answer
  Status → https://YOUR_NGROK_URL/voice/status
"""

import os
import traceback
from flask import Flask, request, Response, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from dotenv import load_dotenv
import database
from receptionist import Receptionist
from functools import wraps
import hmac, hashlib, json, base64

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-me-in-production-please")
CORS(app, supports_credentials=True)


# ── Token utilities ──────────────────────────────────────────────────────

def _make_token(payload: dict) -> str:
    """Sign a JSON payload and return a token string."""
    secret = os.getenv("SECRET_KEY", "default-secret")
    b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(secret.encode(), b64.encode(), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"


def _verify_token(token: str):
    """Return payload dict if valid, else None."""
    try:
        b64, sig = token.rsplit(".", 1)
        secret = os.getenv("SECRET_KEY", "default-secret")
        expected = hmac.new(secret.encode(), b64.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        return json.loads(base64.urlsafe_b64decode(b64).decode())
    except Exception:
        return None


def _get_bearer():
    auth = request.headers.get("Authorization", "")
    return auth[7:] if auth.startswith("Bearer ") else None


def admin_required(f):
    """Admin: session OR bearer token with role=admin."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("admin_logged_in"):
            return f(*args, **kwargs)
        token = _get_bearer()
        if token:
            payload = _verify_token(token)
            if payload and payload.get("role") == "admin":
                return f(*args, **kwargs)
        if request.path.startswith("/admin/api"):
            return jsonify({"error": "Unauthorized"}), 401
        return redirect(url_for("admin_login"))
    return decorated


def client_required(f):
    """Client: bearer token with role=client. Injects business_id into kwargs."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_bearer()
        if token:
            payload = _verify_token(token)
            if payload and payload.get("role") == "client":
                kwargs["_business_id"] = payload["business_id"]
                kwargs["_business_name"] = payload["business_name"]
                return f(*args, **kwargs)
        return jsonify({"error": "Unauthorized"}), 401
    return decorated

# Ensure all tables exist (safe to run on every startup)
database.create_tables()

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


def _voice_params(lang):
    """Return (tts_voice, tts_lang, stt_lang) based on lang."""
    if lang == "hi":
        # TTS: Polly.Aditi speaks Hindi naturally
        # STT: en-IN handles Indian accent English + Hinglish mix perfectly
        #      (hi-IN transcribes English words into Devanagari causing match failures)
        return "Polly.Aditi", "hi-IN", "hi-IN,en-IN"
    return "alice", "en-IN", "en-IN"


def twiml_say_and_listen(text, action="/voice/gather", lang="en"):
    """Speak text then wait for caller's voice input."""
    tts_voice, tts_lang, stt_lang = _voice_params(lang)
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action=action,
        method="POST",
        speech_timeout="auto",
        language=stt_lang,
        enhanced=True,
    )
    gather.say(text, voice=tts_voice, language=tts_lang)
    resp.append(gather)
    resp.redirect("/voice/no_input", method="POST")
    return Response(str(resp), mimetype="text/xml")


def twiml_say_and_hangup(text, lang="en"):
    """Speak final message and end the call."""
    tts_voice, tts_lang, _stt_lang = _voice_params(lang)
    resp = VoiceResponse()
    resp.say(text, voice=tts_voice, language=tts_lang)
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
    """Twilio calls this when a new call comes in. Ask language preference first."""
    call_sid    = request.form.get("CallSid")
    to_number   = request.form.get("To")
    from_number = request.form.get("From")

    print(f"\n📞 Incoming call: {from_number} → {to_number} [{call_sid}]")

    business_id = get_business_for_call(to_number)
    if not business_id:
        return twiml_say_and_hangup(
            "Thank you for calling. We are currently unavailable. Please try again later."
        )

    # Store business_id + caller so /voice/lang can create the Receptionist
    active_calls[call_sid] = {"business_id": business_id, "from_number": from_number}

    lang_prompt = "Hello! Which language do you prefer, English or Hindi?"
    resp = VoiceResponse()
    gather = Gather(
        input="speech",
        action="/voice/lang",
        method="POST",
        speech_timeout="auto",
        language="hi-IN",   # hi-IN understands both "Hindi" and "English"
        enhanced=True,
    )
    gather.say(lang_prompt, voice="alice", language="en-IN")
    resp.append(gather)
    resp.redirect("/voice/lang_timeout", method="POST")
    return Response(str(resp), mimetype="text/xml")


@app.route("/voice/lang", methods=["POST"])
def lang_select():
    """Detect language choice and start the receptionist."""
    call_sid = request.form.get("CallSid")
    speech   = request.form.get("SpeechResult", "").strip().lower()

    session_data = active_calls.get(call_sid, {})
    business_id  = session_data.get("business_id") if isinstance(session_data, dict) else None
    from_number  = session_data.get("from_number") if isinstance(session_data, dict) else None

    if not business_id:
        return twiml_say_and_hangup("Sorry, something went wrong. Please call back.")

    # Detect Hindi — covers "hindi", "हिंदी", "हिन्दी", "hindi hai"
    lang = "hi" if ("hindi" in speech or "हिंदी" in speech or "हिन्दी" in speech) else "en"
    print(f"[{call_sid}] Language selected: {lang} (heard: '{speech}')")

    try:
        receptionist = Receptionist(business_id, caller_phone=from_number, lang=lang)
        active_calls[call_sid] = receptionist
        greeting = receptionist.greeting()
        print(f"[{call_sid}] Greeting: {greeting}")
        return twiml_say_and_listen(greeting, lang=lang)
    except Exception as e:
        print(f"Error starting receptionist: {e}")
        return twiml_say_and_hangup("We are experiencing technical difficulties. Please call back.")


@app.route("/voice/lang_timeout", methods=["POST"])
def lang_timeout():
    """Caller said nothing on language prompt — default to English."""
    call_sid    = request.form.get("CallSid")
    session_data = active_calls.get(call_sid, {})
    business_id  = session_data.get("business_id") if isinstance(session_data, dict) else None
    from_number  = session_data.get("from_number") if isinstance(session_data, dict) else None

    if not business_id:
        return twiml_say_and_hangup("Sorry, something went wrong. Please call back.")

    try:
        receptionist = Receptionist(business_id, caller_phone=from_number, lang="en")
        active_calls[call_sid] = receptionist
        greeting = receptionist.greeting()
        return twiml_say_and_listen(greeting, lang="en")
    except Exception as e:
        print(f"Error on lang_timeout: {e}")
        return twiml_say_and_hangup("We are experiencing technical difficulties. Please call back.")


@app.route("/voice/gather", methods=["POST"])
def gather():
    """Twilio calls this after the caller speaks."""
    call_sid   = request.form.get("CallSid")
    speech     = request.form.get("SpeechResult", "").strip()
    confidence = request.form.get("Confidence", "0")

    receptionist = active_calls.get(call_sid)
    if not receptionist or isinstance(receptionist, dict):
        return twiml_say_and_hangup("I'm sorry, your session has expired. Please call back.")

    lang = getattr(receptionist, "lang", "en")

    if not speech:
        msg = "माफ़ करें, मैंने सुना नहीं। क्या आप फिर से कहेंगे?" if lang == "hi" \
              else "I didn't quite catch that. Could you please repeat?"
        return twiml_say_and_listen(msg, lang=lang)

    print(f"[{call_sid}] Customer (conf {confidence}): {speech}")

    bye_words = ["bye", "goodbye", "hang up", "end call", "disconnect", "धन्यवाद", "बाय", "रखो"]
    if any(w in speech.lower() for w in bye_words):
        del active_calls[call_sid]
        msg = "कॉल करने के लिए धन्यवाद! आपका दिन शुभ हो। नमस्ते!" if lang == "hi" \
              else "Thank you for calling. Have a wonderful day. Goodbye!"
        return twiml_say_and_hangup(msg, lang=lang)

    try:
        response = receptionist.process(speech)
        print(f"[{call_sid}] Assistant: {response}")

        if receptionist.is_done:
            del active_calls[call_sid]
            return twiml_say_and_hangup(response, lang=lang)

        return twiml_say_and_listen(response, lang=lang)

    except Exception as e:
        print(f"Error processing input: {e}")
        traceback.print_exc()
        active_calls.pop(call_sid, None)
        msg = "माफ़ करें, कुछ गड़बड़ हो गई। कृपया दोबारा कॉल करें।" if lang == "hi" \
              else "I'm sorry, something went wrong. Please call back or speak to our team directly."
        return twiml_say_and_hangup(msg, lang=lang)


@app.route("/voice/no_input", methods=["POST"])
def no_input():
    """Called when caller stays silent for too long."""
    call_sid     = request.form.get("CallSid")
    receptionist = active_calls.get(call_sid)

    if receptionist and not isinstance(receptionist, dict):
        lang = getattr(receptionist, "lang", "en")
        msg  = "क्या आप अभी भी लाइन पर हैं? कृपया बोलिए।" if lang == "hi" \
               else "Are you still there? Please go ahead and speak, I'm listening."
        return twiml_say_and_listen(msg, lang=lang)
    return twiml_say_and_hangup("It seems you've disconnected. Thank you for calling. Goodbye!")


@app.route("/voice/status", methods=["POST"])
def call_status():
    """Called when a call ends — cleanup."""
    call_sid = request.form.get("CallSid")
    status   = request.form.get("CallStatus")
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


@app.route("/debug/booking", methods=["GET"])
def debug_booking():
    """Test the full booking flow and return any error."""
    try:
        from receptionist import Receptionist
        import brain, slot_manager
        r = Receptionist("tanuj_dental", "+11234567890")
        step1 = r.process("I want to book an appointment")
        step2 = r.process("cleaning")
        step3 = r.process("Monday")
        return {"step1": step1, "step2": step2, "step3": step3, "ok": True}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}, 500


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


# ------------------------------------------------------------------ #
#  React Dashboard (SPA)                                             #
# ------------------------------------------------------------------ #

@app.route("/dashboard")
@app.route("/dashboard/")
def dashboard():
    """Serve the React admin dashboard SPA."""
    return send_file("static/dashboard/index.html")


# ------------------------------------------------------------------ #
#  Admin Dashboard                                                    #
# ------------------------------------------------------------------ #

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = ""
    if request.method == "POST":
        pwd = request.form.get("password", "")
        admin_pwd = os.getenv("ADMIN_PASSWORD", "admin123")
        if pwd == admin_pwd:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Wrong password. Try again."

    with open("admin_login.html", "r") as f:
        html = f.read()
    if error:
        html = html.replace("<!--ERROR-->", f'<p class="error">{error}</p>')
    return html, 200, {"Content-Type": "text/html"}


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    with open("admin.html", "r") as f:
        return f.read(), 200, {"Content-Type": "text/html"}


@app.route("/admin/api/login", methods=["POST"])
def api_admin_login():
    data = request.get_json() or {}
    pwd  = data.get("password", "")
    if pwd == os.getenv("ADMIN_PASSWORD", "admin123"):
        token = _make_token({"role": "admin"})
        return jsonify({"token": token, "role": "admin"})
    return jsonify({"error": "Wrong password"}), 401


# ── Client login & API ────────────────────────────────────────────────────

@app.route("/client/api/login", methods=["POST"])
def api_client_login():
    data        = request.get_json() or {}
    business_id = data.get("business_id", "").strip()
    password    = data.get("password", "").strip()

    biz = database.get_business(business_id)
    if not biz:
        return jsonify({"error": "Business not found"}), 404
    if not biz.get("client_password") or biz["client_password"] != password:
        return jsonify({"error": "Wrong password"}), 401

    token = _make_token({
        "role":          "client",
        "business_id":   biz["id"],
        "business_name": biz["name"],
    })
    return jsonify({"token": token, "role": "client",
                    "business_id": biz["id"], "business_name": biz["name"]})


@app.route("/client/api/stats", methods=["GET"])
@client_required
def client_stats(_business_id=None, _business_name=None):
    return jsonify(database.get_dashboard_stats(_business_id))


@app.route("/client/api/bookings", methods=["GET"])
@client_required
def client_bookings(_business_id=None, _business_name=None):
    status = request.args.get("status")
    search = request.args.get("search")
    return jsonify(database.get_all_bookings(_business_id, status or None, search or None))


@app.route("/client/api/schedule", methods=["GET"])
@client_required
def client_get_schedule(_business_id=None, _business_name=None):
    biz = database.get_business(_business_id)
    if not biz:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "working_days":  biz["working_days"],
        "start_time":    biz["start_time"],
        "end_time":      biz["end_time"],
        "slot_duration": biz["slot_duration"],
        "services":      biz["services"],
    })


@app.route("/client/api/schedule", methods=["PUT"])
@client_required
def client_update_schedule(_business_id=None, _business_name=None):
    data          = request.get_json() or {}
    working_days  = data.get("working_days", [])
    start_time    = data.get("start_time", "09:00")
    end_time      = data.get("end_time",   "18:00")
    slot_duration = int(data.get("slot_duration", 30))
    database.update_business_schedule(_business_id, working_days, start_time, end_time, slot_duration)
    return jsonify({"success": True})


@app.route("/client/api/leaves", methods=["GET"])
@client_required
def client_get_leaves(_business_id=None, _business_name=None):
    return jsonify(database.get_leaves(_business_id))


@app.route("/client/api/leaves", methods=["POST"])
@client_required
def client_add_leave(_business_id=None, _business_name=None):
    data   = request.get_json() or {}
    date   = data.get("date", "").strip()
    reason = data.get("reason", "").strip()
    if not date:
        return jsonify({"error": "Date is required"}), 400
    database.add_leave(_business_id, date, reason)
    return jsonify({"success": True})


@app.route("/client/api/leaves/<int:leave_id>", methods=["DELETE"])
@client_required
def client_delete_leave(leave_id, _business_id=None, _business_name=None):
    database.delete_leave(leave_id, _business_id)
    return jsonify({"success": True})


@app.route("/client/api/bookings/<int:booking_id>/cancel", methods=["POST"])
@client_required
def client_cancel_booking(booking_id, _business_id=None, _business_name=None):
    # Make sure the booking belongs to this client's business
    bookings = database.get_all_bookings(_business_id)
    if not any(b["id"] == booking_id for b in bookings):
        return jsonify({"error": "Not allowed"}), 403
    database.cancel_booking(booking_id)
    return jsonify({"success": True})


@app.route("/admin/api/businesses", methods=["GET"])
@admin_required
def api_businesses():
    return jsonify(database.get_all_businesses())


@app.route("/admin/api/businesses", methods=["POST"])
@admin_required
def api_create_business():
    data = request.get_json() or {}

    business_id     = data.get("id", "").strip().lower()
    name            = data.get("name", "").strip()
    business_type   = data.get("type", "").strip()
    services        = data.get("services", [])
    working_days    = data.get("working_days", [])
    start_time      = data.get("start_time", "09:00")
    end_time        = data.get("end_time",   "18:00")
    slot_duration   = int(data.get("slot_duration", 30))
    timezone        = data.get("timezone",  "Asia/Kolkata")
    contact_email   = data.get("contact_email", "")
    client_password = data.get("client_password", "")

    if not business_id:
        return jsonify({"error": "Business ID is required"}), 400
    if not name:
        return jsonify({"error": "Business name is required"}), 400
    if database.get_business(business_id):
        return jsonify({"error": f"Business ID '{business_id}' already exists"}), 409

    database.add_business(
        business_id, name, business_type, services, working_days,
        start_time, end_time, slot_duration, timezone, contact_email
    )
    if client_password:
        database.set_client_password(business_id, client_password)

    return jsonify({"success": True, "id": business_id, "name": name})


@app.route("/admin/api/stats", methods=["GET"])
@admin_required
def api_stats():
    biz_id = request.args.get("business_id")
    return jsonify(database.get_dashboard_stats(biz_id or None))


@app.route("/admin/api/bookings", methods=["GET"])
@admin_required
def api_bookings():
    biz_id = request.args.get("business_id")
    status = request.args.get("status")
    search = request.args.get("search")
    bookings = database.get_all_bookings(biz_id or None, status or None, search or None)
    return jsonify(bookings)


@app.route("/admin/api/bookings/<int:booking_id>/cancel", methods=["POST"])
@admin_required
def api_cancel_booking(booking_id):
    database.cancel_booking(booking_id)
    return jsonify({"success": True})


if __name__ == "__main__":
    database.create_tables()
    port = int(os.getenv("PORT", 5000))
    print(f"\n{'='*50}")
    print(f"  AI Receptionist Server")
    print(f"  Running on http://0.0.0.0:{port}")
    print(f"  Health check: http://localhost:{port}/health")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
