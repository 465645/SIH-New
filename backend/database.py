import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# SQLite by default so the project runs with no external services. Set
# DATABASE_URL to a PostgreSQL DSN (the stack the PRD specifies) to switch:
#   DATABASE_URL=postgresql+psycopg2://packgenius:packgenius@localhost:5432/packgenius
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./packgenius.db")

_is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # check_same_thread is a SQLite-only concern; passing it to Postgres errors.
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: one session per request, always closed."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
