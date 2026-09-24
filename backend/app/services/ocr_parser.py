"""Nutrition panel parsing.

Two entry points:

    parse_nutrition_text(text)  - pull macros out of a pasted or OCR'd panel.
    ocr_image(image_bytes)      - run Tesseract over an uploaded label photo.

OCR needs the Tesseract binary, which is a separate system install and is often
absent. Rather than failing the request, ocr_image() reports that clearly so the
caller can fall back to pasted text or manual entry - the text parser is the part
that does the real work either way.
"""

import io
import re
from typing import Optional

try:
    import pytesseract
    from PIL import Image
    _PYTESSERACT_IMPORTED = True
except ImportError:
    _PYTESSERACT_IMPORTED = False


def tesseract_available() -> tuple:
    """Returns (available, detail)."""
    if not _PYTESSERACT_IMPORTED:
        return False, "pytesseract / Pillow is not installed."
    try:
        version = pytesseract.get_tesseract_version()
        return True, f"Tesseract {version}"
    except Exception as exc:
        return False, (
            "The Tesseract binary was not found on PATH. Install it "
            "(https://github.com/UB-Mannheim/tesseract/wiki on Windows) or set "
            f"pytesseract.pytesseract.tesseract_cmd. Underlying error: {exc}"
        )


def ocr_image(image_bytes: bytes) -> dict:
    ok, detail = tesseract_available()
    if not ok:
        return dict(ok=False, text=None, message=detail)
    try:
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "L":
            image = image.convert("L")           # greyscale helps panel OCR
        text = pytesseract.image_to_string(image)
        return dict(ok=True, text=text, message=detail)
    except Exception as exc:
        return dict(ok=False, text=None, message=f"OCR failed: {exc}")


# --------------------------------------------------------------------------
# Text parsing
# --------------------------------------------------------------------------

# Each nutrient maps to the aliases that appear on Indian nutrition panels.
_NUTRIENT_PATTERNS = {
    "energy_kcal":    [r"energy(?:\s*value)?", r"calories"],
    "protein":        [r"protein"],
    "carbohydrate":   [r"carbohydrate(?:s)?(?!.*sugar)", r"total carb"],
    "total_sugar":    [r"total sugar(?:s)?", r"(?<!added )sugar(?:s)?"],
    "added_sugar":    [r"added sugar(?:s)?"],
    "fat":            [r"total fat", r"(?<!saturated )(?<!trans )fat"],
    "saturated_fat":  [r"saturated(?:\s*fat)?", r"sat\.?\s*fat"],
    "trans_fat":      [r"trans(?:\s*fat)?"],
    "fibre":          [r"dietary fib(?:re|er)", r"fib(?:re|er)"],
    "sodium_mg":      [r"sodium"],
    "salt":           [r"salt"],
}

_NUMBER = r"(\d+(?:[.,]\d+)?)"
_UNIT = r"\s*(kcal|kj|mg|g|%)?"


def _to_float(raw: str) -> float:
    return float(raw.replace(",", "."))


def parse_nutrition_text(text: str) -> dict:
    """Extract macros from a nutrition panel. Values are per 100 g/ml as printed."""
    if not text:
        return dict(values={}, warnings=["No text supplied."], raw_lines=[])

    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    values, matched_lines = {}, {}

    for line in lines:
        low = line.lower()
        for nutrient, patterns in _NUTRIENT_PATTERNS.items():
            if nutrient in values:
                continue
            for pat in patterns:
                m = re.search(pat + r"[^0-9\-]{0,25}" + _NUMBER + _UNIT, low)
                if not m:
                    continue
                value = _to_float(m.group(1))
                unit = (m.group(2) or "").lower()

                if nutrient == "energy_kcal" and unit == "kj":
                    value = round(value / 4.184, 1)
                if nutrient == "sodium_mg" and unit == "g":
                    value = value * 1000
                values[nutrient] = value
                matched_lines[nutrient] = line
                break

    warnings = []
    # Derive whichever of salt/sodium is missing
    if "sodium_mg" not in values and "salt" in values:
        values["sodium_mg"] = round(values["salt"] * 1000 / 2.5, 1)
        warnings.append("Sodium derived from the declared salt figure (salt / 2.5).")
    if "salt" not in values and "sodium_mg" in values:
        values["salt"] = round(values["sodium_mg"] * 2.5 / 1000, 3)
        warnings.append("Salt derived from the declared sodium figure (sodium x 2.5).")

    for required in ("energy_kcal", "protein", "fat", "total_sugar"):
        if required not in values:
            warnings.append(f"Could not read '{required.replace('_', ' ')}'. Enter it manually.")

    if values.get("saturated_fat") and values.get("fat") and \
            values["saturated_fat"] > values["fat"]:
        warnings.append("Saturated fat reads higher than total fat, which is impossible. "
                        "Check the OCR result.")

    per_100 = bool(re.search(r"per\s*100\s*(g|ml)", text, re.I))
    if not per_100:
        warnings.append("Could not confirm the panel is declared per 100 g/ml. "
                        "Ratings assume a per-100 basis.")

    return dict(values=values, warnings=warnings,
                matched_lines=matched_lines, per_100_confirmed=per_100)
