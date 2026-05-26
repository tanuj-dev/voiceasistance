from datetime import datetime, timedelta
import database


def get_available_slots(business_id, date_str):
    """Return list of available time slot strings for a given date (YYYY-MM-DD)."""
    business = database.get_business(business_id)
    if not business:
        return []

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return []

    day_name = date.strftime("%A")
    if day_name not in business["working_days"]:
        return []

    start = datetime.strptime(f"{date_str} {business['start_time']}", "%Y-%m-%d %H:%M")
    end = datetime.strptime(f"{date_str} {business['end_time']}", "%Y-%m-%d %H:%M")
    duration = timedelta(minutes=business["slot_duration"])

    slots = []
    current = start
    while current + duration <= end:
        slot_dt_str = current.strftime("%Y-%m-%d %H:%M")
        if not database.is_slot_taken(business_id, slot_dt_str):
            slots.append(current.strftime("%I:%M %p"))
        current += duration

    return slots


def book_appointment(business_id, date_str, time_str,
                     customer_name, customer_phone, customer_email, service):
    """Book a slot. Returns booking ID or None if slot is taken."""
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M"):
        try:
            time_obj = datetime.strptime(time_str.strip().upper(), fmt.upper())
            appointment_datetime = f"{date_str} {time_obj.strftime('%H:%M')}"
            break
        except ValueError:
            continue
    else:
        return None

    if database.is_slot_taken(business_id, appointment_datetime):
        return None

    return database.add_booking(
        business_id, customer_name, customer_phone,
        customer_email, service, appointment_datetime
    )


def normalize_time(time_str, available_slots):
    """Try to match a spoken time string against available slots."""
    clean = time_str.strip().upper().replace(" ", "")
    for slot in available_slots:
        if slot.upper().replace(" ", "") == clean:
            return slot
        # match partial e.g. "5:30" against "05:30 PM"
        if clean.replace("PM", "").replace("AM", "") in slot.replace(" ", ""):
            return slot
    return None
