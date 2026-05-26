# 🤖 AI Voice Receptionist

A fully offline, multi-tenant AI Voice Receptionist SaaS platform that handles real phone calls, understands natural speech, books appointments, and provides a full booking management dashboard — powered by a rule-based AI engine + Twilio. No cloud AI fees. No per-request costs.

---

## 🎯 What It Does

- Answers real phone calls on a Twilio number 24/7
- Greets callers naturally and understands their intent via voice
- Books, reschedules, and cancels appointments through conversation
- Checks real-time slot availability — no double bookings
- Confirms details with the caller before saving
- Supports multiple businesses (dental, salon, barber, clinic) from one server
- Works via browser phone — no physical phone needed
- Admin dashboard to manage all businesses and bookings
- Per-client dashboard — each business owner sees only their own bookings

---

## 🏗️ Architecture Overview

```
Caller speaks (browser or real phone)
        ↓
Twilio — speech → text (STT built into Twilio)
        ↓
Twilio sends text to Flask server via HTTPS webhook (ngrok tunnel)
        ↓
receptionist.py — conversation state machine
        ↓
brain.py — rule-based engine (templates + regex, no LLM needed)
        ↓
Flask returns TwiML → Twilio speaks reply back (TTS built into Twilio)
        ↓
Booking saved to SQLite via slot_manager.py
        ↓
React dashboard shows booking in real time
```

---

## 🧰 Tech Stack

### AI / Intelligence
| Tool | Purpose |
|---|---|
| **brain.py** | Custom rule-based AI engine — response templates + regex extraction. Zero dependencies, instant responses |
| **Response Templates** | Pre-written natural-sounding responses with random variation so it never sounds robotic |
| **Regex Extraction** | Extracts intent, service, date, time, name, phone from caller speech without any LLM |

> Previously used Ollama + LLaMA 3.2. Replaced with brain.py for instant responses and VPS compatibility (no GPU needed).

### Phone / Voice
| Tool | Purpose |
|---|---|
| **Twilio** | Handles real phone calls, built-in STT and TTS |
| **TwiML** | XML instructions telling Twilio what to say, when to listen, when to hang up |
| **Twilio Voice JS SDK v2.18.3** | JavaScript SDK — turns the browser into a WebRTC phone |
| **ngrok** | HTTPS tunnel to expose local server to Twilio |

### Web Server (Backend)
| Tool | Purpose |
|---|---|
| **Flask** | Python web server — Twilio webhooks + admin/client API |
| **flask-cors** | Allows React app to make cross-origin API requests |
| **gunicorn** | Production WSGI server for deployment |
| **python-dotenv** | Loads `.env` config into environment variables |

### Frontend (React Dashboard)
| Tool | Purpose |
|---|---|
| **React 18** | Component-based UI framework |
| **Vite** | Fast build tool and dev server |
| **Vanilla CSS** | No CSS framework — clean custom styles |
| **fetch API** | API calls to Flask backend with Bearer token auth |

### Data
| Tool | Purpose |
|---|---|
| **SQLite** | Local database — businesses + bookings (built into Python) |
| **DB Browser for SQLite** | Desktop GUI to inspect raw database |

---

## 📁 Backend Project Structure

```
VoiceAssistantAI/
├── server.py            # Flask server — Twilio webhooks + Admin/Client API routes
├── receptionist.py      # Conversation state machine (greeting → intent → book → confirm)
├── brain.py             # Rule-based AI — response templates + regex data extraction
├── database.py          # All SQLite operations (businesses, bookings, stats)
├── slot_manager.py      # Slot generation, availability check, booking logic
├── notifier.py          # Email confirmation via Gmail SMTP (optional)
├── assistant.py         # Local mic-based voice assistant (Whisper + macOS TTS)
├── setup_business.py    # CLI to add/list businesses and set client passwords
├── view_bookings.py     # CLI to view all bookings per business
├── browser_phone.html   # Browser WebRTC phone UI (served by Flask)
├── admin.html           # HTML admin dashboard (served by Flask)
├── admin_login.html     # HTML admin login page
├── static/
│   └── twilio.min.js    # Twilio Voice JS SDK (local copy — no CDN needed)
├── Procfile             # Railway/Render/Heroku deployment command
├── runtime.txt          # Python version for deployment
├── requirements.txt     # Python dependencies
├── need.md              # Remaining work tracker
├── .env                 # API keys and config (never commit this)
└── receptionist.db      # SQLite database (auto-created)
```

## 📁 React Dashboard Structure

```
receptionist-admin/              (on Desktop)
├── src/
│   ├── App.jsx                  # Root — handles login state, admin vs client routing
│   ├── api.js                   # All API calls + token storage in localStorage
│   ├── index.css                # All styles
│   └── components/
│       ├── Login.jsx            # 3-screen login: choice → admin or client
│       ├── Sidebar.jsx          # Business list sidebar (admin only)
│       ├── StatsCards.jsx       # Today / Week / Month / All-time stats
│       ├── BookingsTable.jsx    # Table with search, filter, cancel button
│       └── Dashboard.jsx        # Main layout — combines all components
├── vite.config.js               # Vite config + proxy to Flask on port 5001
└── package.json
```

---

## ⚙️ Prerequisites

- macOS (M1/M2/M3)
- Python 3.11+
- Node.js 18+
- [ngrok](https://ngrok.com) account + CLI
- [Twilio](https://twilio.com) account with a phone number

---

## 🚀 Installation

### 1. Clone the repo
```bash
git clone https://github.com/tanuj-dev/voiceasistance.git
cd voiceasistance
```

### 2. Python setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure `.env`
```env
# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# Twilio API Key (for browser calling)
TWILIO_API_KEY_SID=your_api_key_sid
TWILIO_API_KEY_SECRET=your_api_key_secret
TWIML_APP_SID=your_twiml_app_sid

# Phone number → Business ID mapping
PHONE_MAP=+12394238893:tanuj_dental

# Fallback if number not in map
DEFAULT_BUSINESS_ID=tanuj_dental

# Admin dashboard password
ADMIN_PASSWORD=your_admin_password
SECRET_KEY=your-random-secret-key

# Server port
PORT=5001

# Optional: persistent DB path (for Railway/VPS)
# DB_PATH=/data/receptionist.db

# Optional: email confirmations
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### 4. Seed the database
```bash
python setup_business.py
```

### 5. React dashboard setup
```bash
cd ~/Desktop/receptionist-admin
npm install
```

---

## ▶️ Running (Development)

Open **3 terminals:**

```bash
# Terminal 1 — Flask backend
cd ~/Desktop/VoiceAssistantAI
source venv/bin/activate
python server.py

# Terminal 2 — ngrok tunnel
ngrok http 5001

# Terminal 3 — React dashboard
cd ~/Desktop/receptionist-admin
npm run dev
```

Then update Twilio webhooks with the ngrok URL (see below).

---

## 🔗 Configure Twilio Webhooks

After starting ngrok, go to [Twilio Console](https://console.twilio.com) → Phone Numbers → your number:

| Field | Value |
|---|---|
| A call comes in | `https://YOUR_NGROK_URL/voice/answer` |
| Call status changes | `https://YOUR_NGROK_URL/voice/status` |

> ⚠️ ngrok URL changes every restart on the free plan. Redo this step each time.

---

## 🌐 Browser Phone (Test Calls)

Since Indian users can't call US Twilio numbers directly:

1. Open → `http://localhost:5001/phone`
2. Wait for **"Ready to call ✅"**
3. Click **📞 Call Now**
4. Speak to the AI receptionist

---

## 🗓️ Conversation Flow

```
Call comes in
    ↓ Greeting
    ↓ Detect intent  →  book / cancel / reschedule / info
    ↓ Ask service    →  (skipped if only one service)
    ↓ Ask date
    ↓ Fetch & show available slots
    ↓ Ask preferred time
    ↓ Validate time against real slots
    ↓ Ask name
    ↓ Ask phone number
    ↓ Read back summary — "Is this correct?"
    ↓ Caller says yes → save booking to DB
    ↓ Confirm booking ID → goodbye
```

---

## 🧠 brain.py — Rule-Based AI Engine

Replaced Ollama/Groq entirely. Zero external dependencies.

### Response Templates
```python
brain.reply("show_slots", date="Wednesday, May 27", slots="10:00 AM, 10:30 AM, 11:00 AM")
# → "For Wednesday, May 27, the available times are 10:00 AM, 10:30 AM, 11:00 AM. Which do you prefer?"
```

Multiple variants per key — randomly chosen to sound natural.

### Data Extraction
```python
brain.extract("I want to book a cleaning for tomorrow at 10 AM", services=["Cleaning", "Filling"])
# → { intent: "book", service: "Cleaning", date: "2026-05-27", time: "10:00 AM", name: None, phone: None }
```

Extracts:
- **Intent** — keyword matching (book, cancel, reschedule, info)
- **Service** — exact match + fuzzy match against business services
- **Date** — today, tomorrow, day names (Monday/Tuesday...), DD/MM/YYYY, "26th May"
- **Time** — 12-hour (10 AM, 10:30 AM), 24-hour (14:30)
- **Name** — "my name is X" pattern + capitalised word detection
- **Phone** — extracts 10 consecutive digits from any format

---

## 🔐 Admin & Client Dashboard

### Access

| Who | URL | Login |
|---|---|---|
| Admin | `http://localhost:3001` → Admin | `ADMIN_PASSWORD` from .env |
| Business Owner | `http://localhost:3001` → Business Owner | Business ID + their password |

### Admin Dashboard
- Sees **all businesses** with sidebar to switch
- Stats: Today / This Week / This Month / All Time
- Full booking table with search, status filter
- Cancel any booking
- Auto-refreshes every 30 seconds

### Client Dashboard (per business)
- Sees **only their own bookings** — other businesses are invisible
- Same stats and filters, scoped to their business
- Can cancel their own bookings only
- Server enforces the restriction — not just UI

### Auth Flow
```
Login → POST /admin/api/login or /client/api/login
      → Returns signed JWT-style token
      → Stored in localStorage
      → Sent as Authorization: Bearer <token> on every request
      → Server verifies signature + checks role
```

---

## 📋 API Routes

### Twilio Voice Webhooks
| Route | Method | Description |
|---|---|---|
| `/voice/answer` | POST | New call — returns greeting TwiML |
| `/voice/gather` | POST | After caller speaks — processes speech, returns response |
| `/voice/no_input` | POST | Caller silent — re-prompts |
| `/voice/status` | POST | Call ended — cleanup |
| `/token` | GET | Twilio Access Token for browser calling |
| `/phone` | GET | Browser phone HTML UI |
| `/health` | GET | Server status, active calls, business count |

### Admin API (requires admin token)
| Route | Method | Description |
|---|---|---|
| `/admin/api/login` | POST | Admin login → returns token |
| `/admin/api/businesses` | GET | List all businesses |
| `/admin/api/stats` | GET | Booking counts (today/week/month/all) |
| `/admin/api/bookings` | GET | All bookings with optional filters |
| `/admin/api/bookings/:id/cancel` | POST | Cancel a booking |

### Client API (requires client token — scoped to one business)
| Route | Method | Description |
|---|---|---|
| `/client/api/login` | POST | Client login → returns scoped token |
| `/client/api/stats` | GET | Stats for their business only |
| `/client/api/bookings` | GET | Bookings for their business only |
| `/client/api/bookings/:id/cancel` | POST | Cancel (only their own bookings) |

---

## 🏢 Multi-Tenant Setup

One server handles unlimited businesses. Each gets its own phone number and client login.

### Add a new business
```bash
python setup_business.py
# Follow the prompts to add name, services, hours, etc.
```

### Set client login password
```python
import database
database.set_client_password('business_id', 'their_password')
```

### Map phone number to business
In `.env`:
```env
PHONE_MAP=+12394238893:tanuj_dental,+14071234567:glow_salon,+15551234567:sharp_cuts
```

---

## 📊 Database Schema

### `businesses` table
| Column | Type | Description |
|---|---|---|
| id | TEXT | Unique business ID (e.g. `tanuj_dental`) |
| name | TEXT | Display name |
| type | TEXT | Business type (dental, salon, etc.) |
| services | TEXT | JSON array of services |
| working_days | TEXT | JSON array of working days |
| start_time | TEXT | Opening time (HH:MM) |
| end_time | TEXT | Closing time (HH:MM) |
| slot_duration | INT | Minutes per appointment |
| timezone | TEXT | Timezone (default: Asia/Kolkata) |
| contact_email | TEXT | For booking confirmations |
| client_password | TEXT | Password for client dashboard login |

### `bookings` table
| Column | Type | Description |
|---|---|---|
| id | INT | Auto-increment booking ID |
| business_id | TEXT | Which business this booking is for |
| customer_name | TEXT | Caller's name |
| customer_phone | TEXT | Caller's phone number |
| customer_email | TEXT | Optional email |
| service | TEXT | Service booked |
| appointment_datetime | TEXT | YYYY-MM-DD HH:MM |
| status | TEXT | confirmed / cancelled |
| created_at | TEXT | When booking was made |

---

## 👁️ View Bookings (CLI)

```bash
python view_bookings.py
```

Output:
```
=== Tanuj Dental Clinic ===
ID  Name     Phone       Service   Date        Time     Status
1   Tanuj    9876543210  Cleaning  2026-05-27  10:30    confirmed
2   Rahul    9123456789  Filling   2026-05-28  11:00    confirmed
```

---

## 🚀 Deployment (Railway)

### 1. Push to GitHub
```bash
git push origin main
```

### 2. Deploy on Railway
- Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
- Select the repo — Railway auto-detects `Procfile`

### 3. Set environment variables
Add all variables from `.env` in Railway dashboard.

### 4. Add persistent volume
Mount path: `/data` → set `DB_PATH=/data/receptionist.db` in env vars.

### 5. Seed database
In Railway shell: `python setup_business.py`

### 6. Update Twilio webhooks
Replace ngrok URL with your Railway URL:
```
https://your-app.up.railway.app/voice/answer
https://your-app.up.railway.app/voice/status
```

---

## 💰 Cost Breakdown

| Component | Cost |
|---|---|
| brain.py AI engine | Free — pure Python |
| SQLite database | Free — built into Python |
| Flask server | Free |
| ngrok (free tier) | Free (URL changes on restart) |
| Railway hosting | $5/month (fixed URL, 24/7 uptime) |
| Twilio phone number | ~$1.15/month |
| Twilio calls | ~$0.013/min (inbound) |
| **Total per client** | **~₹580/month** |
| **You charge client** | **₹1,499–4,999/month** |
| **Your profit** | **₹900–4,400/month per client** |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| "Ready to call" never shows | Hard reload: `Cmd + Shift + R` |
| "Twilio is not defined" | Check `static/twilio.min.js` exists |
| AI doesn't answer call | Check ngrok URL is updated in Twilio console |
| Port 5001 in use | `lsof -i :5001` then `kill -9 <PID>` |
| ngrok URL expired | Restart ngrok → update Twilio webhooks |
| React dashboard 401 error | Clear localStorage and log in again |
| Client can't log in | Run `database.set_client_password('biz_id', 'password')` |
| Internal server error | Check `/tmp/server.log` for traceback |
| DB not persisting on Railway | Set `DB_PATH=/data/receptionist.db` + add volume |

---

## 📋 Remaining Work (see need.md for details)

- [ ] Move to VPS / Railway (24/7, no Mac dependency)
- [ ] Exotel integration — Indian phone numbers
- [ ] Booking cancellation via voice (detected but DB update missing)
- [ ] Reschedule flow via voice
- [ ] SMS/Email confirmation to customer after booking
- [ ] Razorpay — automated monthly billing per client
- [ ] WhatsApp booking channel
- [ ] Google Calendar sync
- [ ] Hindi language support
- [ ] Multi-location support (chains)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

Built with Python, Flask, React, Twilio, and SQLite.
