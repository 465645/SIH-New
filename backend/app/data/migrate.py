"""Minimal additive schema migration for SQLite.

SQLAlchemy's create_all() only creates missing tables, never new columns on an
existing one. This walks the declarative models and issues ALTER TABLE ADD COLUMN
for anything the live database is missing, so an existing packgenius.db keeps its
data when the models grow.

Additive only: it never drops or retypes a column. A destructive change still
needs a real migration tool (Alembic).
"""

from sqlalchemy import inspect, text

import models

_SQLITE_TYPES = {
    "INTEGER": "INTEGER", "VARCHAR": "VARCHAR", "FLOAT": "FLOAT",
    "BOOLEAN": "BOOLEAN", "DATETIME": "DATETIME", "TEXT": "TEXT",
}


def _sqlite_type(column) -> str:
    compiled = column.type.compile(dialect=None) if hasattr(column.type, "compile") else None
    name = type(column.type).__name__.upper()
    return _SQLITE_TYPES.get(name, compiled or "TEXT")


def add_missing_columns(engine) -> list:
    """Returns a list of 'table.column' strings that were added.

    ALTER TABLE ADD COLUMN is portable across SQLite and PostgreSQL, so this
    works on both. Anything beyond additive changes needs Alembic.
    """
    inspector = inspect(engine)
    added = []

    for table in models.Base.metadata.sorted_tables:
        if table.name not in inspector.get_table_names():
            continue  # create_all will handle a brand new table
        existing = {c["name"] for c in inspector.get_columns(table.name)}

        for column in table.columns:
            if column.name in existing:
                continue
            ddl = f'ALTER TABLE {table.name} ADD COLUMN {column.name} {_sqlite_type(column)}'
            with engine.begin() as conn:
                conn.execute(text(ddl))
            added.append(f"{table.name}.{column.name}")

    return added
