import re
import threading
from datetime import datetime
import brain
import database
import slot_manager
import notifier


URGENT_WORDS = ["urgent", "emergency", "severe", "accident", "critical", "bleeding"]


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _day_name(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d")
    except Exception:
        return date_str


class Receptionist:
    def __init__(self, business_id, caller_phone=None, lang="en"):
        self.business = database.get_business(business_id)
        if not self.business:
            raise ValueError(f"Business '{business_id}' not found in database.")
        self.business_id  = business_id
        self.caller_phone = caller_phone
        self.lang         = lang   # "en" or "hi"
        self.state = "greeting"
        self.collected = {
            "intent":  None,
            "service": None,
            "date":    None,
            "time":    None,
            "name":    None,
            "phone":   None,
        }
        self.available_slots = []

    # ── booking word based on business type ──────────────────────────────
    def _booking_word(self):
        """Returns the right word for a booking based on business type and language."""
        if self.lang == "hi":
            _WORD_MAP_HI = {
                "dental":  "अपॉइंटमेंट",
                "medical": "अपॉइंटमेंट",
                "clinic":  "अपॉइंटमेंट",
                "doctor":  "अपॉइंटमेंट",
                "physio":  "सेशन",
                "gym":     "सेशन",
                "fitness": "सेशन",
                "yoga":    "सेशन",
                "salon":   "बुकिंग",
                "barber":  "बुकिंग",
                "spa":     "बुकिंग",
                "hotel":   "रिज़र्वेशन",
            }
            btype = self.business.get("type", "").lower()
            return _WORD_MAP_HI.get(btype, "अपॉइंटमेंट")

        _WORD_MAP = {
            "dental":   "appointment",
            "medical":  "appointment",
            "clinic":   "appointment",
            "doctor":   "appointment",
            "physio":   "session",
            "gym":      "session",
            "fitness":  "session",
            "yoga":     "session",
            "pilates":  "session",
            "salon":    "booking",
            "barber":   "booking",
            "spa":      "booking",
            "beauty":   "booking",
            "hotel":    "reservation",
        }
        btype = self.business.get("type", "").lower()
        return _WORD_MAP.get(btype, "appointment")

    # ── shortcut to brain.reply with business fields pre-filled ──────────
    def _r(self, key, **extra):
        b = self.business
        days = brain.summarize_days_hi(b["working_days"]) if self.lang == "hi" \
               else brain.summarize_days(b["working_days"])
        return brain.reply(
            key,
            lang         = self.lang,
            business     = b["name"],
            services     = ", ".join(b["services"]),
            start_time   = b["start_time"],
            end_time     = b["end_time"],
            days         = days,
            booking_word = self._booking_word(),
            **extra
        )

    # ── Main entry points ─────────────────────────────────────────────────

    def greeting(self):
        """Opening greeting — no user input yet."""
        msg = self._r("greeting")
        self._last_response = msg
        return msg

    # ── State router ──────────────────────────────────────────────────────

    # Simple words that don't need Groq — just ask what they want
    _GREETING_WORDS = {
        "hi", "hello", "hey", "helo", "hii", "yo", "hiya",
        "नमस्ते", "हेलो", "हाय",
    }

    def _route(self):
        c = self.collected

        if not c["intent"]:
            last = getattr(self, "_last_user", "").strip().lower()
            # If it's just a greeting word, skip Groq — just ask what they want
            if last in self._GREETING_WORDS or len(last.split()) <= 2 and any(
                w in last for w in self._GREETING_WORDS
            ):
                return self._r("no_intent")
            groq = brain.groq_reply(
                user_text     = last,
                business_name = self.business["name"],
                services      = self.business["services"],
                days          = self.business["working_days"],
                start_time    = self.business["start_time"],
                end_time      = self.business["end_time"],
                booking_word  = self._booking_word(),
                lang          = self.lang,
            )
            return groq if groq else self._r("no_intent")

        if c["intent"] == "info":
            groq = brain.groq_reply(
                user_text     = getattr(self, "_last_user", ""),
                business_name = self.business["name"],
                services      = self.business["services"],
                days          = self.business["working_days"],
                start_time    = self.business["start_time"],
                end_time      = self.business["end_time"],
                booking_word  = self._booking_word(),
                lang          = self.lang,
            )
            return groq if groq else self._r("info")

        if c["intent"] == "cancel":
            # Step 1: collect phone number
            if not c["phone"]:
                return self._r("cancel_ask_phone")
            # Step 2: look up the booking
            booking = database.get_booking_by_phone(self.business_id, c["phone"])
            if not booking:
                return self._r("no_booking_found")
            # Step 3: cancel it and confirm
            database.cancel_booking(booking["id"])
            self.state = "done"
            # Send notifications in background
            _bid = booking["id"]
            def _notify_cancel():
                notifier.notify_owner_cancellation(
                    business_name  = self.business["name"],
                    owner_email    = self.business.get("contact_email", ""),
                    customer_phone = c["phone"],
                    booking_id     = _bid,
                )
                notifier.send_sms_cancellation(
                    to_phone      = self.caller_phone,
                    business_name = self.business["name"],
                    booking_id    = _bid,
                )
            threading.Thread(target=_notify_cancel, daemon=True).start()
            return self._r("cancel_confirmed", booking_id=_bid)

        if c["intent"] in ("book", "reschedule"):
            return self._handle_booking()

        return self._r("no_intent")

    # ── Booking flow ──────────────────────────────────────────────────────

    def _handle_booking(self):
        c = self.collected
        b = self.business

        # 1. Service (skip if business has only one)
        if not c["service"]:
            if len(b["services"]) == 1:
                c["service"] = b["services"][0]
            else:
                return self._r("ask_service")

        # 2. Date
        if not c["date"]:
            return self._r("ask_date")

        # 3. Fetch slots for that date
        if not self.available_slots:
            self.available_slots = slot_manager.get_available_slots(
                self.business_id, c["date"])

        if not self.available_slots:
            bad_date = _day_name(c["date"])   # capture before clearing
            c["date"] = None
            return self._r("no_slots", date=bad_date)

        # 4. Time
        if not c["time"]:
            return self._r(
                "show_slots",
                date  = _day_name(c["date"]),
                slots = brain.summarize_slots(self.available_slots),
            )

        # Validate the chosen time against real slots
        matched = slot_manager.normalize_time(c["time"], self.available_slots)
        if not matched:
            c["time"] = None
            return self._r(
                "slot_unavailable",
                slots = brain.summarize_slots(self.available_slots),
            )
        c["time"] = matched

        # 5. Name
        if not c["name"]:
            return self._r("ask_name")

        # 6. Phone — use caller's own number automatically; only ask if unavailable
        if not c["phone"]:
            if self.caller_phone:
                c["phone"] = self.caller_phone
            else:
                return self._r("ask_phone")

        # 7. Confirmation
        if self.state != "confirming":
            self.state = "confirming"
            return self._r(
                "confirm",
                name    = c["name"],
                service = c["service"],
                date    = _day_name(c["date"]),
                time    = c["time"],
            )

        # 8. Check caller's response to confirmation
        last_words = getattr(self, "_last_user", "").lower()

        YES_WORDS = [
            # English
            "yes", "correct", "confirm", "sure", "right",
            "yep", "yeah", "ok", "okay", "perfect", "go ahead",
            # Hindi — spoken and common STT outputs
            "हाँ", "हां", "हा", "जी", "जी हाँ", "जी हां",
            "bilkul", "बिल्कुल", "sahi", "सही", "theek", "ठीक",
            "haan", "han", "ha ", " ha",
        ]
        NO_WORDS = [
            "no", "nope", "wrong", "incorrect", "change", "different",
            "नहीं", "नही", "गलत", "बदलो", "बदलना",
        ]

        if any(w in last_words for w in YES_WORDS):
            return self._finalise()

        if any(w in last_words for w in NO_WORDS):
            # User wants to change something — extraction already ran in process()
            # and may have updated fields (e.g. "no, put it under Sarah").
            # Reset state so we flow back through the booking steps with new values.
            self.state = "booking"
            # If they mentioned a specific field to change, clear it so we re-ask
            if "name" in last_words:
                c["name"] = None
            elif "date" in last_words or "day" in last_words:
                c["date"] = None
                c["time"] = None
                self.available_slots = []
            elif "time" in last_words or "slot" in last_words:
                c["time"] = None
            elif "service" in last_words:
                c["service"] = None
            return self._r("what_to_change")

        # Ambiguous — re-ask yes/no
        return self._r(
            "reconfirm",
            name    = c["name"],
            service = c["service"],
            date    = _day_name(c["date"]),
            time    = c["time"],
        )

    def _finalise(self):
        c = self.collected
        try:
            booking_id = slot_manager.book_appointment(
                self.business_id,
                c["date"], c["time"],
                c["name"], c["phone"], "",
                c["service"],
            )
        except Exception as e:
            import traceback
            print(f"[_finalise] booking error: {e}")
            traceback.print_exc()
            self.state = "done"
            return self._r("unclear")  # fallback — caller hears "could you repeat" then hangup
        if booking_id:
            self.state = "done"
            # Send email + SMS in background so voice response returns instantly
            def _notify():
                notifier.notify_owner(
                    business_name  = self.business["name"],
                    owner_email    = self.business.get("contact_email", ""),
                    customer_name  = c["name"],
                    customer_phone = c["phone"],
                    service        = c["service"],
                    date_str       = _day_name(c["date"]),
                    time_str       = c["time"],
                    booking_id     = booking_id,
                )
                notifier.send_sms_confirmation(
                    to_phone      = self.caller_phone,
                    business_name = self.business["name"],
                    customer_name = c["name"],
                    service       = c["service"],
                    date_str      = _day_name(c["date"]),
                    time_str      = c["time"],
                    booking_id    = booking_id,
                )
            threading.Thread(target=_notify, daemon=True).start()
            return self._r(
                "booked",
                id      = booking_id,
                name    = c["name"],
                service = c["service"],
                date    = _day_name(c["date"]),
                time    = c["time"],
            )
        else:
            # Slot was taken between showing and confirming
            c["time"] = None
            self.available_slots = slot_manager.get_available_slots(
                self.business_id, c["date"])
            self.state = "booking"
            return self._r(
                "slot_taken",
                slots = brain.summarize_slots(self.available_slots)
                        if self.available_slots else "none available",
            )

    # ── Store last user message so confirmation check works ───────────────
    def process(self, user_text):
        self._last_user = user_text

        URGENT_HI = ["इमरजेंसी", "दर्द", "खून", "accident", "emergency"]
        urgent_check = URGENT_WORDS + (URGENT_HI if self.lang == "hi" else [])
        if any(w in user_text.lower() for w in urgent_check):
            self.state = "done"
            response = self._r("urgency")
            self._last_response = response
            return response

        extracted = brain.extract_hi(user_text, self.business["services"]) \
                    if self.lang == "hi" else \
                    brain.extract(user_text, self.business["services"])
        c = self.collected

        for key in ("intent", "service", "name"):
            if extracted.get(key):
                c[key] = extracted[key]
        if extracted.get("date"):
            c["date"] = extracted["date"]
        if extracted.get("time"):
            c["time"] = extracted["time"]
        if extracted.get("phone"):
            c["phone"] = extracted["phone"]

        response = self._route()
        self._last_response = response
        return response

    @property
    def is_done(self):
        return self.state == "done"
