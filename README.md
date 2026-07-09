# PropValuate AI — Streamlit App



## Structure
```
propvaluate_app/
├── app.py                    # Main Streamlit app (all 11 stages as tabs)
├── train_model.py            # Trains & tunes the XGBoost model (run once first)
├── requirements.txt
├── Housing_full_enriched_clean.csv
└── utils/
    ├── preprocessing.py       # Stage 3: cleaning, encoding, feature selection
    ├── explain.py             # Stage 5: real SHAP (TreeExplainer)
    ├── forecast.py            # Stage 6: trend-based future value projection
    ├── heatmap.py              # Stage 7: folium market heatmap
    ├── facilities.py           # Stage 8: nearby facilities + convenience score
    ├── recommendation.py       # Stage 9: Buy / Wait / Avoid logic
    ├── chatbot.py              # Stage 10: Anthropic API-powered assistant
    └── pdf_report.py           # Stage 11: colored PDF report generator
```

## Setup
```bash
cd propvaluate_app
pip install -r requirements.txt

# Train the model once (creates artifacts/ folder)
python train_model.py --data Housing_full_enriched_clean.csv

# Launch the app
streamlit run app.py
```


## Model Performance (from last training run)
| Set | MAE | RMSE | MAPE | R² | Accuracy (100−MAPE) |
|---|---|---|---|---|---|
| Validation | Rs 4,51,193 | Rs 6,53,706 | 8.85% | 0.857 | 91.15% |
| Final Test | Rs 5,10,312 | Rs 8,51,861 | 10.61% | 0.856 | 89.39% |
