"""
Kavch Database Setup
SQLite + SQLAlchemy for local persistent storage.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database file location — sits right next to your backend code
DB_PATH = os.path.join(os.path.dirname(__file__), "shieldher.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite + FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Dependency that provides a database session per request.
    Automatically closes the session when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist."""
    from models import User, ThreatReport, ScanResult, EvidenceItem, LegalDocument
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized at: {DB_PATH}")
