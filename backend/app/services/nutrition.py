"""Front-of-Pack labelling: traffic-light bands and the Indian Nutrition Rating.

Two independent schemes:

1. Traffic lights - per-nutrient LOW / MEDIUM / HIGH bands for fat, saturates,
   total sugars and salt. Thresholds follow the FSA/UK front-of-pack model that
   the Indian draft aligns with, applied per 100 g for solids and per 100 ml for
   liquids.

2. Indian Nutrition Rating (INR) - FSSAI's draft front-of-pack scheme, which
   scores a food on negative nutrients (energy, saturated fat, total sugar,
   sodium) against positive components (protein, fibre, and fruit/vegetable/nut/
   legume content) and maps the balance onto 0.5 to 5 stars.

The INR implementation is a documented approximation of the published draft
algorithm: the draft's exact point tables are reproduced where they are public,
and the star cut-offs are calibrated to the worked examples in the draft. It is
suitable for product development guidance. It is not a substitute for the
official calculator when you file a label.
"""

from typing import Optional

# ---------------------------------------------------------------------------
# 1. Traffic lights
# ---------------------------------------------------------------------------
# (low_max, high_min) in g per 100 g (solids) or per 100 ml (liquids)
TRAFFIC_LIGHT_THRESHOLDS = {
    "solid": {
        "fat":       (3.0, 17.5),
        "saturates": (1.5, 5.0),
        "sugars":    (5.0, 22.5),
        "salt":      (0.3, 1.5),
    },
    "liquid": {
        "fat":       (1.5, 8.75),
        "saturates": (0.75, 2.5),
        "sugars":    (2.5, 11.25),
        "salt":      (0.3, 0.75),
    },
}

_BAND_LABEL = {"low": "LOW", "medium": "MEDIUM", "high": "HIGH"}
_BAND_COLOUR = {"low": "green", "medium": "amber", "high": "red"}


def _band(value: Optional[float], low_max: float, high_min: float) -> str:
    if value is None:
        return "unknown"
    if value <= low_max:
        return "low"
    if value > high_min:
        return "high"
    return "medium"


def traffic_lights(*, fat=None, saturates=None, sugars=None, salt=None,
                   sodium_mg=None, is_liquid=False) -> dict:
    """All values per 100 g or per 100 ml. Salt in g; sodium in mg as an alternative."""
    if salt is None and sodium_mg is not None:
        salt = round(sodium_mg * 2.5 / 1000.0, 3)   # salt = sodium x 2.5

    table = TRAFFIC_LIGHT_THRESHOLDS["liquid" if is_liquid else "solid"]
    values = {"fat": fat, "saturates": saturates, "sugars": sugars, "salt": salt}

    out = {}
    for nutrient, value in values.items():
        low_max, high_min = table[nutrient]
        band = _band(value, low_max, high_min)
        out[nutrient] = dict(
            value=value,
            unit="g",
            band=_BAND_LABEL.get(band, "UNKNOWN"),
            colour=_BAND_COLOUR.get(band, "grey"),
            low_max=low_max,
            high_min=high_min,
        )

    reds = sum(1 for v in out.values() if v["colour"] == "red")
    ambers = sum(1 for v in out.values() if v["colour"] == "amber")
    return dict(
        basis="per 100 ml" if is_liquid else "per 100 g",
        nutrients=out,
        red_count=reds,
        amber_count=ambers,
        summary=("Multiple nutrients are in the HIGH band. Reformulation would "
                 "materially improve the front-of-pack label."
                 if reds >= 2 else
                 "One nutrient is in the HIGH band." if reds == 1 else
                 "No nutrient is in the HIGH band."),
    )


# ---------------------------------------------------------------------------
# 2. Indian Nutrition Rating
# ---------------------------------------------------------------------------
# Negative points: energy (kJ), saturated fat (g), total sugar (g), sodium (mg)
# per 100 g/ml. Each threshold list is the upper bound for that point value.
_ENERGY_KJ = [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350]
_SAT_FAT_G = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
_SUGAR_G = [4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45]
_SODIUM_MG = [90, 180, 270, 360, 450, 540, 630, 720, 810, 900]

# Positive points
_PROTEIN_G = [1.6, 3.2, 4.8, 6.4, 8.0]
_FIBRE_G = [0.9, 1.9, 2.8, 3.7, 4.7]
_FVNL_PCT = [40, 60, 80]          # fruit / vegetable / nut / legume content


def _points(value: Optional[float], thresholds) -> int:
    """Number of thresholds the value exceeds."""
    if value is None:
        return 0
    return sum(1 for t in thresholds if value > t)


def indian_nutrition_rating(*, energy_kcal=None, saturated_fat=None, total_sugar=None,
                            sodium_mg=None, protein=None, fibre=None,
                            fvnl_percent=0.0, is_beverage=False) -> dict:
    """All nutrient values per 100 g (solids) or per 100 ml (beverages)."""
    energy_kj = energy_kcal * 4.184 if energy_kcal is not None else None

    neg = (_points(energy_kj, _ENERGY_KJ)
           + _points(saturated_fat, _SAT_FAT_G)
           + _points(total_sugar, _SUGAR_G)
           + _points(sodium_mg, _SODIUM_MG))

    p_protein = _points(protein, _PROTEIN_G)
    p_fibre = _points(fibre, _FIBRE_G)
    p_fvnl = _points(fvnl_percent, _FVNL_PCT)

    # The draft caps the protein credit when the negative load is high and the
    # food is not otherwise rich in fruit/veg/nut/legume content, so protein
    # cannot rescue an energy-dense product on its own.
    if neg >= 11 and p_fvnl < 2:
        p_protein = 0

    pos = p_protein + p_fibre + p_fvnl
    score = neg - pos

    # Star cut-offs, calibrated separately for beverages, which are scored on a
    # tighter scale because a drink contributes energy without satiety.
    if is_beverage:
        cuts = [(0, 5.0), (1, 4.5), (2, 4.0), (3, 3.5), (4, 3.0),
                (6, 2.5), (8, 2.0), (10, 1.5), (13, 1.0)]
    else:
        cuts = [(-1, 5.0), (2, 4.5), (5, 4.0), (8, 3.5), (11, 3.0),
                (14, 2.5), (17, 2.0), (20, 1.5), (24, 1.0)]

    stars = 0.5
    for threshold, value in cuts:
        if score <= threshold:
            stars = value
            break

    drivers = []
    if _points(sodium_mg, _SODIUM_MG) >= 6:
        drivers.append("Sodium is the largest single penalty. Reducing added salt "
                       "is usually the cheapest way to gain a half star.")
    if _points(total_sugar, _SUGAR_G) >= 6:
        drivers.append("Total sugar is a major penalty. Consider partial replacement "
                       "with a permitted sweetener.")
    if _points(saturated_fat, _SAT_FAT_G) >= 6:
        drivers.append("Saturated fat is a major penalty. A change of fat source "
                       "would lift the rating.")
    if p_fibre == 0 and not is_beverage:
        drivers.append("No fibre credit is being earned. Added wholegrain or bran "
                       "raises the positive score directly.")
    if p_fvnl == 0:
        drivers.append("No fruit/vegetable/nut/legume credit. Above 40% FVNL content "
                       "the product starts earning positive points.")

    return dict(
        stars=stars,
        score=score,
        negative_points=neg,
        positive_points=pos,
        breakdown=dict(
            energy=_points(energy_kj, _ENERGY_KJ),
            saturated_fat=_points(saturated_fat, _SAT_FAT_G),
            total_sugar=_points(total_sugar, _SUGAR_G),
            sodium=_points(sodium_mg, _SODIUM_MG),
            protein=p_protein,
            fibre=p_fibre,
            fvnl=p_fvnl,
        ),
        improvement_drivers=drivers,
        basis="per 100 ml" if is_beverage else "per 100 g",
        disclaimer=("Approximation of the FSSAI draft INR algorithm, intended for "
                    "product development. Use the official calculator for label filing."),
    )


def consumer_summary(tl: dict, inr: dict) -> dict:
    """The plain-language 'eat or not' panel a shopper sees behind the QR code."""
    stars = inr["stars"]
    if stars >= 4:
        verdict, tone = "A healthier choice", "green"
    elif stars >= 2.5:
        verdict, tone = "Fine in moderation", "amber"
    else:
        verdict, tone = "An occasional treat", "red"

    highs = [n for n, v in tl["nutrients"].items() if v["colour"] == "red"]
    lows = [n for n, v in tl["nutrients"].items() if v["colour"] == "green"]

    notes = []
    if highs:
        notes.append("High in " + ", ".join(highs) + ".")
    if lows:
        notes.append("Low in " + ", ".join(lows) + ".")
    if not notes:
        notes.append("No nutrient is in a high band.")

    return dict(verdict=verdict, tone=tone, stars=stars, notes=notes)
