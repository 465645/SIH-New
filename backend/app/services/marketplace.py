"""Marketplace services: vendor matching, tiered pricing, RFQ and PO workflow."""

import datetime
import secrets
from typing import List, Optional

from sqlalchemy.orm import Session

import models
from app.data.vendors_seed import VENDORS

# Kanban columns, in order. A PO may only move to an adjacent column.
PO_STAGES = ["placed", "artwork_approval", "in_production",
             "quality_check", "dispatched", "delivered"]

PO_STAGE_LABELS = {
    "placed": "PO Placed",
    "artwork_approval": "Artwork Approval",
    "in_production": "In Production",
    "quality_check": "Quality Check",
    "dispatched": "Dispatched",
    "delivered": "Delivered",
}


# --------------------------------------------------------------------------
# Seeding
# --------------------------------------------------------------------------

def seed_vendors(db: Session) -> int:
    """Idempotent: vendors are keyed by name."""
    written = 0
    for spec in VENDORS:
        vendor = db.query(models.Vendor).filter(models.Vendor.name == spec["name"]).first()
        if vendor is None:
            vendor = models.Vendor(
                name=spec["name"], location=spec["location"], rating=spec["rating"],
                reviews=spec["reviews"], fssai_verified=spec["fssai_verified"],
                eco_friendly=spec["eco_friendly"], lead_time_days=spec["lead_time_days"],
                about=spec["about"],
            )
            db.add(vendor)
            db.flush()
            written += 1

        for prod in spec["products"]:
            existing = db.query(models.VendorProduct).filter(
                models.VendorProduct.vendor_id == vendor.id,
                models.VendorProduct.title == prod["title"],
            ).first()
            if existing:
                continue
            tiers = prod["tiers"]
            db.add(models.VendorProduct(
                vendor_id=vendor.id,
                material_code=prod["material_code"],
                title=prod["title"],
                structure=prod["structure"],
                thickness_um=prod["thickness_um"],
                min_order_qty=prod["min_order_qty"],
                lead_time_days=prod["lead_time_days"],
                in_stock=True,
                price_tier1_qty=tiers[0][0], price_tier1_per_unit=tiers[0][1],
                price_tier2_qty=tiers[1][0], price_tier2_per_unit=tiers[1][1],
                price_tier3_qty=tiers[2][0], price_tier3_per_unit=tiers[2][1],
            ))
            written += 1

    db.commit()
    return written


# --------------------------------------------------------------------------
# Pricing
# --------------------------------------------------------------------------

def price_at_quantity(product: models.VendorProduct, quantity: int) -> Optional[float]:
    """Unit price at the highest MOQ break the quantity reaches."""
    if quantity < (product.min_order_qty or 0):
        return None
    price = None
    for qty, unit in [
        (product.price_tier1_qty, product.price_tier1_per_unit),
        (product.price_tier2_qty, product.price_tier2_per_unit),
        (product.price_tier3_qty, product.price_tier3_per_unit),
    ]:
        if qty and unit and quantity >= qty:
            price = unit
    return price if price is not None else product.price_tier1_per_unit


def price_curve(db: Session, material_code: str, quantities: List[int]) -> dict:
    """Market price per unit at each quantity, for the results-page histogram.

    Returns the best (lowest) offer across vendors at each break, plus the spread,
    so a buyer can see both the price and how competitive that break is.
    """
    products = db.query(models.VendorProduct).filter(
        models.VendorProduct.material_code == material_code,
        models.VendorProduct.in_stock == True,  # noqa: E712
    ).all()

    points = []
    for qty in quantities:
        offers = []
        for p in products:
            price = price_at_quantity(p, qty)
            if price is not None:
                offers.append(price)
        points.append(dict(
            quantity=qty,
            best_price=round(min(offers), 2) if offers else None,
            worst_price=round(max(offers), 2) if offers else None,
            average_price=round(sum(offers) / len(offers), 2) if offers else None,
            offer_count=len(offers),
        ))
    return dict(material_code=material_code, points=points,
                vendor_count=len({p.vendor_id for p in products}))


def match_vendors(db: Session, material_code: str, quantity: int = 10000,
                  eco_only: bool = False) -> List[dict]:
    """Vendors who can supply a material, cheapest qualifying offer first."""
    rows = (db.query(models.VendorProduct, models.Vendor)
            .join(models.Vendor, models.Vendor.id == models.VendorProduct.vendor_id)
            .filter(models.VendorProduct.material_code == material_code)
            .all())

    out = []
    for product, vendor in rows:
        if eco_only and not vendor.eco_friendly:
            continue
        price = price_at_quantity(product, quantity)
        out.append(dict(
            vendor_id=vendor.id, vendor_name=vendor.name, location=vendor.location,
            rating=vendor.rating, reviews=vendor.reviews,
            fssai_verified=vendor.fssai_verified, eco_friendly=vendor.eco_friendly,
            product_id=product.id, title=product.title, structure=product.structure,
            thickness_um=product.thickness_um, min_order_qty=product.min_order_qty,
            lead_time_days=product.lead_time_days, in_stock=product.in_stock,
            price_per_unit=price,
            meets_moq=quantity >= (product.min_order_qty or 0),
            tiers=[
                dict(qty=product.price_tier1_qty, price=product.price_tier1_per_unit),
                dict(qty=product.price_tier2_qty, price=product.price_tier2_per_unit),
                dict(qty=product.price_tier3_qty, price=product.price_tier3_per_unit),
            ],
        ))

    out.sort(key=lambda v: (not v["meets_moq"], v["price_per_unit"] or 9e9))
    return out


# --------------------------------------------------------------------------
# RFQ / PO workflow
# --------------------------------------------------------------------------

def new_po_number() -> str:
    stamp = datetime.datetime.utcnow().strftime("%Y%m")
    return f"PO-{stamp}-{secrets.token_hex(3).upper()}"


def advance_po(po: models.PurchaseOrder, target: str) -> tuple:
    """Move a PO one column. Returns (ok, message)."""
    if target not in PO_STAGES:
        return False, f"Unknown stage '{target}'."
    current_idx = PO_STAGES.index(po.status) if po.status in PO_STAGES else 0
    target_idx = PO_STAGES.index(target)
    if target_idx == current_idx:
        return False, f"Order is already at {PO_STAGE_LABELS[target]}."
    if abs(target_idx - current_idx) > 1:
        return False, (f"Cannot jump from {PO_STAGE_LABELS[po.status]} to "
                       f"{PO_STAGE_LABELS[target]}. Move one stage at a time.")
    po.status = target
    po.updated_at = datetime.datetime.utcnow()
    return True, f"Moved to {PO_STAGE_LABELS[target]}."


def kanban(db: Session, user: models.User) -> dict:
    """Board grouped by stage, scoped to what this user is allowed to see."""
    q = db.query(models.PurchaseOrder)
    if user.role == "supplier":
        vendor_ids = [v.id for v in db.query(models.Vendor)
                      .filter(models.Vendor.owner_user_id == user.id).all()]
        q = q.filter(models.PurchaseOrder.vendor_id.in_(vendor_ids or [-1]))
    else:
        q = q.filter(models.PurchaseOrder.buyer_user_id == user.id)

    columns = {stage: [] for stage in PO_STAGES}
    for po in q.order_by(models.PurchaseOrder.created_at.desc()).all():
        vendor = db.query(models.Vendor).filter(models.Vendor.id == po.vendor_id).first()
        columns.setdefault(po.status or "placed", []).append(dict(
            id=po.id, po_number=po.po_number, quantity=po.quantity,
            price_per_unit=po.price_per_unit, total_value=po.total_value,
            vendor_name=vendor.name if vendor else None,
            status_note=po.status_note,
            expected_delivery=po.expected_delivery.isoformat() if po.expected_delivery else None,
            created_at=po.created_at.isoformat() if po.created_at else None,
        ))

    return dict(
        stages=[dict(key=s, label=PO_STAGE_LABELS[s], orders=columns.get(s, []))
                for s in PO_STAGES],
        total=sum(len(v) for v in columns.values()),
    )
