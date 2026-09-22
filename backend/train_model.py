import pandas as pd
import numpy as np
import joblib
import random
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

print("1. Generating synthetic FSSAI packaging dataset (10,000 rows)...")

base_profiles = [
    {"fssai_cat": "Beverages", "is_liquid": 1, "ph": 3.2, "process": "Hot Fill", "shelf_life": 90, "lipid": "Low", "moisture": 90.0,
     "material": "Hot-Fill PET Bottle", "barrier": "Medium", "gas": "None", "cost": 3.80, "epr": 90},
    {"fssai_cat": "Beverages", "is_liquid": 1, "ph": 4.5, "process": "Aseptic / Cold Fill", "shelf_life": 180, "lipid": "Low", "moisture": 95.0,
     "material": "Aseptic Brick Carton (6-Layer)", "barrier": "Ultra-High", "gas": "None", "cost": 4.20, "epr": 65},
    {"fssai_cat": "Dairy products", "is_liquid": 1, "ph": 6.7, "process": "Retort Sterilization", "shelf_life": 240, "lipid": "Medium", "moisture": 88.0,
     "material": "4-Ply Retort Pouch", "barrier": "Ultra-High", "gas": "None", "cost": 5.20, "epr": 30},
    {"fssai_cat": "Fats and oils", "is_liquid": 1, "ph": 5.5, "process": "Standard Ambient Fill", "shelf_life": 180, "lipid": "High", "moisture": 0.5,
     "material": "HDPE Rigid Bottle", "barrier": "High O2", "gas": "Nitrogen Blanket", "cost": 3.10, "epr": 85},
    {"fssai_cat": "Ready-to-eat savouries", "is_liquid": 0, "ph": 6.0, "process": "None", "shelf_life": 120, "lipid": "High", "moisture": 2.5,
     "material": "Metallized PET / PE Pouch", "barrier": "High O2", "gas": "N2 Flush (99%)", "cost": 2.60, "epr": 45},
    {"fssai_cat": "Confectionery", "is_liquid": 0, "ph": 6.2, "process": "None", "shelf_life": 365, "lipid": "Medium", "moisture": 1.2,
     "material": "3-Ply Aluminum Foil Laminate", "barrier": "Ultra-High Moisture", "gas": "None", "cost": 3.40, "epr": 35},
    {"fssai_cat": "Bakery products", "is_liquid": 0, "ph": 5.8, "process": "None", "shelf_life": 14, "lipid": "Low", "moisture": 22.0,
     "material": "Micro-perforated BOPP Film", "barrier": "Breathable", "gas": "Equilibrium MAP", "cost": 1.10, "epr": 75},
    {"fssai_cat": "Cereals and pulses", "is_liquid": 0, "ph": 6.5, "process": "None", "shelf_life": 180, "lipid": "Low", "moisture": 11.0,
     "material": "Mono-layer LDPE Pouch", "barrier": "Low", "gas": "None", "cost": 1.40, "epr": 90},
]

dataset = []
for _ in range(10000):
    base = random.choice(base_profiles).copy()
    base["shelf_life"] = int(np.clip(base["shelf_life"] + np.random.normal(0, 20), 5, 730))
    base["moisture"] = round(np.clip(base["moisture"] + np.random.normal(0, 2.0), 0.1, 99.9), 1)
    if base["is_liquid"] == 1:
        base["ph"] = round(np.clip(base["ph"] + np.random.normal(0, 0.5), 2.0, 8.5), 1)
    base["cost"] = round(np.clip(base["cost"] + np.random.normal(0, 0.4), 0.5, 10.0), 2)
    dataset.append(base)

df = pd.DataFrame(dataset)

print("2. Preprocessing Data...")
feature_cols = ["fssai_cat", "is_liquid", "ph", "process", "shelf_life", "lipid", "moisture"]
X = df[feature_cols]

y_clf = df[["material", "barrier", "gas"]]
y_reg = df[["cost", "epr"]]

cat_cols = ["fssai_cat", "process", "lipid"]
num_cols = ["is_liquid", "ph", "shelf_life", "moisture"]

preprocessor = ColumnTransformer(transformers=[
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols)
])

clf_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42))
])

reg_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("regressor", RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42))
])

print("3. Training Models (This takes a few seconds)...")
clf_pipeline.fit(X, y_clf)
reg_pipeline.fit(X, y_reg)

print("4. Saving perfectly compatible models...")
joblib.dump(clf_pipeline, "packaging_classifier.pkl")
joblib.dump(reg_pipeline, "packaging_regressor.pkl")

print("Done! You can now restart your FastAPI server.")