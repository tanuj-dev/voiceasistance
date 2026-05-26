import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def send_confirmation(business_name, customer_name, customer_email,
                      service, date_str, time_str, booking_id):
    """Send booking confirmation email. Silently skips if email not configured."""
    sender = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender or not password or not customer_email:
        return False

    subject = f"Appointment Confirmed — {business_name}"
    body = f"""Hi {customer_name},

Your appointment has been confirmed!

Business  : {business_name}
Service   : {service}
Date      : {date_str}
Time      : {time_str}
Booking ID: #{booking_id}

If you need to reschedule or cancel, please call us.

Thank you!
{business_name}
"""
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = customer_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, customer_email, msg.as_string())
        print(f"Confirmation email sent to {customer_email}")
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False
