"""
brain.py — Rule-based AI brain for the receptionist.
No Ollama, no Groq, no internet. 100% offline. Instant responses.

Two responsibilities:
  1. reply(key, **kwargs)  — pick a natural-sounding template response
  2. extract(text, services) — pull structured data from caller's speech
"""

import re
import random
import os
from datetime import datetime, timedelta
from difflib import get_close_matches
from dotenv import load_dotenv
load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════
#  RESPONSE TEMPLATES
#  Multiple variants per key → sounds less robotic
# ═══════════════════════════════════════════════════════════════════════════

TEMPLATES_HI = {
    "greeting": [
        "नमस्ते! {business} में आपका स्वागत है। मैं आपकी कैसे मदद कर सकती हूँ?",
        "हेलो! आपने {business} को कॉल किया है। बताइए, मैं आपकी क्या सेवा कर सकती हूँ?",
        "नमस्ते, {business} से बोल रही हूँ। आप कैसे हैं? मैं आपकी कैसे मदद करूँ?",
    ],
    "no_intent": [
        "बिल्कुल! मैं आपके लिए {booking_word} बुक कर सकती हूँ, जानकारी दे सकती हूँ, या कैंसिलेशन में मदद कर सकती हूँ। आप क्या चाहते हैं?",
        "ज़रूर! क्या आप {booking_word} बुक करना चाहते हैं, या कोई और जानकारी चाहिए?",
        "हाँ बताइए! मैं {booking_word} बुक करने में, कैंसिल करने में, या जानकारी देने में मदद कर सकती हूँ।",
    ],
    "ask_service": [
        "बढ़िया! हमारी सेवाएँ हैं: {services}। आप कौन सी सेवा लेना चाहेंगे?",
        "ज़रूर! हम {services} की सुविधा देते हैं। आप क्या चुनना चाहेंगे?",
        "हमारे पास {services} उपलब्ध है। आप किसके लिए बुकिंग करना चाहते हैं?",
    ],
    "ask_date": [
        "बढ़िया! हम {days} को खुले रहते हैं। आप किस दिन आना चाहेंगे?",
        "हम {days} को उपलब्ध हैं। आपके लिए कौन सा दिन ठीक रहेगा?",
        "अच्छा! {days} को हमारी सेवा उपलब्ध है। कौन सी तारीख चाहिए आपको?",
    ],
    "show_slots": [
        "{date} के लिए ये समय उपलब्ध हैं: {slots}। आप कौन सा समय चुनेंगे?",
        "बढ़िया! {date} को {slots} का समय खाली है। कौन सा ठीक रहेगा?",
        "{date} के लिए {slots} उपलब्ध है। आप कब आना चाहेंगे?",
    ],
    "slot_unavailable": [
        "यह समय उपलब्ध नहीं है। लेकिन {slots} अभी भी खाली है। कौन सा चुनेंगे?",
        "वो स्लॉट भर गया है। अभी {slots} उपलब्ध है। कौन सा ठीक रहेगा?",
    ],
    "no_slots": [
        "{date} को कोई स्लॉट उपलब्ध नहीं है। हम {days} को खुले रहते हैं — कोई दूसरा दिन बताइए।",
        "खेद है, {date} को सब स्लॉट भरे हुए हैं। {days} में से कोई दूसरा दिन चुनिए।",
    ],
    "ask_name": [
        "आपका नाम क्या है?",
        "बुकिंग किसके नाम पर करूँ?",
        "कृपया अपना नाम बताइए।",
        "और आपका नाम?",
    ],
    "ask_phone": [
        "आपका फ़ोन नंबर बताइए।",
        "संपर्क के लिए आपका मोबाइल नंबर क्या है?",
        "कृपया अपना फ़ोन नंबर दें।",
    ],
    "confirm": [
        "ठीक है, एक बार कन्फर्म करती हूँ — {name} जी, {service}, {date} को {time} बजे। क्या यह सही है?",
        "मैं दोहराती हूँ — {name}, {service}, {date}, {time} बजे। सब ठीक है?",
        "तो {name} जी के लिए {service}, {date} को {time} बजे। कन्फर्म करें?",
    ],
    "reconfirm": [
        "एक बार और — {name} जी, {service}, {date} को {time} बजे। हाँ या नहीं?",
        "क्षमा करें, फिर से बताइए — {name}, {service}, {date}, {time} — सही है?",
    ],
    "booked": [
        "बुकिंग हो गई! {name} जी, आपका {service} {date} को {time} बजे कन्फर्म है। बुकिंग ID है {id}। मिलते हैं!",
        "बढ़िया! {name} जी की {service} बुकिंग {date} को {time} बजे के लिए हो गई। ID: {id}। धन्यवाद!",
        "{name} जी, आपकी {service} बुक हो गई — {date}, {time} बजे। Reference: {id}। शुभकामनाएँ!",
    ],
    "slot_taken": [
        "अफ़सोस, वो स्लॉट अभी किसी और ने ले लिया! लेकिन {slots} अभी भी उपलब्ध है। कौन सा चुनेंगे?",
        "वो समय अभी भर गया। {slots} खाली है — कौन सा ठीक रहेगा?",
    ],
    "cancel_ask_phone": [
        "ज़रूर! जिस फ़ोन नंबर से बुकिंग हुई थी, वो बताइए।",
        "बिल्कुल! बुकिंग वाला फ़ोन नंबर बताइए।",
        "कोई बात नहीं! बुकिंग किस नंबर पर थी?",
    ],
    "cancel_confirmed": [
        "कैंसिल हो गया! बुकिंग ID {booking_id} रद्द कर दी गई है। फिर मिलेंगे!",
        "आपकी बुकिंग {booking_id} कैंसिल हो गई। कोई और मदद चाहिए?",
    ],
    "no_booking_found": [
        "इस नंबर पर कोई बुकिंग नहीं मिली। क्या नंबर सही है?",
        "माफ़ करें, इस नंबर से कोई बुकिंग नहीं है। शायद दूसरे नंबर से की हो?",
    ],
    "info": [
        "हम {services} की सेवा देते हैं और {days} को {start_time} से {end_time} तक खुले रहते हैं। क्या बुकिंग करनी है?",
        "हमारी सेवाएँ हैं {services}। हम {days}, {start_time} से {end_time} तक उपलब्ध हैं। बुकिंग करें?",
    ],
    "urgency": [
        "समझ गई, यह ज़रूरी लग रहा है। कृपया सीधे क्लिनिक या इमरजेंसी सेवा से संपर्क करें।",
        "यह इमरजेंसी लगती है। कृपया तुरंत डॉक्टर या अस्पताल से संपर्क करें।",
    ],
    "goodbye": [
        "{business} को कॉल करने के लिए धन्यवाद! आपका दिन शुभ हो। नमस्ते!",
        "धन्यवाद! {business} की ओर से आपको शुभकामनाएँ। फिर मिलेंगे!",
    ],
    "unclear": [
        "माफ़ करें, मैंने ठीक से नहीं सुना। क्या आप फिर से बताएंगे?",
        "कृपया एक बार और कहें, मुझे सुनाई नहीं दिया।",
        "ज़रा फिर से बताइए — मैं समझ नहीं पाई।",
    ],
}

TEMPLATES = {
    "greeting": [
        "Hey, thanks for calling {business}! How can I help you today?",
        "Good {time_of_day}! You've reached {business} — what can I do for you?",
        "Hi there! Welcome to {business}. How can I help?",
        "Hello, you've called {business}! What can I do for you today?",
        "Thanks for calling {business}. How may I assist you?",
    ],
    "no_intent": [
        "Of course! I can help you book a {booking_word}, check our services, or cancel an existing one. What would you like?",
        "Sure thing! Would you like to make a {booking_word}, or is there something else I can help with?",
        "Happy to help! I can book a {booking_word} for you, answer any questions, or help with a cancellation. What do you need?",
        "Absolutely! Just let me know — are you looking to book a {booking_word} or do you have a question?",
    ],
    "ask_service": [
        "Great! We offer {services} — which one would you like?",
        "Sure! Which service are you after? We've got {services}.",
        "Of course! We have {services} available. Which one works for you?",
        "Happy to help! We offer {services}. Which would you like to book?",
        "No problem! Just pick a service — we have {services}.",
    ],
    "ask_date": [
        "Perfect! We're open on {days}. Which day works for you?",
        "Great choice! We're available {days}. Which date were you thinking?",
        "Sure! We're open {days} — which day suits you best?",
        "Awesome! Pick any day that works — we're open {days}.",
        "We're here {days}. Which day would you like to come in?",
    ],
    "show_slots": [
        "Great, {date} works! I've got {slots} open — which time suits you?",
        "Perfect! For {date}, the available times are {slots}. Which one do you prefer?",
        "Sure thing! On {date} I have {slots} free. Which works best for you?",
        "Here's what's available on {date}: {slots}. Which time would you like?",
        "For {date}, you can pick from {slots}. Which one works for you?",
    ],
    "slot_unavailable": [
        "Hmm, that time's actually taken. But I still have {slots} open — which of those works for you?",
        "Oh, looks like that slot just got filled! Don't worry though, I have {slots} available. Which one would you like?",
        "That one's not available, but no worries — you can still pick from {slots}. Which suits you?",
        "That time's taken, but here are the open ones: {slots}. Which would you prefer?",
    ],
    "no_slots": [
        "Oh, looks like {date} is all booked up! We're open {days} — which other day works for you?",
        "Hmm, we're fully booked on {date}. How about another day? We're available {days}.",
        "Sorry, no slots left on {date}. But we're open {days} — would any of those work?",
        "That day's fully booked, unfortunately. We do have availability on {days} — which day would you prefer?",
    ],
    "ask_name": [
        "And who should I put this down for? Just your name please.",
        "Could I grab your name for the {booking_word}?",
        "What name should I put this under?",
        "Perfect! And your name please?",
        "Almost done! May I have your name?",
    ],
    "ask_phone": [
        "And your phone number? Just in case we need to reach you.",
        "What's the best number to reach you on?",
        "Could I get your mobile number?",
        "Great! And your contact number please?",
        "Last thing — what's your phone number?",
    ],
    "confirm": [
        "Okay, let me just read that back — {name}, {service} on {date} at {time}. Does that sound right?",
        "Almost done! Just confirming — {name} for {service} on {date} at {time}. Is that correct?",
        "Perfect, I've got {name} down for {service} on {date} at {time}. Does everything look good?",
        "So that's {name}, {service}, {date} at {time}. Shall I go ahead and confirm that?",
        "Before I book — {name} for {service} on {date} at {time}. All correct?",
    ],
    "booked": [
        "You're all set, {name}! Your {service} {booking_word} is confirmed for {date} at {time}. Your booking ID is {id}. See you then!",
        "Brilliant! {booking_word} confirmed — {name}, {service} on {date} at {time}. Booking ID {id}. Have a great day!",
        "Done and dusted! {name}, we've got your {service} booked for {date} at {time}. Reference number: {id}. Looking forward to seeing you!",
        "All booked! {service} on {date} at {time} for {name}. Your booking ID is {id} — we'll see you there!",
        "Perfect, {name}! Your {booking_word} for {service} on {date} at {time} is confirmed. ID: {id}. Have a wonderful day!",
    ],
    "slot_taken": [
        "Oh no, that slot was just taken by someone else! But don't worry — I still have {slots} open. Which works for you?",
        "Ah, that one just got booked! Here's what's still available: {slots}. Which would you like?",
    ],
    "cancel_ask": [
        "Of course, I can sort that out for you. Could I get the phone number on the {booking_word}?",
        "No problem at all! What's the phone number that was used for the {booking_word}?",
    ],
    "cancel_ask_phone": [
        "Sure, happy to help with that! What's the phone number on the {booking_word}?",
        "Of course! Could you give me the phone number used when the {booking_word} was made?",
        "No worries at all! What phone number was the {booking_word} booked under?",
        "Let me pull that up for you — what's the phone number linked to the {booking_word}?",
    ],
    "cancel_confirmed": [
        "Done! Your {booking_word} has been cancelled — booking ID {booking_id}. Hope to see you again soon!",
        "All sorted! {booking_word} {booking_id} is now cancelled. Is there anything else I can help with?",
        "Your {booking_word} has been removed — no problem at all! Booking {booking_id} is cancelled. Take care!",
        "Cancelled successfully! Booking ID {booking_id} is all done. Hope we can help you again soon!",
    ],
    "no_booking_found": [
        "Hmm, I couldn't find a {booking_word} under that number. Could you double-check it for me?",
        "I don't see anything booked under that number — are you sure it wasn't under a different one?",
        "I'm not finding a confirmed {booking_word} for that number. Maybe it was booked under a different phone?",
    ],
    "info": [
        "We offer {services} and we're open {days} from {start_time} to {end_time}. Would you like to book a {booking_word}?",
        "Sure! Our services are {services}. We're available {days}, {start_time} to {end_time}. Can I book something for you?",
        "Great question! We're open {days} from {start_time} to {end_time} and offer {services}. Shall I book a {booking_word} for you?",
    ],
    "unclear": [
        "Sorry, I didn't quite catch that — could you say it again?",
        "Hmm, I missed that. Could you repeat it one more time?",
        "I'm sorry, the line wasn't clear. Could you say that again please?",
        "Could you repeat that? I want to make sure I get it right.",
    ],
    "urgency": [
        "I understand — please hold on, I'm connecting you to our team right away.",
        "Got it, this sounds urgent. Let me get someone on the line for you immediately.",
    ],
    "goodbye": [
        "Thanks so much for calling {business} — have a wonderful day! Bye!",
        "It was great helping you today! Bye from {business} — take care!",
        "Thanks for calling {business}. Have a lovely day. Goodbye!",
        "All done! Thanks for calling, and have a great {time_of_day}. Bye!",
    ],
    "reconfirm": [
        "Just to double-check — {name} for {service} on {date} at {time}. Yes or no?",
        "Sorry, could you confirm? I've got {name}, {service}, {date} at {time} — is that right?",
        "Let me read that back one more time — {name}, {service} on {date} at {time}. Correct?",
    ],
}


def _time_of_day():
    h = datetime.now().hour
    if h < 12:
        return "morning"
    if h < 17:
        return "afternoon"
    return "evening"


def reply(key, lang="en", **kwargs):
    """Pick a random template and fill in placeholders."""
    pool = TEMPLATES_HI if lang == "hi" else TEMPLATES
    templates = pool.get(key) or TEMPLATES.get(key, ["How can I help you?"])
    template = random.choice(templates)
    kwargs.setdefault("time_of_day", _time_of_day())
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


# ─────────────────────────────────────────────────────────────────────────────
#  DAY SUMMARISER
#  Turns a long list like "Monday, Tuesday, Wednesday, Thursday, Friday,
#  Saturday, Sunday" into a short spoken phrase like "every day".
#  Keeps phone call latency low — callers hear the answer before the mic opens.
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
#  SLOT SUMMARISER
#  Turns "09:00 AM, 09:30 AM, 10:00 AM, 10:30 AM, 11:00 AM, 02:00 PM, 02:30 PM"
#  into "morning from 9 to 11 AM, and afternoon from 2 to 2:30 PM"
#  so the AI doesn't read 10 individual times before the mic opens.
# ─────────────────────────────────────────────────────────────────────────────

def _short_time(slot):
    """
    "09:00 AM" → "9 AM"
    "09:30 AM" → "9:30 AM"
    "02:30 PM" → "2:30 PM"
    """
    try:
        t = datetime.strptime(slot.strip(), "%I:%M %p")
        h = str(t.hour % 12 or 12)          # no leading zero
        ampm = "AM" if t.hour < 12 else "PM"
        if t.minute == 0:
            return f"{h} {ampm}"
        return f"{h}:{t.strftime('%M')} {ampm}"
    except ValueError:
        return slot


def _drop_ampm(time_str):
    """'9 AM' → '9',  '9:30 AM' → '9:30',  '12 PM' → '12'"""
    return time_str.rsplit(" ", 1)[0]


def summarize_slots(slots):
    """
    Return a short spoken phrase for the available slots list.

    ≤3 slots  → list them  ("9 AM, 10 AM, and 11:30 AM")
    4+ slots  → group by time period and give a range
                ("morning from 9 to 11:30 AM, and afternoon from 2 to 4:30 PM")

    Within a range the AM/PM only appears at the end to keep it short:
        "morning from 9 to 11:30 AM"  ✓
        "morning from 9 AM to 11:30 AM"  ✗  (too long)
    """
    if not slots:
        return "no slots available"

    if len(slots) <= 3:
        short = [_short_time(s) for s in slots]
        if len(short) == 1:
            return short[0]
        if len(short) == 2:
            return f"{short[0]} and {short[1]}"
        return f"{short[0]}, {short[1]}, and {short[2]}"

    # Group into time-of-day buckets
    morning   = []   # before 12:00
    afternoon = []   # 12:00 – 16:59
    evening   = []   # 17:00+

    for slot in slots:
        try:
            t = datetime.strptime(slot.strip(), "%I:%M %p")
            if t.hour < 12:
                morning.append(slot)
            elif t.hour < 17:
                afternoon.append(slot)
            else:
                evening.append(slot)
        except ValueError:
            morning.append(slot)   # safe fallback

    parts = []
    for label, group in [("morning", morning), ("afternoon", afternoon), ("evening", evening)]:
        if not group:
            continue
        last_str = _short_time(group[-1])
        if len(group) == 1:
            # "evening at 5 PM"
            parts.append(f"{label} at {last_str}")
        else:
            # "morning from 9 to 11:30 AM"  — drop AM/PM from the first time
            first_no_ampm = _drop_ampm(_short_time(group[0]))
            parts.append(f"{label} from {first_no_ampm} to {last_str}")

    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]}, and {parts[1]}"
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


_ALL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Named shortcut phrases (most common patterns)
_DAY_SHORTCUTS = {
    frozenset(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]): "every day",
    frozenset(["Monday","Tuesday","Wednesday","Thursday","Friday"])                    : "Monday through Friday",
    frozenset(["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"])          : "Monday through Saturday",
    frozenset(["Saturday","Sunday"])                                                    : "weekends only",
    frozenset(["Monday","Tuesday","Wednesday","Thursday"])                              : "Monday through Thursday",
    frozenset(["Tuesday","Wednesday","Thursday","Friday"])                              : "Tuesday through Friday",
    frozenset(["Monday","Wednesday","Friday"])                                          : "Monday, Wednesday, and Friday",
    frozenset(["Tuesday","Thursday"])                                                   : "Tuesdays and Thursdays",
}


def summarize_days(days):
    """
    Return a short spoken phrase for the given list of open days.

    Examples
    --------
    ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"] → "every day"
    ["Mon","Tue","Wed","Thu","Fri"]             → "Monday through Friday"
    ["Mon","Tue","Wed","Thu","Fri","Sat"]       → "Monday through Saturday"
    ["Sat","Sun"]                               → "weekends only"
    ["Tue","Thu"]                               → "Tuesdays and Thursdays"
    ["Mon","Wed","Thu","Fri","Sat"]             → "Monday, Wednesday, Thursday, Friday, and Saturday"
    """
    if not days:
        return "select days"

    # Normalise to full names (handle abbreviations like "Mon", "Tue")
    abbr_map = {d[:3].lower(): d for d in _ALL_DAYS}
    normalised = []
    for d in days:
        key = d[:3].lower()
        normalised.append(abbr_map.get(key, d))

    day_set = frozenset(normalised)

    # Named shortcut?
    if day_set in _DAY_SHORTCUTS:
        return _DAY_SHORTCUTS[day_set]

    # Consecutive range?  (e.g. Wed–Sat → "Wednesday through Saturday")
    indices = [_ALL_DAYS.index(d) for d in normalised if d in _ALL_DAYS]
    if indices:
        indices.sort()
        if indices == list(range(indices[0], indices[-1] + 1)) and len(indices) >= 3:
            return f"{_ALL_DAYS[indices[0]]} through {_ALL_DAYS[indices[-1]]}"

    # Fallback: natural list with Oxford comma
    ordered = [d for d in _ALL_DAYS if d in day_set]   # keep week order
    if len(ordered) == 1:
        return ordered[0] + "s"
    if len(ordered) == 2:
        return f"{ordered[0]} and {ordered[1]}"
    return ", ".join(ordered[:-1]) + f", and {ordered[-1]}"


# ═══════════════════════════════════════════════════════════════════════════
#  GROQ AI FALLBACK
#  Used when caller asks something the rule-based engine can't handle.
#  e.g. "Do you offer EMI?", "What's the price?", "How long does it take?"
# ═══════════════════════════════════════════════════════════════════════════

def groq_reply(user_text, business_name, services, days, start_time, end_time, booking_word="appointment", lang="en"):
    """
    Call Groq (Llama 3) for natural off-script questions.
    Returns a short spoken response, or None if Groq is not configured / fails.
    """
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key or not user_text:
        return None

    if lang == "hi":
        system_prompt = f"""आप {business_name} की एक friendly voice receptionist हैं।
Business details:
- Services: {', '.join(services) if isinstance(services, list) else services}
- Open: {', '.join(days) if isinstance(days, list) else days}, {start_time} to {end_time}

STRICT RULES (यह phone call है — इन्हें ज़रूर follow करें):
1. MAX 2 छोटे वाक्यों में जवाब दें। इससे ज़्यादा नहीं।
2. अगर caller बुकिंग करना चाहे तो कहें "बिल्कुल, मैं बुकिंग करती हूँ!" — system बाकी handle करेगा।
3. अगर cancel करना हो तो कहें "ज़रूर, मैं help करती हूँ!" — system handle करेगा।
4. Price या policy के बारे में कुछ न बनाएँ। कहें "इसके लिए सीधे हमसे संपर्क करें।"
5. Natural और warm रहें — एक real receptionist की तरह।
6. Hindi में बोलें। Bullet points या markdown का उपयोग न करें।"""
    else:
        system_prompt = f"""You are a friendly voice receptionist for {business_name}.
Business details:
- Services: {', '.join(services) if isinstance(services, list) else services}
- Open: {', '.join(days) if isinstance(days, list) else days}, {start_time} to {end_time}

STRICT RULES (this is a phone call — follow these exactly):
1. Reply in MAX 2 short sentences. Never go longer.
2. If the caller wants to book/schedule/reserve, say "Sure, I can book that for you!" — the system will handle the rest.
3. If the caller wants to cancel, say "Of course, I can help with that!" — the system will handle it.
4. Never invent prices, policies, or details you don't know. Say "For that, I'd suggest calling us directly."
5. Sound warm and natural — like a real human receptionist.
6. Do NOT use bullet points, lists, or markdown. Speak in plain sentences."""

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_text},
            ],
            max_tokens=80,       # keeps it short for phone calls
            temperature=0.6,
        )
        reply_text = response.choices[0].message.content.strip()
        print(f"[groq] {reply_text}")
        return reply_text
    except Exception as e:
        print(f"[groq] failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  DATA EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════

# ── Intent ─────────────────────────────────────────────────────────────────

_INTENT_MAP = {
    "book": [
        "book", "appointment", "schedule", "reserve", "want to come",
        "can i get", "make an appointment", "fix an appointment",
        "need an appointment", "want an appointment", "set up", "slot",
        "coming in", "visit",
    ],
    "cancel": [
        "cancel", "cancellation", "don't want", "want to cancel",
        "remove my", "delete appointment", "not coming",
    ],
    "reschedule": [
        "reschedule", "change appointment", "move appointment",
        "different time", "different date", "change my appointment",
        "shift my", "postpone",
    ],
    "info": [
        "hours", "timing", "services", "offer", "working", "open",
        "price", "cost", "how much", "what do you", "tell me about",
        "what services", "do you have",
    ],
}


def extract_intent(text):
    t = text.lower()
    for intent, keywords in _INTENT_MAP.items():
        if any(kw in t for kw in keywords):
            return intent
    return None


# ── Service ────────────────────────────────────────────────────────────────

def extract_service(text, services):
    if not services:
        return None
    t = text.lower()
    # Exact substring match
    for s in services:
        if s.lower() in t:
            return s
    # Word-level fuzzy match
    words = t.split()
    service_lower = [s.lower() for s in services]
    for word in words:
        matches = get_close_matches(word, service_lower, n=1, cutoff=0.75)
        if matches:
            return services[service_lower.index(matches[0])]
    return None


# ── Date ───────────────────────────────────────────────────────────────────

_DAY_MAP = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1, "tues": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3, "thur": 3, "thurs": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6,
}

_MONTH_MAP = {
    "jan": 1, "january": 1, "feb": 2, "february": 2,
    "mar": 3, "march": 3, "apr": 4, "april": 4,
    "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def extract_date(text):
    t = text.lower()
    today = datetime.now()

    # Relative words
    if "day after tomorrow" in t:
        return (today + timedelta(days=2)).strftime("%Y-%m-%d")
    if "tomorrow" in t:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if "today" in t:
        return today.strftime("%Y-%m-%d")

    # "next Monday" / "this Friday"
    for day_name, day_num in _DAY_MAP.items():
        if day_name in t:
            days_ahead = (day_num - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7   # same weekday = next week
            if "next" in t:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # "26th May" / "26 May"
    month_pattern = "|".join(_MONTH_MAP.keys())
    m = re.search(
        r'(\d{1,2})(?:st|nd|rd|th)?\s+(' + month_pattern + r')', t)
    if m:
        day, month = int(m.group(1)), _MONTH_MAP[m.group(2)]
        year = today.year
        try:
            d = datetime(year, month, day)
            if d.date() < today.date():
                d = datetime(year + 1, month, day)
            return d.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # "May 26" / "May 26th"
    m = re.search(
        r'(' + month_pattern + r')\s+(\d{1,2})(?:st|nd|rd|th)?', t)
    if m:
        month, day = _MONTH_MAP[m.group(1)], int(m.group(2))
        year = today.year
        try:
            d = datetime(year, month, day)
            if d.date() < today.date():
                d = datetime(year + 1, month, day)
            return d.strftime("%Y-%m-%d")
        except ValueError:
            pass

    # DD/MM/YYYY or DD-MM-YYYY
    m = re.search(r'\b(\d{1,2})[\/\-](\d{1,2})(?:[\/\-](\d{2,4}))?\b', text)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        year = int(m.group(3)) if m.group(3) else today.year
        if year < 100:
            year += 2000
        try:
            return datetime(year, month, day).strftime("%Y-%m-%d")
        except ValueError:
            pass

    return None


# ── Time ───────────────────────────────────────────────────────────────────

def extract_time(text):
    t = text.lower()

    # Standard: "10:30 am" / "10:30am" / "10 am" / "10am"
    m = re.search(r'\b(\d{1,2}):(\d{2})\s*(am|pm)\b', t)
    if m:
        hour   = int(m.group(1))
        minute = int(m.group(2))
        period = m.group(3).upper()
        return f"{hour:02d}:{minute:02d} {period}"

    # "10 am" / "10am" (no minutes)
    m = re.search(r'\b(\d{1,2})\s*(am|pm)\b', t)
    if m:
        hour   = int(m.group(1))
        minute = 0
        period = m.group(2).upper()
        return f"{hour:02d}:{minute:02d} {period}"

    # Compact spoken format: "130pm" / "945am" / "130 pm" / "945 am"
    # Whisper often transcribes "one thirty pm" as "130pm" or "130 pm"
    m = re.search(r'\b(\d{3,4})\s*(am|pm)\b', t)
    if m:
        digits = m.group(1)
        period = m.group(2).upper()
        if len(digits) == 3:
            hour, minute = int(digits[0]), int(digits[1:3])
        else:  # 4 digits e.g. "1230"
            hour, minute = int(digits[:2]), int(digits[2:4])
        if 1 <= hour <= 12 and 0 <= minute < 60:
            return f"{hour:02d}:{minute:02d} {period}"

    # 24-hour "14:30"
    m = re.search(r'\b([01]?\d|2[0-3]):([0-5]\d)\b', text)
    if m:
        hour, minute = int(m.group(1)), int(m.group(2))
        period = "PM" if hour >= 12 else "AM"
        display_hour = hour % 12 or 12
        return f"{display_hour:02d}:{minute:02d} {period}"

    return None


# ── Name ───────────────────────────────────────────────────────────────────

_STOP_WORDS = {
    # Pronouns & articles
    "my", "name", "is", "i", "am", "i'm", "call", "me", "it's", "its",
    "the", "a", "an", "he", "she", "we", "they", "our", "your", "their",
    # Filler / conversation words
    "yes", "no", "hi", "hello", "okay", "ok", "sure", "right", "yeah",
    "please", "thank", "you", "this", "that", "and", "for", "with",
    "just", "like", "want", "need", "book", "appointment", "today",
    "tomorrow", "morning", "afternoon", "evening", "pm", "am",
    # Action words commonly spoken during booking
    "go", "going", "come", "coming", "still", "order", "work", "works",
    "tell", "said", "done", "know", "get", "got", "will", "would",
    "here", "there", "then", "also", "from", "have", "has", "had",
    "can", "could", "should", "let", "say", "take", "give",
    # Number words (e.g. "Four wires" — "Four" is not a name)
    "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "first", "second", "third",
}


def extract_name(text, services=None):
    """
    Extract a person's name from text.
    - Must be alphabetic only (no digits)
    - Must not be a service name
    - Requires an explicit "my name is …" pattern OR initial-capital word
      that is at least 3 chars and not a stop-word / service / day / month
    """
    services_lower = {s.lower() for s in (services or [])}
    excluded = _STOP_WORDS | services_lower | set(_DAY_MAP.keys()) | set(_MONTH_MAP.keys())

    def valid(word):
        """True if word could be part of a person's name."""
        return (
            word.isalpha()           # letters only — no digits
            and len(word) >= 3       # at least 3 chars — filters "Go", "Ok", "Hi"
            and word.lower() not in excluded
        )

    # "my name is X" / "I'm X" / "it's X" / "call me X" / "this is X"
    m = re.search(
        r"(?:my name is|i am|i'm|it's|its|this is|call me)\s+"
        r"([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        text, re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
        parts = [w for w in candidate.split() if valid(w)]
        if parts:
            return " ".join(p.title() for p in parts)

    # Capitalised words (likely a proper name given at start)
    words = text.split()
    name_parts = []
    for word in words:
        clean = re.sub(r"[^a-zA-Z]", "", word)
        if clean and clean[0].isupper() and valid(clean):
            name_parts.append(clean)
        elif name_parts:
            break   # stop collecting after first non-name word

    if name_parts:
        return " ".join(name_parts)

    return None


# ── Phone ──────────────────────────────────────────────────────────────────

def extract_phone(text):
    digits = re.sub(r"\D", "", text)
    if len(digits) >= 10:
        return digits[-10:]   # last 10 digits
    return None


# ── Master extract ─────────────────────────────────────────────────────────

def extract(text, services=None):
    """Extract all structured fields from one line of caller speech."""
    return {
        "intent":  extract_intent(text),
        "service": extract_service(text, services or []),
        "date":    extract_date(text),
        "time":    extract_time(text),
        "name":    extract_name(text, services),
        "phone":   extract_phone(text),
    }


# ── Hindi keyword helpers ───────────────────────────────────────────────────

_HINDI_INTENT = {
    "book":   ["बुक", "अपॉइंटमेंट", "appointment", "बुकिंग", "आना", "आना चाहता", "आना चाहती", "समय चाहिए", "book karna", "book"],
    "cancel": ["कैंसिल", "रद्द", "नहीं आना", "cancel"],
    "info":   ["जानकारी", "समय", "सेवा", "कितने बजे", "खुले", "services", "timing", "hours"],
}

_HINDI_DAY_MAP = {
    "सोमवार": "monday", "mangalvar": "tuesday", "मंगलवार": "tuesday",
    "बुधवार": "wednesday", "गुरुवार": "thursday", "शुक्रवार": "friday",
    "शनिवार": "saturday", "रविवार": "sunday",
    "आज": "today", "कल": "tomorrow", "परसों": "day after tomorrow",
}

_HINDI_NUM_MAP = {
    "एक": "1", "दो": "2", "तीन": "3", "चार": "4", "पाँच": "5", "पांच": "5",
    "छह": "6", "छः": "6", "सात": "7", "आठ": "8", "नौ": "9", "दस": "10",
    "ग्यारह": "11", "बारह": "12",
}


def extract_hi(text, services=None):
    """
    Extract structured fields from Hindi caller speech.
    Falls back to English extract() for anything not matched in Hindi.
    """
    t_lower = text.lower()
    result = extract(text, services)   # start with English extraction as base

    # Override intent from Hindi keywords
    if not result["intent"]:
        for intent, kws in _HINDI_INTENT.items():
            if any(kw in text for kw in kws):
                result["intent"] = intent
                break

    # Override date from Hindi day names / relative words
    if not result["date"]:
        today = datetime.now()
        for hindi_word, eng_equiv in _HINDI_DAY_MAP.items():
            if hindi_word in text:
                # Re-run English extract on the equivalent English word
                result["date"] = extract_date(eng_equiv)
                break

    # Replace Hindi number words in text before time extraction
    if not result["time"]:
        normalized = text
        for hindi_num, digit in _HINDI_NUM_MAP.items():
            normalized = normalized.replace(hindi_num, digit)
        if "बजे" in normalized or "am" in normalized.lower() or "pm" in normalized.lower():
            result["time"] = extract_time(normalized)

    return result
