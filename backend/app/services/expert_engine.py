"""Rule-based packaging expert system.

The engine runs in three stages:

  1. derive_requirements()  - food properties + environment -> the numeric barrier
     specification the package must meet (OTR, WVTR, thickness, seal, strength),
     each rule recording why it fired.
  2. recommend_materials()  - screen the material catalogue against that
     specification, score the survivors on cost and sustainability.
  3. recommend()            - orchestrates both and adds the MAP design for
     respiring produce.

Every number the engine emits is traceable to a rule, which is the point: a
recommendation a user cannot interrogate is not a decision-support tool.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional

from app.data.commodity_profiles import (
    lookup_commodity, classify_respiration, respiration_at, DEFAULT_PRODUCE,
)

# Storage regimes and their representative temperatures
STORAGE_REGIMES = {
    "Ambient": 30.0,
    "Cold Chain": 4.0,
    "Chilled": 4.0,
    "Frozen": -18.0,
}

LIPID_BANDS = {"low": 3.0, "medium": 12.0, "high": 30.0}


@dataclass
class Reason:
    rule: str
    detail: str


@dataclass
class Requirements:
    """The numeric specification a candidate material has to satisfy."""
    otr_max: float                  # cc/m2/day - lower means better O2 barrier
    wvtr_max: float                 # g/m2/day  - lower means better moisture barrier
    min_thickness_um: float
    min_tensile_mpa: float
    min_fill_temp_c: float          # material must tolerate at least this
    min_service_temp_c: float       # material must stay intact down to this
    sealability: str
    needs_breathable: bool = False
    needs_map: bool = False
    needs_retort: bool = False
    needs_liquid_suitable: bool = False
    light_barrier_required: bool = False
    reasons: List[Reason] = field(default_factory=list)

    def add(self, rule: str, detail: str):
        self.reasons.append(Reason(rule, detail))


@dataclass
class MapDesign:
    """Equilibrium modified-atmosphere design for respiring produce."""
    o2_percent: float
    co2_percent: float
    n2_percent: float
    initial_flush: str
    respiration_rate_at_storage: float   # mg CO2 / kg / h
    respiration_band: str
    required_o2_transmission: float      # cc O2 / m2 / day the film must ADMIT
    perforation_guidance: str
    warnings: List[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Stage 1 - requirements
# --------------------------------------------------------------------------

def derive_requirements(
    *,
    product_name: str,
    category: str,
    shelf_life_days: int,
    moisture_content: float,
    lipid_content: str,
    ph_level: Optional[float],
    is_liquid: bool,
    storage_type: str = "Ambient",
    relative_humidity: float = 65.0,
    transit_condition: str = "Standard Road",
    filling_process: str = "None",
    is_fresh_produce: bool = False,
) -> Requirements:
    storage_temp = STORAGE_REGIMES.get(storage_type, 30.0)
    lipid_pct = LIPID_BANDS.get((lipid_content or "low").strip().lower(), 3.0)

    # --- Oxygen barrier -------------------------------------------------
    # Start from a permissive baseline and tighten it. The scale is logarithmic:
    # each step down is roughly an order of magnitude of barrier performance.
    otr_max = 5000.0
    req = Requirements(
        otr_max=otr_max, wvtr_max=20.0, min_thickness_um=30.0, min_tensile_mpa=10.0,
        min_fill_temp_c=40.0, min_service_temp_c=0.0, sealability="Heat seal",
    )

    if shelf_life_days <= 30:
        otr_max = 3000.0
        req.add("shelf_life.short",
                f"{shelf_life_days} day target is short, so a mono-layer film is acceptable.")
    elif shelf_life_days <= 90:
        otr_max = 150.0
        req.add("shelf_life.medium",
                f"{shelf_life_days} day target needs a moderate oxygen barrier.")
    elif shelf_life_days <= 180:
        otr_max = 10.0
        req.add("shelf_life.long",
                f"{shelf_life_days} day target needs a high oxygen barrier.")
    else:
        otr_max = 1.0
        req.add("shelf_life.extended",
                f"{shelf_life_days} day target needs an ultra-high oxygen barrier.")

    # Fat oxidation is the dominant spoilage route for lipid-rich foods.
    if lipid_pct >= 30.0:
        otr_max = min(otr_max, 0.5)
        req.light_barrier_required = True
        req.add("lipid.high",
                "High fat content oxidises and turns rancid. OTR capped at 0.5 cc/m2/day "
                "and an opaque or metallized structure is required to block light-driven "
                "oxidation.")
    elif lipid_pct >= 12.0:
        otr_max = min(otr_max, 5.0)
        req.add("lipid.medium",
                "Medium fat content is oxidation-prone, so the oxygen barrier is tightened "
                "to 5 cc/m2/day.")

    # --- Moisture barrier ------------------------------------------------
    # Dry products gain moisture and go soft; wet products lose it and dry out.
    # Both directions call for a moisture barrier, sized by the gradient.
    if moisture_content <= 5.0:
        wvtr_max = 1.0
        req.add("moisture.very_dry",
                f"At {moisture_content}% moisture the product is hygroscopic and will lose "
                "crispness if it picks up water. WVTR capped at 1 g/m2/day.")
    elif moisture_content <= 15.0:
        wvtr_max = 5.0
        req.add("moisture.dry",
                f"{moisture_content}% moisture needs a moderate moisture barrier "
                "(5 g/m2/day) to hold texture.")
    elif moisture_content >= 70.0:
        wvtr_max = 10.0
        req.add("moisture.high",
                f"{moisture_content}% moisture means the risk is water loss and weight "
                "shrinkage, so WVTR is held at 10 g/m2/day.")
    else:
        wvtr_max = 15.0
        req.add("moisture.moderate",
                f"{moisture_content}% moisture is a mid-range product, 15 g/m2/day is "
                "sufficient.")

    # A humid warehouse steepens the vapour gradient across the film.
    if relative_humidity >= 75.0 and moisture_content <= 15.0:
        wvtr_max = min(wvtr_max, 0.5)
        req.add("environment.humid",
                f"{relative_humidity}% ambient RH against a dry product is a steep moisture "
                "gradient. WVTR tightened to 0.5 g/m2/day.")

    # --- Temperature envelope --------------------------------------------
    if storage_type == "Frozen":
        req.min_service_temp_c = -25.0
        req.min_tensile_mpa = max(req.min_tensile_mpa, 25.0)
        req.add("storage.frozen",
                "Frozen distribution embrittles film. Material must stay intact to -25 C "
                "and carry at least 25 MPa tensile strength.")
    elif storage_type in ("Cold Chain", "Chilled"):
        req.min_service_temp_c = -5.0
        req.add("storage.chilled",
                "Chilled chain at about 4 C. Condensation on the pack surface makes a "
                "humidity-tolerant barrier preferable.")
    else:
        req.min_service_temp_c = 0.0
        req.add("storage.ambient",
                f"Ambient storage assumed at {storage_temp:.0f} C, which roughly doubles "
                "reaction rates against a chilled chain.")

    # --- Filling process --------------------------------------------------
    process = (filling_process or "None").lower()
    if "retort" in process:
        req.needs_retort = True
        req.min_fill_temp_c = 121.0
        req.add("process.retort",
                "Retort sterilisation at 121 C. Only autoclave-rated structures qualify.")
    elif "hot fill" in process:
        req.min_fill_temp_c = 88.0
        req.add("process.hot_fill",
                "Hot fill at 85-92 C requires a heat-set container that will not distort.")
    elif "aseptic" in process or "cold fill" in process:
        req.min_fill_temp_c = 30.0
        otr_max = min(otr_max, 0.5)
        req.add("process.aseptic",
                "Aseptic cold fill puts the whole shelf life on the package barrier, so "
                "OTR is capped at 0.5 cc/m2/day.")

    # --- pH / microbial safety --------------------------------------------
    if ph_level is not None and is_liquid:
        if ph_level > 4.6:
            req.add("safety.low_acid",
                    f"pH {ph_level} is above 4.6, the Clostridium botulinum threshold. "
                    "This is a low-acid food: it needs retort sterilisation or a validated "
                    "aseptic process, not barrier packaging alone.")
            if not req.needs_retort and "aseptic" not in process:
                req.needs_retort = True
                req.min_fill_temp_c = max(req.min_fill_temp_c, 121.0)
        else:
            req.add("safety.high_acid",
                    f"pH {ph_level} is below 4.6, so the product is self-protecting against "
                    "C. botulinum and hot fill is sufficient.")

    # --- Liquid handling ---------------------------------------------------
    if is_liquid:
        req.needs_liquid_suitable = True
        req.min_tensile_mpa = max(req.min_tensile_mpa, 25.0)
        req.add("form.liquid",
                "Liquid product needs a leak-proof seal and enough tensile strength to "
                "carry hydrostatic load in transit.")

    # --- Transit -----------------------------------------------------------
    transit = (transit_condition or "").lower()
    if "long haul" in transit or "export" in transit:
        req.min_tensile_mpa = max(req.min_tensile_mpa, 40.0)
        req.min_thickness_um = max(req.min_thickness_um, 60.0)
        req.add("transit.long_haul",
                "Long-haul or export transit adds vibration and stacking load. Minimum "
                "60 micron gauge and 40 MPa tensile strength.")
    elif "rough" in transit or "rural" in transit:
        req.min_tensile_mpa = max(req.min_tensile_mpa, 30.0)
        req.add("transit.rough",
                "Rough or rural roads raise puncture and flex-crack risk, so tensile "
                "strength is raised to 30 MPa.")

    # --- Fresh produce overrides everything above --------------------------
    if is_fresh_produce:
        req.needs_breathable = True
        req.needs_map = True
        # A respiring commodity must NOT be given a high barrier - it would
        # suffocate. The O2 requirement inverts.
        otr_max = float("inf")
        # A perforated film is permeable by design; capping its WVTR would reject
        # every breathable structure. Moisture here is managed by RH equilibrium
        # and anti-fog additives, not by a barrier ceiling.
        wvtr_max = float("inf")
        req.add("produce.respiring",
                "Fresh produce keeps respiring after harvest. A high oxygen barrier would "
                "drive it anaerobic and cause off-flavours, so the film must be breathable "
                "and the oxygen requirement inverts from 'block' to 'admit'.")

    # --- Gauge -------------------------------------------------------------
    if shelf_life_days > 180:
        req.min_thickness_um = max(req.min_thickness_um, 60.0)
        req.add("thickness.extended_life",
                "Shelf life beyond 6 months needs at least 60 micron total gauge for "
                "pinhole and flex-crack resistance.")

    req.otr_max = otr_max
    req.wvtr_max = wvtr_max
    return req


# --------------------------------------------------------------------------
# Stage 2 - material screening
# --------------------------------------------------------------------------

def _scale_barrier(value: float, ref_um: float, target_um: float) -> float:
    """Permeation is inversely proportional to thickness for a monolithic film."""
    if not ref_um or not target_um:
        return value
    return value * (ref_um / target_um)


def recommend_materials(req: Requirements, materials: List[dict], limit: int = 4):
    """Screen the catalogue against the requirement set and rank the survivors."""
    qualified, rejected = [], []

    for m in materials:
        fails = []

        if req.needs_breathable and not m["is_breathable"]:
            fails.append("not breathable - would suffocate respiring produce")
        if not req.needs_breathable and m["is_breathable"]:
            fails.append("perforated film gives no barrier for a non-respiring product")
        if req.needs_retort and not m["retort_safe"]:
            fails.append("not rated for 121 C autoclave")
        if req.needs_liquid_suitable and not m["liquid_suitable"]:
            fails.append("not suitable for liquid fill")
        if m["max_fill_temp_c"] < req.min_fill_temp_c:
            fails.append(f"tolerates only {m['max_fill_temp_c']:.0f} C fill, "
                         f"needs {req.min_fill_temp_c:.0f} C")
        if m["min_service_temp_c"] > req.min_service_temp_c:
            fails.append(f"rated to {m['min_service_temp_c']:.0f} C, "
                         f"needs {req.min_service_temp_c:.0f} C")
        if m["tensile_strength_mpa"] < req.min_tensile_mpa:
            fails.append(f"{m['tensile_strength_mpa']:.0f} MPa tensile, "
                         f"needs {req.min_tensile_mpa:.0f} MPa")

        # Barrier screening at the thickness we would actually specify
        target_um = max(req.min_thickness_um, m["thickness_min_um"])
        if target_um > m["thickness_max_um"]:
            fails.append(f"cannot be made at {target_um:.0f} micron")
            target_um = m["thickness_max_um"]

        eff_otr = _scale_barrier(m["otr"], m["ref_thickness_um"], target_um)
        eff_wvtr = _scale_barrier(m["wvtr"], m["ref_thickness_um"], target_um)

        if not req.needs_breathable and eff_otr > req.otr_max:
            fails.append(f"OTR {eff_otr:.2f} exceeds the {req.otr_max:.2f} cc/m2/day limit")
        if not req.needs_breathable and eff_wvtr > req.wvtr_max:
            fails.append(f"WVTR {eff_wvtr:.2f} exceeds the {req.wvtr_max:.2f} g/m2/day limit")
        if req.light_barrier_required and m["code"] not in (
                "MET-PET", "ALU-FOIL", "RETORT-4PLY", "ASEPTIC-CARTON", "SPOUT-POUCH", "HDPE"):
            fails.append("transparent structure offers no light barrier for a high-fat product")

        entry = dict(
            code=m["code"], name=m["name"], family=m["family"],
            specified_thickness_um=round(target_um, 1),
            effective_otr=round(eff_otr, 3), effective_wvtr=round(eff_wvtr, 3),
            sealability=m["sealability"], tensile_strength_mpa=m["tensile_strength_mpa"],
            cost_per_m2=m["cost_per_m2"], epr_score=m["epr_score"],
            recyclable=m["recyclable"], compostable=m["compostable"],
            map_suitable=m["map_suitable"], notes=m["notes"],
        )

        if fails:
            entry["rejected_because"] = fails
            rejected.append(entry)
        else:
            # Rank on cost first, sustainability second. Over-specifying barrier
            # is waste, so a material far better than needed is mildly penalised.
            over_spec = 0.0
            if not req.needs_breathable and req.otr_max > 0 and eff_otr > 0:
                ratio = req.otr_max / eff_otr
                if ratio > 100:
                    over_spec = 8.0
                elif ratio > 10:
                    over_spec = 3.0
            entry["score"] = round(
                100.0 - (m["cost_per_m2"] * 0.9) + (m["epr_score"] * 0.25) - over_spec, 1)
            entry["over_specified"] = over_spec > 0
            qualified.append(entry)

    qualified.sort(key=lambda e: e["score"], reverse=True)
    rejected.sort(key=lambda e: len(e["rejected_because"]))
    return qualified[:limit], rejected


# --------------------------------------------------------------------------
# Stage 3 - MAP design for respiring produce
# --------------------------------------------------------------------------

def design_map(product_name: str, storage_type: str,
               respiration_override: Optional[float] = None) -> MapDesign:
    profile, matched = lookup_commodity(product_name)
    if profile is None:
        profile, matched = DEFAULT_PRODUCE, None

    storage_temp = STORAGE_REGIMES.get(storage_type, 20.0)
    resp_5c = respiration_override if respiration_override else profile["resp_5c"]
    rate = respiration_at(resp_5c, profile["q10"], storage_temp)

    o2 = round((profile["o2_min"] + profile["o2_max"]) / 2, 1)
    co2 = round((profile["co2_min"] + profile["co2_max"]) / 2, 1)
    n2 = round(100.0 - o2 - co2, 1)

    # Oxygen the film must let IN to match what the produce consumes.
    # RQ of ~1.0 means O2 uptake roughly equals CO2 output; convert
    # mg CO2/kg/h to cc O2/kg/day: /1.98 mg per cc, x24 h.
    o2_demand_per_kg_day = (rate / 1.98) * 24.0
    required_otr = round(o2_demand_per_kg_day, 1)

    band = classify_respiration(resp_5c)
    if rate > 40:
        perf = ("Macro-perforation or a vented bag. Respiration is too fast for a "
                "micro-perforated film to keep up, and a sealed pack would go anaerobic "
                "within hours.")
    elif rate > 15:
        perf = ("Micro-perforated film, roughly 60-120 perforations per m2 at 70-100 "
                "micron hole diameter. Confirm against a pack-size trial.")
    elif rate > 5:
        perf = ("Micro-perforated film, roughly 20-60 perforations per m2. Equilibrium "
                "is typically reached in 24-48 h.")
    else:
        perf = ("Low perforation density, roughly 5-20 per m2, or a naturally permeable "
                "film. The commodity respires slowly enough to tolerate a tight pack.")

    warnings = []
    if profile["eth_sensitive"]:
        warnings.append(
            "Ethylene-sensitive commodity. Include a potassium permanganate scrubber or "
            "keep it separated from ethylene producers in mixed loads.")
    if storage_type == "Ambient":
        warnings.append(
            f"At ambient the respiration rate is {rate:.0f} mg CO2/kg/h, about "
            f"{rate / max(respiration_at(resp_5c, profile['q10'], 4.0), 0.01):.1f}x the "
            "chilled rate. Cold chain is strongly recommended for fresh produce.")
    if storage_type == "Frozen":
        warnings.append(
            "Freezing halts respiration entirely, so MAP is unnecessary. Specify a "
            "moisture-barrier film rated for -25 C instead.")
    if matched is None:
        warnings.append(
            "This commodity is not in the reference table, so a moderate-respiration "
            "default was used. Enter a measured respiration rate for a precise design.")

    return MapDesign(
        o2_percent=o2, co2_percent=co2, n2_percent=n2,
        initial_flush=f"{o2}% O2 / {co2}% CO2 / {n2}% N2",
        respiration_rate_at_storage=round(rate, 1),
        respiration_band=band,
        required_o2_transmission=required_otr,
        perforation_guidance=perf,
        warnings=warnings,
    )


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------

def recommend(*, materials: List[dict], **kwargs) -> dict:
    """Full recommendation: requirements, ranked materials, and MAP where relevant."""
    is_fresh = kwargs.get("is_fresh_produce", False)
    # respiration_rate is consumed by the MAP stage, not by the barrier rules
    respiration_rate = kwargs.pop("respiration_rate", None)
    req = derive_requirements(**kwargs)
    qualified, rejected = recommend_materials(req, materials)

    result = dict(
        requirements=dict(
            otr_max=None if req.otr_max == float("inf") else round(req.otr_max, 3),
            wvtr_max=None if req.wvtr_max == float("inf") else round(req.wvtr_max, 2),
            min_thickness_um=req.min_thickness_um,
            min_tensile_mpa=req.min_tensile_mpa,
            sealability=req.sealability,
            needs_breathable=req.needs_breathable,
            needs_map=req.needs_map,
            needs_retort=req.needs_retort,
            light_barrier_required=req.light_barrier_required,
        ),
        reasons=[asdict(r) for r in req.reasons],
        recommended=qualified,
        rejected=rejected[:6],
    )

    if is_fresh:
        md = design_map(
            kwargs.get("product_name", ""),
            kwargs.get("storage_type", "Ambient"),
            respiration_rate,
        )
        result["map_design"] = asdict(md)
        _rerank_breathable(result["recommended"], md.respiration_rate_at_storage)
    return result


def _rerank_breathable(recommended: List[dict], rate: float):
    """Match perforation level to respiration rate.

    Cost alone would always pick the cheapest vented bag, but a macro-perforated
    bag exchanges gas too freely to hold a modified atmosphere. It is the right
    answer only when respiration is fast enough that nothing else can keep up.
    """
    fast = rate > 40.0
    for entry in recommended:
        if entry["code"] == "MACRO-PE":
            if fast:
                entry["score"] += 20.0
                entry["fit_note"] = (
                    "Respiration is too fast for a micro-perforated film to keep pace; "
                    "free venting is the only way to avoid an anaerobic pack.")
            else:
                entry["score"] -= 25.0
                entry["fit_note"] = (
                    "Vents too freely to hold a modified atmosphere at this respiration "
                    "rate. Usable as a low-cost fallback, but it forfeits MAP shelf-life gain.")
        elif entry["code"] == "MICRO-BOPP":
            if fast:
                entry["score"] -= 15.0
                entry["fit_note"] = (
                    "Perforations would saturate at this respiration rate and the pack "
                    "would still go anaerobic.")
            else:
                entry["score"] += 20.0
                entry["fit_note"] = (
                    "Perforation density can be tuned to this respiration rate to hold "
                    "the target equilibrium atmosphere.")
    recommended.sort(key=lambda e: e["score"], reverse=True)
