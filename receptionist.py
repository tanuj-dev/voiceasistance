import re
from datetime import datetime
import brain
import database
import slot_manager


URGENT_WORDS = ["urgent", "emergency", "severe", "accident", "critical", "bleeding"]


def _today():
    return datetime.now().strftime("%Y-%m-%d")


def _day_name(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%A, %B %d")
    except Exception:
        return date_str


class Receptionist:
    def __init__(self, business_id):
        self.business = database.get_business(business_id)
        if not self.business:
            raise ValueError(f"Business '{business_id}' not found in database.")
        self.business_id = business_id
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

    # ── shortcut to brain.reply with business fields pre-filled ──────────
    def _r(self, key, **extra):
        b = self.business
        return brain.reply(
            key,
            business  = b["name"],
            services  = ", ".join(b["services"]),
            start_time= b["start_time"],
            end_time  = b["end_time"],
            days      = ", ".join(b["working_days"]),
            **extra
        )

    # ── Main entry points ─────────────────────────────────────────────────

    def greeting(self):
        """Opening greeting — no user input yet."""
        return self._r("greeting")

    def process(self, user_text):
        """Process one turn of caller speech. Returns response string."""

        # Urgency check first
        if any(w in user_text.lower() for w in URGENT_WORDS):
            self.state = "done"
            return self._r("urgency")

        # Extract structured data from what the caller said
        extracted = brain.extract(user_text, self.business["services"])
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

        return self._route()

    # ── State router ──────────────────────────────────────────────────────

    def _route(self):
        c = self.collected

        if not c["intent"]:
            return self._r("no_intent")

        if c["intent"] == "info":
            return self._r("info")

        if c["intent"] == "cancel":
            return self._r("cancel_ask")

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
            c["date"] = None
            return self._r("no_slots", date=_day_name(c["date"] or "that date"))

        # 4. Time
        if not c["time"]:
            return self._r(
                "show_slots",
                date  = _day_name(c["date"]),
                slots = ", ".join(self.available_slots[:6]),
            )

        # Validate the chosen time against real slots
        matched = slot_manager.normalize_time(c["time"], self.available_slots)
        if not matched:
            c["time"] = None
            return self._r(
                "slot_unavailable",
                slots = ", ".join(self.available_slots[:6]),
            )
        c["time"] = matched

        # 5. Name
        if not c["name"]:
            return self._r("ask_name")

        # 6. Phone
        if not c["phone"]:
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

        # 8. Finalise after caller says yes
        last_words = getattr(self, "_last_user", "").lower()
        YES_WORDS = ["yes", "correct", "confirm", "sure", "right",
                     "yep", "yeah", "ok", "okay", "perfect", "go ahead"]
        if any(w in last_words for w in YES_WORDS):
            return self._finalise()

        # Unclear answer — re-ask
        return self._r(
            "reconfirm",
            name    = c["name"],
            service = c["service"],
            date    = _day_name(c["date"]),
            time    = c["time"],
        )

    def _finalise(self):
        c = self.collected
        booking_id = slot_manager.book_appointment(
            self.business_id,
            c["date"], c["time"],
            c["name"], c["phone"], "",
            c["service"],
        )
        if booking_id:
            self.state = "done"
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
                slots = ", ".join(self.available_slots[:6])
                        if self.available_slots else "none available",
            )

    # ── Store last user message so confirmation check works ───────────────
    def process(self, user_text):
        self._last_user = user_text

        if any(w in user_text.lower() for w in URGENT_WORDS):
            self.state = "done"
            return self._r("urgency")

        extracted = brain.extract(user_text, self.business["services"])
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

        return self._route()

    @property
    def is_done(self):
        return self.state == "done"
