# PropValuate AI — Python Backend (FastAPI)

This is the full Python rewrite of PropValuate AI. The valuation model,
SHAP-style explanations, forecast, recommendation logic, and — importantly —
the **PDF report generation** all run on the server now, in Python, instead
of in the browser. This fixes the original "Download PDF report" bug for
good: it can't break due to a missing or misnamed JS library, because there
is no client-side PDF library anymore.

## Project layout

```
main.py              → FastAPI app: routes for the page, valuation, PDF, chat
model.py             → Valuation engine: XGBoost tree evaluator + business logic
schemas.py           → Pydantic request models
pdf_report.py         → Server-side PDF generation (ReportLab)
data/
  model.json          → Trained XGBoost trees (exported from train_model.py's model.json)
  meta.json           → Feature maps, growth rates, R²/MAE, dropdown options
  sub_stats.json       → Per-sublocality stats (distances, demand, convenience score)
  heatmap.json        → All properties for the map view
templates/
  index.html          → The page (served as a static file — no template variables needed)
static/
  app.js              → Frontend logic; now calls the FastAPI backend instead of embedding data
  style.css           → Unchanged design
  leaflet.js/.css      → Map library
train_model.py         → Retrains the model from the housing CSV (unchanged from before)
requirements.txt       → Python dependencies
```

## Running it

1. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
4. Open **http://127.0.0.1:8000** in your browser.

That's it — no Live Server, no `file://` quirks, no separate library files
to keep in sync. Everything (page, styles, scripts, model, and PDF) is
served by this one FastAPI app.

## API endpoints

| Method | Path              | Purpose                                                        |
|--------|-------------------|------------------------------------------------------------------|
| GET    | `/`               | Serves the page                                                  |
| GET    | `/api/meta`       | Dropdown options, sub-locality stats, model R²/MAE, ticker stats |
| GET    | `/api/heatmap`    | All properties for the map                                       |
| POST   | `/api/valuate`    | Runs a valuation, returns predicted price + explanations         |
| POST   | `/api/pdf-report` | Runs a valuation and streams back a PDF report                   |
| POST   | `/api/chat`       | Rule-based assistant answers about the last valuation            |

## Retraining the model

`train_model.py` is unchanged — it still trains the XGBoost model from the
housing CSV and writes `model.json` / `meta.json`. If you retrain, copy the
new `model.json` into `data/model.json`, and merge the printed feature
importances / R² / MAE into `data/meta.json` (the other fields in
`meta.json` — locations, sub-locality stats, growth rates, etc. — come from
a separate enrichment step, not from `train_model.py` alone).

## Why the PDF button was broken before

The old `index.html` loaded `<script src="jspdf.umd.min.js">`, but the
uploaded library file was actually named `jspdf_umd_min.js` (underscores
instead of dots). The browser 404'd silently, so `window.jspdf` was never
defined, and clicking "Download PDF report" did nothing. This Python
version sidesteps the whole class of bug: the PDF is built with ReportLab
on the server and streamed to the browser as a file download, no client-side
library required at all.

## Why the ₹ symbol looked garbled in the PDF

ReportLab's built-in Helvetica/Times fonts are Adobe's "standard 14" fonts,
which do not include the ₹ (Indian Rupee, U+20B9) glyph — so it silently
rendered as a stray superscript character instead. `pdf_report.py` now
embeds DejaVu Sans/Serif (bundled in `fonts/`), which does include ₹, and
uses them for all text in the report.

## Tier 1 / Tier 2 / Tier 3 city coverage

The location dropdown now covers 73 cities across three tiers (grouped with
`<optgroup>` in the UI):

- **Tier 1** (8): Delhi NCR, Mumbai, Bengaluru, Chennai, Hyderabad, Kolkata, Pune, Ahmedabad
- **Tier 2** (35): Coimbatore, Madurai, Kochi, plus Tiruchirappalli, Salem,
  Jaipur, Lucknow, Surat, Nagpur, Visakhapatnam, Guwahati, and 28 others
- **Tier 3** (30): Dindigul, Karur, Sivakasi, Warangal, Kolhapur, Siliguri,
  and 25 others

**Important caveat, spelled out because it matters:** the XGBoost model was
only ever trained on real transaction data for the original 10 cities
(Ahmedabad, Bengaluru, Chennai, Coimbatore, Delhi NCR, Hyderabad, Kochi,
Madurai, Mumbai, Pune). There's no real data for the ~63 newly added cities,
so `generate_city_expansion.py` does **not** invent fake "real" listings —
instead:

1. Each new city gets a tier and, purely for feeding the model's
   `location_c` feature, is mapped to a same-tier **proxy city** from the
   original 10 (Mumbai for Tier 1, Coimbatore for Tier 2, Madurai for Tier 3).
   This avoids the model extrapolating into a categorical code it never saw
   in training.
2. The features that actually carry most of the location signal — demand
   index, local market index, convenience score, and distances to
   facilities — are generated per sub-locality from tier-calibrated ranges
   (calibrated against the min/max actually observed across the real 10
   cities), with a fixed seed so results are reproducible run to run.
3. Every generated sub-locality is flagged `"estimated": true` in
   `sub_stats.json` — the app already had this mechanism (for sub-localities
   in the original cities with too few sampled listings), so the UI already
   shows an honest "modeled rather than measured" note for these areas
   without any extra frontend work.

To add real data for any of these cities later, retrain on real transactions
and re-run/extend `generate_city_expansion.py` accordingly — or just replace
the relevant entries in `sub_stats.json` directly.
