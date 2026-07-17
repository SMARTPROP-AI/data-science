"""
main.py — PropValuate AI backend (FastAPI).

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload
Then open http://127.0.0.1:8000
"""
import re
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles

from model import get_engine
from schemas import ValuationRequest, ChatRequest
from pdf_report import build_pdf, fmt_inr_short

BASE_DIR = Path(__file__).parent

app = FastAPI(title="PropValuate AI")

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def index():
    # index.html has no template variables, so it's served directly rather
    # than through Jinja2 — one less moving part, one less thing to break.
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/api/health")
def health():
    """Quick diagnostic: confirms the model/data files loaded and reports counts."""
    try:
        engine = get_engine()
        return {
            "status": "ok",
            "locations_loaded": len(engine.meta["locations"]),
            "trees_loaded": len(engine.model["trees"]),
            "heatmap_points": len(engine.heatmap),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/api/meta")
def get_meta():
    """Everything the frontend needs to build the form dropdowns and the ticker stats."""
    engine = get_engine()
    meta = engine.meta
    heatmap = engine.heatmap
    avg_psf = sum(p["price_per_sqft"] for p in heatmap) / len(heatmap)
    avg_demand = sum(p["demand_index"] for p in heatmap) / len(heatmap)
    return {
        "locations": meta["locations"],
        "furnish": meta["furnish"],
        "city_ptypes": meta["city_ptypes"],
        "city_tier": meta.get("city_tier", {}),
        "sub_stats": engine.sub_stats,
        "r2": meta["r2"],
        "mae": meta["mae"],
        "avg_price_per_sqft": round(avg_psf),
        "avg_demand": round(avg_demand),
        "cities_count": len(meta["locations"]),
    }


@app.get("/api/heatmap")
def get_heatmap():
    return get_engine().heatmap


@app.post("/api/valuate")
def valuate(req: ValuationRequest):
    engine = get_engine()
    try:
        result = engine.run_valuation(req.model_dump())
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unknown option: {e}")
    return result


@app.post("/api/pdf-report")
def pdf_report(req: ValuationRequest):
    """Runs the valuation fresh and streams back a PDF — this is the fix for
    the old 'Download PDF report' button, now generated server-side so it
    can never fail due to a missing/misnamed JS library in the browser."""
    engine = get_engine()
    try:
        result = engine.run_valuation(req.model_dump())
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unknown option: {e}")

    pdf_bytes = build_pdf(result, engine.meta)
    filename = f"PropValuate_Report_{req.sublocality}_{req.location}.pdf".replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Rule-based assistant, ported from chatRespond() in the old app.js."""
    m = req.message.lower()
    v = req.valuation
    if not v or "predicted" not in v:
        return {"reply": "Run a valuation first (fill the form and hit 'Estimate value') and I'll be able to answer questions about your specific property."}

    predicted = v["predicted"]
    loc = v["location"]
    rec = v["recommendation"]
    forecast = v["forecast"]
    contribs = v["contributions"]

    def fmt(n):
        return fmt_inr_short(n)

    if re.search(r"price|value|worth|cost", m):
        reply = f"The estimated market value is {fmt(predicted)}, based on comparable sales in {loc['sublocality']}, {loc['location']}."
    elif re.search(r"forecast|future|5 year|next year|appreciat", m):
        yr5 = forecast[5]["value"]
        growth_pct = ((yr5 / predicted) - 1) * 100
        reply = f"In {loc['growth_rate_zone'].lower()} conditions, the model projects {fmt(yr5)} in 5 years — about {growth_pct:.0f}% total growth."
    elif re.search(r"buy|wait|avoid|recommend|should i", m):
        reply = f"My read: {rec['verdict'].upper()}. {rec['reasons'][0]}"
    elif re.search(r"negotiat|offer|discount", m):
        reply = f"A reasonable opening offer would be around {fmt(rec['negotiation'])}, versus a typical property price of {fmt(rec['comparable'])} in this area."
    elif re.search(r"school|hospital|park|transit|metro|market|facilit|nearby", m):
        reply = (f"Nearest school: {loc['nearest_school']} ({loc['distance_to_school_km']:.1f}km). "
                 f"Nearest hospital: {loc['nearest_hospital']} ({loc['distance_to_hospital_km']:.1f}km). "
                 f"Convenience score: {loc['location_convenience_score']:.0f}/100.")
    elif re.search(r"demand", m):
        reply = f"{loc['sublocality']}, {loc['location']} has a demand index of {loc['demand_index']:.0f}/100, in a {loc['growth_rate_zone'].lower()} zone."
    elif re.search(r"why|explain|factor|shap", m):
        top3 = ", ".join(c["label"].lower() for c in contribs[:3])
        reply = f"The biggest drivers for this estimate were {top3}. See the \"Why this price\" panel for the full breakdown."
    else:
        reply = f"I can help with the price, 5-year forecast, buy/wait/avoid recommendation, negotiation range, or nearby facilities for {loc['sublocality']}, {loc['location']} — what would you like to know?"

    return {"reply": reply}
