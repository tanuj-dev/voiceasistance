"""
brain.py — Rule-based AI brain for the receptionist.
No Ollama, no Groq, no internet. 100% offline. Instant responses.

Two responsibilities:
  1. reply(key, **kwargs)  — pick a natural-sounding template response
  2. extract(text, services) — pull structured data from caller's speech
"""

import re
import random
from datetime import datetime, timedelta
from difflib import get_close_matches


# ═══════════════════════════════════════════════════════════════════════════
#  RESPONSE TEMPLATES
#  Multiple variants per key → sounds less robotic
# ═══════════════════════════════════════════════════════════════════════════

TEMPLATES = {
    "greeting": [
        "Thank you for calling {business}! How can I help you today?",
        "Good {time_of_day}! You've reached {business}. How may I assist you?",
        "Hello! Welcome to {business}. What can I do for you today?",
    ],
    "no_intent": [
        "How can I help you today? I can book a {booking_word}, answer questions, or help with cancellations.",
        "What can I do for you? I can schedule a {booking_word} or answer any questions.",
        "I'm here to help! Would you like to book a {booking_word} or do you have a question?",
    ],
    "ask_service": [
        "Which service would you like? We offer {services}.",
        "What service can I book for you? We have {services} available.",
        "Sure! Which service do you need? We offer {services}.",
    ],
    "ask_date": [
        "What date works for you?",
        "Which date would you prefer?",
        "When would you like to come in?",
        "What date are you looking at?",
    ],
    "show_slots": [
        "On {date}, I have slots available at {slots}. Which time works for you?",
        "For {date}, the available times are {slots}. Which do you prefer?",
        "I have the following slots open on {date}: {slots}. Which would you like?",
    ],
    "slot_unavailable": [
        "Sorry, that time isn't available. The open slots are {slots}. Which works for you?",
        "That slot is taken. I still have {slots} available. Which would you prefer?",
        "Unfortunately that time is booked. Available slots are {slots}. Which suits you?",
    ],
    "no_slots": [
        "I'm sorry, there are no available slots on {date}. Could you try a different date?",
        "We're fully booked on {date}. What other date would work for you?",
        "Unfortunately {date} is fully booked. Could you suggest another date?",
    ],
    "ask_name": [
        "May I have your full name please?",
        "Could I get your name?",
        "What name should I put the booking under?",
        "And your name please?",
    ],
    "ask_phone": [
        "What's your phone number?",
        "Could I get your contact number?",
        "And your mobile number please?",
        "What number can we reach you on?",
    ],
    "confirm": [
        "Let me confirm — {name} for {service} on {date} at {time}. Is that correct?",
        "Just to confirm — {name}, {service}, {date} at {time}. Does that sound right?",
        "So I have {name} booked for {service} on {date} at {time}. Is everything correct?",
    ],
    "booked": [
        "Your {booking_word} is confirmed! Booking ID {id}. We'll see you on {date} at {time} for {service}. Have a wonderful day!",
        "All done! {name}, your {service} {booking_word} is set for {date} at {time}. Booking ID {id}. Thank you and goodbye!",
        "{booking_word} confirmed! ID {id}. See you on {date} at {time} for your {service}. Have a great day!",
    ],
    "slot_taken": [
        "I'm sorry, that slot was just taken. Remaining slots are {slots}. Which would you like?",
        "Unfortunately that slot went just now. I still have {slots} available. Which works for you?",
    ],
    "cancel_ask": [
        "I can help with that. Could you give me your name and the date of your {booking_word}?",
        "Sure, I can cancel that for you. What's your name and {booking_word} date?",
    ],
    "cancel_ask_phone": [
        "I can help cancel that. What's the phone number on the {booking_word}?",
        "Sure, I'll cancel that for you. Could you give me the phone number used for the {booking_word}?",
        "No problem. What phone number was the {booking_word} booked under?",
    ],
    "cancel_confirmed": [
        "Done! Your {booking_word} has been cancelled. Booking ID {booking_id} is now cancelled. Is there anything else I can help you with?",
        "Your {booking_word} {booking_id} has been successfully cancelled. Have a good day!",
        "Cancelled! Booking {booking_id} has been removed. Hope to see you again soon!",
    ],
    "no_booking_found": [
        "I couldn't find any upcoming {booking_word}s with that number. Could you double-check the phone number?",
        "I don't see any confirmed {booking_word}s under that number. Is it possible it was booked under a different number?",
        "Sorry, I couldn't locate a {booking_word} for that phone number. Please check and try again.",
    ],
    "info": [
        "We offer {services}. Our hours are {start_time} to {end_time}, {days}. Can I book a {booking_word} for you?",
        "Our services include {services}. We're open {days} from {start_time} to {end_time}. Would you like to book a {booking_word}?",
    ],
    "unclear": [
        "I didn't quite catch that. Could you please repeat?",
        "Sorry, could you say that again?",
        "I'm sorry, I didn't get that. Could you repeat please?",
    ],
    "urgency": [
        "I understand this is urgent. Please hold while I connect you to our staff immediately.",
    ],
    "goodbye": [
        "Thank you for calling {business}. Have a wonderful day! Goodbye!",
        "Thanks for calling {business}. Take care, goodbye!",
    ],
    "reconfirm": [
        "Just to make sure — {name} for {service} on {date} at {time}. Can you confirm with yes or no?",
        "Let me read that back — {name}, {service}, {date} at {time}. Is that correct?",
    ],
}


def _time_of_day():
    h = datetime.now().hour
    if h < 12:
        return "morning"
    if h < 17:
        return "afternoon"
    return "evening"


def reply(key, **kwargs):
    """Pick a random template and fill in placeholders."""
    templates = TEMPLATES.get(key, ["How can I help you?"])
    template = random.choice(templates)
    kwargs.setdefault("time_of_day", _time_of_day())
    try:
        return template.format(**kwargs)
    except KeyError:
        # Return template as-is if a placeholder is missing
        return template


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

    # "10:30 am" / "10:30am" / "10 am" / "10am"
    m = re.search(r'\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b', t)
    if m:
        hour   = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        period = m.group(3).upper()
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
    "my", "name", "is", "i", "am", "i'm", "call", "me", "it's", "its",
    "the", "a", "an", "yes", "no", "hi", "hello", "okay", "ok", "sure",
    "please", "thank", "you", "this", "that", "and", "for", "with",
    "just", "like", "want", "need", "book", "appointment", "today",
    "tomorrow", "morning", "afternoon", "evening", "pm", "am",
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
            and len(word) >= 2
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
