"""Seed the packaging_materials table from the reference catalogue.

Idempotent: safe to run on every startup. Existing rows are updated in place so
catalogue edits propagate without dropping the table.
"""

from sqlalchemy.orm import Session

import models
from app.data.materials_seed import MATERIALS


def seed_materials(db: Session) -> int:
    existing = {m.code: m for m in db.query(models.PackagingMaterial).all()}
    written = 0

    for spec in MATERIALS:
        row = existing.get(spec["code"])
        if row is None:
            db.add(models.PackagingMaterial(**spec))
            written += 1
        else:
            for key, value in spec.items():
                if getattr(row, key) != value:
                    setattr(row, key, value)
                    written += 1

    db.commit()
    return written


def material_dicts(db: Session):
    """Catalogue as plain dicts, the shape the expert engine expects."""
    columns = [c.name for c in models.PackagingMaterial.__table__.columns]
    return [
        {c: getattr(row, c) for c in columns}
        for row in db.query(models.PackagingMaterial).all()
    ]
