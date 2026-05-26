# 🦷 AI Voice Receptionist

A fully local, multi-tenant AI Voice Receptionist that handles real phone calls, understands natural speech, and books appointments — powered by Ollama (LLaMA 3.2) + Twilio. No cloud AI fees, no per-request costs.

---

## 🎯 What It Does

- Answers real phone calls on your Twilio number
- Greets callers naturally and understands their intent
- Books, reschedules, or cancels appointments via voice
- Checks available slots in real time and avoids double-booking
- Confirms booking details before saving
- Supports multiple businesses (dental, barber, salon, etc.) from one server
- Works via browser phone (no physical phone needed)

---

## 🏗️ Architecture Overview

```
Caller speaks (browser or real phone)
        ↓
Twilio — captures audio, converts speech → text (STT)
        ↓
Twilio sends text to Flask server via webhook (tunneled through ngrok)
        ↓
receptionist.py — conversation state machine
        ↓
Ollama (LLaMA 3.2 3B) — understands intent, extracts data, generates reply
        ↓
Flask returns TwiML → Twilio speaks reply back to caller (TTS)
        ↓
Booking saved to SQLite database via slot_manager.py
```

---

## 🧰 Tech Stack

### AI / Intelligence
| Tool | Purpose |
|---|---|
| **Ollama** | Runs LLM locally on your machine — no API keys, no cost |
| **LLaMA 3.2 3B** | The language model — understands conversations, extracts name/date/time, generates natural replies |

### Phone / Voice
| Tool | Purpose |
|---|---|
| **Twilio** | Handles real phone calls, built-in STT (speech → text) and TTS (text → speech) |
| **TwiML** | XML instructions that tell Twilio what to say, when to listen, when to hang up |
| **Twilio Voice JS SDK v2.18.3** | JavaScript SDK — turns the browser into a phone via WebRTC |
| **ngrok** | Creates a public HTTPS tunnel to your localhost so Twilio can reach your server |

### Web Server
| Tool | Purpose |
|---|---|
| **Flask** | Python web server — receives Twilio webhooks, returns TwiML responses |
| **flask-cors** | Allows browser JS to make requests to Flask without CORS errors |
| **python-dotenv** | Loads `.env` file (API keys, config) into environment variables |

### Data
| Tool | Purpose |
|---|---|
| **SQLite** | Local database — stores businesses and bookings (built into Python, no setup needed) |

---

## 📁 Project Structure

```
VoiceAssistantAI/
├── server.py            # Flask server — all Twilio webhook routes
├── receptionist.py      # Core AI logic — conversation state machine
├── database.py          # SQLite DB operations (businesses + bookings)
├── slot_manager.py      # Slot generation, availability check, booking
├── notifier.py          # Email confirmation via Gmail SMTP (optional)
├── assistant.py         # Local voice assistant (mic + Whisper, no phone)
├── setup_business.py    # CLI to add / list businesses
├── view_bookings.py     # CLI to view booked appointments
├── browser_phone.html   # Browser-based phone UI (served by Flask)
├── static/
│   └── twilio.min.js    # Twilio Voice JS SDK (local copy, no CDN needed)
├── requirements.txt     # Python dependencies
├── .env                 # API keys and config (never commit this)
└── receptionist.db      # SQLite database file (auto-created)
```

---

## ⚙️ Prerequisites

- macOS (M1/M2/M3 recommended)
- Python 3.10+
- [Ollama](https://ollama.com) installed
- [ngrok](https://ngrok.com) account + CLI installed
- [Twilio](https://twilio.com) account with a phone number

---

## 🚀 Installation

### 1. Clone the repo
```bash
git clone https://github.com/tanuj-dev/voiceasistance.git
cd voiceasistance
```

### 2. Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
pip install flask-cors
```

### 4. Pull the AI model
```bash
ollama pull llama3.2:3b
```

### 5. Configure environment variables
Create a `.env` file in the project root:
```env
# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# Twilio API Key (for browser calling)
TWILIO_API_KEY_SID=your_api_key_sid
TWILIO_API_KEY_SECRET=your_api_key_secret
TWIML_APP_SID=your_twiml_app_sid

# Phone number → Business mapping
PHONE_MAP=+12394238893:tanuj_dental

# Fallback business if number not in map
DEFAULT_BUSINESS_ID=tanuj_dental

# Server port
PORT=5001

# Email notifications (optional)
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=your_app_password
```

### 6. Seed the database with a business
```bash
python setup_business.py
```

---

## ▶️ Running the Server

### Every time you start (3 terminals needed):

**Terminal 1 — Start Ollama**
```bash
ollama serve
```

**Terminal 2 — Start ngrok**
```bash
ngrok http 5001
```
Copy the `https://xxxx.ngrok-free.app` URL — you'll need it next.

**Terminal 3 — Start Flask**
```bash
source venv/bin/activate
python server.py
```

---

## 🔗 Configure Twilio Webhooks

After starting ngrok, update your Twilio number's webhook URLs:

1. Go to [Twilio Console](https://console.twilio.com) → Phone Numbers → Active Numbers
2. Click your number
3. Under **Voice Configuration** set:
   - **A call comes in:** `https://YOUR_NGROK_URL/voice/answer`
   - **Call status changes:** `https://YOUR_NGROK_URL/voice/status`
4. Save

> ⚠️ ngrok URL changes every restart on the free plan. Always redo this step.

---

## 🌐 Browser Phone

Since Indian users can't call US numbers directly, a browser-based WebRTC phone is included.

1. Open: `http://localhost:5001/phone`
2. Wait for **"Ready to call ✅"** (green)
3. Click **📞 Call Now**
4. Speak to the AI receptionist

---

## 📋 API Routes

| Route | Method | Description |
|---|---|---|
| `/voice/answer` | POST | Called when a new call comes in — returns greeting TwiML |
| `/voice/gather` | POST | Called after caller speaks — processes input, returns response TwiML |
| `/voice/no_input` | POST | Called when caller stays silent — re-prompts |
| `/voice/status` | POST | Called when call ends — cleans up session |
| `/token` | GET | Returns Twilio Access Token for browser calling |
| `/phone` | GET | Serves the browser phone HTML UI |
| `/health` | GET | Returns server status, active calls, businesses count |

---

## 🗓️ Conversation Flow

```
Incoming call
    → Greeting
    → Detect intent (book / cancel / reschedule / info)
    → Ask for service (if multiple options)
    → Ask for preferred date
    → Show available time slots
    → Ask for preferred time
    → Ask for name
    → Ask for phone number
    → Read back summary → ask to confirm
    → Save booking to DB
    → Thank caller and hang up
```

---

## 🏢 Multi-Tenant Support

One server handles multiple businesses. Map each Twilio number to a business ID in `.env`:

```env
PHONE_MAP=+12394238893:tanuj_dental,+10987654321:sharp_cuts_barber
```

Each business has its own:
- Name, type, services
- Working days and hours
- Slot duration
- Independent bookings

---

## 👁️ View Bookings

```bash
python view_bookings.py
```

Output:
```
=== Tanuj Dental Clinic ===
ID  Name        Phone       Service         Date        Time     Status
1   Tanuj        9876543210  Teeth Cleaning  2026-05-26  10:00 AM confirmed
```

---

## 🔧 Manage Businesses

```bash
python setup_business.py
```

Options:
- Add a new business
- List all businesses
- Seed sample data (Dental, Barber, Salon)

---

## 💰 Cost Breakdown

| Component | Cost |
|---|---|
| Ollama + LLaMA 3.2 | Free — runs locally |
| SQLite | Free — built into Python |
| Flask + ngrok (free tier) | Free |
| Twilio phone number | ~$1/month |
| Twilio per-minute call rate | ~$0.013/min (inbound) |

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| "Ready to call" never appears | Hard reload browser: `Cmd + Shift + R` |
| "Twilio is not defined" | Check `/static/twilio.min.js` exists and Flask is running |
| AI doesn't answer the call | Verify ngrok URL is updated in Twilio console |
| Greeting is empty / silent | Ensure `ollama serve` is running |
| Port 5001 already in use | `lsof -i :5001` then `kill -9 <PID>` |
| ngrok URL expired | Restart ngrok → update Twilio webhooks |

---

## 🔮 Roadmap

- [ ] Exotel integration (Indian phone numbers, no KYC delay)
- [ ] WhatsApp booking channel
- [ ] Email/SMS confirmation after booking
- [ ] Admin dashboard (view/manage bookings via web UI)
- [ ] Google Calendar sync
- [ ] Hindi language support

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

Built with ❤️ using Ollama, Twilio, and Flask.
