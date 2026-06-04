# 📊 RingReply — Complete Project Status
> Owner: Tanuj Prajapati | hello@ringreply.in | +91 9319801618
> Auto-updated: June 4, 2026
> Project: VoiceAssistantAI (github.com/tanuj-dev/voiceasistance)
> Live Server: https://api.ringreply.in (Railway)

---

## 🚦 Overall Status

| Area | Status | Last Updated |
|---|---|---|
| Server (Railway) | ✅ Live & Running | June 4, 2026 |
| Voice Bot (Twilio) | ✅ Working | June 4, 2026 |
| WhatsApp Bot (Meta) | ✅ Configured, test only | June 4, 2026 |
| Indian Numbers (Exotel) | ⏳ KYC Pending | June 4, 2026 |
| GST Registration | ⏳ Pending for Processing | June 4, 2026 |
| DPIIT Recognition | ❌ Not applied yet | June 4, 2026 |
| Razorpay Payments | ❌ Not set up | June 4, 2026 |
| Meta App Review | ❌ Not submitted | June 4, 2026 |
| First Paying Client | ❌ Not onboarded | June 4, 2026 |

---

---

# 📞 TWILIO — Voice & WhatsApp (US)

## Credentials
| Item | Value |
|---|---|
| Account SID | (see Railway env — TWILIO_ACCOUNT_SID) |
| Auth Token | (see Railway env — TWILIO_AUTH_TOKEN) |
| API Key SID | (see Railway env — TWILIO_API_KEY_SID) |
| API Key Secret | (see Railway env — TWILIO_API_KEY_SECRET) |
| TwiML App SID | (see Twilio Console → TwiML Apps) |
| Phone Number | +1 239 423 8893 |
| WhatsApp Sandbox | +1 415 523 8886 |
| Sandbox Code | join actually-pitch |

## Status
| Feature | Status | Notes |
|---|---|---|
| Voice calls | ✅ Working | Webhook: api.ringreply.in/voice/answer |
| Browser phone | ✅ Working | api.ringreply.in/phone |
| WhatsApp Sandbox | ✅ Configured | join actually-pitch to connect |
| SMS confirmations | ✅ Working | Fires after every booking |
| Call recording | ❌ Not set up | Future feature |

## Webhook URLs (set in Twilio Console)
```
Voice:     https://api.ringreply.in/voice/answer
Status:    https://api.ringreply.in/voice/status
WhatsApp:  https://api.ringreply.in/whatsapp/message
```

## Numbers Owned
| Number | Business Mapped | Type | Cost |
|---|---|---|---|
| +1 239 423 8893 | tanuj_dental | US Voice + WhatsApp | $1.15/mo |

---

---

# 📱 META (WhatsApp Cloud API)

## App Details
| Item | Value |
|---|---|
| App Name | RingReply |
| App ID | 2300693804034024 |
| App Mode | Development (unpublished) |
| Business | RingReply |
| Business ID | 961940723310825 |

## WhatsApp Business Account
| Item | Value |
|---|---|
| WABA ID | 2212548976250195 |
| Phone Number ID | 1210238258828453 |
| Test Number | +1 555 634 9042 |
| Display Name | Test Number |

## Webhook Configuration
| Item | Value |
|---|---|
| Callback URL | https://api.ringreply.in/whatsapp/meta |
| Verify Token | ringreply2024 |
| messages field | ✅ Subscribed |

## Railway Environment Variables (set ✅)
```
META_PHONE_NUMBER_ID = 1210238258828453
META_WABA_ID         = 2212548976250195
META_ACCESS_TOKEN    = (set in Railway — expires every 24hrs currently)
META_VERIFY_TOKEN    = ringreply2024
```

## Status
| Feature | Status | Notes |
|---|---|---|
| Meta Developer App | ✅ Created | App ID: 2300693804034024 |
| WhatsApp product added | ✅ Done | |
| Webhook configured | ✅ Done | api.ringreply.in/whatsapp/meta |
| messages subscribed | ✅ Done | |
| Test number working | ✅ Working | +1 555 634 9042 |
| Access token | ⚠️ Temporary | Expires every 24 hours — need permanent |
| Permanent token | ❌ Not created | Need System User token |
| App published | ❌ Not submitted | Need GST/business docs |
| Meta Business Verification | ❌ Pending | Need GST certificate |
| Real client numbers | ❌ Blocked | App must be published first |

## ⚠️ Pending Actions — Meta
1. **Create permanent access token** (System User token — never expires)
   - Go to: business.facebook.com → Settings → System Users → Add
   - Name: RingReply Bot, Role: Admin
   - Generate token with whatsapp_business_messaging + whatsapp_business_management
   - Update META_ACCESS_TOKEN in Railway

2. **Submit for App Review** (after GST approved)
   - Need: GST certificate as business proof
   - Submit at: developers.facebook.com → your app → App Review
   - Timeline: 1-4 weeks for Meta approval

3. **Become Tech Provider** (after app published)
   - Allows adding other businesses' WhatsApp numbers
   - Submit at: Meta Developer → Tech Provider onboarding

---

---

# 🇮🇳 EXOTEL — Indian Phone Numbers (+91)

## Account Details
| Item | Value |
|---|---|
| Account SID | self6649 |
| Dashboard | https://my.exotel.com/self6649 |
| API Key | (see Railway env — EXOTEL_API_KEY) |
| API Token | (see Railway env — EXOTEL_API_TOKEN) |
| Subdomain | api.exotel.com |

## KYC Status — INCOMPLETE ❌
| Document | Status | What to Upload |
|---|---|---|
| Company PAN Card | ❌ Not uploaded | Personal PAN card photo |
| Certificate of Incorporation | ❌ Not uploaded | GST certificate (once approved) |
| Company Address Proof | ❌ Not uploaded | Aadhaar card |
| Passport Size Photo | ❌ Not uploaded | Selfie with white background |

## Why Blocked
- GST certificate not yet approved (ARN: AA0905262662820)
- Once GST approved → upload GST certificate as "Certificate of Incorporation"
- After KYC approved (2-3 days) → can buy Indian +91 number

## ⚠️ Pending Actions — Exotel
1. Wait for GST approval
2. Download GST certificate
3. Upload all 4 KYC docs at: my.exotel.com/self6649/settings/kyc
4. Wait 2-3 days for KYC approval
5. Buy Indian +91 virtual number (~₹500-1,000/month)
6. Set Exotel webhook → https://api.ringreply.in/voice/answer
7. Add to Railway env: EXOTEL_PHONE_NUMBER=+91XXXXXXXXXX
8. Add to PHONE_MAP: +91XXXXXXXXXX:tanuj_dental

---

---

# 🏛️ GST REGISTRATION

## Details
| Item | Value |
|---|---|
| ARN Number | AA0905262662820 |
| Status | Pending for Processing |
| Applied | June 2026 |
| Check Status | gst.gov.in → Services → Registration → Track Application Status |

## What Happens Next
1. ⏳ GST officer reviews application (7-30 working days)
2. May raise query (Form GST REG-03) — respond within 7 days
3. ✅ Approved → get GSTIN + GST certificate
4. Use GST certificate for: Exotel KYC + Meta App Review + Exotel KYC

## Status Progression
```
Pending for Processing → Pending for Verification → Pending for Order → Approved ✅
```

---

---

# 🏆 DPIIT RECOGNITION

## Status: ❌ NOT APPLIED YET

## Why Needed
- Business credibility
- Exotel KYC (as Certificate of Incorporation)
- Meta Business Verification
- Tax benefits (80IAC)
- LetsVenture investor credibility

## How to Apply
1. Go to: startupindia.gov.in
2. Login with your account
3. Recognition → Apply for DPIIT Recognition
4. Fill business details (RingReply, AI/Tech sector)
5. Submit → approval in 2-7 days (usually automatic)

## Note
- You have a Startup India account (BHASKAR registered)
- But DPIIT Recognition was NOT applied
- Easy to apply — takes 30 mins
- Free of cost

---

---

# 💰 RAZORPAY — Payments

## Status: ❌ NOT SET UP

## What's Needed
- Collect monthly subscription fees from clients
- India Plan: ₹2,999/month per client
- US Plan: $49/month per client

## Steps to Set Up
1. Go to: razorpay.com → Sign Up (free)
2. Complete KYC (PAN + bank account)
3. Create subscription plans:
   - India Plan: ₹2,999/month
   - US Plan: $49/month (via Stripe for US clients)
4. Share payment link with each client monthly
5. Future: integrate Razorpay API for auto-billing

---

---

# 🖥️ RAILWAY — Hosting

## Details
| Item | Value |
|---|---|
| App URL | https://web-production-851bb3.up.railway.app |
| Custom Domain | https://api.ringreply.in |
| Plan | Hobby ($5/month) |
| Database | PostgreSQL (postgres-volume) |
| Auto-deploy | ✅ Yes — pushes to GitHub trigger deploy |
| UptimeRobot | ✅ Monitoring every 5 mins |

## Environment Variables Set
```
TWILIO_ACCOUNT_SID     ✅
TWILIO_AUTH_TOKEN      ✅
TWILIO_API_KEY_SID     ✅
TWILIO_API_KEY_SECRET  ✅
TWIML_APP_SID          ✅
TWILIO_PHONE_NUMBER    ✅ (+12394238893)
PHONE_MAP              ✅ (+12394238893:tanuj_dental)
DEFAULT_BUSINESS_ID    ✅ (tanuj_dental)
ADMIN_PASSWORD         ✅ (tanuj123)
SECRET_KEY             ✅
PORT                   ✅ (5001)
GROQ_API_KEY           ✅
GMAIL_ADDRESS          ✅ (noreply.aireceptionist@gmail.com)
GMAIL_APP_PASSWORD     ✅
DATABASE_URL           ✅ (PostgreSQL on Railway)
EXOTEL_ACCOUNT_SID     ✅
EXOTEL_API_KEY         ✅
EXOTEL_API_TOKEN       ✅
META_PHONE_NUMBER_ID   ✅ (1210238258828453)
META_WABA_ID           ✅ (2212548976250195)
META_ACCESS_TOKEN      ⚠️ (temporary — expires 24hrs)
META_VERIFY_TOKEN      ✅ (ringreply2024)
```

---

---

# 🗄️ DATABASE — Businesses

## Businesses in DB
| Business ID | Name | Type | Status |
|---|---|---|---|
| tanuj_dental | Tanuj Dental Clinic | dental | ✅ Active (demo) |
| premier_cars | Premier Cars Showroom | carshowroom | ✅ Active (demo) |

## Admin Access
```
Dashboard: https://api.ringreply.in/dashboard
Login:     admin / tanuj123
```

---

---

# 🌐 RINGREPLY WEBSITE

## Details
| Item | Value |
|---|---|
| Domain | ringreply.in |
| Repo | github.com/tanuj-dev/ringreply-web |
| Hosting | Vercel (auto-deploy on push) |
| Analytics | Google Analytics G-6RF70QYSFW |

## Pages Live
| Page | URL | Status |
|---|---|---|
| Home | ringreply.in | ✅ Live |
| How it Works | ringreply.in/how-it-works | ✅ Live |
| Features | ringreply.in/features | ✅ Live |
| Pricing | ringreply.in/pricing | ✅ Live |
| Contact | ringreply.in/contact | ✅ Live |
| Privacy Policy | ringreply.in/privacy-policy | ✅ Live |
| Terms of Service | ringreply.in/terms | ✅ Live |
| Cookie Policy | ringreply.in/cookie-policy | ✅ Live |

## SEO
| Item | Status |
|---|---|
| Google Search Console | ✅ Connected |
| Sitemap submitted | ✅ Submitted (sitemap.xml) |
| Google Analytics | ✅ Active |

---

---

# ✅ COMPLETED TASKS (History)

| Date | What Was Done |
|---|---|
| June 2026 | Railway deployment — server live 24/7 |
| June 2026 | Custom domain api.ringreply.in configured |
| June 2026 | PostgreSQL database set up on Railway |
| June 2026 | Twilio voice bot working end-to-end |
| June 2026 | Browser phone UI working |
| June 2026 | Admin dashboard built |
| June 2026 | Multi-tenant system (multiple businesses) |
| June 2026 | Booking cancellation flow completed |
| June 2026 | Reschedule flow built |
| June 2026 | SMS/Email notifications working |
| June 2026 | Car showroom business type added |
| June 2026 | Premier Cars Showroom demo added |
| June 2026 | Hindi language support added |
| June 2026 | Meta Developer app created (RingReply) |
| June 2026 | WhatsApp webhook configured (api.ringreply.in/whatsapp/meta) |
| June 2026 | Meta access token added to Railway |
| June 2026 | messages webhook field subscribed |
| June 2026 | ringreply.in website launched (8 pages) |
| June 2026 | Google Analytics added to website |
| June 2026 | Google Search Console connected + sitemap submitted |
| June 2026 | SEO keywords added to all pages |
| June 2026 | UptimeRobot monitoring set up |
| June 2026 | BHASKAR (Startup India) registration done |
| June 2026 | DPIIT application done |
| June 2026 | GST application submitted (ARN: AA0905262662820) |
| June 2026 | LetsVenture investor PDF generated |
| June 2026 | requirements.txt updated with all dependencies |

---

---

# ❌ PENDING TASKS (Priority Order)

## 🔴 Priority 1 — Do This Week

| Task | Blocked By | Steps |
|---|---|---|
| Create permanent Meta token | Nothing | business.facebook.com → System Users → Generate token |
| Apply for DPIIT Recognition | Nothing | startupindia.gov.in → Recognition → Apply (30 mins, free) |
| Set up Razorpay | Nothing | razorpay.com → signup → KYC |

## 🟡 Priority 2 — After GST Approved

| Task | Blocked By | Steps |
|---|---|---|
| Complete Exotel KYC | GST certificate | Upload 4 docs at my.exotel.com/self6649/settings/kyc |
| Submit Meta App Review | GST certificate | developers.facebook.com → App Review → Submit |
| Buy Indian Exotel number | Exotel KYC approval | Exotel dashboard → Buy Number |

## 🟢 Priority 3 — Business

| Task | Blocked By | Steps |
|---|---|---|
| First paying client | Nothing | Outreach → onboard via call forwarding |
| LetsVenture listing | Nothing | Fill form at letsventure.com |
| WhatsApp for clients | Meta App Review | After Meta approves |

---

---

# 📋 QUICK REFERENCE — Daily Use

## Add New Client (Call Forwarding)
```bash
# 1. Add business to DB
curl -X POST https://api.ringreply.in/admin/api/businesses \
  -H "Authorization: Bearer tanuj123" \
  -H "Content-Type: application/json" \
  -d '{"id":"biz_id","name":"Business Name","type":"salon","services":["S1","S2"],"working_days":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"start_time":"10:00","end_time":"20:00","slot_duration":30,"contact_email":"client@gmail.com","location":"Address here"}'

# 2. Set client password
curl -X POST https://api.ringreply.in/admin/api/set-password \
  -H "Authorization: Bearer tanuj123" \
  -H "Content-Type: application/json" \
  -d '{"business_id":"biz_id","password":"pass123"}'

# 3. Add to PHONE_MAP in Railway env vars:
# +1XXXXXXXXXX:biz_id

# 4. Send forwarding code to client (see tanuj.setup.guide.md)
```

## Check Server Health
```bash
curl https://api.ringreply.in/health
```

## List All Bookings
```bash
curl https://api.ringreply.in/admin/api/bookings \
  -H "Authorization: Bearer tanuj123"
```

## Check GST Status
- URL: gst.gov.in → Services → Registration → Track Application Status
- ARN: AA0905262662820

---

*Last updated: June 4, 2026 by Claude*
*Update this file whenever something changes!*
