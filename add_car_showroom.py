"""
One-time script to add Premier Cars Showroom to the live database.
Run: python add_car_showroom.py
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

import database

database.create_tables()
database.migrate_call_mode_columns()  # also adds location column

database.add_business(
    business_id   = "premier_cars",
    name          = "Premier Cars Showroom",
    business_type = "carshowroom",
    services      = [
        "Maruti Swift",
        "Hyundai Creta",
        "Tata Nexon",
        "Honda City",
        "Toyota Fortuner",
        "Mahindra Scorpio",
    ],
    working_days  = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    start_time    = "10:00",
    end_time      = "19:00",
    slot_duration = 45,
    timezone      = "America/New_York",
    contact_email = "hello@ringreply.in",
    location      = "42 Auto Plaza Drive, Suite 1, Tampa, FL 33601, USA",
)

# Set the same Twilio number and call mode
database.set_call_mode("premier_cars", "always", "+12394238893")

print("✅ Premier Cars Showroom added successfully!")
print("   ID       : premier_cars")
print("   Number   : +1 (239) 423-8893")
print("   Location : 42 Auto Plaza Drive, Suite 1, Tampa, FL 33601, USA")
print("   Models   : Maruti Swift, Hyundai Creta, Tata Nexon, Honda City,")
print("              Toyota Fortuner, Mahindra Scorpio")
print("   Hours    : Mon–Sat, 10:00 AM – 7:00 PM")
