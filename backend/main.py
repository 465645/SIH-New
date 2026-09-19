from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="PackGenius Local Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PackagingRequest(BaseModel):
    product_name: str
    fssai_category: str
    shelf_life_days: int
    moisture_content: Optional[float] = None
    lipid_content: Optional[str] = None
    is_liquid: bool
    ph_level: Optional[float] = None
    filling_process: Optional[str] = None

@app.get("/")
def health_check():
    return {"status": "Local ML Engine Live", "version": "4.0"}

# Local Rule-Based Decision Model
def predict_packaging(req: PackagingRequest):
    material = "Standard Mono-layer PE Pouch"
    cost = 1.50
    score = 80
    barrier = "Low"
    gas = "None"

    fssai_lower = req.fssai_category.lower()

    # 1. Liquid Packaging Logic
    if req.is_liquid:
        if req.filling_process and "Aseptic" in req.filling_process:
            material = "6-Layer Aseptic Carton (Paperboard/Alu/PE)"
            cost = 4.20
            score = 65
            barrier = "Ultra-High"
        elif req.filling_process and "Hot Fill" in req.filling_process:
            material = "Hot-Fill PET Bottle (Heat Set)"
            cost = 3.80
            score = 90
            barrier = "Medium"
        elif req.filling_process and "Retort" in req.filling_process:
            material = "4-Ply Retort Pouch (PET/ALU/NYLON/CPP)"
            cost = 5.50
            score = 30
            barrier = "Ultra-High"
        else:
            material = "HDPE Rigid Bottle"
            cost = 2.50
            score = 85
            barrier = "Medium"
            
        # High acidity (low pH) liquids need better inert barriers
        if req.ph_level and req.ph_level < 4.0:
            barrier = "High (Acid Resistant)"

    # 2. Solid/Dry Packaging Logic
    else:
        # High Fat/Lipid content requires Oxygen barrier to prevent rancidity
        if req.lipid_content and "High" in req.lipid_content:
            material = "Metallized PET / PE Laminate"
            cost = 2.80
            score = 45
            barrier = "High O2"
            gas = "N2 Flush (Nitrogen)"
        
        # High moisture sensitivity or long shelf life
        elif req.shelf_life_days > 180 or (req.moisture_content and req.moisture_content < 5.0):
            material = "3-Ply Foil Laminate (PET/ALU/PE)"
            cost = 3.50
            score = 35
            barrier = "Ultra-High Moisture"
        
        # Fresh produce / Bakery
        elif "bakery" in fssai_lower or "fruits" in fssai_lower:
            material = "Micro-perforated BOPP Film"
            cost = 1.20
            score = 75
            barrier = "Breathable"
            gas = "Equilibrium MAP"

    return {
        "optimal_material": material,
        "estimated_cost_per_unit": cost,
        "epr_green_score": score,
        "barrier_requirement": barrier,
        "map_gas": gas
    }


@app.post("/api/analyze")
def analyze_packaging(req: PackagingRequest):
    try:
        # Generate prediction locally
        ai_data = predict_packaging(req)
        
        return {
            "status": "success",
            "data": ai_data
        }
    except Exception as e:
        print(f"Local Engine Error: {e}")
        return {"status": "error", "message": "Failed to generate recommendation"}