import os
import json
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def _fetchone(cursor):
    row = cursor.fetchone()
    return dict(row) if row else None


def _fetchall(cursor):
    return [dict(r) for r in cursor.fetchall()]


def create_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
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
                    client_password TEXT DEFAULT '',
                    call_mode TEXT DEFAULT 'always',
                    twilio_number TEXT DEFAULT ''
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,
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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS leaves (
                    id SERIAL PRIMARY KEY,
                    business_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    reason TEXT DEFAULT '',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (business_id) REFERENCES businesses(id),
                    UNIQUE(business_id, date)
                )
            """)
            # Seed default business if not exists
            cur.execute("SELECT id FROM businesses WHERE id = 'tanuj_dental'")
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO businesses
                    (id, name, type, services, working_days, start_time, end_time,
                     slot_duration, timezone, contact_email, client_password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    'tanuj_dental',
                    'Tanuj Dental Clinic',
                    'dental',
                    json.dumps(['Cleaning', 'Filling', 'Root Canal', 'Whitening', 'Extraction']),
                    json.dumps(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']),
                    '09:00', '18:00', 30, 'Asia/Kolkata',
                    'tanujprajapati2000@gmail.com',
                    'dental123'
                ))
        conn.commit()


def add_business(business_id, name, business_type, services, working_days,
                 start_time, end_time, slot_duration=30,
                 timezone="Asia/Kolkata", contact_email="", location=""):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO businesses
                (id, name, type, services, working_days, start_time, end_time,
                 slot_duration, timezone, contact_email, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name=EXCLUDED.name, type=EXCLUDED.type,
                    services=EXCLUDED.services, working_days=EXCLUDED.working_days,
                    start_time=EXCLUDED.start_time, end_time=EXCLUDED.end_time,
                    slot_duration=EXCLUDED.slot_duration, timezone=EXCLUDED.timezone,
                    contact_email=EXCLUDED.contact_email,
                    location=EXCLUDED.location
            """, (business_id, name, business_type, json.dumps(services),
                  json.dumps(working_days), start_time, end_time,
                  slot_duration, timezone, contact_email, location))
        conn.commit()


def get_business(business_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM businesses WHERE id = %s", (business_id,))
            row = cur.fetchone()
            if row:
                d = dict(row)
                d["services"] = json.loads(d["services"])
                d["working_days"] = json.loads(d["working_days"])
                return d
            return None


def get_all_businesses():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, name, type FROM businesses")
            return [dict(r) for r in cur.fetchall()]


def add_booking(business_id, customer_name, customer_phone,
                customer_email, service, appointment_datetime):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO bookings
                (business_id, customer_name, customer_phone, customer_email,
                 service, appointment_datetime)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (business_id, customer_name, customer_phone,
                  customer_email, service, appointment_datetime))
            booking_id = cur.fetchone()[0]
        conn.commit()
        return booking_id


def is_slot_taken(business_id, appointment_datetime):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id FROM bookings
                WHERE business_id = %s AND appointment_datetime = %s AND status = 'confirmed'
            """, (business_id, appointment_datetime))
            return cur.fetchone() is not None


def get_bookings_for_date(business_id, date_str):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM bookings
                WHERE business_id = %s AND appointment_datetime LIKE %s AND status = 'confirmed'
            """, (business_id, f"{date_str}%"))
            return [dict(r) for r in cur.fetchall()]


def set_client_password(business_id, password):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE businesses SET client_password = %s WHERE id = %s",
                (password, business_id)
            )
        conn.commit()


def set_call_mode(business_id, call_mode, twilio_number=""):
    """Update call mode and twilio number for a business."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE businesses SET call_mode = %s, twilio_number = %s WHERE id = %s",
                (call_mode, twilio_number, business_id)
            )
        conn.commit()


def migrate_call_mode_columns():
    """Add call_mode, twilio_number, and location columns if they don't exist."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                ALTER TABLE businesses
                ADD COLUMN IF NOT EXISTS call_mode TEXT DEFAULT 'always'
            """)
            cur.execute("""
                ALTER TABLE businesses
                ADD COLUMN IF NOT EXISTS twilio_number TEXT DEFAULT ''
            """)
            cur.execute("""
                ALTER TABLE businesses
                ADD COLUMN IF NOT EXISTS location TEXT DEFAULT ''
            """)
        conn.commit()


def cancel_booking(booking_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE bookings SET status = 'cancelled' WHERE id = %s", (booking_id,)
            )
        conn.commit()


def get_booking_by_phone(business_id, phone):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM bookings
                WHERE business_id = %s AND customer_phone = %s AND status = 'confirmed'
                ORDER BY id DESC LIMIT 1
            """, (business_id, phone))
            row = cur.fetchone()
            return dict(row) if row else None


def get_all_bookings(business_id=None, status=None, search=None):
    query = "SELECT * FROM bookings WHERE 1=1"
    params = []
    if business_id:
        query += " AND business_id = %s"
        params.append(business_id)
    if status:
        query += " AND status = %s"
        params.append(status)
    if search:
        query += " AND (customer_name LIKE %s OR customer_phone LIKE %s)"
        params += [f"%{search}%", f"%{search}%"]
    query += " ORDER BY id DESC"
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]


def update_business_schedule(business_id, working_days, start_time, end_time, slot_duration):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE businesses
                SET working_days = %s, start_time = %s, end_time = %s, slot_duration = %s
                WHERE id = %s
            """, (json.dumps(working_days), start_time, end_time, int(slot_duration), business_id))
        conn.commit()


def add_leave(business_id, date, reason=''):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO leaves (business_id, date, reason)
                VALUES (%s, %s, %s)
                ON CONFLICT (business_id, date) DO UPDATE SET reason = EXCLUDED.reason
            """, (business_id, date, reason))
        conn.commit()


def get_leaves(business_id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM leaves WHERE business_id = %s ORDER BY date ASC",
                (business_id,)
            )
            return [dict(r) for r in cur.fetchall()]


def delete_leave(leave_id, business_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM leaves WHERE id = %s AND business_id = %s",
                (leave_id, business_id)
            )
        conn.commit()


def is_leave_day(business_id, date_str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM leaves WHERE business_id = %s AND date = %s",
                (business_id, date_str)
            )
            return cur.fetchone() is not None


def get_dashboard_stats(business_id=None):
    today     = datetime.now().strftime("%Y-%m-%d")
    week_ago  = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    biz_filter = "AND business_id = %s" if business_id else ""
    base_params = [business_id] if business_id else []

    def count(extra_where, extra_params):
        q = f"SELECT COUNT(*) FROM bookings WHERE status='confirmed' {biz_filter} {extra_where}"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(q, base_params + extra_params)
                return cur.fetchone()[0]

    return {
        "today":    count("AND appointment_datetime LIKE %s", [f"{today}%"]),
        "week":     count("AND appointment_datetime >= %s",   [week_ago]),
        "month":    count("AND appointment_datetime >= %s",   [month_ago]),
        "all_time": count("", []),
    }
