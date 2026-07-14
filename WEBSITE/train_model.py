import pandas as pd, numpy as np, json
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import r2_score, mean_absolute_error
import xgboost as xgb

df = pd.read_csv('/mnt/user-data/uploads/1783659962212_Housing_full_enriched_clean.csv')

bin_cols = ['mainroad','guestroom','basement','hotwaterheating','airconditioning','prefarea']
for c in bin_cols:
    df[c+'_b'] = (df[c]=='yes').astype(int)

locations = sorted(df['location'].unique().tolist())
ptypes = sorted(df['property_type'].unique().tolist())
furnish = sorted(df['furnishingstatus'].unique().tolist())

loc_map = {l:i for i,l in enumerate(locations)}
pt_map = {p:i for i,p in enumerate(ptypes)}
fn_map = {f:i for i,f in enumerate(furnish)}

df['location_c'] = df['location'].map(loc_map)
df['ptype_c'] = df['property_type'].map(pt_map)
df['furnish_c'] = df['furnishingstatus'].map(fn_map)

feature_cols = ['area','bedrooms','bathrooms','stories','parking','property_age_years',
                'mainroad_b','guestroom_b','basement_b','hotwaterheating_b','airconditioning_b','prefarea_b',
                'location_c','ptype_c','furnish_c','distance_to_school_km','distance_to_hospital_km',
                'distance_to_supermarket_km','distance_to_transit_km','distance_to_park_km',
                'location_convenience_score','demand_index','local_market_index']

X = df[feature_cols]
y = df['price']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

params = {
    'max_depth':[3,4,5],
    'n_estimators':[80,120],
    'learning_rate':[0.05,0.1],
}
base = xgb.XGBRegressor(random_state=42, objective='reg:squarederror')
grid = GridSearchCV(base, params, cv=4, scoring='r2', n_jobs=-1)
grid.fit(X_train, y_train)
model = grid.best_estimator_
print("Best params:", grid.best_params_)

pred = model.predict(X_test)
r2 = r2_score(y_test, pred)
mae = mean_absolute_error(y_test, pred)
print(f"R2={r2:.4f} MAE={mae:.0f}")

import shap
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)
mean_abs_shap = np.abs(shap_values).mean(axis=0)
importance = dict(zip(feature_cols, mean_abs_shap.tolist()))
importance = dict(sorted(importance.items(), key=lambda x:-x[1]))
print("Feature importance (mean |SHAP|):")
for k,v in importance.items():
    print(f"  {k}: {v:.1f}")

model.save_model('model.json')
print("Saved model.json")

meta = {
    'feature_cols': feature_cols,
    'locations': locations,
    'loc_map': loc_map,
    'ptype_map': pt_map,
    'furnish_map': fn_map,
    'importance': importance,
    'r2': r2,
    'mae': mae,
    'base_value': float(explainer.expected_value),
    'feature_means': X.mean().to_dict(),
}
with open('meta.json','w') as f:
    json.dump(meta, f, indent=2)
print("Saved meta.json")
