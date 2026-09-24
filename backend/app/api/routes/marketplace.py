"""Module 6 - B2B packaging marketplace: vendors, RFQs, quotes, POs, Kanban."""

import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import auth
import models
from app.services import dieline_gen, marketplace
from database import get_db

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


def _require_supplier(user: models.User):
    if user.role != "supplier":
        raise HTTPException(status_code=403,
                            detail="This action is for supplier accounts.")


def _my_vendor(db: Session, user: models.User) -> models.Vendor:
    vendor = (db.query(models.Vendor)
              .filter(models.Vendor.owner_user_id == user.id).first())
    if not vendor:
        raise HTTPException(status_code=404,
                            detail="No vendor profile yet. Create one with "
                                   "POST /api/marketplace/vendor.")
    return vendor


# ============================== browse ==============================

@router.get("/vendors")
def list_vendors(material_code: Optional[str] = None, quantity: int = 10000,
                 eco_only: bool = False, db: Session = Depends(get_db)):
    """Browse vendors, or match them against a recommended material."""
    if material_code:
        return {"vendors": marketplace.match_vendors(db, material_code, quantity, eco_only)}

    rows = db.query(models.Vendor).all()
    out = []
    for v in rows:
        if eco_only and not v.eco_friendly:
            continue
        products = (db.query(models.VendorProduct)
                    .filter(models.VendorProduct.vendor_id == v.id).all())
        out.append(dict(
            vendor_id=v.id, vendor_name=v.name, location=v.location,
            rating=v.rating, reviews=v.reviews, fssai_verified=v.fssai_verified,
            eco_friendly=v.eco_friendly, lead_time_days=v.lead_time_days,
            about=v.about,
            products=[dict(id=p.id, title=p.title, material_code=p.material_code,
                           structure=p.structure, thickness_um=p.thickness_um,
                           min_order_qty=p.min_order_qty, in_stock=p.in_stock,
                           price_per_unit=marketplace.price_at_quantity(p, quantity))
                      for p in products],
        ))
    return {"vendors": out}


@router.get("/price-curve")
def price_curve(material_code: str, db: Session = Depends(get_db)):
    """Market price at each MOQ break - the data behind the pricing histogram."""
    return marketplace.price_curve(
        db, material_code, [5000, 10000, 25000, 50000, 100000, 250000])


# ============================== vendor side ==============================

class VendorIn(BaseModel):
    name: str
    location: Optional[str] = ""
    about: Optional[str] = ""
    eco_friendly: bool = False
    lead_time_days: int = 14


@router.post("/vendor")
def upsert_vendor(body: VendorIn, db: Session = Depends(get_db),
                  current_user: models.User = Depends(auth.get_current_user)):
    _require_supplier(current_user)
    vendor = (db.query(models.Vendor)
              .filter(models.Vendor.owner_user_id == current_user.id).first())
    if vendor is None:
        vendor = models.Vendor(owner_user_id=current_user.id)
        db.add(vendor)

    vendor.name = body.name
    vendor.location = body.location
    vendor.about = body.about
    vendor.eco_friendly = body.eco_friendly
    vendor.lead_time_days = body.lead_time_days
    # Verified status is earned through KYC, never self-declared
    vendor.fssai_verified = current_user.kyc_status == "verified"
    db.commit()
    db.refresh(vendor)
    return dict(vendor_id=vendor.id, name=vendor.name,
                fssai_verified=vendor.fssai_verified)


class ProductIn(BaseModel):
    material_code: str
    title: str
    structure: Optional[str] = ""
    thickness_um: Optional[float] = None
    min_order_qty: int = 10000
    lead_time_days: int = 14
    in_stock: bool = True
    tier1_qty: int = 10000
    tier1_price: float
    tier2_qty: int = 50000
    tier2_price: Optional[float] = None
    tier3_qty: int = 100000
    tier3_price: Optional[float] = None


@router.post("/inventory")
def add_product(body: ProductIn, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    """Add a SKU to the vendor's catalogue with tiered MOQ pricing."""
    _require_supplier(current_user)
    vendor = _my_vendor(db, current_user)

    material = (db.query(models.PackagingMaterial)
                .filter(models.PackagingMaterial.code == body.material_code).first())
    if not material:
        raise HTTPException(status_code=400,
                            detail=f"Unknown material code '{body.material_code}'.")

    product = models.VendorProduct(
        vendor_id=vendor.id, material_code=body.material_code, title=body.title,
        structure=body.structure, thickness_um=body.thickness_um,
        min_order_qty=body.min_order_qty, lead_time_days=body.lead_time_days,
        in_stock=body.in_stock,
        price_tier1_qty=body.tier1_qty, price_tier1_per_unit=body.tier1_price,
        price_tier2_qty=body.tier2_qty, price_tier2_per_unit=body.tier2_price,
        price_tier3_qty=body.tier3_qty, price_tier3_per_unit=body.tier3_price,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return dict(product_id=product.id, title=product.title)


@router.get("/inventory")
def my_inventory(db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    _require_supplier(current_user)
    vendor = _my_vendor(db, current_user)
    rows = (db.query(models.VendorProduct)
            .filter(models.VendorProduct.vendor_id == vendor.id).all())
    return {"vendor": vendor.name, "products": [
        dict(id=p.id, title=p.title, material_code=p.material_code,
             structure=p.structure, thickness_um=p.thickness_um,
             min_order_qty=p.min_order_qty, in_stock=p.in_stock,
             tiers=[dict(qty=p.price_tier1_qty, price=p.price_tier1_per_unit),
                    dict(qty=p.price_tier2_qty, price=p.price_tier2_per_unit),
                    dict(qty=p.price_tier3_qty, price=p.price_tier3_per_unit)])
        for p in rows]}


# ============================== RFQ ==============================

class RFQIn(BaseModel):
    report_id: Optional[int] = None
    product_name: str
    material_code: str
    material_name: Optional[str] = ""
    required_otr: Optional[float] = None
    required_wvtr: Optional[float] = None
    thickness_um: Optional[float] = None
    width_mm: float = 150
    height_mm: float = 250
    gusset_mm: float = 60
    quantity: int = 10000
    target_price_per_unit: Optional[float] = None
    notes: Optional[str] = ""
    attach_dieline: bool = True


@router.post("/rfq")
def create_rfq(body: RFQIn, db: Session = Depends(get_db),
               current_user: models.User = Depends(auth.get_current_user)):
    """Raise an RFQ straight from a recommendation.

    The technical specification and the generated die-line travel with the
    request, which is the whole point: a vendor receives a quotable package
    rather than a vague enquiry.
    """
    svg = None
    if body.attach_dieline:
        geo = dieline_gen.compute_geometry(body.width_mm, body.height_mm, body.gusset_mm)
        svg = dieline_gen.generate_dieline_svg(
            geometry=geo, product_name=body.product_name,
            material_name=body.material_name or "")

    rfq = models.RFQ(
        buyer_user_id=current_user.id, report_id=body.report_id,
        product_name=body.product_name, material_code=body.material_code,
        material_name=body.material_name, required_otr=body.required_otr,
        required_wvtr=body.required_wvtr, thickness_um=body.thickness_um,
        width_mm=body.width_mm, height_mm=body.height_mm, gusset_mm=body.gusset_mm,
        quantity=body.quantity, target_price_per_unit=body.target_price_per_unit,
        dieline_svg=svg, notes=body.notes, status="open",
    )
    db.add(rfq)
    db.commit()
    db.refresh(rfq)

    matched = marketplace.match_vendors(db, body.material_code, body.quantity)
    return dict(rfq_id=rfq.id, status=rfq.status,
                matched_vendors=[m["vendor_name"] for m in matched],
                matched_count=len(matched),
                dieline_attached=svg is not None)


@router.get("/rfqs")
def list_rfqs(db: Session = Depends(get_db),
              current_user: models.User = Depends(auth.get_current_user)):
    """Buyers see their own RFQs; suppliers see open RFQs they can supply."""
    if current_user.role == "supplier":
        vendor = _my_vendor(db, current_user)
        codes = [p.material_code for p in db.query(models.VendorProduct)
                 .filter(models.VendorProduct.vendor_id == vendor.id).all()]
        rows = (db.query(models.RFQ)
                .filter(models.RFQ.material_code.in_(codes or [""]),
                        models.RFQ.status == "open").all())
    else:
        rows = (db.query(models.RFQ)
                .filter(models.RFQ.buyer_user_id == current_user.id)
                .order_by(models.RFQ.created_at.desc()).all())

    return {"rfqs": [
        dict(id=r.id, product_name=r.product_name, material_code=r.material_code,
             material_name=r.material_name, quantity=r.quantity,
             dimensions=f"{r.width_mm}x{r.height_mm}mm gusset {r.gusset_mm}mm",
             required_otr=r.required_otr, required_wvtr=r.required_wvtr,
             target_price_per_unit=r.target_price_per_unit, status=r.status,
             quote_count=db.query(models.Quote).filter(models.Quote.rfq_id == r.id).count(),
             created_at=r.created_at.isoformat() if r.created_at else None)
        for r in rows]}


@router.get("/rfq/{rfq_id}/dieline.svg")
def rfq_dieline(rfq_id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    from fastapi import Response
    rfq = db.query(models.RFQ).filter(models.RFQ.id == rfq_id).first()
    if not rfq or not rfq.dieline_svg:
        raise HTTPException(status_code=404, detail="No die-line on this RFQ.")
    return Response(content=rfq.dieline_svg, media_type="image/svg+xml")


# ============================== quotes ==============================

class QuoteIn(BaseModel):
    rfq_id: int
    price_per_unit: float
    moq: int = 10000
    lead_time_days: int = 14
    validity_days: int = 30
    tooling_cost: float = 0.0
    notes: Optional[str] = ""


@router.post("/quote")
def submit_quote(body: QuoteIn, db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    _require_supplier(current_user)
    vendor = _my_vendor(db, current_user)

    rfq = db.query(models.RFQ).filter(models.RFQ.id == body.rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found.")
    if rfq.status not in ("open", "quoted"):
        raise HTTPException(status_code=400, detail=f"RFQ is {rfq.status}.")

    quote = models.Quote(
        rfq_id=rfq.id, vendor_id=vendor.id, price_per_unit=body.price_per_unit,
        moq=body.moq, lead_time_days=body.lead_time_days,
        validity_days=body.validity_days, tooling_cost=body.tooling_cost,
        notes=body.notes, status="submitted",
    )
    db.add(quote)
    rfq.status = "quoted"
    db.commit()
    db.refresh(quote)
    return dict(quote_id=quote.id, rfq_id=rfq.id, status=quote.status)


@router.get("/rfq/{rfq_id}/quotes")
def compare_quotes(rfq_id: int, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    """Side-by-side comparison, including the landed cost with tooling amortised."""
    rfq = db.query(models.RFQ).filter(models.RFQ.id == rfq_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found.")
    if rfq.buyer_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your RFQ.")

    rows = db.query(models.Quote).filter(models.Quote.rfq_id == rfq_id).all()
    out = []
    for q in rows:
        vendor = db.query(models.Vendor).filter(models.Vendor.id == q.vendor_id).first()
        qty = max(rfq.quantity or q.moq, q.moq)
        landed = q.price_per_unit + ((q.tooling_cost or 0) / qty if qty else 0)
        out.append(dict(
            quote_id=q.id, vendor_id=q.vendor_id,
            vendor_name=vendor.name if vendor else None,
            vendor_rating=vendor.rating if vendor else None,
            fssai_verified=vendor.fssai_verified if vendor else False,
            price_per_unit=q.price_per_unit, moq=q.moq,
            tooling_cost=q.tooling_cost,
            landed_cost_per_unit=round(landed, 3),
            order_value=round(landed * qty, 2),
            lead_time_days=q.lead_time_days, validity_days=q.validity_days,
            notes=q.notes, status=q.status,
        ))
    out.sort(key=lambda q: q["landed_cost_per_unit"])
    if out:
        out[0]["best_price"] = True
    return dict(rfq_id=rfq_id, quantity=rfq.quantity, quotes=out)


# ============================== purchase orders ==============================

class POIn(BaseModel):
    quote_id: int
    quantity: Optional[int] = None
    expected_delivery_days: int = 21


@router.post("/purchase-order")
def raise_po(body: POIn, db: Session = Depends(get_db),
             current_user: models.User = Depends(auth.get_current_user)):
    quote = db.query(models.Quote).filter(models.Quote.id == body.quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    rfq = db.query(models.RFQ).filter(models.RFQ.id == quote.rfq_id).first()
    if not rfq or rfq.buyer_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your RFQ.")

    qty = body.quantity or rfq.quantity or quote.moq
    if qty < quote.moq:
        raise HTTPException(
            status_code=400,
            detail=f"Quantity {qty} is below this vendor's MOQ of {quote.moq}.")

    po = models.PurchaseOrder(
        po_number=marketplace.new_po_number(), quote_id=quote.id, rfq_id=rfq.id,
        buyer_user_id=current_user.id, vendor_id=quote.vendor_id,
        quantity=qty, price_per_unit=quote.price_per_unit,
        total_value=round(quote.price_per_unit * qty + (quote.tooling_cost or 0), 2),
        status="placed",
        expected_delivery=datetime.datetime.utcnow() + datetime.timedelta(
            days=body.expected_delivery_days),
    )
    db.add(po)
    quote.status = "accepted"
    rfq.status = "awarded"
    for other in db.query(models.Quote).filter(
            models.Quote.rfq_id == rfq.id, models.Quote.id != quote.id).all():
        other.status = "rejected"
    db.commit()
    db.refresh(po)
    return dict(po_number=po.po_number, po_id=po.id, quantity=po.quantity,
                total_value=po.total_value, status=po.status)


class POMoveIn(BaseModel):
    status: str
    note: Optional[str] = ""


@router.patch("/purchase-order/{po_id}")
def move_po(po_id: int, body: POMoveIn, db: Session = Depends(get_db),
            current_user: models.User = Depends(auth.get_current_user)):
    po = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found.")

    allowed = po.buyer_user_id == current_user.id
    if not allowed and current_user.role == "supplier":
        vendor = (db.query(models.Vendor)
                  .filter(models.Vendor.owner_user_id == current_user.id).first())
        allowed = vendor is not None and vendor.id == po.vendor_id
    if not allowed:
        raise HTTPException(status_code=403, detail="Not your order.")

    ok, message = marketplace.advance_po(po, body.status)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    po.status_note = body.note
    db.commit()
    return dict(po_number=po.po_number, status=po.status, message=message)


@router.get("/board")
def kanban_board(db: Session = Depends(get_db),
                 current_user: models.User = Depends(auth.get_current_user)):
    """Order tracking board, scoped to the caller's side of the transaction."""
    return marketplace.kanban(db, current_user)
