from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import PageBreak

OUTPUT = "/Users/apple/Desktop/AI_Receptionist_Proposal.pdf"

# ── Brand colours ──────────────────────────────────────────────────────────
BLUE       = colors.HexColor("#11418A")
BLUE_LIGHT = colors.HexColor("#E8EEF8")
ACCENT     = colors.HexColor("#22C55E")
DARK       = colors.HexColor("#1A1A2E")
GREY       = colors.HexColor("#64748B")
GREY_LIGHT = colors.HexColor("#F1F5F9")
WHITE      = colors.white

W, H = A4   # 210 × 297 mm

# ── Styles ─────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def sty(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=base[parent], **kw)

S = {
    "cover_title": sty("cover_title", "Title",
        fontSize=32, leading=40, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER),

    "cover_sub": sty("cover_sub",
        fontSize=14, leading=20, textColor=colors.HexColor("#CBD5E1"),
        fontName="Helvetica", alignment=TA_CENTER),

    "cover_tag": sty("cover_tag",
        fontSize=11, leading=16, textColor=ACCENT,
        fontName="Helvetica-Bold", alignment=TA_CENTER),

    "section": sty("section",
        fontSize=18, leading=24, textColor=BLUE,
        fontName="Helvetica-Bold", spaceBefore=18, spaceAfter=8),

    "subsection": sty("subsection",
        fontSize=13, leading=18, textColor=DARK,
        fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=4),

    "body": sty("body",
        fontSize=10, leading=16, textColor=DARK,
        fontName="Helvetica", spaceAfter=4),

    "body_grey": sty("body_grey",
        fontSize=10, leading=16, textColor=GREY,
        fontName="Helvetica", spaceAfter=4),

    "bullet": sty("bullet",
        fontSize=10, leading=16, textColor=DARK,
        fontName="Helvetica", leftIndent=14, spaceAfter=2,
        bulletIndent=4),

    "table_head": sty("table_head",
        fontSize=10, leading=14, textColor=WHITE,
        fontName="Helvetica-Bold", alignment=TA_CENTER),

    "table_cell": sty("table_cell",
        fontSize=10, leading=14, textColor=DARK,
        fontName="Helvetica", alignment=TA_LEFT),

    "table_cell_c": sty("table_cell_c",
        fontSize=10, leading=14, textColor=DARK,
        fontName="Helvetica", alignment=TA_CENTER),

    "highlight": sty("highlight",
        fontSize=11, leading=16, textColor=BLUE,
        fontName="Helvetica-Bold", alignment=TA_CENTER),

    "footer": sty("footer",
        fontSize=8, leading=12, textColor=GREY,
        fontName="Helvetica", alignment=TA_CENTER),

    "pitch": sty("pitch",
        fontSize=12, leading=20, textColor=DARK,
        fontName="Helvetica-Oblique", alignment=TA_CENTER,
        spaceAfter=6),
}

# ── Table helper ───────────────────────────────────────────────────────────
def make_table(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths)
    cmds = [
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, GREY_LIGHT]),
        ("GRID",           (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROUNDEDCORNERS", [4]),
        ("TOPPADDING",     (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 7),
        ("LEFTPADDING",    (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",   (0, 0), (-1, -1), 10),
        ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
    ]
    if header:
        cmds += [
            ("BACKGROUND",  (0, 0), (-1, 0), BLUE),
            ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 10),
        ]
    t.setStyle(TableStyle(cmds))
    return t

def divider():
    return HRFlowable(width="100%", thickness=1,
                      color=colors.HexColor("#E2E8F0"), spaceAfter=8, spaceBefore=4)

# ── Cover page canvas callback ─────────────────────────────────────────────
def cover_background(canvas, doc):
    canvas.saveState()
    # Deep blue gradient background
    canvas.setFillColor(BLUE)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # Decorative circle top-right
    canvas.setFillColor(colors.HexColor("#1A56B0"))
    canvas.circle(W - 20*mm, H - 10*mm, 60*mm, fill=1, stroke=0)
    # Decorative circle bottom-left
    canvas.setFillColor(colors.HexColor("#0D3270"))
    canvas.circle(20*mm, 30*mm, 50*mm, fill=1, stroke=0)
    canvas.restoreState()

def normal_background(canvas, doc):
    canvas.saveState()
    # Subtle top bar
    canvas.setFillColor(BLUE)
    canvas.rect(0, H - 12*mm, W, 12*mm, fill=1, stroke=0)
    # Footer
    canvas.setFillColor(GREY_LIGHT)
    canvas.rect(0, 0, W, 10*mm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(W/2, 3*mm,
        "AI Voice Receptionist  |  Confidential Business Proposal  |  tanuj@code-brew.com")
    canvas.restoreState()

# ── Build document ─────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=18*mm,
    )

    story = []

    # ── PAGE 1: Cover ───────────────────────────────────────────────────────
    story.append(Spacer(1, 45*mm))
    story.append(Paragraph("AI Voice Receptionist", S["cover_title"]))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        "Never Miss a Booking Again", S["cover_sub"]))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        "Your Business. Your Number. Your 24/7 AI Receptionist.", S["cover_tag"]))
    story.append(Spacer(1, 20*mm))

    # Stats row on cover
    stats = Table(
        [[
            Paragraph("<b>24/7</b><br/>Available", sty("cs1", fontSize=14, leading=20,
                textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>0</b><br/>Missed Calls", sty("cs2", fontSize=14, leading=20,
                textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
            Paragraph("<b>100%</b><br/>Automated", sty("cs3", fontSize=14, leading=20,
                textColor=WHITE, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        ]],
        colWidths=[55*mm, 55*mm, 55*mm]
    )
    stats.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), colors.HexColor("#1A56B0")),
        ("TOPPADDING",   (0,0), (-1,-1), 14),
        ("BOTTOMPADDING",(0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS", [8]),
        ("LINEAFTER",    (0,0), (1,-1), 1, colors.HexColor("#2563EB")),
    ]))
    story.append(stats)
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph(
        "Prepared by  Tanuj  |  tanuj@code-brew.com",
        sty("prep", fontSize=10, leading=16,
            textColor=colors.HexColor("#94A3B8"),
            fontName="Helvetica", alignment=TA_CENTER)))

    story.append(PageBreak())

    # ── PAGE 2: What Is It ─────────────────────────────────────────────────
    story.append(Paragraph("What Is AI Voice Receptionist?", S["section"]))
    story.append(divider())
    story.append(Paragraph(
        "An AI-powered phone receptionist that answers your business calls, "
        "understands what customers say, and books appointments — automatically, "
        "round the clock, with zero human effort.",
        S["body"]))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("The Problem We Solve", S["subsection"]))
    problems = [
        ["Pain Point", "Impact on Business"],
        ["Missed calls during busy hours", "Lost bookings, unhappy customers"],
        ["No one to answer after 8 PM", "Competitors get the booking instead"],
        ["Receptionist salary + leaves", "High cost, unreliable coverage"],
        ["Customer has to call back multiple times", "Bad experience, low retention"],
    ]
    story.append(make_table(problems, [90*mm, 80*mm]))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("How It Works — In 6 Steps", S["subsection"]))
    steps = [
        ["Step", "What Happens"],
        ["1. Customer calls your number", "They dial the business phone number as usual"],
        ["2. AI answers instantly", "Greets them warmly — sounds like a real receptionist"],
        ["3. AI understands their need", "Books, reschedules, or answers questions"],
        ["4. AI offers available slots", "Checks real-time availability, no double booking"],
        ["5. Customer confirms by voice", "Says 'Yes' — appointment is locked in"],
        ["6. Booking saved automatically", "Owner sees it on the dashboard instantly"],
    ]
    story.append(make_table(steps, [85*mm, 85*mm]))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("Who Is This For?", S["subsection"]))
    for biz in [
        "Beauty Salons & Parlours",
        "Dental Clinics",
        "Physiotherapy & Wellness Centers",
        "Barber Shops",
        "Diagnostic Labs & Doctor Clinics",
        "Coaching Institutes & Tutors",
    ]:
        story.append(Paragraph(f"  ✓  {biz}", S["bullet"]))

    story.append(PageBreak())

    # ── PAGE 3: Tech Stack ─────────────────────────────────────────────────
    story.append(Paragraph("Technology Stack", S["section"]))
    story.append(divider())
    story.append(Paragraph(
        "Everything runs on proven, production-grade technology. "
        "The AI model runs locally — no third-party AI API costs.",
        S["body_grey"]))
    story.append(Spacer(1, 3*mm))

    tech = [
        ["Layer", "Technology", "Purpose"],
        ["AI Brain", "Ollama + LLaMA 3.2 (Local)", "Understands speech, generates natural replies"],
        ["Phone / Voice", "Twilio", "Handles real calls, speech-to-text, text-to-speech"],
        ["Browser Phone", "Twilio Voice JS SDK", "Call from browser — no physical phone needed"],
        ["Web Server", "Flask (Python)", "Receives calls, processes logic, returns responses"],
        ["Database", "SQLite", "Stores businesses, bookings, slots"],
        ["Tunnel", "ngrok / VPS", "Connects local server to Twilio securely"],
    ]
    story.append(make_table(tech, [40*mm, 65*mm, 65*mm]))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("Call Flow Diagram", S["subsection"]))
    flow = [
        [Paragraph(
            "<b>Customer Speaks</b><br/>"
            "<font color='#64748B' size='9'>via phone or browser</font>",
            sty("f1", fontSize=10, leading=15, alignment=TA_CENTER)),
         Paragraph("→", sty("arr", fontSize=16, alignment=TA_CENTER, textColor=BLUE)),
         Paragraph(
            "<b>Twilio</b><br/>"
            "<font color='#64748B' size='9'>speech → text</font>",
            sty("f2", fontSize=10, leading=15, alignment=TA_CENTER)),
         Paragraph("→", sty("arr2", fontSize=16, alignment=TA_CENTER, textColor=BLUE)),
         Paragraph(
            "<b>Flask Server</b><br/>"
            "<font color='#64748B' size='9'>webhook handler</font>",
            sty("f3", fontSize=10, leading=15, alignment=TA_CENTER)),
         Paragraph("→", sty("arr3", fontSize=16, alignment=TA_CENTER, textColor=BLUE)),
         Paragraph(
            "<b>Ollama AI</b><br/>"
            "<font color='#64748B' size='9'>generates reply</font>",
            sty("f4", fontSize=10, leading=15, alignment=TA_CENTER)),
         Paragraph("→", sty("arr4", fontSize=16, alignment=TA_CENTER, textColor=BLUE)),
         Paragraph(
            "<b>Twilio speaks</b><br/>"
            "<font color='#64748B' size='9'>text → voice</font>",
            sty("f5", fontSize=10, leading=15, alignment=TA_CENTER)),
        ]
    ]
    ft = Table(flow, colWidths=[26*mm, 8*mm, 24*mm, 8*mm, 26*mm, 8*mm, 24*mm, 8*mm, 26*mm])
    ft.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (0,0), BLUE_LIGHT),
        ("BACKGROUND",   (2,0), (2,0), BLUE_LIGHT),
        ("BACKGROUND",   (4,0), (4,0), BLUE_LIGHT),
        ("BACKGROUND",   (6,0), (6,0), BLUE_LIGHT),
        ("BACKGROUND",   (8,0), (8,0), colors.HexColor("#DCFCE7")),
        ("ROUNDEDCORNERS", [6]),
        ("TOPPADDING",   (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0), (-1,-1), 10),
        ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(ft)

    story.append(PageBreak())

    # ── PAGE 4: Onboarding & Pricing ──────────────────────────────────────
    story.append(Paragraph("Client Onboarding — What You Need From Them", S["section"]))
    story.append(divider())
    story.append(Paragraph(
        "Onboarding a new client takes less than 30 minutes. "
        "They don't need to install anything or touch any code.",
        S["body_grey"]))
    story.append(Spacer(1, 3*mm))

    onboard = [
        ["#", "What We Need", "Example (Salon)"],
        ["1", "Business Name", "Glow Beauty Salon"],
        ["2", "Services Offered", "Haircut, Waxing, Facial, Manicure"],
        ["3", "Working Days", "Monday to Saturday"],
        ["4", "Working Hours", "10:00 AM to 8:00 PM"],
        ["5", "Slot Duration", "30 minutes per appointment"],
        ["6", "Contact Email", "salon@gmail.com"],
    ]
    story.append(make_table(onboard, [10*mm, 65*mm, 95*mm]))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph(
        "We set up everything on our end — dedicated phone number, AI configuration, "
        "database, and booking system. The salon owner just starts sharing their new number.",
        S["body_grey"]))

    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Pricing Plans", S["section"]))
    story.append(divider())

    plans = [
        ["Plan", "Price / Month", "Calls / Month", "Features"],
        ["Starter", "Rs. 1,499", "Up to 200", "Booking only, 1 phone number"],
        ["Growth", "Rs. 2,999", "Unlimited", "Book + Cancel + Reschedule, 1 number"],
        ["Pro", "Rs. 4,999", "Unlimited", "All features, 2 numbers, Email alerts"],
    ]
    pt = Table(plans, colWidths=[35*mm, 38*mm, 38*mm, 59*mm])
    pt.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BACKGROUND",   (0, 2), (-1, 2), BLUE_LIGHT),   # Growth highlight
        ("FONTNAME",     (0, 2), (-1, 2), "Helvetica-Bold"),
        ("TEXTCOLOR",    (0, 2), (-1, 2), BLUE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, BLUE_LIGHT, WHITE]),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",        (1, 0), (2, -1), "CENTER"),
    ]))
    story.append(pt)
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "* One-time setup fee: Rs. 3,000 – Rs. 5,000 (covers configuration, testing, and training session)",
        S["body_grey"]))

    story.append(PageBreak())

    # ── PAGE 5: Unit Economics & Scale ────────────────────────────────────
    story.append(Paragraph("Unit Economics — Real Numbers", S["section"]))
    story.append(divider())
    story.append(Paragraph(
        "Based on a typical salon receiving 150 calls per month, "
        "averaging 3 minutes per call:",
        S["body_grey"]))
    story.append(Spacer(1, 3*mm))

    econ = [
        ["Item", "Calculation", "Monthly Cost"],
        ["Twilio phone number", "1 number", "Rs. 95"],
        ["Twilio call charges", "150 calls x 3 min x Rs. 1.08", "Rs. 486"],
        ["Server share (VPS)", "Shared across all clients", "Rs. 100"],
        ["Total cost to us", "", "Rs. 681"],
        ["Client pays (Starter)", "", "Rs. 1,499"],
        ["Our profit per client", "", "Rs. 818"],
    ]
    et = Table(econ, colWidths=[65*mm, 65*mm, 40*mm])
    et.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0,1), (-1,4), [WHITE, GREY_LIGHT, WHITE, GREY_LIGHT]),
        ("BACKGROUND",   (0, 5), (-1, 5), colors.HexColor("#DCFCE7")),
        ("FONTNAME",     (0, 4), (-1, 4), "Helvetica-Bold"),
        ("FONTNAME",     (0, 5), (-1, 5), "Helvetica-Bold"),
        ("FONTNAME",     (0, 6), (-1, 6), "Helvetica-Bold"),
        ("TEXTCOLOR",    (2, 6), (2, 6), ACCENT),
        ("BACKGROUND",   (0, 6), (-1, 6), colors.HexColor("#F0FDF4")),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING",   (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 8),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("ALIGN",        (2, 0), (2, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(et)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("Revenue Potential at Scale", S["subsection"]))
    scale = [
        ["No. of Clients", "Monthly Revenue", "Monthly Cost", "Monthly Profit"],
        ["5 clients", "Rs. 7,495", "Rs. 3,405", "Rs. 4,090"],
        ["10 clients", "Rs. 14,990", "Rs. 6,810", "Rs. 8,180"],
        ["25 clients", "Rs. 37,475", "Rs. 17,025", "Rs. 20,450"],
        ["50 clients", "Rs. 74,950", "Rs. 34,050", "Rs. 40,900"],
    ]
    story.append(make_table(scale, [45*mm, 47*mm, 47*mm, 47*mm]))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "All 50 clients run on a single server costing Rs. 800/month. "
        "Each new client added is nearly pure profit after the fixed server cost.",
        S["body_grey"]))

    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Roadmap — What's Coming Next", S["section"]))
    story.append(divider())

    roadmap = [
        ["Feature", "Status", "Benefit"],
        ["Indian phone numbers (Exotel)", "In Progress", "No need for US Twilio numbers"],
        ["WhatsApp booking channel", "Planned", "Customers book via WhatsApp too"],
        ["SMS / Email confirmation", "Planned", "Auto-send booking details to customer"],
        ["Admin dashboard (web)", "Planned", "Business owner views all bookings online"],
        ["Google Calendar sync", "Planned", "Bookings appear in owner's calendar"],
        ["Hindi / regional language", "Planned", "Serve Tier 2 and Tier 3 cities"],
        ["Multi-location support", "Planned", "Chain businesses with multiple branches"],
    ]
    story.append(make_table(roadmap, [75*mm, 30*mm, 65*mm]))

    story.append(PageBreak())

    # ── PAGE 6: Sales Pitch & CTA ─────────────────────────────────────────
    story.append(Spacer(1, 10*mm))
    story.append(Paragraph("The Pitch In One Paragraph", S["section"]))
    story.append(divider())
    story.append(Spacer(1, 4*mm))

    # Styled quote box
    quote = Table(
        [[Paragraph(
            "Your customers call at 9 PM. Your staff has gone home. "
            "The call rings out. That customer books with your competitor.<br/><br/>"
            "Our AI receptionist answers every call, every time — morning, evening, weekends. "
            "It understands what they need, checks your availability, and locks in the booking. "
            "You wake up to confirmed appointments in your inbox.<br/><br/>"
            "<b>For less than Rs. 1,500 a month — less than one day of a part-time staff member.</b>",
            sty("quote_inner", fontSize=11, leading=19,
                textColor=DARK, fontName="Helvetica"))]],
        colWidths=[154*mm]
    )
    quote.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), BLUE_LIGHT),
        ("LEFTPADDING",  (0,0), (-1,-1), 16),
        ("RIGHTPADDING", (0,0), (-1,-1), 16),
        ("TOPPADDING",   (0,0), (-1,-1), 16),
        ("BOTTOMPADDING",(0,0), (-1,-1), 16),
        ("LINEAFTER",    (0,0), (0,-1), 4, BLUE),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(quote)

    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("Why Choose Us?", S["section"]))
    story.append(divider())

    why = [
        ["Advantage", "Detail"],
        ["No AI API costs", "Model runs locally — costs don't scale with usage"],
        ["Quick setup", "Your business is live in under 30 minutes"],
        ["No hardware needed", "Client just shares their new phone number"],
        ["Multi-language ready", "Hindi and regional language support coming soon"],
        ["Fully managed", "We handle everything — you just collect payment"],
        ["Cancel anytime", "No long-term contracts, month-to-month"],
    ]
    story.append(make_table(why, [65*mm, 105*mm]))

    story.append(Spacer(1, 8*mm))

    # CTA box
    cta = Table(
        [[Paragraph(
            "<b>Ready to Get Started?</b><br/><br/>"
            "Contact us to schedule a free live demo call.<br/>"
            "We will set up your AI receptionist and you can try it yourself.<br/><br/>"
            "<b>tanuj@code-brew.com</b>",
            sty("cta_inner", fontSize=12, leading=20,
                textColor=WHITE, fontName="Helvetica", alignment=TA_CENTER))]],
        colWidths=[154*mm]
    )
    cta.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), BLUE),
        ("LEFTPADDING",  (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
        ("TOPPADDING",   (0,0), (-1,-1), 20),
        ("BOTTOMPADDING",(0,0), (-1,-1), 20),
        ("ROUNDEDCORNERS", [10]),
    ]))
    story.append(cta)

    # ── Build with page templates ──────────────────────────────────────────
    def on_page(canvas, doc):
        if doc.page == 1:
            cover_background(canvas, doc)
        else:
            normal_background(canvas, doc)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF saved → {OUTPUT}")

build()
