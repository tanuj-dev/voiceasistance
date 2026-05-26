"""
View all bookings for a business.
Run: python view_bookings.py
"""
import database


def show_bookings(business_id, business_name):
    import sqlite3
    conn = database.get_connection()
    rows = conn.execute("""
        SELECT id, customer_name, customer_phone, service,
               appointment_datetime, status, created_at
        FROM bookings
        WHERE business_id = ?
        ORDER BY appointment_datetime ASC
    """, (business_id,)).fetchall()
    conn.close()

    if not rows:
        print(f"\n  No bookings found for {business_name}.\n")
        return

    print(f"\n{'='*75}")
    print(f"  Bookings — {business_name}")
    print(f"{'='*75}")
    print(f"{'#':<5} {'Name':<20} {'Phone':<15} {'Service':<15} {'Date & Time':<20} {'Status'}")
    print("-" * 75)
    for r in rows:
        print(f"{r['id']:<5} {r['customer_name']:<20} {r['customer_phone']:<15} "
              f"{r['service']:<15} {r['appointment_datetime']:<20} {r['status']}")
    print(f"{'='*75}")
    print(f"  Total: {len(rows)} booking(s)\n")


def main():
    database.create_tables()
    businesses = database.get_all_businesses()

    if not businesses:
        print("\nNo businesses found.\n")
        return

    print("\n" + "=" * 50)
    print("  View Bookings")
    print("=" * 50)
    print("  0. All businesses")
    for i, b in enumerate(businesses, 1):
        print(f"  {i}. {b['name']}")
    print("=" * 50)

    choice = input("Choose: ").strip()

    if choice == "0":
        for b in businesses:
            show_bookings(b["id"], b["name"])
    else:
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(businesses):
                b = businesses[idx]
                show_bookings(b["id"], b["name"])
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
