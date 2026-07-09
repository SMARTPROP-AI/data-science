"""
train_model.py
Stages 4, 5, 6, 8, 9 of the pipeline:
Train/Val/Test split -> XGBoost -> Train -> Tune -> Final test.
Run once to produce model artifacts consumed by the Streamlit app.

Usage:
    python train_model.py --data Housing_full_enriched_clean.csv
"""
import argparse
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
from xgboost import XGBRegressor

from utils.preprocessing import full_pipeline_fit

ARTIFACT_DIR = "artifacts"


def main(data_path: str):
    import os
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    raw = pd.read_csv(data_path)
    X, y, encoders, feature_cols = full_pipeline_fit(raw)

    # Train(65%) / Validation(15%) / Test(20%)
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.1875, random_state=42)

    print(f"Train: {len(X_train)}  Val: {len(X_val)}  Test: {len(X_test)}")

    param_grid = {
        "n_estimators": [200, 300, 500],
        "max_depth": [3, 4, 5],
        "learning_rate": [0.03, 0.05, 0.1],
        "subsample": [0.8, 1.0],
        "colsample_bytree": [0.8, 1.0],
    }
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    grid = GridSearchCV(
        XGBRegressor(random_state=42, verbosity=0),
        param_grid, scoring="neg_mean_absolute_error", cv=cv, n_jobs=-1,
    )
    print("Running GridSearchCV...")
    grid.fit(X_train, y_train)
    model = grid.best_estimator_
    print("Best params:", grid.best_params_)

    def report(y_true, pred, label):
        mae = mean_absolute_error(y_true, pred)
        rmse = np.sqrt(mean_squared_error(y_true, pred))
        mape = mean_absolute_percentage_error(y_true, pred) * 100
        r2 = r2_score(y_true, pred)
        acc = 100 - mape
        print(f"[{label}] MAE={mae:,.0f} RMSE={rmse:,.0f} MAPE={mape:.2f}% R2={r2:.4f} Accuracy={acc:.2f}%")
        return dict(MAE=mae, RMSE=rmse, MAPE=mape, R2=r2, Accuracy=acc)

    val_metrics = report(y_val, model.predict(X_val), "Validation")
    test_metrics = report(y_test, model.predict(X_test), "Final Test")

    joblib.dump(model, f"{ARTIFACT_DIR}/xgb_model.pkl")
    joblib.dump(encoders, f"{ARTIFACT_DIR}/encoders.pkl")
    joblib.dump(feature_cols, f"{ARTIFACT_DIR}/feature_cols.pkl")
    joblib.dump(raw, f"{ARTIFACT_DIR}/reference_data.pkl")
    pd.DataFrame([val_metrics, test_metrics], index=["validation", "test"]).to_csv(
        f"{ARTIFACT_DIR}/metrics.csv"
    )
    print(f"\nSaved artifacts to {ARTIFACT_DIR}/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="Housing_full_enriched_clean.csv")
    args = parser.parse_args()
    main(args.data)
