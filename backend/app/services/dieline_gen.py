"""Print-ready die-line and FSSAI label artwork generation.

Produces a flat, scaled vector die-line for a stand-up pouch: the cut outline,
fold lines, seal zones, and the mandatory FSSAI label elements placed onto the
front and back panels.

Output is SVG (which any pre-press tool and every browser reads) and, when
reportlab is installed, a PDF at true physical scale.

Geometry, all in millimetres:

    Front and back panels are W wide by H tall. A stand-up pouch is a single flat
    web: back panel, front panel, and a bottom gusset that folds under. Laid flat
    for the die it reads as

        [ seal | back W | front W | seal ]  x  (H + gusset/2 + seals)

Mandatory label elements follow the Legal Metrology (Packaged Commodities) Rules
and the FSS (Labelling and Display) Regulations 2020: minimum type heights scale
with the principal display panel area, which is why font sizes here are computed
rather than fixed.
"""

import io
from typing import Optional
from xml.sax.saxutils import escape

MM = 3.7795275591  # 1 mm in px at 96 dpi, used for the SVG user unit

SEAL_MM = 8.0       # side and top seal width
BLEED_MM = 3.0


def _min_type_height_mm(panel_area_cm2: float) -> float:
    """Minimum height of the numerals in the net quantity declaration.

    Legal Metrology (Packaged Commodities) Rules, Rule 9: type height steps up
    with the area of the principal display panel.
    """
    if panel_area_cm2 <= 100:
        return 1.0
    if panel_area_cm2 <= 500:
        return 2.0
    if panel_area_cm2 <= 2500:
        return 4.0
    return 6.0


def compute_geometry(width_mm: float, height_mm: float, gusset_mm: float = 0.0) -> dict:
    """Flat-web dimensions and material consumption for a pouch."""
    web_width = (width_mm * 2) + (SEAL_MM * 2)
    web_height = height_mm + (gusset_mm / 2.0) + (SEAL_MM * 2)

    total_area_mm2 = web_width * web_height
    total_area_m2 = total_area_mm2 / 1_000_000.0

    # Usable front panel, excluding seals, is what the label must fit inside
    panel_area_cm2 = (width_mm * height_mm) / 100.0

    return dict(
        width_mm=width_mm, height_mm=height_mm, gusset_mm=gusset_mm,
        seal_mm=SEAL_MM, bleed_mm=BLEED_MM,
        web_width_mm=round(web_width, 1),
        web_height_mm=round(web_height, 1),
        film_area_m2=round(total_area_m2, 5),
        panel_area_cm2=round(panel_area_cm2, 1),
        min_type_height_mm=_min_type_height_mm(panel_area_cm2),
    )


def material_cost(geometry: dict, cost_per_m2: float, waste_factor: float = 1.08) -> dict:
    """Film cost per pouch, including a trim and start-up waste allowance."""
    net = geometry["film_area_m2"] * cost_per_m2
    gross = net * waste_factor
    return dict(
        film_area_m2=geometry["film_area_m2"],
        cost_per_m2=cost_per_m2,
        waste_factor=waste_factor,
        net_cost=round(net, 3),
        cost_per_unit=round(gross, 2),
    )


# --------------------------------------------------------------------------
# SVG
# --------------------------------------------------------------------------

def _veg_mark(x: float, y: float, size: float, is_veg: bool) -> str:
    """The mandatory green (veg) or brown (non-veg) symbol: a filled dot in a square."""
    colour = "#0A7B3E" if is_veg else "#7B2D26"
    r = size / 4.0
    cx, cy = x + size / 2.0, y + size / 2.0
    return (
        f'<g>'
        f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="#FFFFFF" '
        f'stroke="{colour}" stroke-width="{size * 0.09:.2f}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{colour}"/>'
        f'</g>'
    )


def _stars(x: float, y: float, size: float, stars: float) -> str:
    """INR star graphic: five star outlines with `stars` of them filled."""
    out = [f'<g transform="translate({x},{y})">']
    for i in range(5):
        filled = stars - i
        cx = i * size * 1.15 + size / 2
        pts = []
        import math
        for k in range(10):
            radius = size / 2 if k % 2 == 0 else size / 4.6
            angle = math.pi / 2 * 3 + k * math.pi / 5
            pts.append(f"{cx + radius * math.cos(angle):.2f},"
                       f"{size / 2 + radius * math.sin(angle):.2f}")
        poly = " ".join(pts)
        if filled >= 1:
            fill = "#F5A623"
        elif filled >= 0.5:
            fill = "url(#halfStar)"
        else:
            fill = "#FFFFFF"
        out.append(f'<polygon points="{poly}" fill="{fill}" stroke="#C8811B" '
                   f'stroke-width="{size * 0.05:.2f}"/>')
    out.append('</g>')
    return "".join(out)


def _wrap(text: str, chars_per_line: int):
    words, lines, current = text.split(), [], ""
    for w in words:
        if len(current) + len(w) + 1 > chars_per_line:
            lines.append(current)
            current = w
        else:
            current = f"{current} {w}".strip()
    if current:
        lines.append(current)
    return lines


def generate_dieline_svg(
    *,
    geometry: dict,
    product_name: str = "Product Name",
    brand: str = "",
    net_quantity: str = "250 g",
    fssai_licence: str = "10000000000000",
    ingredients: str = "",
    is_veg: bool = True,
    inr_stars: Optional[float] = None,
    manufacturer: str = "",
    material_name: str = "",
    best_before: str = "Best before 9 months from packaging",
) -> str:
    g = geometry
    W, H = g["width_mm"], g["height_mm"]
    seal, gusset = g["seal_mm"], g["gusset_mm"]
    web_w, web_h = g["web_width_mm"], g["web_height_mm"]
    type_h = g["min_type_height_mm"]

    pad = 14.0
    canvas_w, canvas_h = web_w + pad * 2, web_h + pad * 2 + 16

    back_x = pad + seal
    front_x = back_x + W
    panel_y = pad + seal
    gusset_y = panel_y + H

    s = []
    s.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{canvas_w}mm" height="{canvas_h}mm" '
        f'viewBox="0 0 {canvas_w} {canvas_h}">'
    )
    s.append('<defs>'
             '<linearGradient id="halfStar" x1="0" x2="1" y1="0" y2="0">'
             '<stop offset="50%" stop-color="#F5A623"/>'
             '<stop offset="50%" stop-color="#FFFFFF"/>'
             '</linearGradient></defs>')
    s.append(f'<rect width="{canvas_w}" height="{canvas_h}" fill="#FFFFFF"/>')

    # --- die outline (cut line) ---
    s.append(f'<rect x="{pad}" y="{pad}" width="{web_w}" height="{web_h}" '
             f'fill="none" stroke="#D2143C" stroke-width="0.5"/>')
    # bleed
    s.append(f'<rect x="{pad - BLEED_MM}" y="{pad - BLEED_MM}" '
             f'width="{web_w + BLEED_MM * 2}" height="{web_h + BLEED_MM * 2}" '
             f'fill="none" stroke="#D2143C" stroke-width="0.25" stroke-dasharray="2 1.5"/>')

    # --- seal zones ---
    for sx, sy, sw, sh in [
        (pad, pad, seal, web_h),                       # left seal
        (pad + web_w - seal, pad, seal, web_h),        # right seal
        (pad, pad, web_w, seal),                       # top seal
        (pad, pad + web_h - seal, web_w, seal),        # bottom seal
    ]:
        s.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" '
                 f'fill="#2F6FED" fill-opacity="0.10"/>')

    # --- fold lines ---
    s.append(f'<line x1="{front_x}" y1="{pad}" x2="{front_x}" y2="{pad + web_h}" '
             f'stroke="#2F6FED" stroke-width="0.35" stroke-dasharray="3 2"/>')
    if gusset > 0:
        s.append(f'<line x1="{pad}" y1="{gusset_y}" x2="{pad + web_w}" y2="{gusset_y}" '
                 f'stroke="#2F6FED" stroke-width="0.35" stroke-dasharray="3 2"/>')
        s.append(f'<text x="{pad + 2}" y="{gusset_y + 4}" font-family="Helvetica,Arial" '
                 f'font-size="2.6" fill="#2F6FED">gusset fold ({gusset} mm)</text>')

    # ================= FRONT PANEL (principal display panel) =================
    fx = front_x + 5
    fy = panel_y + 10

    if brand:
        s.append(f'<text x="{fx}" y="{fy}" font-family="Helvetica,Arial" '
                 f'font-size="{max(type_h * 1.1, 3.5):.1f}" font-weight="bold" '
                 f'fill="#3A3A3A" letter-spacing="0.6">{escape(brand.upper())}</text>')
        fy += max(type_h * 1.6, 6)

    for i, line in enumerate(_wrap(product_name, 20)[:3]):
        s.append(f'<text x="{fx}" y="{fy}" font-family="Helvetica,Arial" '
                 f'font-size="{max(type_h * 2.0, 6.0):.1f}" font-weight="bold" '
                 f'fill="#111111">{escape(line)}</text>')
        fy += max(type_h * 2.4, 7.5)

    # Veg / non-veg mark, top right of the front panel
    mark = max(type_h * 1.6, 5.0)
    s.append(_veg_mark(front_x + W - mark - 5, panel_y + 5, mark, is_veg))

    # INR stars
    if inr_stars is not None:
        star_size = max(type_h * 1.3, 4.5)
        sy_ = panel_y + H - star_size - 26
        s.append(f'<text x="{fx}" y="{sy_ - 1.6}" font-family="Helvetica,Arial" '
                 f'font-size="2.6" fill="#666666">INDIAN NUTRITION RATING</text>')
        s.append(_stars(fx, sy_, star_size, inr_stars))

    # Net quantity - statutory type height
    s.append(f'<text x="{fx}" y="{panel_y + H - 14}" font-family="Helvetica,Arial" '
             f'font-size="{type_h:.1f}" font-weight="bold" fill="#111111">'
             f'Net Qty: {escape(net_quantity)}</text>')

    # FSSAI licence on the front panel
    s.append(f'<text x="{fx}" y="{panel_y + H - 7}" font-family="Helvetica,Arial" '
             f'font-size="{max(type_h * 0.75, 2.2):.1f}" fill="#111111">'
             f'FSSAI Lic. No. {escape(fssai_licence)}</text>')

    s.append(f'<text x="{front_x + W / 2}" y="{pad + web_h + 6}" text-anchor="middle" '
             f'font-family="Helvetica,Arial" font-size="3" fill="#888888">'
             f'FRONT PANEL {W} x {H} mm</text>')

    # ================= BACK PANEL =================
    bx = back_x + 5
    by = panel_y + 9
    small = max(type_h * 0.7, 2.1)

    s.append(f'<text x="{bx}" y="{by}" font-family="Helvetica,Arial" '
             f'font-size="{small * 1.25:.1f}" font-weight="bold" fill="#111111">'
             f'INGREDIENTS</text>')
    by += small * 1.9

    ing_text = ingredients or "Ingredient list to be supplied."
    for line in _wrap(ing_text, int(W / (small * 0.52)))[:9]:
        s.append(f'<text x="{bx}" y="{by}" font-family="Helvetica,Arial" '
                 f'font-size="{small:.1f}" fill="#333333">{escape(line)}</text>')
        by += small * 1.35

    by += small
    for label, value in [
        ("Best Before", best_before),
        ("Manufactured / Packed by", manufacturer or "To be supplied"),
        ("Packaging Material", material_name or "To be specified"),
        ("Customer Care", "To be supplied"),
    ]:
        if not value:
            continue
        s.append(f'<text x="{bx}" y="{by}" font-family="Helvetica,Arial" '
                 f'font-size="{small:.1f}" fill="#333333">'
                 f'<tspan font-weight="bold">{escape(label)}: </tspan>'
                 f'{escape(value[:48])}</text>')
        by += small * 1.5

    s.append(f'<rect x="{back_x + W - 24}" y="{panel_y + H - 26}" width="19" height="19" '
             f'fill="none" stroke="#999999" stroke-width="0.3" stroke-dasharray="1 1"/>')
    s.append(f'<text x="{back_x + W - 14.5}" y="{panel_y + H - 15.5}" text-anchor="middle" '
             f'font-family="Helvetica,Arial" font-size="2.2" fill="#999999">QR</text>')
    s.append(f'<text x="{back_x + W - 14.5}" y="{panel_y + H - 4}" text-anchor="middle" '
             f'font-family="Helvetica,Arial" font-size="2" fill="#999999">scan to trace</text>')

    s.append(f'<text x="{back_x + W / 2}" y="{pad + web_h + 6}" text-anchor="middle" '
             f'font-family="Helvetica,Arial" font-size="3" fill="#888888">'
             f'BACK PANEL {W} x {H} mm</text>')

    # --- legend ---
    ly = pad + web_h + 12
    s.append(f'<text x="{pad}" y="{ly}" font-family="Helvetica,Arial" font-size="2.8" '
             f'fill="#D2143C">--- cut line / bleed 3 mm</text>')
    s.append(f'<text x="{pad + 52}" y="{ly}" font-family="Helvetica,Arial" font-size="2.8" '
             f'fill="#2F6FED">--- fold line / seal zone {seal} mm</text>')
    s.append(f'<text x="{pad + 132}" y="{ly}" font-family="Helvetica,Arial" font-size="2.8" '
             f'fill="#555555">film area {g["film_area_m2"]} m2 per pouch</text>')

    s.append('</svg>')
    return "".join(s)


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------

def generate_dieline_pdf(svg_geometry: dict, **kwargs) -> Optional[bytes]:
    """True-scale PDF of the same die-line. Returns None if reportlab is absent."""
    try:
        from reportlab.lib.units import mm as RL_MM
        from reportlab.pdfgen import canvas as rl_canvas
    except ImportError:
        return None

    g = svg_geometry
    W, H, seal = g["width_mm"], g["height_mm"], g["seal_mm"]
    web_w, web_h = g["web_width_mm"], g["web_height_mm"]
    pad = 14.0
    page_w, page_h = (web_w + pad * 2) * RL_MM, (web_h + pad * 2 + 16) * RL_MM

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(page_w, page_h))
    c.setTitle(f"Die-line {W}x{H}mm")

    def y(v):  # PDF origin is bottom-left; the SVG layout is top-left
        return page_h - v * RL_MM

    c.setStrokeColorRGB(0.82, 0.08, 0.24)
    c.setLineWidth(0.5)
    c.rect(pad * RL_MM, y(pad + web_h), web_w * RL_MM, web_h * RL_MM)

    c.setDash(3, 2)
    c.setStrokeColorRGB(0.18, 0.44, 0.93)
    front_x = pad + seal + W
    c.line(front_x * RL_MM, y(pad), front_x * RL_MM, y(pad + web_h))
    if g["gusset_mm"] > 0:
        gy = pad + seal + H
        c.line(pad * RL_MM, y(gy), (pad + web_w) * RL_MM, y(gy))
    c.setDash()

    c.setFillColorRGB(0.1, 0.1, 0.1)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(pad * RL_MM, y(pad + web_h + 8),
                 f"{kwargs.get('product_name', 'Product')} - die-line")
    c.setFont("Helvetica", 7)
    c.drawString(pad * RL_MM, y(pad + web_h + 13),
                 f"{W} x {H} mm, gusset {g['gusset_mm']} mm, seal {seal} mm | "
                 f"film {g['film_area_m2']} m2/pouch | "
                 f"min type height {g['min_type_height_mm']} mm")

    c.showPage()
    c.save()
    return buf.getvalue()
