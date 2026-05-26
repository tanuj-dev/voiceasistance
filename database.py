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
                contact_email TEXT DEFAULT '',
                client_password TEXT DEFAULT ''
            )
        """)
        # Migration: add client_password if upgrading old DB
        try:
            conn.execute("ALTER TABLE businesses ADD COLUMN client_password TEXT DEFAULT ''")
            conn.commit()
        except Exception:
            pass  # Column already exists
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_id TEXT NOT NULL,
                date TEXT NOT NULL,
                reason TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses(id),
                UNIQUE(business_id, date)
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


def set_client_password(business_id, password):
    with get_connection() as conn:
        conn.execute(
            "UPDATE businesses SET client_password = ? WHERE id = ?",
            (password, business_id)
        )
        conn.commit()


def cancel_booking(booking_id):
    with get_connection() as conn:
        conn.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,)
        )
        conn.commit()


def get_all_bookings(business_id=None, status=None, search=None):
    """Fetch bookings with optional filters. Returns newest first."""
    query = "SELECT * FROM bookings WHERE 1=1"
    params = []
    if business_id:
        query += " AND business_id = ?"
        params.append(business_id)
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (customer_name LIKE ? OR customer_phone LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    query += " ORDER BY id DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


def update_business_schedule(business_id, working_days, start_time, end_time, slot_duration):
    """Update a business's working hours and slot settings."""
    with get_connection() as conn:
        conn.execute("""
            UPDATE businesses
            SET working_days = ?, start_time = ?, end_time = ?, slot_duration = ?
            WHERE id = ?
        """, (json.dumps(working_days), start_time, end_time, int(slot_duration), business_id))
        conn.commit()


def add_leave(business_id, date, reason=''):
    """Mark a date as closed (leave/holiday). Silently replaces if already exists."""
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO leaves (business_id, date, reason) VALUES (?, ?, ?)",
            (business_id, date, reason)
        )
        conn.commit()


def get_leaves(business_id):
    """Return all leave dates for a business, sorted ascending."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM leaves WHERE business_id = ? ORDER BY date ASC",
            (business_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_leave(leave_id, business_id):
    """Remove a leave entry (ownership-safe)."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM leaves WHERE id = ? AND business_id = ?",
            (leave_id, business_id)
        )
        conn.commit()


def is_leave_day(business_id, date_str):
    """Return True if this date is a marked leave day for the business."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM leaves WHERE business_id = ? AND date = ?",
            (business_id, date_str)
        ).fetchone()
        return row is not None


def get_dashboard_stats(business_id=None):
    """Return booking counts: today / this week / this month / all time."""
    from datetime import datetime, timedelta
    today     = datetime.now().strftime("%Y-%m-%d")
    week_ago  = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    biz_filter = "AND business_id = ?" if business_id else ""
    base_params = [business_id] if business_id else []

    def count(extra_where, extra_params):
        q = f"SELECT COUNT(*) FROM bookings WHERE status='confirmed' {biz_filter} {extra_where}"
        with get_connection() as conn:
            return conn.execute(q, base_params + extra_params).fetchone()[0]

    return {
        "today":     count("AND appointment_datetime LIKE ?", [f"{today}%"]),
        "week":      count("AND appointment_datetime >= ?",   [week_ago]),
        "month":     count("AND appointment_datetime >= ?",   [month_ago]),
        "all_time":  count("", []),
    }
