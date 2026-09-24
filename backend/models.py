from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Role-based onboarding: a buyer runs analyses and raises RFQs, a supplier
    # lists inventory and answers them.
    role = Column(String, default="buyer")        # buyer | supplier
    company_name = Column(String)
    contact_name = Column(String)
    phone = Column(String)

    # Vendor KYC. A supplier is only shown as verified once these are recorded.
    gstin = Column(String)
    fssai_licence = Column(String)
    epr_registration = Column(String)
    kyc_status = Column(String, default="not_submitted")  # not_submitted|pending|verified|rejected
    kyc_notes = Column(String)

class PackagingReport(Base):
    __tablename__ = "packaging_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Links report to the logged-in user
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # User Inputs
    product_name = Column(String, index=True)
    fssai_category = Column(String)
    shelf_life_days = Column(Integer)
    is_liquid = Column(Boolean)
    
    # Environment / supply chain inputs
    storage_type = Column(String)
    relative_humidity = Column(Float)
    transit_condition = Column(String)
    is_fresh_produce = Column(Boolean, default=False)

    # Recommendation outputs
    optimal_material = Column(String)
    barrier_requirement = Column(String)
    map_gas = Column(String)
    estimated_cost_per_unit = Column(Float)
    epr_green_score = Column(Integer)

    # Numeric specification derived by the expert engine
    required_otr = Column(Float)        # cc/m2/day ceiling (null when breathable)
    required_wvtr = Column(Float)       # g/m2/day ceiling  (null when breathable)
    specified_thickness_um = Column(Float)
    sealability = Column(String)
    respiration_rate = Column(Float)    # mg CO2/kg/h at storage temperature

class PackagingMaterial(Base):
    """Reference catalogue of packaging films/structures and their measured
    barrier and mechanical properties. Seeded from app/data/materials_seed.py.

    Barrier figures are indicative industry typicals for the stated reference
    thickness: OTR at 23 C / 0% RH, WVTR at 38 C / 90% RH.
    """
    __tablename__ = "packaging_materials"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    family = Column(String)              # Flexible / Rigid / Paper-based / Breathable

    # Barrier properties
    otr = Column(Float)                  # cc / m2 / day
    wvtr = Column(Float)                 # g / m2 / day
    ref_thickness_um = Column(Float)     # thickness the above were measured at

    # Physical / processing envelope
    thickness_min_um = Column(Float)
    thickness_max_um = Column(Float)
    tensile_strength_mpa = Column(Float)
    max_fill_temp_c = Column(Float)      # highest product/process temperature tolerated
    min_service_temp_c = Column(Float)   # frozen suitability
    sealability = Column(String)         # Heat seal / Cold seal / Induction / None

    # Suitability flags
    is_breathable = Column(Boolean, default=False)
    map_suitable = Column(Boolean, default=False)
    liquid_suitable = Column(Boolean, default=False)
    retort_safe = Column(Boolean, default=False)
    food_contact_safe = Column(Boolean, default=True)

    # Commercial / sustainability
    cost_per_m2 = Column(Float)          # INR
    recyclable = Column(Boolean, default=False)
    compostable = Column(Boolean, default=False)
    epr_score = Column(Integer)          # 1-100 sustainability index
    notes = Column(String)


# ===========================================================================
# Marketplace
# ===========================================================================

class Vendor(Base):
    """A packaging supplier's public profile."""
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    owner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String, index=True)
    location = Column(String)
    rating = Column(Float, default=0.0)
    reviews = Column(Integer, default=0)
    fssai_verified = Column(Boolean, default=False)
    eco_friendly = Column(Boolean, default=False)
    lead_time_days = Column(Integer, default=14)
    about = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class VendorProduct(Base):
    """One SKU in a vendor's catalogue, linked to a catalogue material."""
    __tablename__ = "vendor_products"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), index=True)
    material_code = Column(String, index=True)     # -> packaging_materials.code
    title = Column(String)
    structure = Column(String)                     # e.g. "PET12/ALU9/PE60"
    thickness_um = Column(Float)
    min_order_qty = Column(Integer, default=10000)
    lead_time_days = Column(Integer, default=14)
    in_stock = Column(Boolean, default=True)

    # Tiered pricing: price per 1000 units at each MOQ break
    price_tier1_qty = Column(Integer, default=10000)
    price_tier1_per_unit = Column(Float)
    price_tier2_qty = Column(Integer, default=50000)
    price_tier2_per_unit = Column(Float)
    price_tier3_qty = Column(Integer, default=100000)
    price_tier3_per_unit = Column(Float)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class RFQ(Base):
    """A buyer's request for quote, generated from a recommendation."""
    __tablename__ = "rfqs"

    id = Column(Integer, primary_key=True, index=True)
    buyer_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    report_id = Column(Integer, ForeignKey("packaging_reports.id"), nullable=True)

    product_name = Column(String)
    material_code = Column(String)
    material_name = Column(String)
    required_otr = Column(Float)
    required_wvtr = Column(Float)
    thickness_um = Column(Float)
    width_mm = Column(Float)
    height_mm = Column(Float)
    gusset_mm = Column(Float)
    quantity = Column(Integer)
    target_price_per_unit = Column(Float)
    dieline_svg = Column(String)          # the generated artwork travels with the RFQ
    notes = Column(String)

    status = Column(String, default="open")   # open | quoted | awarded | closed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Quote(Base):
    """A vendor's response to an RFQ."""
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    rfq_id = Column(Integer, ForeignKey("rfqs.id"), index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), index=True)

    price_per_unit = Column(Float)
    moq = Column(Integer)
    lead_time_days = Column(Integer)
    validity_days = Column(Integer, default=30)
    tooling_cost = Column(Float, default=0.0)   # cylinder / plate charges
    notes = Column(String)

    status = Column(String, default="submitted")  # submitted | accepted | rejected
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class PurchaseOrder(Base):
    """A buyer's PO against an accepted quote, tracked on a Kanban board."""
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String, unique=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    rfq_id = Column(Integer, ForeignKey("rfqs.id"))
    buyer_user_id = Column(Integer, ForeignKey("users.id"), index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), index=True)

    quantity = Column(Integer)
    price_per_unit = Column(Float)
    total_value = Column(Float)

    # Kanban column
    status = Column(String, default="placed")
    # placed -> artwork_approval -> in_production -> quality_check -> dispatched -> delivered
    status_note = Column(String)
    expected_delivery = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)


# ===========================================================================
# Compliance and consumer traceability
# ===========================================================================

class ProductLabel(Base):
    """A finished label: nutrition, compliance verdict and the public trace code."""
    __tablename__ = "product_labels"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    report_id = Column(Integer, ForeignKey("packaging_reports.id"), nullable=True)
    trace_code = Column(String, unique=True, index=True)

    product_name = Column(String)
    brand = Column(String)
    fssai_category = Column(String)
    fssai_licence = Column(String)
    is_veg = Column(Boolean, default=True)
    net_quantity = Column(String)
    ingredients = Column(String)
    manufacturer = Column(String)

    # Nutrition per 100 g/ml
    energy_kcal = Column(Float)
    protein = Column(Float)
    carbohydrate = Column(Float)
    total_sugar = Column(Float)
    fat = Column(Float)
    saturated_fat = Column(Float)
    trans_fat = Column(Float)
    fibre = Column(Float)
    sodium_mg = Column(Float)
    fvnl_percent = Column(Float, default=0.0)

    # Derived
    inr_stars = Column(Float)
    traffic_light_json = Column(String)
    compliance_status = Column(String)      # pass | review | fail
    packaging_material = Column(String)
    recyclable = Column(Boolean, default=False)
    compostable = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
