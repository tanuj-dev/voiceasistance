"""
notifier.py — Email notifications via Gmail SMTP.

Two flows:
  1. notify_owner()              → New booking alert to business owner
  2. notify_owner_cancellation() → Cancellation alert to business owner
  3. send_confirmation()         → Booking confirmation to customer (when email collected)

Setup in .env:
  GMAIL_ADDRESS=your@gmail.com
  GMAIL_APP_PASSWORD=xxxx (16-char Google App Password)

How to get App Password:
  Google Account → Security → 2-Step Verification → App Passwords
  → Select "Mail" + "Other" → name it "AI Receptionist" → copy 16-char code
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


# ── 3. Booking confirmation to customer ──────────────────────────────────

def send_confirmation(business_name, customer_name, customer_email,
                      service, date_str, time_str, booking_id):
    """
    Sent to the customer after their booking is confirmed.
    Only fires when customer_email is available (not collected during voice calls yet).
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
