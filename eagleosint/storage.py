"""
SQLite persistence layer for investigation sessions and provider results.

Engine is lazily initialized - call init_db() before first use.
Tests inject "sqlite:///:memory:" via init_db() in fixtures.
"""
from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, ForeignKey, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from eagleosint.models import (
    AccountHit, DomainResult, DorkResult, EmailResult,
    GitHubProfile, IPResult, PhoneResult, ProviderResult, URLExpansion,
)

from platformdirs import user_data_dir

# --------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------

_DATA_DIR = user_data_dir("eagleosint", appauthor=False)
DB_PATH = os.path.join(_DATA_DIR, "investigations.db")

class _Base(DeclarativeBase):
    pass

class InvestigationRow(_Base):
    __tablename__ = "investigations"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    updated_at = Column(String, nullable=False)
    tags = Column(Text, nullable=False, default="[]")
    notes = Column(Text, nullable=False, default="")
    results = relationship(
        "ResultRow", back_populates="investigation",
        cascade="all, delete-orphan"
    )

class ResultRow(_Base):
    __tablename__ = "results"

    id = Column(String, primary_key=True)
    investigation_id = Column(String, ForeignKey("investigations.id"), nullable=False)
    source = Column(String, nullable=False)
    query = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    confidence = Column(String, nullable=False, default="unknown")
    data = Column(Text, nullable=False) # full model_dump JSON
    investigation = relationship("InvestigationRow", back_populates="results")


# --------------------------------------------------------------------
# Engine - lazy init
# --------------------------------------------------------------------

_engine = None
_SessionLocal = None

def init_db(url: str | None = None) -> None:
    """
    Initialize (or re-initialize) the database engine.
    Call with no arguments for production use,
    Call with "sqlite:///:memory:" in tests for full isolation.
    """
    global _engine, _SessionLocal

    db_url = url or f"sqlite:///{DB_PATH}"

    kwargs: dict[str, Any] = {}
    if db_url == "sqlite:///:memory:":
        from sqlalchemy.pool import StaticPool
        kwargs = {
            "connect_args": {"check_same_thread": False},
            "poolclass": StaticPool,
        }

    os.makedirs(_DATA_DIR, exist_ok=True)
    _engine = create_engine(db_url, echo=False, **kwargs)
    _Base.metadata.create_all(_engine)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)

def _session():
    """Return a new session, initializing the DB if needed."""
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()

# ---------------------------------------------------------------------------
# Type registry for result deserialization
# ---------------------------------------------------------------------------

_SOURCE_MAP: dict[str, type[ProviderResult]] = {
    "userrecon": AccountHit,
    "mailfinder": EmailResult,
    "phoneinfo": PhoneResult,
    "github": GitHubProfile,
    "godorker": DorkResult,
    "bitly": URLExpansion,
    "network": IPResult,
}

def _deserialize(row: ResultRow) -> ProviderResult:
    data = json.loads(row.data)
    # DomainResult and IPResult both have source="network"; disambiguate by fields
    if row.source == "network" and "query_type" in data:
        return DomainResult.model_validate(data)
    cls = _SOURCE_MAP.get(row.source, ProviderResult)
    return cls.model_validate(data)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()

def _make_id(name: str) -> str:
    """Slug + timestamp suffix - readable and collision-free."""
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-") or "investigation"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"{slug}-{ts}"

# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

def create_investigation(
        name: str,
        tags: list[str] | None = None,
        notes: str = "",
) -> InvestigationRow:
    """Create and persist a new investigation. Returns the ORM row."""
    row = InvestigationRow(
        id = _make_id(name),
        name = name,
        created_at = _utcnow(),
        updated_at = _utcnow(),
        tags = json.dumps(tags or []),
        notes = notes,
    )
    with _session() as s:
        s.add(row)
        s.commit()
        s.refresh(row)
    return row

def get_investigation(investigation_id: str) -> InvestigationRow | None:
    """Fetch an investigation by ID. Returns None if not found"""
    with _session() as s:
        return s.get(InvestigationRow, investigation_id)

def list_investigations() -> list[InvestigationRow]:
    """Return all investigations, newest first"""
    with _session() as s:
        return (
            s.query(InvestigationRow)
            .order_by(InvestigationRow.created_at.desc())
            .all()
        )

def save_result(investigation_id: str, result: ProviderResult) -> ResultRow:
    """Persist a ProviderResult under and existing investigation."""
    row = ResultRow(
        id = str(uuid.uuid4()),
        investigation_id = investigation_id,
        source = result.source,
        query = result.query,
        timestamp = result.timestamp.isoformat(),
        confidence = result.confidence.value,
        data = result.model_dump_json(),
    )
    with _session() as s:
        inv = s.get(InvestigationRow, investigation_id)
        if inv:
            inv.updated_at = _utcnow()
            s.add(row)
            s.commit()
    return row

def get_results(investigation_id: str) -> list[ProviderResult]:
    """Load and deserialize all results for an investigation."""
    with _session() as s:
        rows = (
            s.query(ResultRow)
            .filter(ResultRow.investigation_id == investigation_id)
            .order_by(ResultRow.timestamp)
            .all()
        )
    return [_deserialize(r) for r in rows]

def delete_investigation(investigation_id: str) -> bool:
    """Delete an investigation and all its results. Return True if found."""
    with _session() as s:
        row = s.get(InvestigationRow, investigation_id)
        if not row:
            return False
        s.delete(row)
        s.commit()
    return True

