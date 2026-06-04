# 🛠️ Tanuj's Complete Setup Guide — RingReply
> WhatsApp Bot + Call Forwarding — Step by Step
> Last updated: June 2026

---

## 📌 Quick Overview

| What | Status | Time Needed |
|---|---|---|
| Call Forwarding (Twilio US numbers) | ✅ Working | Ready now |
| WhatsApp Bot (Meta Cloud API) | ❌ Not set up | ~1 hour today |
| Indian Numbers (Exotel) | ⏳ KYC pending | After GST approved |
| Adding each client's existing WA number | ⏳ 3-7 days per client | Meta review |

---

---

# PART 1 — 📞 CALL FORWARDING SETUP
> Status: ✅ Working. Twilio number +1 239 423 8893 is live.

---

## Step 1 — For Each New Client (Call Only)

### 1A. Collect Client Details
Ask the client:
- Business name (exact — AI says this on every call)
- Business type (dental / salon / clinic / gym / other)
- Services offered (e.g. Haircut, Beard, Facial)
- Working days (e.g. Monday to Saturday)
- Opening time / Closing time
- Slot duration (30 min / 45 min / 1 hour)
- Owner email (for booking alerts)
- Shop address (AI tells callers when asked)
- Language: Hindi / English / Both

---

### 1B. Buy a Twilio Phone Number (~5 mins)

1. Go to → https://console.twilio.com
2. Left sidebar → Phone Numbers → Manage → Buy a Number
3. Search for a US number → buy one (~$1.15/month)
4. Go to the number's settings
5. Set webhook:
   - "A Call Comes In" → `https://web-production-851bb3.up.railway.app/voice/answer`
   - HTTP POST
6. Save

---

### 1C. Add Business to Database (~5 mins)

Run this curl command (replace values with client's details):

```bash
curl -X POST https://web-production-851bb3.up.railway.app/admin/api/businesses \
  -H "Authorization: Bearer tanuj123" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "sharma_dental",
    "name": "Sharma Dental Clinic",
    "type": "dental",
    "services": ["Cleaning", "Filling", "Root Canal"],
    "working_days": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],
    "start_time": "09:00",
    "end_time": "18:00",
    "slot_duration": 30,
    "contact_email": "client@gmail.com",
    "location": "Shop 4, MG Road, Delhi"
  }'
```

---

### 1D. Set Client Dashboard Password (~1 min)

```bash
curl -X POST https://web-production-851bb3.up.railway.app/admin/api/set-password \
  -H "Authorization: Bearer tanuj123" \
  -H "Content-Type: application/json" \
  -d '{"business_id": "sharma_dental", "password": "dental123"}'
```

---

### 1E. Map Twilio Number to Business (~2 mins)

1. Go to → https://railway.app
2. Open your project → web service → Variables tab
3. Find `PHONE_MAP` variable
4. Add the new number:
   ```
   +12394238893:tanuj_dental,+1XXXXXXXXXX:sharma_dental
   ```
5. Click Save → Railway auto-redeploys (~1 min)

---

### 1F. Send Forwarding Code to Client

Send this WhatsApp message to client:

```
Hi! To activate your RingReply AI receptionist, 
please dial this code from your business phone:

When busy:     **67*+91XXXXXXXXXX#
When no answer: **61*+91XXXXXXXXXX#

(Replace XXXXXXXXXX with your RingReply number)

This takes 10 seconds. After dialing, your AI 
receptionist will answer all missed calls automatically!
```

Carrier-specific codes (replace +91XXXXXXXXXX with client's RingReply number):

| Carrier | When Busy | When Not Answered |
|---|---|---|
| Airtel | **67*+91XXXXXXXXXX# | **61*+91XXXXXXXXXX# |
| Jio | **67*+91XXXXXXXXXX# | **61*+91XXXXXXXXXX# |
| Vi | **67*+91XXXXXXXXXX# | **61*+91XXXXXXXXXX# |
| BSNL | **67*+91XXXXXXXXXX# | **61*+91XXXXXXXXXX# |

---

### 1G. Test the Setup (~5 mins)

1. Call the client's RingReply number from your phone
2. AI should greet: "Hey, thanks for calling [Business Name]!"
3. Say "I want to book an appointment"
4. Complete the booking flow
5. Check dashboard: https://web-production-851bb3.up.railway.app/dashboard

---

### 1H. Hand Over to Client

Give client:
```
✅ Your RingReply number: +1 XXX XXX XXXX
✅ Dashboard URL: https://web-production-851bb3.up.railway.app/dashboard
✅ Your login ID: sharma_dental
✅ Your password: dental123
✅ Support: WhatsApp me at +91 9319801618
```

---

---

# PART 2 — 💬 WHATSAPP BOT SETUP (Meta Cloud API)
> Status: ❌ Not set up yet. Do these steps ONCE for RingReply.

---

## PHASE A — One-Time RingReply Setup (Do Once, ~1 hour)

---

### Step A1 — Create Meta Developer Account (~10 mins)

1. Go to → https://developers.facebook.com
2. Login with your Facebook account
3. Click "My Apps" → "Create App"
4. Select → "Business" type
5. App name: `RingReply`
6. App contact email: `hello@ringreply.in`
7. Click "Create App"

---

### Step A2 — Add WhatsApp to Your App (~5 mins)

1. Inside your new app → click "Add Product"
2. Find "WhatsApp" → click "Set Up"
3. You'll see "WhatsApp Business Platform" dashboard
4. It gives you a FREE TEST NUMBER automatically
   - Note this test number (looks like +1 555 XXXXXXX)
   - Note the Phone Number ID
   - Note the WhatsApp Business Account ID (WABA ID)

---

### Step A3 — Get Your Access Token (~5 mins)

1. In Meta Developer dashboard → your RingReply app
2. Left sidebar → WhatsApp → API Setup
3. You'll see "Temporary access token" — copy it
   - ⚠️ This expires in 24 hours — for production use permanent token (Step A6)
4. Save this token — you'll add it to Railway .env

---

### Step A4 — Add Env Variables to Railway (~5 mins)

Go to Railway → your project → Variables → Add these:

```
META_PHONE_NUMBER_ID = (from Step A2 — Phone Number ID)
META_ACCESS_TOKEN    = (from Step A3 — your token)
META_VERIFY_TOKEN    = ringreply2024
META_WABA_ID         = (from Step A2 — WABA ID)
```

Save → Railway redeploys automatically.

---

### Step A5 — Set Up Webhook (~5 mins)

1. Meta Developer dashboard → your app → WhatsApp → Configuration
2. Click "Edit" next to Webhook
3. Callback URL:
   ```
   https://web-production-851bb3.up.railway.app/whatsapp/meta
   ```
4. Verify Token:
   ```
   ringreply2024
   ```
5. Click "Verify and Save"
6. It should show ✅ green — means your server responded correctly
7. Under Webhook Fields → click "Manage" → subscribe to `messages`

---

### Step A6 — Create Permanent Access Token (~10 mins)

The temporary token expires in 24 hours. Create a permanent one:

1. Go to → https://business.facebook.com
2. Settings → System Users → Add
3. Name: `RingReply Bot`, Role: Admin
4. Click "Generate New Token"
5. Select your RingReply app
6. Permissions needed:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
7. Copy the token → update `META_ACCESS_TOKEN` in Railway

---

### Step A7 — Test with Meta Test Number (~10 mins)

Meta gives you a free test number. Add your personal number as a test recipient:

1. Meta Developer → WhatsApp → API Setup
2. Under "To" field → add your WhatsApp number (+91 9319801618)
3. Click "Send message" → you'll get a test message on your WhatsApp
4. Reply to that message → your bot should respond!

✅ If bot replies → WhatsApp bot is working!

---

## PHASE B — Adding Each Client's WhatsApp Number

---

### OPTION 1: New Dedicated WhatsApp Number for Client (1-2 days)

**When to use:** Client doesn't care about existing number, just wants WhatsApp bot.

#### Step B1-1 — Get a new SIM or virtual number
- Buy a new SIM (any carrier) OR
- Use Twilio virtual number (but requires WhatsApp Business API approval)

#### Step B1-2 — Register number on WhatsApp Business API
1. Meta Developer → your RingReply app → WhatsApp → Phone Numbers
2. Click "Add phone number"
3. Enter the new number
4. Verify via OTP
5. Wait for Meta approval: **1-3 days**

#### Step B1-3 — Add business to DB + map number
Same as Call Forwarding steps 1C, 1D, 1E above.
- For PHONE_MAP use: `whatsapp:+91XXXXXXXXXX:business_id`

#### Step B1-4 — Give client their WhatsApp number
Client promotes this number on:
- Google My Business
- Instagram bio
- Visiting cards
- Website

---

### OPTION 2: Client's Existing WhatsApp Number (3-14 days)

**When to use:** Client has an existing WhatsApp Business number with customers already using it.

#### ⚠️ BLOCKERS — Check these BEFORE starting:

| Check | If YES | If NO |
|---|---|---|
| Is number on personal WhatsApp? | Must delete personal WA account first — client loses all chats | ✅ OK |
| Is number on WhatsApp Business App? | Must delete WA Business App account — client loses all chats | ✅ OK |
| Does client have FB Business Manager? | ✅ OK | Must create one first |
| Is FB Business verified? | ✅ OK | Must submit verification docs |

#### Step B2-1 — Client creates Facebook Business Manager
1. Go to → https://business.facebook.com
2. Create account with business name and email
3. Add business documents for verification:
   - GST certificate OR
   - Shop & Establishment certificate OR
   - DPIIT certificate

#### Step B2-2 — Client deletes WhatsApp from their phone
⚠️ WARN CLIENT: They will lose all WhatsApp chats on that number.
1. Open WhatsApp on phone with the business number
2. Settings → Account → Delete Account
3. Confirm deletion
4. Wait 5 minutes

#### Step B2-3 — Add number to Meta
1. Meta Developer → your RingReply app → WhatsApp → Phone Numbers
2. Click "Add phone number"
3. Display name: Client's business name
4. Enter client's number
5. Verify via OTP (client receives OTP on their phone)

#### Step B2-4 — Submit for Meta review
1. Fill in business details:
   - Business name
   - Business category
   - Business description
   - Website URL (use ringreply.in if they don't have one)
2. Submit → Meta reviews in 3-14 days
3. Keep checking email for any Meta queries

#### Step B2-5 — After approval
1. Update Railway env: add number to PHONE_MAP
2. Add business to DB (same as 1C above)
3. Test: send a message to client's number — bot should reply
4. Hand over dashboard credentials to client

---

---

# PART 3 — 🇮🇳 INDIAN NUMBERS (Exotel)
> Status: ⏳ KYC pending. Complete after GST is approved.

---

## Step 3A — Complete Exotel KYC

Go to → https://my.exotel.com/self6649/settings/kyc

Upload these 4 documents:
1. **Company PAN Card** → your personal PAN card photo
2. **Certificate of Incorporation** → GST certificate (once approved) OR DPIIT cert
3. **Company Address Proof** → Aadhaar card (has your address)
4. **Passport Size Photo** → selfie with white background

Wait: **2-3 working days** for approval.

---

## Step 3B — Buy Indian Virtual Number

After KYC approved:
1. Exotel dashboard → Buy Number
2. Choose an Indian +91 number (~₹500-1,000/month)
3. Set webhook:
   - Incoming Call: `https://web-production-851bb3.up.railway.app/voice/answer`

---

## Step 3C — Add Exotel Credentials to Railway

Add these to Railway env variables:
```
EXOTEL_ACCOUNT_SID  = self6649          (already in .env)
EXOTEL_API_KEY      = (from Exotel dashboard)
EXOTEL_API_TOKEN    = (from Exotel dashboard)
EXOTEL_PHONE_NUMBER = +91XXXXXXXXXX     (your new Exotel number)
```

---

## Step 3D — Test Indian Number

1. Call your Exotel +91 number from your phone
2. AI should answer in Hindi + English
3. Book a test appointment
4. Confirm booking appears in dashboard

---

---

# PART 4 — 🔧 ADMIN REFERENCE

---

## Your Credentials

| Service | URL | Login |
|---|---|---|
| Railway Dashboard | railway.app | your account |
| Twilio Console | console.twilio.com | your account |
| Exotel Dashboard | my.exotel.com/self6649 | your account |
| Meta Developer | developers.facebook.com | your FB account |
| RingReply Admin Dashboard | web-production-851bb3.up.railway.app/dashboard | admin / tanuj123 |
| UptimeRobot | uptimerobot.com | your account |

---

## Important URLs

| Name | URL |
|---|---|
| Railway App (live server) | https://web-production-851bb3.up.railway.app |
| Voice webhook | https://web-production-851bb3.up.railway.app/voice/answer |
| WhatsApp webhook | https://web-production-851bb3.up.railway.app/whatsapp/meta |
| Health check | https://web-production-851bb3.up.railway.app/health |
| Admin dashboard | https://web-production-851bb3.up.railway.app/dashboard |
| Browser phone | https://web-production-851bb3.up.railway.app/phone |

---

## Twilio Numbers Owned

| Number | Business | Type |
|---|---|---|
| +1 239 423 8893 | tanuj_dental (demo) | US Voice |

---

## Useful curl Commands

### List all businesses:
```bash
curl https://web-production-851bb3.up.railway.app/admin/api/businesses \
  -H "Authorization: Bearer tanuj123"
```

### List all bookings:
```bash
curl https://web-production-851bb3.up.railway.app/admin/api/bookings \
  -H "Authorization: Bearer tanuj123"
```

### Cancel a booking:
```bash
curl -X POST https://web-production-851bb3.up.railway.app/admin/api/bookings/12/cancel \
  -H "Authorization: Bearer tanuj123"
```

### Check server health:
```bash
curl https://web-production-851bb3.up.railway.app/health
```

---

## Pending Tasks Tracker

| # | Task | Status | Blocked By |
|---|---|---|---|
| 1 | Exotel KYC | ⏳ Waiting | GST approval |
| 2 | GST approval | ⏳ Pending for Processing | ARN: AA0905262662820 |
| 3 | Meta Developer App setup | ❌ Not started | Nothing — do today |
| 4 | Razorpay payment setup | ❌ Not started | Nothing — do anytime |
| 5 | First paying client | ❌ Not started | Nothing |
| 6 | LetsVenture listing | ❌ Not filled | Nothing |

---

## Cost per Client (Monthly)

| Item | Cost |
|---|---|
| Railway hosting | ₹420/month (shared across all clients) |
| Twilio number | ₹96/month per client |
| Twilio calls | ₹1.1/min (inbound) |
| Exotel number (India) | ₹500-1,000/month per client |
| Meta WhatsApp API | ₹0.42 per conversation (24hr window) |
| **You charge client** | **₹2,999–6,999/month** |
| **Your profit** | **₹1,800–5,500/month per client** |

---

*Built by Tanuj Prajapati · RingReply · hello@ringreply.in · +91 9319801618*
