"""FSSAI preservative and additive validator.

Takes the additives a formulator intends to use, resolves each against the
reference tables, and reports one of four verdicts:

    banned      - the substance is prohibited outright, or in this use
    over_limit  - permitted, but the stated level exceeds the category ceiling
    ok          - permitted and within limit
    unknown     - not in the reference table, so it needs manual lookup

The module never certifies compliance. It flags likely problems for a human to
verify against the current gazette, and every response says so.
"""

import re
from typing import List, Optional

from app.data.fssai_additives import (
    BANNED_SUBSTANCES, PERMITTED_ADDITIVES, INTERACTION_WARNINGS, INFANT_PROHIBITED,
)

DISCLAIMER = (
    "Indicative screening only. Additive limits are category-specific and are "
    "amended regularly. Verify every result against the current FSS (Food Products "
    "Standards and Food Additives) Regulations before production."
)

# Maps an FSSAI category string onto the keyword used in the limit tables.
_CATEGORY_KEYWORDS = [
    ("dairy", "dairy"), ("fats and oils", "fats and oils"), ("edible ices", "dairy"),
    ("fruits", "fruits"), ("vegetables", "fruits"), ("confectionery", "confectionery"),
    ("cereals", "cereals"), ("bakery", "bakery"), ("sweeteners", "sweeteners"),
    ("salts", "salts"), ("spices", "salts"), ("beverages", "beverages"),
    ("savouries", "ready-to-eat savouries"), ("prepared foods", "prepared foods"),
    ("meat", "meat"), ("fish", "meat"),
]


def _normalise(name: str) -> str:
    """Lowercase, strip INS/E prefixes and punctuation so lookups are forgiving."""
    s = (name or "").strip().lower()
    s = re.sub(r"^(ins|e)\s*[-.]?\s*(\d{3,4})$", r"\2", s)   # "INS 211" -> "211"
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def _category_key(category: str) -> Optional[str]:
    c = (category or "").lower()
    for needle, key in _CATEGORY_KEYWORDS:
        if needle in c:
            return key
    return None


def _resolve(name: str):
    """Find an additive by name, alias or INS number. Returns (kind, key, record)."""
    n = _normalise(name)
    if not n:
        return None, None, None

    for key, rec in BANNED_SUBSTANCES.items():
        if n == _normalise(key) or n in [_normalise(a) for a in rec["aliases"]]:
            return "banned", key, rec
        if rec.get("ins") and n == rec["ins"]:
            return "banned", key, rec

    for key, rec in PERMITTED_ADDITIVES.items():
        if n == _normalise(key) or n in [_normalise(a) for a in rec["aliases"]]:
            return "permitted", key, rec
        if rec.get("ins") and n == rec["ins"]:
            return "permitted", key, rec

    # Loose containment as a last resort, so "sodium benzoate (preservative)" resolves
    for key, rec in PERMITTED_ADDITIVES.items():
        if _normalise(key) in n:
            return "permitted", key, rec
    for key, rec in BANNED_SUBSTANCES.items():
        if _normalise(key) in n:
            return "banned", key, rec

    return None, None, None


def validate_additives(
    additives: List[dict],
    category: str = "",
    is_infant_food: bool = False,
) -> dict:
    """additives: [{"name": str, "level_ppm": float | None}, ...]"""
    cat_key = _category_key(category)
    results, resolved_keys = [], []

    for item in additives:
        name = (item.get("name") or "").strip()
        if not name:
            continue
        level = item.get("level_ppm")
        kind, key, rec = _resolve(name)

        if kind == "banned":
            results.append(dict(
                input=name, resolved=key, ins=rec.get("ins"),
                verdict="banned", severity="critical",
                message=rec["reason"], legal_basis=rec["legal_basis"], limit_ppm=None,
            ))
            continue

        if kind is None:
            results.append(dict(
                input=name, resolved=None, ins=None,
                verdict="unknown", severity="info",
                message=("Not found in the reference table. Confirm it is a permitted "
                         "additive for this category and check its ceiling manually."),
                legal_basis=None, limit_ppm=None,
            ))
            continue

        resolved_keys.append(key)
        limit = rec["limits"].get(cat_key, rec["default_limit_ppm"])

        if is_infant_food and key in INFANT_PROHIBITED:
            results.append(dict(
                input=name, resolved=key, ins=rec["ins"],
                verdict="banned", severity="critical",
                message=(f"{key.title()} is not permitted in food for infants and young "
                         "children."),
                legal_basis="FSS (Foods for Infant Nutrition) Regulations",
                limit_ppm=limit,
            ))
            continue

        if limit is None:
            results.append(dict(
                input=name, resolved=key, ins=rec["ins"],
                verdict="ok", severity="ok",
                message=f"Permitted at GMP level ({rec['function']}). {rec['notes']}",
                legal_basis=None, limit_ppm=None,
            ))
        elif level is not None and level > limit:
            results.append(dict(
                input=name, resolved=key, ins=rec["ins"],
                verdict="over_limit", severity="critical",
                message=(f"{level} ppm exceeds the {limit} ppm ceiling for "
                         f"{cat_key or 'this category'}. Reduce to {limit} ppm or below."),
                legal_basis="FSS (Food Products Standards and Food Additives) Regulations",
                limit_ppm=limit,
            ))
        else:
            stated = f"{level} ppm is within" if level is not None else "Permitted, ceiling"
            results.append(dict(
                input=name, resolved=key, ins=rec["ins"],
                verdict="ok", severity="ok",
                message=(f"{stated} the {limit} ppm limit for "
                         f"{cat_key or 'this category'}. {rec['notes']}"),
                legal_basis=None, limit_ppm=limit,
            ))

    # Pairwise interactions
    interactions = []
    for (a, b), note in INTERACTION_WARNINGS:
        if a in resolved_keys and b in resolved_keys:
            interactions.append(dict(additives=[a, b], message=note))

    # Combined synthetic colour ceiling
    colours = [k for k in resolved_keys if PERMITTED_ADDITIVES[k]["function"] == "Colour"]
    if len(colours) > 1:
        interactions.append(dict(
            additives=colours,
            message=("Total synthetic colour across all colours must not exceed 100 ppm "
                     "in the final product, not 100 ppm each."),
        ))

    counts = {v: sum(1 for r in results if r["verdict"] == v)
              for v in ("banned", "over_limit", "ok", "unknown")}
    if counts["banned"]:
        overall = "fail"
    elif counts["over_limit"]:
        overall = "fail"
    elif counts["unknown"]:
        overall = "review"
    else:
        overall = "pass"

    return dict(
        overall=overall, counts=counts, results=results,
        interactions=interactions, category_matched=cat_key,
        disclaimer=DISCLAIMER,
    )


def parse_additive_text(text: str) -> List[dict]:
    """Pull additive names and levels out of a free-text ingredient declaration.

    Handles the usual shapes:
        "Sodium Benzoate (INS 211) - 250 ppm"
        "Potassium sorbate 800ppm, citric acid"
        "INS 924"
    """
    if not text:
        return []

    # Split on commas and newlines, but not inside brackets
    chunks = re.split(r"[,\n;]+(?![^(]*\))", text)
    out = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue
        level = None
        m = re.search(r"(\d+(?:\.\d+)?)\s*(ppm|mg/kg|mg per kg)", chunk, re.I)
        if m:
            level = float(m.group(1))
            chunk = chunk[:m.start()] + chunk[m.end():]
        # Drop a trailing INS reference in brackets, it is resolved by name anyway
        name = re.sub(r"\((?:ins|e)\s*\d{3,4}\)", "", chunk, flags=re.I)
        name = name.strip(" -:–\t")
        if name:
            out.append({"name": name, "level_ppm": level})
    return out
