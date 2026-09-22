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
from database import engine, get_db

# Create database tables
models.Base.metadata.create_all(bind=engine)

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

class PackagingRequest(BaseModel):
    product_name: str
    fssai_category: str
    shelf_life_days: int
    moisture_content: Optional[float] = 10.0
    lipid_content: Optional[str] = "Low"
    is_liquid: bool
    ph_level: Optional[float] = 7.0
    filling_process: Optional[str] = "None"

# --- AUTHENTICATION ENDPOINTS ---
@app.post("/api/signup", status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- PACKAGING AI ENDPOINTS ---
@app.post("/api/analyze")
def analyze_packaging(
    req: PackagingRequest, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) # Secures the endpoint
):
    if not classifier or not regressor:
        raise HTTPException(status_code=500, detail="ML Models are not initialized.")

    input_data = pd.DataFrame([{
        "fssai_cat": req.fssai_category if req.fssai_category else "Beverages",
        "is_liquid": 1 if req.is_liquid else 0,
        "ph": req.ph_level if req.ph_level is not None else 7.0,
        "process": req.filling_process if req.filling_process else "None",
        "shelf_life": req.shelf_life_days,
        "lipid": req.lipid_content if req.lipid_content else "Low",
        "moisture": req.moisture_content if req.moisture_content is not None else 10.0
    }])

    try:
        pred_class = classifier.predict(input_data)[0]
        pred_numeric = regressor.predict(input_data)[0]
        
        material = str(pred_class[0])
        barrier = str(pred_class[1])
        gas = str(pred_class[2])
        cost = round(float(pred_numeric[0]), 2)
        score = int(round(float(pred_numeric[1])))

        # Save to Database with the User's ID
        db_report = models.PackagingReport(
            user_id=current_user.id,
            product_name=req.product_name,
            fssai_category=req.fssai_category,
            shelf_life_days=req.shelf_life_days,
            is_liquid=req.is_liquid,
            optimal_material=material,
            barrier_requirement=barrier,
            map_gas=gas,
            estimated_cost_per_unit=cost,
            epr_green_score=score
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)

        return {
            "status": "success",
            "report_id": db_report.id,
            "data": {
                "optimal_material": material,
                "barrier_requirement": barrier,
                "map_gas": gas,
                "estimated_cost_per_unit": cost,
                "epr_green_score": score
            }
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/reports")
def get_reports(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user) # Secures the endpoint
):
    # Only return reports that belong to the logged-in user
    reports = db.query(models.PackagingReport).filter(models.PackagingReport.user_id == current_user.id).order_by(models.PackagingReport.created_at.desc()).all()
    return {"reports": reports}