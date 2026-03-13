"""
Kavch Database Models
All tables for users, threat reports, scans, evidence vault, and legal documents.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    threat_reports = relationship("ThreatReport", back_populates="user", cascade="all, delete-orphan")
    scan_results = relationship("ScanResult", back_populates="user", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItem", back_populates="user", cascade="all, delete-orphan")
    legal_documents = relationship("LegalDocument", back_populates="user", cascade="all, delete-orphan")


class ThreatReport(Base):
    __tablename__ = "threat_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String(50), default="English")
    tier = Column(Integer, default=1)
    label = Column(String(100), default="")
    confidence = Column(Float, default=0.0)
    raw_result = Column(JSON, nullable=True)  # Store full classifier response
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="threat_reports")


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), default="uploaded_image")
    is_clean = Column(Boolean, default=True)
    manipulation_score = Column(Float, default=0.0)
    analysis_notes = Column(Text, default="")
    raw_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="scan_results")


class EvidenceItem(Base):
    __tablename__ = "evidence_vault"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    evidence_id = Column(String(20), unique=True, index=True)  # e.g. KV-A4F2C8...
    type = Column(String(50), default="url")  # url, image, threat, scan
    title = Column(String(500), default="")
    platform = Column(String(200), default="")
    hash = Column(String(64), nullable=False)
    content_preview = Column(Text, default="")
    raw_data = Column(Text, nullable=True)  # URL or base64 (for evidence retrieval)
    locked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="evidence_items")


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doc_type = Column(String(100), nullable=False)
    city = Column(String(100), default="")
    platform = Column(String(200), default="")
    language = Column(String(50), default="English")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="legal_documents")
