"""
pdf_report.py — Generates the PropValuate AI valuation report as a PDF,
entirely on the server using ReportLab.

Font note: ReportLab's built-in Helvetica/Times fonts are Adobe's standard-14
fonts, which do NOT include the ₹ (Indian Rupee, U+20B9) glyph — so it was
rendering as a garbled superscript character in the PDF. This version embeds
DejaVu Sans/Serif (bundled in fonts/), which does contain the ₹ glyph, and
uses them for all text in the report instead.
"""
import io
from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

FONTS_DIR = Path(__file__).parent / "fonts"

# Register the bundled Unicode fonts once, at import time.
_registered = False
def _ensure_fonts():
    global _registered
    if _registered:
        return
    pdfmetrics.registerFont(TTFont("DejaVuSans", str(FONTS_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(FONTS_DIR / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSerif", str(FONTS_DIR / "DejaVuSerif.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVuSerif-Bold", str(FONTS_DIR / "DejaVuSerif-Bold.ttf")))
    _registered = True


def fmt_inr(n: float) -> str:
    n = round(n)
    return f"₹{n:,}"


def fmt_inr_short(n: float) -> str:
    if n >= 10_000_000:
        return f"₹{n/10_000_000:.2f} Cr"
    if n >= 100_000:
        return f"₹{n/100_000:.2f} L"
    return fmt_inr(n)


def build_pdf(valuation: dict, meta: dict) -> bytes:
    _ensure_fonts()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    x_margin = 15 * mm
    y = height - 20 * mm

    form = valuation["form"]
    loc = valuation["location"]
    rec = valuation["recommendation"]
    forecast = valuation["forecast"]
    contribs = valuation["contributions"]
    predicted = valuation["predicted"]

    def line(y_pos, x1=x_margin, x2=width - x_margin, gray=0.82):
        c.setStrokeColor(colors.Color(gray, gray, gray))
        c.line(x1, y_pos, x2, y_pos)

    def heading(text, size=13):
        nonlocal y
        c.setFont("DejaVuSans-Bold", size)
        c.setFillColor(colors.black)
        c.drawString(x_margin, y, text)
        y -= size + 6

    def body(text, size=10.5, indent=0):
        nonlocal y
        c.setFont("DejaVuSans", size)
        c.setFillColor(colors.black)
        c.drawString(x_margin + indent, y, text)
        y -= size + 4

    def check_page_break(min_remaining=40 * mm):
        nonlocal y
        if y < min_remaining:
            c.showPage()
            y = height - 20 * mm

    # ---- Title ----
    c.setFont("DejaVuSerif-Bold", 20)
    c.drawCentredString(width / 2, y, "PropValuate AI — Valuation Report")
    y -= 20
    c.setFont("DejaVuSans", 10)
    c.setFillColor(colors.Color(0.47, 0.47, 0.47))
    c.drawCentredString(width / 2, y, f"Generated {date.today().strftime('%d %b %Y')}")
    y -= 16
    line(y)
    y -= 16

    # ---- Property details ----
    heading("Property Details")
    details = [
        ("Sub-locality", form["sublocality"]), ("Location", form["location"]),
        ("Property type", form["ptype"]), ("Area", f"{form['area']} sq.ft"),
        ("Bedrooms", form["bedrooms"]), ("Bathrooms", form["bathrooms"]),
        ("Stories", form["stories"]), ("Age", f"{form['age']} years"),
        ("Furnishing", form["furnish"]),
    ]
    c.setFont("DejaVuSans", 11)
    for k, v in details:
        c.drawString(x_margin, y, f"{k}:")
        c.drawString(x_margin + 55 * mm, y, str(v))
        y -= 7  # line step, mirrors the spacing used in the original JS report
    y -= 4
    line(y); y -= 16

    # ---- Predicted value ----
    heading("Predicted Market Value")
    c.setFont("DejaVuSerif-Bold", 18)
    c.setFillColor(colors.Color(0.59, 0.43, 0.12))
    c.drawString(x_margin, y, fmt_inr(predicted))
    y -= 20
    c.setFont("DejaVuSans", 10.5)
    c.setFillColor(colors.black)
    c.drawString(x_margin, y, f"Model R-squared: {meta['r2']*100:.1f}%  |  Mean abs. error: {fmt_inr_short(meta['mae'])}")
    y -= 16

    # ---- Top drivers ----
    heading("Top Value Drivers (SHAP)", size=12)
    for con in contribs[:6]:
        sign = "+" if con["value"] >= 0 else ""
        body(f"{con['label']}: {sign}{fmt_inr_short(con['value'])}")
    y -= 4
    line(y); y -= 16

    # ---- Forecast ----
    check_page_break()
    heading("5-Year Forecast", size=12)
    for pt in forecast:
        label = "Today" if pt["year"] == 0 else f"Year {pt['year']}"
        body(f"{label}: {fmt_inr_short(pt['value'])}")
    y -= 4
    check_page_break()
    line(y); y -= 16

    # ---- Facilities ----
    heading("Market & Facilities Summary", size=12)
    for t in [
        f"Demand index: {loc['demand_index']:.0f}/100 ({loc['growth_rate_zone']})",
        f"Location convenience score: {loc['location_convenience_score']:.0f}/100",
        f"Nearest school: {loc['nearest_school']} ({loc['distance_to_school_km']:.1f} km)",
        f"Nearest hospital: {loc['nearest_hospital']} ({loc['distance_to_hospital_km']:.1f} km)",
        f"Nearest transit: {loc['nearest_transit_station']} ({loc['distance_to_transit_km']:.1f} km)",
    ]:
        body(t)
    y -= 4
    check_page_break()
    line(y); y -= 16

    # ---- Recommendation ----
    heading("Buying & Negotiation Recommendation", size=12)
    verdict_colors = {
        "buy": colors.Color(0.24, 0.61, 0.51),
        "avoid": colors.Color(0.82, 0.38, 0.29),
        "wait": colors.Color(0.78, 0.6, 0.24),
    }
    c.setFont("DejaVuSans-Bold", 13)
    c.setFillColor(verdict_colors.get(rec["verdict"], colors.black))
    c.drawString(x_margin, y, rec["verdict"].upper())
    y -= 18
    c.setFillColor(colors.black)
    for r in rec["reasons"]:
        body(f"- {r}")
    body(f"Suggested negotiation price: {fmt_inr_short(rec['negotiation'])}")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()
