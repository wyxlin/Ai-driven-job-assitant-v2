from __future__ import annotations

import enum
from contextlib import contextmanager
from datetime import datetime
from typing import Generator, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

_engine = None
_SessionLocal: Optional[sessionmaker] = None


class LLMStatus(str, enum.Enum):
    pending = "pending"
    processed = "processed"
    failed = "failed"


class Base(DeclarativeBase):
    pass


def _structured_data_column():
    # JSON on SQLite; JSONB on PostgreSQL — resolved at query time, not import time
    return mapped_column(JSON().with_variant(JSONB(), "postgresql"), nullable=True)


class Resume(Base):
    __tablename__ = "resume"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    structured_data: Mapped[Optional[dict]] = _structured_data_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now()
    )


class Job(Base):
    __tablename__ = "job"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    company: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    date_posted: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    apply_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_filtered: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=None)
    llm_status: Mapped[LLMStatus] = mapped_column(
        Enum(LLMStatus, name="llmstatus"),
        default=LLMStatus.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now()
    )

    evaluations: Mapped[List[JobEvaluation]] = relationship(
        "JobEvaluation", back_populates="job", cascade="all, delete-orphan"
    )


class JobEvaluation(Base):
    __tablename__ = "job_evaluation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("job.id"), nullable=False)
    match_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, server_default=func.now()
    )

    job: Mapped[Job] = relationship("Job", back_populates="evaluations")


def init_db(engine=None) -> None:
    global _engine, _SessionLocal
    if engine is not None:
        _engine = engine
    elif _engine is None:
        raise RuntimeError("No engine configured. Pass an engine to init_db().")
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    Base.metadata.create_all(bind=_engine)


def set_engine(engine) -> None:
    global _engine, _SessionLocal
    _engine = engine
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    if _SessionLocal is None:
        raise RuntimeError("Call init_db() before using get_session().")
    session: Session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def upsert_jobs(data: List[dict]) -> None:
    if not data:
        return
    if _engine is None:
        raise RuntimeError("Call init_db() before using upsert_jobs().")

    dialect = _engine.dialect.name
    with get_session() as session:
        if dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert
            stmt = pg_insert(Job).values(data).on_conflict_do_nothing(
                index_elements=["external_id"]
            )
        else:
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert
            stmt = sqlite_insert(Job).values(data).on_conflict_do_nothing(
                index_elements=["external_id"]
            )
        session.execute(stmt)


def get_pending_jobs(limit: int = 100) -> List[Job]:
    with get_session() as session:
        results = (
            session.query(Job)
            .filter(Job.is_filtered == True)  # noqa: E712
            .filter(Job.llm_status == LLMStatus.pending)
            .order_by(Job.id.asc())
            .limit(limit)
            .all()
        )
        for obj in results:
            session.expunge(obj)
        return results
