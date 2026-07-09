"""
app.py
Pr input stream corruptedopValuate AI - Streamlit frontend.
Run with: streamlit run app.py
"""
import os
import joblib
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from utils.preprocessing import full_pipeline_transform
from utils.explain import get_shap_explanation
from utils.forecast import project_future_value
from utils.heatmap import build_market_heatmap, city_summary
from utils.facilities import find_nearby_facilities
from utils.recommendation import buying_recommendation
from utils.chatbot import ask_property_assistant
from utils.pdf_report import generate_report

st.set_page_config(page_title="PropValuate AI", page_icon="🏠", layout="wide")

ARTIFACT_DIR = "artifacts"


@st.cache_resource
def load_artifacts():
    model = joblib.load(f"{ARTIFACT_DIR}/xgb_model.pkl")
    encoders = joblib.load(f"{ARTIFACT_DIR}/encoders.pkl")
    feature_cols = joblib.load(f"{ARTIFACT_DIR}/feature_cols.pkl")
    reference_data = joblib.load(f"{ARTIFACT_DIR}/reference_data.pkl")
    return model, encoders, feature_cols, reference_data


try:
    model, encoders, feature_cols, reference_data = load_artifacts()
except FileNotFoundError:
    st.error("Model artifacts not found. Run `python train_model.py --data <your_csv>` first.")
    st.stop()

st.title("🏠 PropValuate AI")
st.caption("AI-Based Automated Property Valuation System")

# ---------------------------------------------------------
# 2. USER PROPERTY DETAILS INPUT
# ---------------------------------------------------------
st.sidebar.header("Property Details")
locations = sorted(reference_data["location"].unique())
location = st.sidebar.selectbox("Location", locations)
area = st.sidebar.number_input("Area (sq.ft)", min_value=200, value=2400)
bedrooms = st.sidebar.number_input("Bedrooms (BHK)", min_value=1, max_value=8, value=3)
bathrooms = st.sidebar.number_input("Bathrooms", min_value=1, max_value=6, value=2)
stories = st.sidebar.number_input("Stories", min_value=1, max_value=4, value=2)
parking = st.sidebar.number_input("Parking spaces", min_value=0, max_value=4, value=1)
age = st.sidebar.number_input("Property age (years)", min_value=0, max_value=60, value=8)
property_type = st.sidebar.selectbox("Property type", ["Apartment", "Independent House", "Villa"])
furnishing = st.sidebar.selectbox("Furnishing", ["furnished", "semi-furnished", "unfurnished"])

st.sidebar.subheader("Amenities")
mainroad = st.sidebar.checkbox("Main road access", value=True)
guestroom = st.sidebar.checkbox("Guest room")
basement = st.sidebar.checkbox("Basement")
hotwaterheating = st.sidebar.checkbox("Hot water heating")
airconditioning = st.sidebar.checkbox("Air conditioning", value=True)
prefarea = st.sidebar.checkbox("Preferred area")

st.sidebar.subheader("Budget")
budget = st.sidebar.number_input("Your budget (Rs)", min_value=0, value=6000000)

st.sidebar.subheader("AI Assistant (optional)")
api_key_input = st.sidebar.text_input("Anthropic API key", type="password",
                                       help="Only needed for the AI Assistant tab. Not stored.")

run_btn = st.sidebar.button("Generate Valuation", type="primary")

# ---------------------------------------------------------
# 3. DATA PREPROCESSING (build one-row input frame)
# ---------------------------------------------------------
def build_input_row():
    subset = reference_data[reference_data["location"] == location]
    lookup_row = subset.iloc[0] if not subset.empty else reference_data.iloc[0]

    comp_match = reference_data[
        (reference_data["location"] == location) & (reference_data["bedrooms"] == bedrooms)
    ]
    comp_price = comp_match["price"].mean() if not comp_match.empty else \
        reference_data[reference_data["location"] == location]["price"].mean()

    row = {
        "area": area, "bedrooms": bedrooms, "bathrooms": bathrooms, "stories": stories,
        "mainroad": "yes" if mainroad else "no", "guestroom": "yes" if guestroom else "no",
        "basement": "yes" if basement else "no", "hotwaterheating": "yes" if hotwaterheating else "no",
        "airconditioning": "yes" if airconditioning else "no", "parking": parking,
        "prefarea": "yes" if prefarea else "no", "furnishingstatus": furnishing,
        "location": location, "property_age_years": age, "property_type": property_type,
        "local_market_index": lookup_row["local_market_index"],
        "comparable_sale_price": comp_price,
        "sale_date": pd.Timestamp.today().strftime("%Y-%m-%d"),
        "age_band": ("0-5yrs" if age <= 5 else "6-15yrs" if age <= 15 else "16-30yrs" if age <= 30 else "31-45yrs"),
        "latitude": lookup_row["latitude"], "longitude": lookup_row["longitude"],
        "demand_index": lookup_row["demand_index"], "growth_rate_zone": lookup_row["growth_rate_zone"],
    }
    return pd.DataFrame([row]), comp_price


# ---------------------------------------------------------
# MAIN TABS
# ---------------------------------------------------------
tabs = st.tabs([
    "💰 Prediction", "🔍 Explainability", "📈 Forecast", "🗺️ Market Heatmap",
    "📍 Nearby Facilities", "🧭 Buy/Wait/Avoid", "🤖 AI Assistant", "📄 PDF Report",
])

if run_btn:
    input_df, comp_price = build_input_row()
    X_input = full_pipeline_transform(input_df, encoders, feature_cols,
                                       reference_date=pd.Timestamp.today())
    predicted_price = float(model.predict(X_input)[0])
    mape_err = 0.093
    low, high = predicted_price * (1 - mape_err), predicted_price * (1 + mape_err)

    st.session_state["predicted_price"] = predicted_price
    st.session_state["price_range"] = (low, high)
    st.session_state["X_input"] = X_input
    st.session_state["comp_price"] = comp_price
    st.session_state["property_details"] = {
        "Location": location, "Area": f"{area} sqft", "Bedrooms": bedrooms,
        "Bathrooms": bathrooms, "Type": property_type, "Age": f"{age} yrs", "Furnishing": furnishing,
    }

# ---- 4. Prediction tab ----
with tabs[0]:
    st.header("House Price Prediction (XGBoost)")
    if "predicted_price" in st.session_state:
        p = st.session_state["predicted_price"]
        low, high = st.session_state["price_range"]
        st.metric("Estimated Market Value", f"Rs {p:,.0f}")
        st.caption(f"Likely range: Rs {low:,.0f} - Rs {high:,.0f}  (±9.3% avg. model error)")
    else:
        st.info("Fill in property details in the sidebar and click **Generate Valuation**.")

# ---- 5. Explainability tab ----
with tabs[1]:
    st.header("Explainable AI (SHAP)")
    if "X_input" in st.session_state:
        contribs, base_value = get_shap_explanation(model, st.session_state["X_input"])
        st.caption(f"Base value (average model prediction): Rs {base_value:,.0f}")
        for name, val in contribs:
            color = "green" if val >= 0 else "red"
            st.markdown(f"**{name}**: :{color}[{'+' if val>=0 else ''}{val:,.0f}]")
    else:
        st.info("Generate a valuation first.")

# ---- 6. Forecast tab ----
with tabs[2]:
    st.header("Future Price Forecast")
    st.warning("⚠️ Trend-based projection only — this dataset has no repeated-property "
               "time series, so a real Prophet/ARIMA/LSTM model cannot be trained on it.")
    if "predicted_price" in st.session_state:
        fc = project_future_value(st.session_state["predicted_price"], location)
        st.caption(f"Assumed annual appreciation for {location}: {fc['rate_used']*100:.1f}%")
        st.session_state["forecast"] = fc
        st.table(pd.DataFrame(list(fc["projection"].items()), columns=["Year", "Projected Value (Rs)"]))
    else:
        st.info("Generate a valuation first.")

# ---- 7. Market Heatmap tab ----
with tabs[3]:
    st.header("Market Heatmap Analysis")
    st.caption("Demand heatmap + growth-zone markers across all cities in the dataset.")
    fmap = build_market_heatmap(reference_data)
    st_folium(fmap, width=900, height=500)
    st.subheader("City Summary")
    st.session_state["city_summary_df"] = city_summary(reference_data)
    st.dataframe(st.session_state["city_summary_df"])

# ---- 8. Nearby Facilities tab ----
with tabs[4]:
    st.header("Nearby Facilities Analysis")
    facilities, convenience = find_nearby_facilities(reference_data, location, area, bedrooms)
    st.session_state["facilities"] = facilities
    st.session_state["convenience_score"] = convenience
    st.metric("Location Convenience Score", f"{convenience:.0f} / 100")
    cols = st.columns(len(facilities))
    icons = {"School": "🏫", "Hospital": "🏥", "Supermarket": "🛒", "Bus/Metro Station": "🚉", "Park": "🌳"}
    for col, (label, info) in zip(cols, facilities.items()):
        with col:
            st.markdown(f"### {icons.get(label,'')} {label}")
            st.write(info["name"])
            st.caption(f"{info['distance_km']:.2f} km away")

# ---- 9. Buy/Wait/Avoid tab ----
with tabs[5]:
    st.header("Smart Buying & Negotiation Recommendation")
    if all(k in st.session_state for k in ["predicted_price", "comp_price", "forecast", "convenience_score"]):
        rec = buying_recommendation(
            st.session_state["predicted_price"], st.session_state["comp_price"],
            list(st.session_state["forecast"]["projection"].values())[-1],
            reference_data[reference_data["location"] == location]["demand_index"].mean(),
            st.session_state["convenience_score"],
        )
        st.session_state["recommendation"] = rec
        badge_color = {"BUY": "green", "WAIT": "orange", "AVOID": "red"}[rec["decision"]]
        st.markdown(f"## :{badge_color}[{rec['decision']}]")
        st.write(rec["rationale"])
        st.metric("Suggested negotiation price", f"Rs {rec['suggested_negotiation_price']:,.0f}")
    else:
        st.info("Visit the Prediction, Forecast, and Nearby Facilities tabs first (or just click Generate Valuation).")

# ---- 10. AI Assistant tab ----
with tabs[6]:
    st.header("AI Real Estate Assistant")
    st.caption("Powered by the Anthropic API. Requires your own API key (sidebar). "
               "Each question sent here uses real API credits on that key.")
    question = st.text_input("Ask about this property (e.g. 'Is this a good investment?')")
    if st.button("Ask Assistant"):
        if "predicted_price" not in st.session_state:
            st.warning("Generate a valuation first so the assistant has context.")
        else:
            context = {
                "predicted_price": st.session_state["predicted_price"],
                "comparable_price": st.session_state.get("comp_price"),
                "location": location, "area": area, "bedrooms": bedrooms,
                "recommendation": st.session_state.get("recommendation"),
            }
            answer = ask_property_assistant(question, context, api_key="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")

# ---- 11. PDF Report tab ----
with tabs[7]:
    st.header("PDF Valuation Report")
    if st.button("Generate PDF Report"):
        required = ["predicted_price", "price_range", "X_input", "forecast", "facilities",
                    "convenience_score", "recommendation", "city_summary_df", "property_details"]
        if not all(k in st.session_state for k in required):
            st.warning("Please visit all tabs (Prediction, Forecast, Heatmap, Facilities, "
                       "Buy/Wait/Avoid) before generating the report.")
        else:
            contribs, _ = get_shap_explanation(model, st.session_state["X_input"])
            city_row = st.session_state["city_summary_df"].loc[location].to_dict()
            out_path = "PropValuate_Valuation_Report.pdf"
            generate_report(
                out_path,
                st.session_state["property_details"],
                st.session_state["predicted_price"],
                st.session_state["price_range"],
                contribs,
                st.session_state["forecast"],
                city_row,
                st.session_state["facilities"],
                st.session_state["convenience_score"],
                st.session_state["recommendation"],
            )
            with open(out_path, "rb") as f:
                st.download_button("⬇ Download PDF Report", f, file_name=out_path, mime="application/pdf")
