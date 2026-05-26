"""
CLI tool to add and manage businesses in the receptionist system.
Run: python setup_business.py
"""
import sys
import database

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def prompt(label, default=None):
    suffix = f" [{default}]" if default else ""
    value = input(f"{label}{suffix}: ").strip()
    return value if value else default


def add_business_interactive():
    print("\n--- Add New Business ---\n")

    business_id = prompt("Business ID (unique slug, e.g. dental_001)").lower().replace(" ", "_")
    name = prompt("Business name (e.g. Bright Smile Dental Clinic)")
    business_type = prompt("Business type (e.g. dental, barber, salon, clinic)")

    print("\nServices offered (comma-separated, e.g. Cleaning, Filling, Whitening):")
    services_raw = prompt("Services")
    services = [s.strip() for s in services_raw.split(",") if s.strip()]

    print("\nWorking days — enter numbers separated by commas:")
    for i, d in enumerate(DAYS_OF_WEEK, 1):
        print(f"  {i}. {d}")
    days_input = prompt("Days (e.g. 1,2,3,4,5,6 for Mon–Sat)", default="1,2,3,4,5,6")
    working_days = []
    for n in days_input.split(","):
        try:
            idx = int(n.strip()) - 1
            if 0 <= idx < len(DAYS_OF_WEEK):
                working_days.append(DAYS_OF_WEEK[idx])
        except ValueError:
            pass

    start_time = prompt("Opening time (HH:MM, 24h)", default="09:00")
    end_time = prompt("Closing time (HH:MM, 24h)", default="18:00")
    slot_duration = int(prompt("Appointment slot duration in minutes", default="30"))
    timezone = prompt("Timezone", default="Asia/Kolkata")
    contact_email = prompt("Business contact email (for sending confirmations)", default="")

    print(f"""
--- Summary ---
ID       : {business_id}
Name     : {name}
Type     : {business_type}
Services : {', '.join(services)}
Days     : {', '.join(working_days)}
Hours    : {start_time} – {end_time}
Slot     : {slot_duration} min
Timezone : {timezone}
Email    : {contact_email or '(none)'}
""")

    confirm = input("Save this business? (yes/no): ").strip().lower()
    if confirm == "yes":
        database.create_tables()
        database.add_business(
            business_id, name, business_type, services,
            working_days, start_time, end_time,
            slot_duration, timezone, contact_email
        )
        print(f"\nBusiness '{name}' saved with ID '{business_id}'.")
    else:
        print("Cancelled.")


def list_businesses():
    database.create_tables()
    businesses = database.get_all_businesses()
    if not businesses:
        print("\nNo businesses registered yet.\n")
        return
    print(f"\n{'ID':<20} {'Name':<35} {'Type'}")
    print("-" * 65)
    for b in businesses:
        print(f"{b['id']:<20} {b['name']:<35} {b['type']}")
    print()


def seed_samples():
    """Add sample businesses for quick testing."""
    database.create_tables()
    samples = [
        {
            "id": "dental_001",
            "name": "Bright Smile Dental Clinic",
            "type": "dental",
            "services": ["Cleaning", "Filling", "Root Canal", "Whitening", "Extraction"],
            "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "start_time": "09:00",
            "end_time": "18:00",
            "slot_duration": 30,
        },
        {
            "id": "barber_001",
            "name": "Sharp Cuts Barber Shop",
            "type": "barber",
            "services": ["Haircut", "Beard Trim", "Shave", "Hair Color"],
            "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "start_time": "10:00",
            "end_time": "20:00",
            "slot_duration": 20,
        },
        {
            "id": "salon_001",
            "name": "Glow Beauty Salon",
            "type": "salon",
            "services": ["Haircut", "Facial", "Manicure", "Pedicure", "Waxing"],
            "working_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "start_time": "10:00",
            "end_time": "19:00",
            "slot_duration": 45,
        },
    ]
    for s in samples:
        database.add_business(
            s["id"], s["name"], s["type"], s["services"],
            s["working_days"], s["start_time"], s["end_time"],
            s["slot_duration"]
        )
        print(f"Added: {s['name']}")
    print("\nSample businesses added.")


def main():
    print("=" * 50)
    print("  Voice Receptionist — Business Manager")
    print("=" * 50)
    print("  1. Add new business")
    print("  2. List all businesses")
    print("  3. Add sample businesses (for testing)")
    print("  4. Exit")
    print("=" * 50)

    choice = input("Choose: ").strip()
    if choice == "1":
        add_business_interactive()
    elif choice == "2":
        list_businesses()
    elif choice == "3":
        seed_samples()
    elif choice == "4":
        sys.exit(0)
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
