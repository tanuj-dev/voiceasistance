# 💰 RingReply — Charges & Pricing Breakdown
> For internal use — explaining costs to clients and tracking profitability
> Last updated: June 4, 2026

---

## 📌 Quick Summary

| Service | Current Setup | Future Setup |
|---|---|---|
| Voice Calls | Twilio US number | Exotel Indian +91 number |
| WhatsApp | Twilio Sandbox (limited) | Meta Cloud API (full) |
| Client Charges | ₹2,999/month | ₹2,999–6,999/month |
| Your Cost | ₹400–800/month per client | ₹200–400/month per client |
| Your Profit | ₹2,200–2,600/month per client | ₹2,600–6,500/month per client |

---

---

# 📞 VOICE CALLS — CURRENT SITUATION (Twilio US Number)

## How the Call Works
```
Customer calls client's Indian number (free for customer)
        ↓
Indian carrier forwards call to RingReply US Twilio number
        ↓
Twilio receives the call — charges YOU per minute
        ↓
AI answers, talks, books appointment (3-5 mins avg)
        ↓
Booking saved → client gets WhatsApp + email alert
```

---

## Who Pays What — Voice (Current)

### You Pay (Twilio):
| Charge | Rate | Notes |
|---|---|---|
| Inbound call receiving | $0.0085/min (~₹0.71/min) | Twilio charges per minute |
| Twilio phone number rental | $1.15/month (~₹96/month) | Per number, per client |
| Railway hosting | $5/month (~₹420/month) | Shared across ALL clients |

### Client Pays (Their Phone Bill):
| Charge | Rate | Notes |
|---|---|---|
| International call forwarding | ₹1–2/min | Airtel/Jio/Vi charges client |
| This is on their phone bill | | NOT your problem |

### Customer Pays:
| Charge | Rate | Notes |
|---|---|---|
| Calling client's number | Normal local rate | Customer dials same number as always |
| No international charges for customer | ✅ | Customer never dials US number |

---

## Your Monthly Cost Per Client (Twilio)

| Calls/Month | Avg Duration | Total Minutes | Twilio Cost | Number Rental | Your Total Cost |
|---|---|---|---|---|---|
| 50 calls | 3 min | 150 min | ₹107 | ₹96 | **~₹200/month** |
| 100 calls | 3 min | 300 min | ₹213 | ₹96 | **~₹310/month** |
| 200 calls | 4 min | 800 min | ₹568 | ₹96 | **~₹665/month** |
| 300 calls | 4 min | 1200 min | ₹852 | ₹96 | **~₹950/month** |
| 500 calls | 4 min | 2000 min | ₹1,420 | ₹96 | **~₹1,520/month** |

---

## Your Profit Per Client (Twilio, You Charge ₹2,999/month)

| Calls/Month | Your Cost | You Charge | Your Profit |
|---|---|---|---|
| 50 calls | ₹200 | ₹2,999 | **₹2,800** ✅ |
| 100 calls | ₹310 | ₹2,999 | **₹2,690** ✅ |
| 200 calls | ₹665 | ₹2,999 | **₹2,334** ✅ |
| 300 calls | ₹950 | ₹2,999 | **₹2,049** ✅ |
| 500 calls | ₹1,520 | ₹2,999 | **₹1,479** ✅ |
| 1000 calls | ₹3,000 | ₹4,999* | **₹1,999** ✅ |

*Upgrade high-volume clients to ₹4,999/month plan

---

## ⚠️ Current Limitations — Voice (Twilio)

| Limitation | Impact | Fix |
|---|---|---|
| US number (+1 239...) | Client's carrier charges international forwarding rates (₹1-2/min) | Switch to Exotel after KYC |
| Client may notice forwarding charges | Client's phone bill shows international calls | Explain upfront — or wait for Exotel |
| No direct Indian number | Can't give client a +91 number yet | Exotel after GST approved |

---

---

# 📞 VOICE CALLS — FUTURE SITUATION (Exotel Indian Number)

## When Available
- After GST approved (ARN: AA0905262662820)
- After Exotel KYC approved (2-3 days after GST)
- Expected: 2-4 weeks from now

## How It Will Work
```
Customer calls client's Indian number
        ↓
Indian carrier forwards to RingReply INDIAN Exotel number (+91)
        ↓
Exotel receives call — charges YOU Indian rates (much cheaper)
        ↓
AI answers in Hindi + English
        ↓
Booking saved → alerts sent
```

## Your Monthly Cost Per Client (Exotel — Future)

| Calls/Month | Twilio Cost Now | Exotel Cost Future | Savings |
|---|---|---|---|
| 100 calls | ₹310 | ₹150 | **₹160 saved** |
| 200 calls | ₹665 | ₹280 | **₹385 saved** |
| 500 calls | ₹1,520 | ₹600 | **₹920 saved** |

## Exotel Rates (Approximate)
| Charge | Rate |
|---|---|
| Inbound call | ₹0.25–0.50/min |
| Exotel number rental | ₹500–1,000/month |
| No international forwarding charges for client | ✅ |

## Benefits Over Twilio
- ✅ Indian +91 number — clients trust it more
- ✅ No international forwarding charges for client
- ✅ 60% cheaper per minute for you
- ✅ Better call quality for Indian networks
- ✅ Hindi support built in

---

---

# 💬 WHATSAPP BOT — CURRENT SITUATION (Twilio Sandbox)

## How It Works Now
```
Customer sends WhatsApp to +1 415 523 8886 (Twilio Sandbox)
        ↓
Twilio forwards message to your server
        ↓
AI replies → full booking conversation
        ↓
Booking saved → alerts sent
```

## Current Limitations
| Limitation | Impact |
|---|---|
| Sandbox number (+1 415 523 8886) | Customers must message an unfamiliar US number |
| Customers must join sandbox first | Send "join actually-pitch" before messaging — friction |
| Sandbox expires every 72 hours | Customers must rejoin every 3 days |
| Not suitable for real clients | Too much friction for daily business use |

## Cost — WhatsApp Sandbox
| Item | Cost |
|---|---|
| Twilio WhatsApp Sandbox | FREE (for testing) |
| Twilio WhatsApp messages (production) | $0.005/message (~₹0.42/message) |

## What You Can Do Right Now
- ✅ Test the bot yourself
- ✅ Demo to potential clients
- ✅ Give to clients willing to test (tech-savvy clients)
- ❌ Not suitable for client's end customers yet

---

# 💬 WHATSAPP BOT — FUTURE SITUATION (Meta Cloud API)

## When Available
- After Meta App Review approved
- Needs: GST certificate for Meta Business Verification
- Expected: 4-6 weeks from now

## Option A — New Dedicated WhatsApp Number Per Client

### How It Works
```
Client gets new WhatsApp number (new SIM or virtual)
        ↓
Number connected to Meta Cloud API
        ↓
Customer messages client's WhatsApp bot number
        ↓
AI replies 24/7 — books appointments automatically
        ↓
Client gets alert, customer gets confirmation
```

### Cost Structure — New Number
| Item | Your Cost | Notes |
|---|---|---|
| New SIM for client | ₹50 one-time | Jio/Airtel prepaid |
| Meta WhatsApp API | ₹0/month | Free up to 1,000 conversations |
| Per conversation (after 1,000) | ₹3.5/conversation | 24hr window per customer |
| Railway hosting | Shared | Already covered |

### Conversations vs Messages
> 1 conversation = unlimited messages within 24 hours = ₹3.5
> Most clients get 50-200 conversations/month

### Your Monthly Cost — WhatsApp New Number
| Conversations/Month | Meta Cost | You Charge Extra | Your Profit |
|---|---|---|---|
| 0–1,000 | ₹0 (FREE) | ₹0 | ✅ Pure profit |
| 1,000–2,000 | ₹3,500 | ₹2,000 extra | Still profitable |

---

## Option B — Client's Existing WhatsApp Number

### Additional Requirements
- Client must have Facebook Business Manager
- Meta must verify their business
- Number must be removed from personal WhatsApp first
- Client LOSES all existing WhatsApp chats on that number

### Cost Structure — Existing Number
| Item | Cost | Who Pays |
|---|---|---|
| Setup fee (your time) | ₹3,000 one-time | Client pays you |
| Meta API messages | ₹3.5/conversation | You pay, covered in monthly fee |
| Takes 1-2 weeks | | Meta review time |

---

---

# 📊 COMPLETE PRICING PLANS — WHAT TO CHARGE CLIENTS

## Current Plans (Available Now)

### Plan 1 — Voice Only ₹2,999/month
| What's Included | Details |
|---|---|
| AI answers missed/busy calls | 24/7 |
| Hindi + English | Both supported |
| Appointment booking via call | Fully automatic |
| Cancellation + Reschedule | Via call |
| SMS confirmation to customer | After every booking |
| Email alert to owner | After every booking |
| Booking dashboard | View/manage all bookings |
| Dedicated RingReply number | US Twilio number |
| Setup | Free, 10 minutes |

**Your cost:** ₹300–700/month
**Your profit:** ₹2,300–2,700/month ✅

---

## Future Plans (After GST + Meta Approval)

### Plan 2 — Voice + WhatsApp ₹3,999/month
| What's Included | Details |
|---|---|
| Everything in Plan 1 | ✅ |
| WhatsApp booking bot | New dedicated number |
| 24/7 WhatsApp replies | Instant AI responses |
| Hindi + English WhatsApp | Both supported |

**Your cost:** ₹500–900/month
**Your profit:** ₹3,100–3,500/month ✅

---

### Plan 3 — Voice + Existing WhatsApp ₹6,999/month + ₹3,000 setup
| What's Included | Details |
|---|---|
| Everything in Plan 2 | ✅ |
| Client's existing WhatsApp number | Customers message same number |
| Meta Business API integration | Full production setup |
| Priority support | Direct WhatsApp with Tanuj |

**Your cost:** ₹1,500–2,000/month
**Your profit:** ₹5,000–5,500/month ✅

---

### Plan 4 — Indian Number (After Exotel) ₹3,499/month
| What's Included | Details |
|---|---|
| Everything in Plan 1 | ✅ |
| Indian +91 number | No international forwarding |
| No extra charges for client's carrier | ✅ |
| Better call quality | Indian network optimized |

**Your cost:** ₹200–500/month
**Your profit:** ₹3,000–3,300/month ✅

---

---

# 🗓️ TIMELINE — WHEN WHAT BECOMES AVAILABLE

```
TODAY (June 2026)
├── ✅ Voice bot (Twilio US number)    → Sell Plan 1 NOW
├── ✅ WhatsApp sandbox (testing only) → Demo only
└── ✅ Dashboard for clients           → Ready

WEEK 2-3 (After GST Approved)
├── ⏳ Exotel KYC submission
├── ⏳ Meta App Review submission
└── ⏳ DPIIT application (if company registered)

WEEK 3-4 (After Exotel KYC)
├── 🔜 Indian +91 numbers available   → Sell Plan 4
└── 🔜 No forwarding charges for clients

WEEK 4-6 (After Meta Approval)
├── 🔜 WhatsApp on new numbers        → Sell Plan 2
└── 🔜 WhatsApp on existing numbers   → Sell Plan 3

MONTH 2+
├── 🔜 Scale to 10+ clients
├── 🔜 Hindi-only plans for Tier 2 cities
└── 🔜 Multi-location business support
```

---

---

# ❓ COMMON CLIENT QUESTIONS — HOW TO ANSWER

### Q: "Will my customers have to pay extra to call?"
> No. Your customers call your same existing number — zero change for them. The forwarding to our system happens invisibly in the background.

### Q: "Will I be charged extra on my phone bill?"
> When a call forwards to our system, your carrier may charge you a small international forwarding rate (₹1-2/min). Most clients see ₹200-400 extra on their bill for 100 missed calls. We're working on Indian numbers to eliminate this completely.

### Q: "What if I pick up the call myself?"
> If you answer the call, the AI never gets involved. It only kicks in when you're busy or don't answer. You always take priority.

### Q: "What about WhatsApp?"
> Currently we're in the process of getting full WhatsApp API approval from Meta (like how Zomato and Swiggy use WhatsApp). Expected in 3-4 weeks. Once approved, your customers can book directly on WhatsApp 24/7.

### Q: "Is there a contract?"
> No contracts. Cancel anytime. Your number goes back to normal immediately.

### Q: "What if the AI makes a mistake?"
> You can see every booking in your dashboard and cancel/edit anything. We recommend checking your dashboard once a day. The AI is accurate 95%+ of the time.

---

*Last updated: June 4, 2026 | Tanuj Prajapati | hello@ringreply.in*
