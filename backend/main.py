import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

import models
import auth
from database import engine, get_db, SessionLocal
from app.data.migrate import add_missing_columns
from app.data.seed_db import seed_materials, material_dicts
from app.services import expert_engine, marketplace as marketplace_service
from app.api.routes import account, compliance as compliance_routes
from app.api.routes import dieline, marketplace as marketplace_routes, traceability

# Create database tables, then add any columns the models have grown
models.Base.metadata.create_all(bind=engine)
_added = add_missing_columns(engine)
if _added:
    print(f"Schema updated: added {', '.join(_added)}")

# Load the packaging material catalogue into the database
with SessionLocal() as _db:
    _changes = seed_materials(_db)
    _count = _db.query(models.PackagingMaterial).count()
    _vendors = marketplace_service.seed_vendors(_db)
    _vendor_count = _db.query(models.Vendor).count()
print(f"Material catalogue ready: {_count} materials ({_changes} fields written).")
print(f"Marketplace ready: {_vendor_count} vendors ({_vendors} rows written).")

app = FastAPI(title="PackGenius ML Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML Models
try:
    classifier = joblib.load("packaging_classifier.pkl")
    regressor = joblib.load("packaging_regressor.pkl")
    print("Scikit-Learn models loaded successfully.")
except Exception as e:
    print(f"Failed to load ML artifacts: {e}")
    classifier, regressor = None, None

# --- PYDANTIC SCHEMAS ---
class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[str] = "buyer"          # buyer | supplier
    company_name: Optional[str] = None
    contact_name: Optional[str] = None

class PackagingRequest(BaseModel):
    product_name: str
    fssai_category: str
    shelf_life_days: int
    moisture_content: Optional[float] = 10.0
    lipid_content: Optional[str] = "Low"
    is_liquid: bool
    ph_level: Optional[float] = 7.0
    filling_process: Optional[str] = "None"

    # Storage and supply chain (Step 3 of the wizard)
    storage_type: Optional[str] = "Ambient"          # Ambient | Cold Chain | Frozen
    relative_humidity: Optional[float] = 65.0        # % RH of the storage environment
    transit_condition: Optional[str] = "Standard Road"

    # Fresh produce
    is_fresh_produce: Optional[bool] = False
    respiration_rate: Optional[float] = None         # mg CO2/kg/h at 5 C, if measured

    # Pack format, used to convert cost per m2 into cost per unit
    fill_weight_g: Optional[float] = 250.0


def estimate_pack_area_m2(fill_weight_g: float) -> float:
    """Approximate the film area of a stand-up pouch for a given fill weight.

    Area is both faces plus a gusset allowance. These are the same standard pack
    sizes the results dashboard shows, so the cost figure matches the dimensions
    displayed next to it.
    """
    if fill_weight_g <= 100:
        w, h = 0.100, 0.150
    elif fill_weight_g <= 500:
        w, h = 0.150, 0.250
    else:
        w, h = 0.200, 0.350
    return round(2 * w * h * 1.15, 4)   # 15% gusset and seal allowance

# --- AUTHENTICATION ENDPOINTS ---
@app.post("/api/signup", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if user.role not in ("buyer", "supplier"):
        raise HTTPException(status_code=400, detail="role must be 'buyer' or 'supplier'.")

    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email, hashed_password=hashed_password,
        role=user.role, company_name=user.company_name, contact_name=user.contact_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "role": new_user.role}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- PACKAGING AI ENDPOINTS ---
def _ml_second_opinion(req: "PackagingRequest"):
    """Run the trained scikit-learn pipeline alongside the rules.

    The rule engine owns the material decision because it can explain itself.
    The ML model is kept as a corroborating second opinion: when both agree the
    confidence is higher, and when they disagree that is worth surfacing.
    """
    if not classifier or not regressor:
        return None
    frame = pd.DataFrame([{
        "fssai_cat": req.fssai_category or "Beverages",
        "is_liquid": 1 if req.is_liquid else 0,
        "ph": req.ph_level if req.ph_level is not None else 7.0,
        "process": req.filling_process or "None",
        "shelf_life": req.shelf_life_days,
        "lipid": req.lipid_content or "Low",
        "moisture": req.moisture_content if req.moisture_content is not None else 10.0,
    }])
    try:
        pred_class = classifier.predict(frame)[0]
        pred_numeric = regressor.predict(frame)[0]
        return {
            "material": str(pred_class[0]),
            "barrier": str(pred_class[1]),
            "map_gas": str(pred_class[2]),
            "cost_per_unit": round(float(pred_numeric[0]), 2),
            "epr_score": int(round(float(pred_numeric[1]))),
        }
    except Exception as exc:
        print(f"ML second opinion unavailable: {exc}")
        return None


@app.post("/api/analyze")
def analyze_packaging(
    req: PackagingRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)  # Secures the endpoint
):
    catalogue = material_dicts(db)
    if not catalogue:
        raise HTTPException(status_code=500,
                            detail="Packaging material catalogue is empty.")

    try:
        result = expert_engine.recommend(
            materials=catalogue,
            product_name=req.product_name,
            category=req.fssai_category,
            shelf_life_days=req.shelf_life_days,
            moisture_content=req.moisture_content if req.moisture_content is not None else 10.0,
            lipid_content=req.lipid_content or "Low",
            ph_level=req.ph_level,
            is_liquid=req.is_liquid,
            storage_type=req.storage_type or "Ambient",
            relative_humidity=req.relative_humidity if req.relative_humidity is not None else 65.0,
            transit_condition=req.transit_condition or "Standard Road",
            filling_process=req.filling_process or "None",
            is_fresh_produce=bool(req.is_fresh_produce),
            respiration_rate=req.respiration_rate,
        )
    except Exception as exc:
        print(f"Recommendation error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))

    spec = result["requirements"]
    picks = result["recommended"]
    map_design = result.get("map_design")

    if not picks:
        # No material in the catalogue satisfies every constraint. That is a real
        # answer, not an error: tell the user which constraints did the rejecting.
        blockers = [
            {"material": entry["name"], "reasons": entry["rejected_because"]}
            for entry in result["rejected"][:3]
        ]
        return {
            "status": "no_match",
            "message": ("No catalogued material meets every requirement. Relax the shelf "
                        "life target, the storage condition, or the sustainability constraint."),
            "requirements": spec,
            "why": result["reasons"],
            "closest_rejected": blockers,
        }

    best = picks[0]
    pack_area = estimate_pack_area_m2(req.fill_weight_g or 250.0)
    cost_per_unit = round(best["cost_per_m2"] * pack_area, 2)

    ml = _ml_second_opinion(req)
    agreement = None
    if ml:
        a, b = ml["material"].lower(), best["name"].lower()
        agreement = a in b or b in a

    barrier_label = ("Breathable (respiring produce)" if spec["needs_breathable"]
                     else f"OTR <= {spec['otr_max']} cc/m2/day")
    gas_label = map_design["initial_flush"] if map_design else "None (no MAP required)"

    db_report = models.PackagingReport(
        user_id=current_user.id,
        product_name=req.product_name,
        fssai_category=req.fssai_category,
        shelf_life_days=req.shelf_life_days,
        is_liquid=req.is_liquid,
        storage_type=req.storage_type,
        relative_humidity=req.relative_humidity,
        transit_condition=req.transit_condition,
        is_fresh_produce=bool(req.is_fresh_produce),
        optimal_material=best["name"],
        barrier_requirement=barrier_label,
        map_gas=gas_label,
        estimated_cost_per_unit=cost_per_unit,
        epr_green_score=best["epr_score"],
        required_otr=spec["otr_max"],
        required_wvtr=spec["wvtr_max"],
        specified_thickness_um=best["specified_thickness_um"],
        sealability=best["sealability"],
        respiration_rate=map_design["respiration_rate_at_storage"] if map_design else None,
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)

    return {
        "status": "success",
        "report_id": db_report.id,
        "data": {
            # --- keys the existing dashboard already renders ---
            "optimal_material": best["name"],
            "material_code": best["code"],
            "barrier_requirement": barrier_label,
            "map_gas": gas_label,
            "estimated_cost_per_unit": cost_per_unit,
            "epr_green_score": best["epr_score"],

            # --- the engineering specification ---
            "specification": {
                "otr_max_cc_m2_day": spec["otr_max"],
                "wvtr_max_g_m2_day": spec["wvtr_max"],
                "film_thickness_um": best["specified_thickness_um"],
                "achieved_otr": best["effective_otr"],
                "achieved_wvtr": best["effective_wvtr"],
                "sealability": best["sealability"],
                "mechanical_strength_mpa": best["tensile_strength_mpa"],
                "map_suitable": best["map_suitable"],
                "breathable": spec["needs_breathable"],
                "light_barrier_required": spec["light_barrier_required"],
                "retort_required": spec["needs_retort"],
            },

            # --- commercial ---
            "cost": {
                "cost_per_m2": best["cost_per_m2"],
                "pack_area_m2": pack_area,
                "cost_per_unit": cost_per_unit,
                "fill_weight_g": req.fill_weight_g,
            },

            # --- sustainability ---
            "sustainability": {
                "epr_score": best["epr_score"],
                "recyclable": best["recyclable"],
                "compostable": best["compostable"],
            },

            "material_notes": best["notes"],
            "fit_note": best.get("fit_note"),
            "over_specified": best.get("over_specified", False),
        },
        "why": result["reasons"],
        "alternatives": picks[1:],
        "rejected": result["rejected"],
        "map_design": map_design,
        "ml_second_opinion": ({**ml, "agrees_with_rules": agreement} if ml else None),
    }


@app.get("/api/materials")
def list_materials(db: Session = Depends(get_db)):
    """The packaging material reference database, for browsing and comparison."""
    return {"materials": material_dicts(db)}


@app.get("/api/reports")
def get_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) # Secures the endpoint
):
    # Only return reports that belong to the logged-in user
    reports = db.query(models.PackagingReport).filter(models.PackagingReport.user_id == current_user.id).order_by(models.PackagingReport.created_at.desc()).all()
    return {"reports": reports}


# --- FEATURE MODULES ---
app.include_router(account.router)                 # roles, KYC
app.include_router(compliance_routes.router)       # preservatives, nutrition, labels
app.include_router(dieline.router)                 # die-line geometry and artwork
app.include_router(marketplace_routes.router)      # vendors, RFQ, quotes, POs
app.include_router(traceability.router)            # public QR trace pages
