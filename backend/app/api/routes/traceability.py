"""Public B2C traceability: the QR code and the page a shopper lands on.

These endpoints are deliberately unauthenticated - they are what a consumer
reaches by scanning the pack in a shop. They expose only label information that
is already printed on the packaging, never the manufacturer's account data.
"""

import io
import json

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

import models
from app.services import nutrition
from database import get_db

router = APIRouter(prefix="/api/public", tags=["traceability"])

DISPOSAL_GUIDANCE = {
    True: {  # recyclable
        "action": "Recycle",
        "detail": "Empty and rinse the pack, then place it in dry waste for recycling.",
    },
    False: {
        "action": "Dry waste",
        "detail": ("This is a multi-layer laminate and cannot go into the regular "
                   "recycling stream. Place it in dry waste, or return it through an "
                   "EPR collection point if one is available near you."),
    },
}


def _label_or_404(db: Session, trace_code: str) -> models.ProductLabel:
    label = (db.query(models.ProductLabel)
             .filter(models.ProductLabel.trace_code == trace_code).first())
    if not label:
        raise HTTPException(status_code=404, detail="Unknown trace code.")
    return label


@router.get("/trace/{trace_code}")
def public_trace(trace_code: str, db: Session = Depends(get_db)):
    """The 'eat or not' summary plus disposal instructions."""
    label = _label_or_404(db, trace_code)

    try:
        tl = json.loads(label.traffic_light_json) if label.traffic_light_json else None
    except json.JSONDecodeError:
        tl = None

    inr = nutrition.indian_nutrition_rating(
        energy_kcal=label.energy_kcal, saturated_fat=label.saturated_fat,
        total_sugar=label.total_sugar, sodium_mg=label.sodium_mg,
        protein=label.protein, fibre=label.fibre,
        fvnl_percent=label.fvnl_percent or 0.0)

    summary = nutrition.consumer_summary(tl, inr) if tl else None

    if label.compostable:
        disposal = {"action": "Compost",
                    "detail": ("This pack is industrially compostable. Use a certified "
                               "composting facility - it will not break down in a "
                               "landfill or a home compost heap.")}
    else:
        disposal = DISPOSAL_GUIDANCE[bool(label.recyclable)]

    return dict(
        product=dict(
            name=label.product_name, brand=label.brand,
            net_quantity=label.net_quantity, is_veg=label.is_veg,
            manufacturer=label.manufacturer, fssai_licence=label.fssai_licence,
            ingredients=label.ingredients,
        ),
        health=dict(
            inr_stars=label.inr_stars, summary=summary, traffic_lights=tl,
            nutrition_per_100=dict(
                energy_kcal=label.energy_kcal, protein=label.protein,
                carbohydrate=label.carbohydrate, total_sugar=label.total_sugar,
                fat=label.fat, saturated_fat=label.saturated_fat,
                trans_fat=label.trans_fat, fibre=label.fibre,
                sodium_mg=label.sodium_mg,
            ),
        ),
        packaging=dict(
            material=label.packaging_material,
            recyclable=label.recyclable, compostable=label.compostable,
            disposal=disposal,
        ),
        compliance_status=label.compliance_status,
    )


@router.get("/trace/{trace_code}/qr.png")
def trace_qr(trace_code: str, base_url: str = "", db: Session = Depends(get_db)):
    """PNG QR code pointing at the public trace page, for placing on the die-line."""
    _label_or_404(db, trace_code)
    try:
        import qrcode
    except ImportError:
        raise HTTPException(status_code=503,
                            detail="qrcode is not installed on the server.")

    target = f"{base_url.rstrip('/')}/trace/{trace_code}" if base_url \
        else f"/api/public/trace/{trace_code}"

    qr = qrcode.QRCode(version=None, box_size=8, border=2,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(target)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png",
                    headers={"Cache-Control": "public, max-age=3600"})
