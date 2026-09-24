"""Module 3 - formulation, nutrition and compliance endpoints."""

import json
import secrets
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

import auth
import models
from app.services import compliance, nutrition, ocr_parser
from database import get_db

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


# ---------------------------------------------------------------- schemas
class AdditiveIn(BaseModel):
    name: str
    level_ppm: Optional[float] = None


class PreservativeCheck(BaseModel):
    additives: List[AdditiveIn] = []
    raw_text: Optional[str] = None
    fssai_category: str = ""
    is_infant_food: bool = False


class NutritionIn(BaseModel):
    energy_kcal: Optional[float] = None
    protein: Optional[float] = None
    carbohydrate: Optional[float] = None
    total_sugar: Optional[float] = None
    fat: Optional[float] = None
    saturated_fat: Optional[float] = None
    trans_fat: Optional[float] = None
    fibre: Optional[float] = None
    sodium_mg: Optional[float] = None
    salt: Optional[float] = None
    fvnl_percent: float = 0.0
    is_liquid: bool = False


class LabelIn(BaseModel):
    product_name: str
    brand: Optional[str] = ""
    fssai_category: Optional[str] = ""
    fssai_licence: Optional[str] = ""
    is_veg: bool = True
    net_quantity: Optional[str] = "250 g"
    ingredients: Optional[str] = ""
    manufacturer: Optional[str] = ""
    nutrition: NutritionIn
    report_id: Optional[int] = None
    packaging_material: Optional[str] = ""
    recyclable: bool = False
    compostable: bool = False


# ---------------------------------------------------------------- endpoints
@router.post("/preservatives")
def check_preservatives(body: PreservativeCheck,
                        current_user: models.User = Depends(auth.get_current_user)):
    """Screen additives against the FSSAI permitted list and category ceilings."""
    additives = [a.model_dump() for a in body.additives]
    if body.raw_text:
        additives += compliance.parse_additive_text(body.raw_text)
    if not additives:
        raise HTTPException(status_code=400,
                            detail="Supply either 'additives' or 'raw_text'.")
    return compliance.validate_additives(
        additives, category=body.fssai_category, is_infant_food=body.is_infant_food)


@router.post("/nutrition")
def analyse_nutrition(body: NutritionIn,
                      current_user: models.User = Depends(auth.get_current_user)):
    """Traffic-light bands and the Indian Nutrition Rating for a set of macros."""
    salt = body.salt
    if salt is None and body.sodium_mg is not None:
        salt = round(body.sodium_mg * 2.5 / 1000.0, 3)

    tl = nutrition.traffic_lights(
        fat=body.fat, saturates=body.saturated_fat, sugars=body.total_sugar,
        salt=salt, sodium_mg=body.sodium_mg, is_liquid=body.is_liquid)

    inr = nutrition.indian_nutrition_rating(
        energy_kcal=body.energy_kcal, saturated_fat=body.saturated_fat,
        total_sugar=body.total_sugar, sodium_mg=body.sodium_mg,
        protein=body.protein, fibre=body.fibre,
        fvnl_percent=body.fvnl_percent, is_beverage=body.is_liquid)

    return dict(traffic_lights=tl, inr=inr,
                consumer_summary=nutrition.consumer_summary(tl, inr))


@router.post("/ocr")
async def ocr_nutrition_panel(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user),
):
    """Read a nutrition panel photograph.

    If the Tesseract binary is unavailable the response says so and stays a 200,
    so the client can fall back to the paste-text route rather than showing an error.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty upload.")

    result = ocr_parser.ocr_image(content)
    if not result["ok"]:
        return dict(ok=False, ocr_available=False, message=result["message"],
                    fallback="POST the panel text to /api/compliance/parse-text instead.",
                    parsed=None)

    parsed = ocr_parser.parse_nutrition_text(result["text"])
    return dict(ok=True, ocr_available=True, message=result["message"],
                raw_text=result["text"], parsed=parsed)


class TextIn(BaseModel):
    text: str


@router.post("/parse-text")
def parse_panel_text(body: TextIn,
                     current_user: models.User = Depends(auth.get_current_user)):
    """Parse a pasted or typed nutrition panel. Works without Tesseract."""
    return ocr_parser.parse_nutrition_text(body.text)


@router.get("/ocr-status")
def ocr_status():
    available, detail = ocr_parser.tesseract_available()
    return dict(available=available, detail=detail)


@router.post("/label")
def create_label(body: LabelIn,
                 db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    """Persist a finished label and mint its public traceability code."""
    n = body.nutrition
    salt = n.salt
    if salt is None and n.sodium_mg is not None:
        salt = round(n.sodium_mg * 2.5 / 1000.0, 3)

    tl = nutrition.traffic_lights(
        fat=n.fat, saturates=n.saturated_fat, sugars=n.total_sugar,
        salt=salt, sodium_mg=n.sodium_mg, is_liquid=n.is_liquid)
    inr = nutrition.indian_nutrition_rating(
        energy_kcal=n.energy_kcal, saturated_fat=n.saturated_fat,
        total_sugar=n.total_sugar, sodium_mg=n.sodium_mg, protein=n.protein,
        fibre=n.fibre, fvnl_percent=n.fvnl_percent, is_beverage=n.is_liquid)

    additives = compliance.parse_additive_text(body.ingredients or "")
    verdict = compliance.validate_additives(additives, category=body.fssai_category or "")

    label = models.ProductLabel(
        user_id=current_user.id,
        report_id=body.report_id,
        trace_code=secrets.token_urlsafe(8),
        product_name=body.product_name, brand=body.brand,
        fssai_category=body.fssai_category, fssai_licence=body.fssai_licence,
        is_veg=body.is_veg, net_quantity=body.net_quantity,
        ingredients=body.ingredients, manufacturer=body.manufacturer,
        energy_kcal=n.energy_kcal, protein=n.protein, carbohydrate=n.carbohydrate,
        total_sugar=n.total_sugar, fat=n.fat, saturated_fat=n.saturated_fat,
        trans_fat=n.trans_fat, fibre=n.fibre, sodium_mg=n.sodium_mg,
        fvnl_percent=n.fvnl_percent,
        inr_stars=inr["stars"], traffic_light_json=json.dumps(tl),
        compliance_status=verdict["overall"],
        packaging_material=body.packaging_material,
        recyclable=body.recyclable, compostable=body.compostable,
    )
    db.add(label)
    db.commit()
    db.refresh(label)

    return dict(
        label_id=label.id,
        trace_code=label.trace_code,
        trace_url=f"/api/public/trace/{label.trace_code}",
        inr=inr, traffic_lights=tl, compliance=verdict,
    )


@router.get("/labels")
def my_labels(db: Session = Depends(get_db),
              current_user: models.User = Depends(auth.get_current_user)):
    rows = (db.query(models.ProductLabel)
            .filter(models.ProductLabel.user_id == current_user.id)
            .order_by(models.ProductLabel.created_at.desc()).all())
    return {"labels": [
        dict(id=r.id, product_name=r.product_name, brand=r.brand,
             trace_code=r.trace_code, inr_stars=r.inr_stars,
             compliance_status=r.compliance_status,
             created_at=r.created_at.isoformat() if r.created_at else None)
        for r in rows
    ]}
