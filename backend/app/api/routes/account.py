"""Role-based onboarding and vendor KYC."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

import auth
import models
from database import get_db

router = APIRouter(prefix="/api/account", tags=["account"])

VALID_ROLES = ("buyer", "supplier")

# Format checks only. Real verification means calling the GST and FSSAI APIs,
# which needs credentials the platform operator has to hold - see /kyc below.
GSTIN_LENGTH = 15
FSSAI_LICENCE_LENGTH = 14


class ProfileIn(BaseModel):
    role: Optional[str] = None
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None


class KYCIn(BaseModel):
    gstin: str
    fssai_licence: str
    epr_registration: Optional[str] = None


@router.get("/me")
def me(current_user: models.User = Depends(auth.get_current_user)):
    return dict(
        id=current_user.id, email=current_user.email, role=current_user.role or "buyer",
        company_name=current_user.company_name, contact_name=current_user.contact_name,
        phone=current_user.phone, kyc_status=current_user.kyc_status or "not_submitted",
        gstin=current_user.gstin, fssai_licence=current_user.fssai_licence,
        epr_registration=current_user.epr_registration, kyc_notes=current_user.kyc_notes,
    )


@router.patch("/profile")
def update_profile(body: ProfileIn, db: Session = Depends(get_db),
                   current_user: models.User = Depends(auth.get_current_user)):
    if body.role is not None:
        if body.role not in VALID_ROLES:
            raise HTTPException(status_code=400,
                                detail=f"role must be one of {VALID_ROLES}.")
        current_user.role = body.role
    for field in ("company_name", "contact_name", "phone"):
        value = getattr(body, field)
        if value is not None:
            setattr(current_user, field, value)
    db.commit()
    return me(current_user)


@router.post("/kyc")
def submit_kyc(body: KYCIn, db: Session = Depends(get_db),
               current_user: models.User = Depends(auth.get_current_user)):
    """Submit supplier KYC documents.

    This records and format-checks the identifiers. Actual verification requires
    the GST and FSSAI lookup APIs, which need operator credentials, so the record
    lands in 'pending' for a human or a background job to clear - it is never
    auto-approved, because a self-declared 'verified' badge is worse than none.
    """
    if (current_user.role or "buyer") != "supplier":
        raise HTTPException(status_code=403,
                            detail="KYC applies to supplier accounts. Set your role "
                                   "with PATCH /api/account/profile first.")

    problems = []
    gstin = (body.gstin or "").strip().upper()
    licence = (body.fssai_licence or "").strip()

    if len(gstin) != GSTIN_LENGTH or not gstin.isalnum():
        problems.append(f"GSTIN must be {GSTIN_LENGTH} alphanumeric characters.")
    if len(licence) != FSSAI_LICENCE_LENGTH or not licence.isdigit():
        problems.append(f"FSSAI licence must be {FSSAI_LICENCE_LENGTH} digits.")

    if problems:
        raise HTTPException(status_code=400, detail=" ".join(problems))

    current_user.gstin = gstin
    current_user.fssai_licence = licence
    current_user.epr_registration = (body.epr_registration or "").strip() or None
    current_user.kyc_status = "pending"
    current_user.kyc_notes = ("Format checks passed. Awaiting verification against the "
                              "GST and FSSAI registries.")
    db.commit()

    return dict(kyc_status=current_user.kyc_status, notes=current_user.kyc_notes,
                epr_on_file=bool(current_user.epr_registration))
