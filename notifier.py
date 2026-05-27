"""
notifier.py — Email (Gmail SMTP) + SMS (Twilio) notifications.

Email flows  (business owner gets these):
  1. notify_owner()              → New booking alert
  2. notify_owner_cancellation() → Cancellation alert

SMS flows  (customer gets these — sent to their real phone number):
  3. send_sms_confirmation()     → Booking confirmed SMS to customer
  4. send_sms_cancellation()     → Cancellation confirmed SMS to customer

Email setup in .env:
  GMAIL_ADDRESS=your@gmail.com
  GMAIL_APP_PASSWORD=xxxx (16-char Google App Password)
  → Google Account → Security → 2-Step Verification → App Passwords

SMS setup in .env:
  TWILIO_ACCOUNT_SID=ACxxxx  (already there)
  TWILIO_AUTH_TOKEN=xxxx     (already there)
  TWILIO_PHONE_NUMBER=+12394238893  (your Twilio virtual number)
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def _get_credentials():
    sender   = os.getenv("GMAIL_ADDRESS", "")
    password = os.getenv("GMAIL_APP_PASSWORD", "")
    # Skip if still using placeholder values
    if sender == "your@gmail.com" or not sender or not password:
        return None, None
    return sender, password


def _send(to_email, subject, body):
    """Internal: send a plain-text email. Returns True/False."""
    sender, password = _get_credentials()
    if not sender or not to_email:
        return False

    msg = MIMEMultipart()
    msg["From"]    = sender
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, to_email, msg.as_string())
        print(f"[notifier] Email sent → {to_email} | {subject}")
        return True
    except Exception as e:
        print(f"[notifier] Email failed → {e}")
        return False


# ── 1. New booking alert to business owner ────────────────────────────────

def notify_owner(business_name, owner_email, customer_name, customer_phone,
                 service, date_str, time_str, booking_id):
    """
    Sent to the business owner whenever a new booking is made via AI receptionist.
    owner_email comes from business.contact_email in the database.
    """
    subject = f"New Booking #{booking_id} — {business_name}"
    body = f"""\
New appointment booked via your AI Receptionist!

  Customer  : {customer_name}
  Phone     : {customer_phone}
  Service   : {service}
  Date      : {date_str}
  Time      : {time_str}
  Booking ID: #{booking_id}

This was booked automatically — no action needed.
You can view and manage all bookings in your dashboard.

— {business_name} AI Receptionist
"""
    return _send(owner_email, subject, body)


# ── 2. Cancellation alert to business owner ───────────────────────────────

def notify_owner_cancellation(business_name, owner_email, customer_phone, booking_id):
    """
    Sent to the business owner whenever a booking is cancelled via AI receptionist.
    """
    subject = f"Booking #{booking_id} Cancelled — {business_name}"
    body = f"""\
A booking has been cancelled via your AI Receptionist.

  Booking ID: #{booking_id}
  Phone     : {customer_phone}

The slot is now free and available for new bookings.
You can view all bookings in your dashboard.

— {business_name} AI Receptionist
"""
    return _send(owner_email, subject, body)


# ── 3. Booking confirmation to customer (email — future use) ─────────────

def send_confirmation(business_name, customer_name, customer_email,
                      service, date_str, time_str, booking_id):
    """
    Email to customer — only fires when customer_email is available.
    Not used during voice calls (can't collect email over phone).
    """
    if not customer_email:
        return False

    subject = f"Appointment Confirmed — {business_name}"
    body = f"""\
Hi {customer_name},

Your appointment has been confirmed!

  Business  : {business_name}
  Service   : {service}
  Date      : {date_str}
  Time      : {time_str}
  Booking ID: #{booking_id}

To reschedule or cancel, please call us directly.

Thank you for choosing {business_name}!
"""
    return _send(customer_email, subject, body)


# ── 4. SMS to customer — booking confirmed ────────────────────────────────

def send_sms_confirmation(to_phone, business_name, customer_name,
                          service, date_str, time_str, booking_id):
    """
    SMS sent to the caller's real phone number right after booking is confirmed.
    to_phone must be in E.164 format e.g. +12394238893 (passed from Twilio's From field).
    """
    account_sid  = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token   = os.getenv("TWILIO_AUTH_TOKEN")
    from_number  = os.getenv("TWILIO_PHONE_NUMBER")   # your Twilio virtual number

    if not account_sid or not auth_token or not from_number or not to_phone:
        return False

    message = (
        f"Booking Confirmed! Hi {customer_name}, your {service} at "
        f"{business_name} is booked for {date_str} at {time_str}. "
        f"Booking ID: #{booking_id}. To cancel, call us."
    )

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        client.messages.create(to=to_phone, from_=from_number, body=message)
        print(f"[notifier] SMS sent → {to_phone}")
        return True
    except Exception as e:
        print(f"[notifier] SMS failed → {e}")
        return False


# ── 5. SMS to customer — cancellation confirmed ───────────────────────────

def send_sms_cancellation(to_phone, business_name, booking_id):
    """
    SMS sent to the caller's real phone number right after their booking is cancelled.
    """
    account_sid  = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token   = os.getenv("TWILIO_AUTH_TOKEN")
    from_number  = os.getenv("TWILIO_PHONE_NUMBER")

    if not account_sid or not auth_token or not from_number or not to_phone:
        return False

    message = (
        f"Booking #{booking_id} at {business_name} has been cancelled. "
        f"Call us anytime to rebook. Thank you!"
    )

    try:
        from twilio.rest import Client
        client = Client(account_sid, auth_token)
        client.messages.create(to=to_phone, from_=from_number, body=message)
        print(f"[notifier] Cancellation SMS sent → {to_phone}")
        return True
    except Exception as e:
        print(f"[notifier] Cancellation SMS failed → {e}")
        return False
