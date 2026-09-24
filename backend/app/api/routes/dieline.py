"""Module 5 - die-line geometry, artwork and cost recalculation."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

import auth
import models
from app.services import dieline_gen
from database import get_db

router = APIRouter(prefix="/api/dieline", tags=["dieline"])


class DielineIn(BaseModel):
    width_mm: float = 150
    height_mm: float = 250
    gusset_mm: float = 60

    product_name: str = "Product Name"
    brand: Optional[str] = ""
    net_quantity: Optional[str] = "250 g"
    fssai_licence: Optional[str] = "10000000000000"
    ingredients: Optional[str] = ""
    is_veg: bool = True
    inr_stars: Optional[float] = None
    manufacturer: Optional[str] = ""
    material_code: Optional[str] = None
    material_name: Optional[str] = ""
    best_before: Optional[str] = "Best before 9 months from packaging"


def _validate(body: DielineIn):
    if not (40 <= body.width_mm <= 600):
        raise HTTPException(status_code=400, detail="width_mm must be 40-600.")
    if not (60 <= body.height_mm <= 900):
        raise HTTPException(status_code=400, detail="height_mm must be 60-900.")
    if not (0 <= body.gusset_mm <= body.height_mm):
        raise HTTPException(status_code=400,
                            detail="gusset_mm must be between 0 and height_mm.")


def _cost_for(db: Session, material_code: Optional[str], geometry: dict):
    if not material_code:
        return None
    material = (db.query(models.PackagingMaterial)
                .filter(models.PackagingMaterial.code == material_code).first())
    if not material:
        return None
    return dieline_gen.material_cost(geometry, material.cost_per_m2)


@router.post("/geometry")
def geometry(body: DielineIn, db: Session = Depends(get_db),
             current_user: models.User = Depends(auth.get_current_user)):
    """Flat-web dimensions, film consumption and the recalculated unit cost.

    This is the endpoint the dimension sliders call: every change of width,
    height or gusset changes the film area and therefore the cost per pouch.
    """
    _validate(body)
    geo = dieline_gen.compute_geometry(body.width_mm, body.height_mm, body.gusset_mm)
    return dict(geometry=geo, cost=_cost_for(db, body.material_code, geo))


@router.post("/svg")
def dieline_svg(body: DielineIn, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """Print-ready SVG die-line with the FSSAI label elements placed."""
    _validate(body)
    geo = dieline_gen.compute_geometry(body.width_mm, body.height_mm, body.gusset_mm)
    svg = dieline_gen.generate_dieline_svg(
        geometry=geo, product_name=body.product_name, brand=body.brand or "",
        net_quantity=body.net_quantity or "", fssai_licence=body.fssai_licence or "",
        ingredients=body.ingredients or "", is_veg=body.is_veg,
        inr_stars=body.inr_stars, manufacturer=body.manufacturer or "",
        material_name=body.material_name or "", best_before=body.best_before or "",
    )
    return Response(content=svg, media_type="image/svg+xml",
                    headers={"Content-Disposition":
                             f'inline; filename="dieline-{int(body.width_mm)}x'
                             f'{int(body.height_mm)}.svg"'})


@router.post("/pdf")
def dieline_pdf(body: DielineIn, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """True-scale PDF of the same die-line."""
    _validate(body)
    geo = dieline_gen.compute_geometry(body.width_mm, body.height_mm, body.gusset_mm)
    pdf = dieline_gen.generate_dieline_pdf(geo, product_name=body.product_name)
    if pdf is None:
        raise HTTPException(
            status_code=503,
            detail="reportlab is not installed on the server. Use /api/dieline/svg, "
                   "which is equally print-ready vector artwork.")
    return Response(content=pdf, media_type="application/pdf",
                    headers={"Content-Disposition":
                             f'attachment; filename="dieline-{int(body.width_mm)}x'
                             f'{int(body.height_mm)}.pdf"'})
