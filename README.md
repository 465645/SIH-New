# PackGenius — AI-Based Intelligent Food Packaging Recommendation System

A decision-support tool that recommends packaging **materials and numeric specifications**
for food commodities, checks the formulation against FSSAI additive limits, generates
print-ready label artwork, and connects the result to a B2B supplier marketplace.

Built for the SIH problem statement *"AI-Based Intelligent Food Packaging Material
Recommendation System for Food Commodities"*.

---

## What it does

Give it a food product's properties and its storage environment, and it returns an
engineering specification rather than a vague label:

```
Product: Aloo Bhujia, 1.2% moisture, high fat, 180-day ambient shelf life

  MATERIAL   Metallized PET / PE Pouch, 40 µm
  SPEC       OTR  ≤ 0.5 cc/m²/day   (achieves 0.36)
             WVTR ≤ 1.0 g/m²/day    (achieves 0.21)
             Heat seal, 150 MPa tensile
  COST       ₹31.0/m² × 0.086 m² = ₹2.67 per pouch
  EPR        45/100, not recyclable (multi-layer laminate)

  WHY
   [shelf_life.long]     180-day target needs a high oxygen barrier.
   [lipid.high]          High fat oxidises and turns rancid. OTR capped at
                         0.5 cc/m²/day; opaque structure required to block
                         light-driven oxidation.
   [moisture.very_dry]   At 1.2% moisture the product is hygroscopic…
```

For **fresh produce** the logic inverts: a respiring commodity must be allowed to
breathe, so the system designs a modified atmosphere instead of a barrier.

```
Product: broccoli, chilled

  MATERIAL   Macro-perforated PE Bag
  MAP        1.5% O₂ / 7.5% CO₂ / 91% N₂
  RESPIRATION 40.5 mg CO₂/kg/h at 4 °C (Very High band)
  FILM must admit ≥ 490 cc O₂/kg/day
  ! Ethylene-sensitive: include a KMnO₄ scrubber or separate in mixed loads.
```

---

## Architecture

| Layer | Choice | Why |
|---|---|---|
| Frontend | React 18 + Vite + Tailwind | |
| Backend | FastAPI | |
| Recommendation | **Rule engine first, ML second** | The rules explain themselves; a RandomForest cannot. The trained model runs alongside as a labelled second opinion with an `agrees_with_rules` flag. |
| Database | SQLite by default, PostgreSQL via `DATABASE_URL` | Runs with zero setup; scales to the PRD's stack without a code change. |

### Backend layout

```
backend/
  main.py                      app entry, auth, /api/analyze
  auth.py  models.py  database.py
  app/
    data/
      materials_seed.py        18 materials with real OTR/WVTR/thickness data
      commodity_profiles.py    respiration rates + MAP windows, 22 commodities
      fssai_additives.py       permitted / banned additives with category limits
      vendors_seed.py          supplier catalogue with tiered MOQ pricing
      seed_db.py  migrate.py
    services/
      expert_engine.py         the rule engine (requirements → screening → MAP)
      compliance.py            FSSAI additive validator
      nutrition.py             traffic lights + Indian Nutrition Rating
      ocr_parser.py            nutrition panel OCR / text parsing
      dieline_gen.py           SVG + PDF die-line with statutory layout
      marketplace.py           vendor matching, pricing, RFQ/PO workflow
    api/routes/
      account.py  compliance.py  dieline.py  marketplace.py  traceability.py
```

---

## Running it

### Local (two terminals)

**Backend** — http://127.0.0.1:8000, docs at `/docs`

```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows;  source venv/bin/activate elsewhere
pip install -r requirements.txt
cp .env.example .env             # then set SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"
uvicorn main:app --reload --port 8000
```

Run it from inside `backend/` — the model artefacts and the SQLite file are
resolved relative to the working directory. Tables, schema migrations, the
material catalogue and the vendor seed all run automatically on startup.

**Frontend** — http://localhost:5173

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(48))")
docker compose up --build
```

Brings up PostgreSQL, the API on :8000 and the web app on :5173, with
Tesseract installed so label-photo OCR works.

---

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `SECRET_KEY` | *(none — required)* | JWT signing key. The app refuses to start without it. |
| `JWT_ALGORITHM` | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | |
| `DATABASE_URL` | `sqlite:///./packgenius.db` | Set a `postgresql+psycopg2://…` DSN to use Postgres. |
| `VITE_API_BASE` | `http://127.0.0.1:8000` | Frontend only, build-time. |

---

## API tour

| Endpoint | Purpose |
|---|---|
| `POST /api/signup`, `/api/login` | JWT auth, buyer or supplier role |
| `POST /api/analyze` | The core recommendation — specs, reasons, MAP, alternatives |
| `GET  /api/materials` | The packaging material reference database |
| `PATCH /api/account/profile`, `POST /api/account/kyc` | Role and vendor KYC |
| `POST /api/compliance/preservatives` | FSSAI additive screening |
| `POST /api/compliance/nutrition` | Traffic lights + INR stars |
| `POST /api/compliance/parse-text`, `/ocr` | Nutrition panel reading |
| `POST /api/compliance/label` | Persist a label, mint a trace code |
| `GET  /api/public/trace/{code}` | Public consumer page (no auth) |
| `GET  /api/public/trace/{code}/qr.png` | QR code for the pack |
| `POST /api/dieline/geometry` \| `/svg` \| `/pdf` | Die-line geometry and artwork |
| `GET  /api/marketplace/vendors`, `/price-curve` | Supplier matching, volume pricing |
| `POST /api/marketplace/rfq`, `/quote`, `/purchase-order` | Sourcing workflow |
| `GET  /api/marketplace/board` | Order-tracking Kanban |

---

## Data provenance and limits

Read this before quoting any number to a regulator or a customer.

- **Barrier figures** in `materials_seed.py` are indicative industry typicals at the
  stated reference thickness (OTR at 23 °C/0 % RH, WVTR at 38 °C/90 % RH). Real film
  varies by supplier and grade; a vendor confirms against their own datasheet.
- **Respiration rates** are published post-harvest values at 5 °C with a Q10
  temperature correction. Commodities outside the 22-entry table fall back to a
  moderate default, and the response says so.
- **FSSAI additive limits** are indicative and category-dependent, and the
  regulations are amended regularly. Every compliance response carries a disclaimer:
  this screens for likely problems, it does not certify compliance.
- **The INR star rating** is a documented approximation of the FSSAI draft algorithm,
  suitable for product development. Use the official calculator for label filing.
- **The ML model** is trained on synthetic data expanded from 8 profiles. It informs
  nothing on its own — it is displayed as a second opinion only.

## Known gaps

- **SSO (Google / LinkedIn)** is not implemented. It needs OAuth client credentials
  registered to the deploying organisation, which cannot be committed to a repo.
- **KYC verification** records and format-checks GSTIN/FSSAI/EPR identifiers and marks
  them `pending`. Clearing to `verified` requires the GST and FSSAI lookup APIs, which
  need operator credentials. Nothing is ever auto-approved — a self-declared
  "verified" badge would be worse than none.
- **OCR** needs the Tesseract binary. Without it `/api/compliance/ocr` returns a clear
  message and the paste-text route handles the work; the Docker image includes it.
- **Schema migrations** are additive only (`ALTER TABLE ADD COLUMN`). A destructive
  change needs Alembic.
