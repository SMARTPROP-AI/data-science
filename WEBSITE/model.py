"""
model.py — Core valuation engine for PropValuate AI.

This is a direct Python port of the tree-evaluation and business logic that
used to live in app.js. It reads the same model.json / meta.json / sub_stats.json
/ heatmap.json that the JS frontend used (extracted from the original data.js),
so predictions are identical to the old client-side version — just computed
on the server now.
"""
import json
import math
from pathlib import Path
from functools import lru_cache

DATA_DIR = Path(__file__).parent / "data"

FEATURE_LABELS = {
    "local_market_index": "Local market index", "location_c": "Location",
    "area": "Area (sq.ft)", "demand_index": "Area demand index",
    "airconditioning_b": "Air conditioning", "bathrooms": "Bathrooms",
    "furnish_c": "Furnishing", "parking": "Parking", "basement_b": "Basement",
    "stories": "Stories", "distance_to_hospital_km": "Distance to hospital",
    "mainroad_b": "Main road access", "property_age_years": "Property age",
    "distance_to_school_km": "Distance to school", "ptype_c": "Property type",
    "prefarea_b": "Preferred area", "distance_to_supermarket_km": "Distance to supermarket",
    "guestroom_b": "Guest room", "distance_to_transit_km": "Distance to transit",
    "distance_to_park_km": "Distance to park", "location_convenience_score": "Convenience score",
    "hotwaterheating_b": "Hot water heating", "bedrooms": "Bedrooms",
}


class ValuationEngine:
    def __init__(self):
        self.model = json.loads((DATA_DIR / "model.json").read_text())
        self.meta = json.loads((DATA_DIR / "meta.json").read_text())
        self.sub_stats = json.loads((DATA_DIR / "sub_stats.json").read_text())
        self.heatmap = json.loads((DATA_DIR / "heatmap.json").read_text())
        # index trees' children by nodeid for O(1) lookup instead of .find()
        for tree in self.model["trees"]:
            self._index_children(tree)

    def _index_children(self, node):
        if "children" in node:
            node["_by_id"] = {c["nodeid"]: c for c in node["children"]}
            for c in node["children"]:
                self._index_children(c)

    # ---------- XGBoost tree evaluator ----------
    def _eval_tree(self, node, feats):
        if "leaf" in node:
            return node["leaf"]
        v = feats.get(node["split"])
        if v is None or (isinstance(v, float) and math.isnan(v)):
            v = float("-inf")  # mimic missing-goes-default handling loosely
        target_id = node["yes"] if v < node["split_condition"] else node["no"]
        child = node["_by_id"][target_id]
        return self._eval_tree(child, feats)

    def predict_raw(self, feats: dict) -> float:
        total = self.model["base_score"]
        for tree in self.model["trees"]:
            total += self._eval_tree(tree, feats)
        return total

    # ---------- Build feature vector from form input ----------
    def build_features(self, form: dict) -> dict:
        sub = self.sub_stats[form["location"]][form["sublocality"]]
        return {
            "area": form["area"], "bedrooms": form["bedrooms"], "bathrooms": form["bathrooms"],
            "stories": form["stories"], "parking": form["parking"],
            "property_age_years": form["age"],
            "mainroad_b": int(form["mainroad"]), "guestroom_b": int(form["guestroom"]),
            "basement_b": int(form["basement"]), "hotwaterheating_b": int(form["hotwater"]),
            "airconditioning_b": int(form["ac"]), "prefarea_b": int(form["prefarea"]),
            "location_c": self.meta["loc_map"][form["location"]],
            "ptype_c": self.meta["ptype_map"][form["ptype"]],
            "furnish_c": self.meta["furnish_map"][form["furnish"]],
            "distance_to_school_km": sub["distance_to_school_km"],
            "distance_to_hospital_km": sub["distance_to_hospital_km"],
            "distance_to_supermarket_km": sub["distance_to_supermarket_km"],
            "distance_to_transit_km": sub["distance_to_transit_km"],
            "distance_to_park_km": sub["distance_to_park_km"],
            "location_convenience_score": sub["location_convenience_score"],
            "demand_index": sub["demand_index"],
            "local_market_index": sub["local_market_index"],
        }, sub

    # ---------- Approx SHAP-like marginal contributions ----------
    def compute_contributions(self, feats: dict, top_n: int = 8):
        baseline = dict(self.meta["feature_means"])
        base_pred = self.predict_raw(baseline)
        contribs = []
        for key in baseline:
            perturbed = dict(baseline)
            perturbed[key] = feats[key]
            p = self.predict_raw(perturbed)
            contribs.append({
                "key": key,
                "label": FEATURE_LABELS.get(key, key),
                "value": p - base_pred,
            })
        contribs.sort(key=lambda c: -abs(c["value"]))
        return base_pred, contribs[:top_n]

    # ---------- Forecast ----------
    def compute_forecast(self, predicted: float, growth_zone: str):
        rate = self.meta["growth_rates"].get(growth_zone, 0.05)
        return [{"year": y, "value": predicted * ((1 + rate) ** y)} for y in range(6)]

    # ---------- Typical/comparable property in this area ----------
    def compute_comparable_prediction(self, loc: dict) -> float:
        baseline = dict(self.meta["feature_means"])
        baseline["location_c"] = self.meta["loc_map"][loc["location"]]
        for k in ("distance_to_school_km", "distance_to_hospital_km", "distance_to_supermarket_km",
                  "distance_to_transit_km", "distance_to_park_km", "location_convenience_score",
                  "demand_index", "local_market_index"):
            baseline[k] = loc[k]
        return self.predict_raw(baseline)

    # ---------- Buy / Wait / Avoid recommendation ----------
    def compute_recommendation(self, predicted: float, loc: dict):
        comparable = self.compute_comparable_prediction(loc)
        diff_pct = (predicted - comparable) / comparable
        rate = self.meta["growth_rates"].get(loc["growth_rate_zone"], 0.05)
        high_demand = loc["demand_index"] >= 65
        reasons = []

        if diff_pct <= -0.06 and loc["growth_rate_zone"] != "Stable":
            verdict = "buy"
            reasons.append(f"Priced {abs(diff_pct*100):.1f}% below a typical property in {loc['sublocality']}, {loc['location']}.")
            reasons.append(f"{loc['growth_rate_zone']} zone — projected ~{rate*100:.0f}% annual appreciation.")
        elif diff_pct >= 0.10:
            verdict = "wait" if high_demand else "avoid"
            reasons.append(f"Priced {diff_pct*100:.1f}% above a typical property in this area — limited room to negotiate.")
            reasons.append(f"Demand is still high (index {loc['demand_index']:.0f}/100), so it may settle with time."
                            if high_demand else f"Demand index is only {loc['demand_index']:.0f}/100 in this micro-market.")
        else:
            verdict = "wait"
            sign = "+" if diff_pct >= 0 else ""
            reasons.append(f"Priced close to a typical property here ({sign}{diff_pct*100:.1f}% vs. the area norm).")
            reasons.append(f"{loc['growth_rate_zone']} zone with demand index {loc['demand_index']:.0f}/100 — no urgency either way.")

        reasons.append(f"Location convenience score: {loc['location_convenience_score']:.0f}/100.")
        if loc.get("estimated"):
            reasons.append(f"Note: no sampled listings within a few km of {loc['sublocality']} — figures lean on nearby-area interpolation.")

        negotiation = predicted * (0.90 if verdict == "avoid" else 0.96 if verdict == "wait" else 0.985)
        return {
            "verdict": verdict, "reasons": reasons, "negotiation": negotiation,
            "diff_pct": diff_pct, "comparable": comparable,
        }

    # ---------- Full pipeline used by /api/valuate ----------
    def run_valuation(self, form: dict):
        feats, loc = self.build_features(form)
        predicted = self.predict_raw(feats)
        base_pred, contribs = self.compute_contributions(feats)
        forecast = self.compute_forecast(predicted, loc["growth_rate_zone"])
        rec = self.compute_recommendation(predicted, loc)
        return {
            "predicted": predicted,
            "contributions": contribs,
            "forecast": forecast,
            "recommendation": rec,
            "location": loc,
            "form": form,
        }


@lru_cache
def get_engine() -> "ValuationEngine":
    return ValuationEngine()
