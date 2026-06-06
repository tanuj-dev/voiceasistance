# 📋 Remaining Work — AI Voice Receptionist

Everything that is pending, prioritized by what blocks real client delivery first.

---

## 🔴 Priority 1 — Must Have Before First Client

### 1. Move Server to VPS (Not Local Mac)
- **Why:** Right now the server only works when your Mac is ON. Clients need 24/7 uptime.
- **What to do:**
  - Rent a VPS — DigitalOcean Droplet or AWS EC2 (cheapest ~$6/month)
  - Copy project files to VPS
  - Install Python, Ollama, llama3.2:3b on the VPS
  - Run `python server.py` as a background service (systemd or screen)
  - Point Twilio webhooks to the VPS IP directly (no ngrok needed anymore)
- **Status:** ❌ Not started

### 2. Replace ngrok with a Fixed Domain
- **Why:** ngrok URL changes every restart. Twilio webhooks break every time.
- **What to do:**
  - Option A: Use VPS public IP directly (free, no ngrok needed)
  - Option B: Buy a domain (~₹700/year) and point it to VPS
  - Update Twilio webhook URLs to the fixed domain — done once, never again
- **Status:** ❌ Not started

### 3. Exotel KYC — Indian Phone Numbers
- **Why:** Twilio US numbers can't be called from Indian mobile phones directly. Exotel gives Indian (+91) numbers.
- **What to do:**
  - Complete KYC at https://my.exotel.com/self6649
  - Submit: Aadhaar / PAN + business proof
  - Wait 2–3 days for approval
  - Buy an Indian virtual number from Exotel dashboard
  - Integrate Exotel webhooks into `server.py` (similar to Twilio but different API)
- **Status:** ⏳ KYC not submitted yet

### 4. Payment Collection Setup
- **Why:** You need to auto-collect monthly fees from clients.
- **What to do:**
  - Create Razorpay account (free) → razorpay.com
  - Set up subscription plans matching your pricing (Starter / Growth / Pro)
  - Send clients a Razorpay payment link each month
  - Optional later: auto-debit via Razorpay subscriptions API
- **Status:** ❌ Not started

---

## 🟡 Priority 2 — Needed for Good Client Experience

### 5. SMS / Email Confirmation After Booking
- **Status:** ✅ Done — `_finalise()` fires `notifier.notify_owner()` (email to owner) + `notifier.send_sms_confirmation()` (SMS to customer) in a background thread. `.env` has real Gmail + Twilio credentials.

### 6. Booking Cancellation Flow
- **Status:** ✅ Done — `_route()` handles cancel: asks for phone, looks up booking via `database.get_booking_by_phone()`, calls `database.cancel_booking()`, confirms to caller, fires owner email + customer SMS in background.

### 7. Reschedule Flow
- **Status:** ✅ Done (commit `5b2353b`) — Full `_handle_reschedule()` + `_finalise_reschedule()` added. Flow: asks phone → finds old booking → shows old details → collects new date/time → confirms → cancels old + creates new atomically → owner email + customer SMS fired in background.

### 8. Admin Dashboard (Web UI)
- **Why:** Salon owner needs to see their bookings without calling you.
- **What to do:**
  - Build a simple Flask web page at `/dashboard`
  - Login with a password (one per business)
  - Show table of upcoming bookings (date, time, customer name, service, status)
  - Add buttons to cancel/confirm a booking manually
- **Status:** ❌ Not started

---

## 🟢 Priority 3 — Nice to Have (Growth Features)

### 9. WhatsApp Booking Channel
- **Why:** Many customers prefer WhatsApp over phone calls in India.
- **What to do:**
  - Use Twilio WhatsApp sandbox or Gupshup API
  - Plug the same `Receptionist` class into a WhatsApp message handler
  - Same AI logic works — just text instead of voice
- **Status:** ❌ Not started

### 10. Google Calendar Sync
- **Why:** Business owner wants bookings to appear in their Google Calendar automatically.
- **What to do:**
  - Integrate Google Calendar API (OAuth 2.0)
  - On `_finalise()`, create a calendar event for the booking
  - Share the calendar with the business owner's Gmail
- **Status:** ❌ Not started

### 11. Hindi / Regional Language Support
- **Why:** Huge market in Tier 2 / Tier 3 cities where English is not comfortable.
- **What to do:**
  - Twilio Gather supports `language="hi-IN"` (Hindi STT)
  - Change `gather.say()` voice to a Hindi voice (`language="hi-IN"`)
  - Update Ollama prompt to respond in Hindi
  - Add a `language` field per business in the DB
- **Status:** ❌ Not started

### 12. Multi-Location Support
- **Why:** Chain businesses (e.g. salon with 3 branches) need one system for all locations.
- **What to do:**
  - Add `location` field to businesses table
  - Map one phone number per branch
  - Dashboard shows all branches with filters
- **Status:** ❌ Not started

### 13. Call Recording + Transcript Logs
- **Why:** Business owner can review calls, catch AI mistakes, improve service.
- **What to do:**
  - Enable Twilio call recording (one flag in TwiML)
  - Save transcript (speech text) to DB alongside booking
  - Show in dashboard under each booking
- **Status:** ❌ Not started

---

## 🔧 Tech Debt / Cleanup

| Item | What to Fix |
|---|---|
| Push latest code to GitHub | ✅ Done — all code pushed to tanuj-dev/voiceasistance |
| `requirements.txt` is incomplete | ✅ Done — has flask-cors, reportlab, psycopg2-binary, groq, gunicorn |
| No error logging | Add Python `logging` module — write errors to a log file so you can debug client issues |
| `.env` has real credentials | Should never be committed — double-check `.gitignore` has `.env` |
| `notifier.py` silently skips | Add a visible warning if email is not configured so you notice during setup |
| No health check alerts | Add uptime monitoring (UptimeRobot — free) so you know if your server goes down |

---

## ✅ Already Done

- [x] Local AI voice assistant (Whisper + Ollama + macOS say)
- [x] Multi-tenant SQLite database (businesses + bookings)
- [x] Slot manager (availability check, conflict prevention, booking)
- [x] Flask server with all Twilio webhook routes
- [x] Booking flow end-to-end (service → date → slot → name → phone → confirm → save)
- [x] Browser phone UI (Twilio Voice JS SDK, served locally)
- [x] Twilio number purchased (+1 239 423 8893)
- [x] Browser calling working (token endpoint, WebRTC)
- [x] CORS fix (flask-cors added)
- [x] Twilio SDK served locally (no CDN dependency)
- [x] README.md written
- [x] Business proposal PDF generated

---

## 📅 Suggested Order to Complete

```
Week 1  →  VPS setup + fixed domain + Exotel KYC submission
Week 2  →  Exotel integration + SMS/Email confirmation + cancellation fix
Week 3  →  Admin dashboard (basic) + Razorpay payment setup
Week 4  →  First paying client onboarded and live
Month 2 →  WhatsApp channel + reschedule flow + Google Calendar
Month 3 →  Hindi language + multi-location + call transcripts
```
