import os
import sqlite3
import json
from pathlib import Path

# On Railway/Render: set DB_PATH env var to a persistent volume path e.g. /data/receptionist.db
# Locally: defaults to the project folder
_db_env = os.getenv("DB_PATH")
DB_PATH = Path(_db_env) if _db_env else Path(__file__).parent / "receptionist.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                services TEXT,
                working_days TEXT,
                start_time TEXT DEFAULT '09:00',
                end_time TEXT DEFAULT '18:00',
                slot_duration INTEGER DEFAULT 30,
                timezone TEXT DEFAULT 'Asia/Kolkata',
                contact_email TEXT DEFAULT ''
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                customer_name TEXT,
                customer_phone TEXT,
                customer_email TEXT DEFAULT '',
                service TEXT,
                appointment_datetime TEXT,
                status TEXT DEFAULT 'confirmed',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses(id)
            )
        """)
        conn.commit()


def add_business(business_id, name, business_type, services, working_days,
                 start_time, end_time, slot_duration=30,
                 timezone="Asia/Kolkata", contact_email=""):
    with get_connection() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO businesses
            (id, name, type, services, working_days, start_time, end_time,
             slot_duration, timezone, contact_email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (business_id, name, business_type, json.dumps(services),
              json.dumps(working_days), start_time, end_time,
              slot_duration, timezone, contact_email))
        conn.commit()


def get_business(business_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM businesses WHERE id = ?", (business_id,)
        ).fetchone()
        if row:
            d = dict(row)
            d["services"] = json.loads(d["services"])
            d["working_days"] = json.loads(d["working_days"])
            return d
        return None


def get_all_businesses():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, name, type FROM businesses").fetchall()
        return [dict(r) for r in rows]


def add_booking(business_id, customer_name, customer_phone,
                customer_email, service, appointment_datetime):
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO bookings
            (business_id, customer_name, customer_phone, customer_email,
             service, appointment_datetime)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (business_id, customer_name, customer_phone,
              customer_email, service, appointment_datetime))
        conn.commit()
        return cursor.lastrowid


def is_slot_taken(business_id, appointment_datetime):
    with get_connection() as conn:
        row = conn.execute("""
            SELECT id FROM bookings
            WHERE business_id = ? AND appointment_datetime = ? AND status = 'confirmed'
        """, (business_id, appointment_datetime)).fetchone()
        return row is not None


def get_bookings_for_date(business_id, date_str):
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM bookings
            WHERE business_id = ? AND appointment_datetime LIKE ? AND status = 'confirmed'
        """, (business_id, f"{date_str}%")).fetchall()
        return [dict(r) for r in rows]


def cancel_booking(booking_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,)
        )
        conn.commit()
