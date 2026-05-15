# backend/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ── Local fallback ──────────────────────────────────────────────────────────
# If DATABASE_URL is not set, default to a local SQLite database so the app
# runs out-of-the-box without any external database.
# To use PostgreSQL locally, set DATABASE_URL in your .env file, e.g.:
#   DATABASE_URL=postgresql://postgres:password@localhost:5432/mydb
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///./local_dev.db"
# ───────────────────────────────────────────────────────────────────────────

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# Fix old-style PostgreSQL URLs
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ── Engine kwargs vary by DB backend ────────────────────────────────────────
# SQLite doesn't support pool_size / max_overflow; PostgreSQL does.
is_sqlite = DATABASE_URL.startswith("sqlite")

engine_kwargs = dict(pool_pre_ping=True)  # shared option
if not is_sqlite:
    engine_kwargs.update(pool_size=10, max_overflow=20)
else:
    # SQLite requires check_same_thread=False when used with FastAPI/threading
    engine_kwargs["connect_args"] = {"check_same_thread": False}
# ───────────────────────────────────────────────────────────────────────────

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    # connect_args={"sslmode": "require"},  # Enforce SSL for Supabase
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,
    max_overflow=20
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()