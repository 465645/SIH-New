"""Respiration and storage reference data for fresh commodities.

Respiration rates are given as mg CO2 / kg / h at 5 C, the usual reference point
in post-harvest literature, together with a Q10 factor describing how fast the
rate climbs with temperature. Rate at any temperature T is approximated by

    R(T) = R_5 * Q10 ** ((T - 5) / 10)

Recommended MAP atmospheres are the equilibrium targets the package should settle
at, not the initial flush. O2 below the listed floor pushes the commodity into
anaerobic respiration and off-flavours, which is why each entry carries a minimum.
"""

# Classification bands used when a commodity is not in the table below.
RESPIRATION_BANDS = [
    # (label, upper bound of mg CO2/kg/h at 5 C, typical examples)
    ("Very Low", 5, "dates, dried fruit, nuts, potato (cured)"),
    ("Low", 10, "apple, grape, onion, garlic, citrus"),
    ("Moderate", 20, "banana, mango, carrot, tomato, cabbage"),
    ("High", 40, "avocado, cauliflower, leek, strawberry"),
    ("Very High", 60, "broccoli, green beans, brussels sprouts"),
    ("Extremely High", 10 ** 6, "asparagus, mushroom, spinach, sweet corn, peas"),
]

# resp_5c  - mg CO2 / kg / h at 5 C
# o2_min/o2_max, co2_min/co2_max - recommended equilibrium MAP window, % v/v
# eth_sensitive - damaged by ethylene, needs scrubbing or separation
COMMODITY_PROFILES = {
    "apple":        dict(resp_5c=5,   q10=2.6, o2_min=1.5, o2_max=3.0, co2_min=1.0, co2_max=3.0,
                         temp_c=1.0,  rh=92, eth_sensitive=False),
    "banana":       dict(resp_5c=18,  q10=2.4, o2_min=2.0, o2_max=5.0, co2_min=2.0, co2_max=5.0,
                         temp_c=13.5, rh=90, eth_sensitive=True),
    "mango":        dict(resp_5c=16,  q10=2.7, o2_min=3.0, o2_max=5.0, co2_min=5.0, co2_max=8.0,
                         temp_c=12.0, rh=90, eth_sensitive=True),
    "grape":        dict(resp_5c=6,   q10=2.5, o2_min=2.0, o2_max=5.0, co2_min=1.0, co2_max=3.0,
                         temp_c=0.0,  rh=92, eth_sensitive=False),
    "strawberry":   dict(resp_5c=35,  q10=2.8, o2_min=5.0, o2_max=10.0, co2_min=15.0, co2_max=20.0,
                         temp_c=0.5,  rh=92, eth_sensitive=False),
    "tomato":       dict(resp_5c=14,  q10=2.3, o2_min=3.0, o2_max=5.0, co2_min=2.0, co2_max=3.0,
                         temp_c=10.0, rh=90, eth_sensitive=True),
    "carrot":       dict(resp_5c=15,  q10=2.4, o2_min=2.0, o2_max=5.0, co2_min=3.0, co2_max=4.0,
                         temp_c=0.5,  rh=95, eth_sensitive=True),
    "potato":       dict(resp_5c=4,   q10=2.2, o2_min=3.0, o2_max=5.0, co2_min=2.0, co2_max=3.0,
                         temp_c=8.0,  rh=93, eth_sensitive=True),
    "onion":        dict(resp_5c=4,   q10=2.2, o2_min=1.0, o2_max=3.0, co2_min=0.0, co2_max=5.0,
                         temp_c=0.5,  rh=70, eth_sensitive=False),
    "cabbage":      dict(resp_5c=12,  q10=2.5, o2_min=2.0, o2_max=5.0, co2_min=2.5, co2_max=6.0,
                         temp_c=0.5,  rh=96, eth_sensitive=True),
    "cauliflower":  dict(resp_5c=22,  q10=2.6, o2_min=2.0, o2_max=5.0, co2_min=2.0, co2_max=5.0,
                         temp_c=0.5,  rh=95, eth_sensitive=True),
    "broccoli":     dict(resp_5c=45,  q10=2.9, o2_min=1.0, o2_max=2.0, co2_min=5.0, co2_max=10.0,
                         temp_c=0.5,  rh=96, eth_sensitive=True),
    "spinach":      dict(resp_5c=65,  q10=3.0, o2_min=1.0, o2_max=3.0, co2_min=5.0, co2_max=10.0,
                         temp_c=0.5,  rh=96, eth_sensitive=True),
    "mushroom":     dict(resp_5c=70,  q10=2.6, o2_min=3.0, o2_max=6.0, co2_min=5.0, co2_max=15.0,
                         temp_c=1.0,  rh=93, eth_sensitive=False),
    "green beans":  dict(resp_5c=42,  q10=2.7, o2_min=2.0, o2_max=3.0, co2_min=4.0, co2_max=7.0,
                         temp_c=5.0,  rh=95, eth_sensitive=True),
    "peas":         dict(resp_5c=60,  q10=2.8, o2_min=2.0, o2_max=3.0, co2_min=5.0, co2_max=7.0,
                         temp_c=0.5,  rh=95, eth_sensitive=False),
    "sweet corn":   dict(resp_5c=58,  q10=2.8, o2_min=2.0, o2_max=4.0, co2_min=5.0, co2_max=10.0,
                         temp_c=0.5,  rh=95, eth_sensitive=False),
    "lettuce":      dict(resp_5c=25,  q10=2.7, o2_min=1.0, o2_max=3.0, co2_min=0.0, co2_max=2.0,
                         temp_c=0.5,  rh=98, eth_sensitive=True),
    "okra":         dict(resp_5c=38,  q10=2.6, o2_min=3.0, o2_max=5.0, co2_min=4.0, co2_max=10.0,
                         temp_c=8.0,  rh=92, eth_sensitive=True),
    "guava":        dict(resp_5c=17,  q10=2.6, o2_min=2.0, o2_max=5.0, co2_min=2.0, co2_max=5.0,
                         temp_c=8.0,  rh=90, eth_sensitive=True),
    "papaya":       dict(resp_5c=20,  q10=2.7, o2_min=2.0, o2_max=5.0, co2_min=5.0, co2_max=8.0,
                         temp_c=10.0, rh=90, eth_sensitive=True),
    "pomegranate":  dict(resp_5c=8,   q10=2.4, o2_min=3.0, o2_max=5.0, co2_min=5.0, co2_max=10.0,
                         temp_c=5.0,  rh=92, eth_sensitive=False),
}

# Fallback when the commodity is unknown but the user has told us it is fresh produce.
DEFAULT_PRODUCE = dict(resp_5c=20, q10=2.6, o2_min=2.0, o2_max=5.0,
                       co2_min=3.0, co2_max=8.0, temp_c=5.0, rh=92, eth_sensitive=True)


def classify_respiration(resp_5c: float) -> str:
    """Map a respiration rate onto its post-harvest band."""
    for label, upper, _examples in RESPIRATION_BANDS:
        if resp_5c <= upper:
            return label
    return "Extremely High"


def respiration_at(resp_5c: float, q10: float, temp_c: float) -> float:
    """Adjust a 5 C respiration rate to the actual storage temperature."""
    return resp_5c * (q10 ** ((temp_c - 5.0) / 10.0))


def lookup_commodity(name: str):
    """Best-effort match of a free-text product name against the profile table.

    Returns (profile, matched_name) or (None, None) when nothing matches.
    """
    if not name:
        return None, None
    key = name.strip().lower()
    if key in COMMODITY_PROFILES:
        return COMMODITY_PROFILES[key], key
    # substring match so "fresh alphonso mango" finds "mango"
    for commodity, profile in COMMODITY_PROFILES.items():
        if commodity in key or key in commodity:
            return profile, commodity
    return None, None
