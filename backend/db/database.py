"""
Storage for analysis history and the response cache.

Uses MySQL / TiDB Cloud when DB_HOST is set, otherwise a local SQLite file.
Every function here is best-effort: if the database is unavailable the
analysis still works, it just isn't saved or served from cache.
"""
import hashlib
import json
import logging
import ssl
from datetime import datetime, timezone

from sqlalchemy import (Column, DateTime, Integer, String, Text, create_engine,
                        select)
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker

import config

logger = logging.getLogger(__name__)

# TEXT is limited to 64 KB in MySQL; results can be larger
LongText = Text().with_variant(mysql.MEDIUMTEXT(), "mysql")

Base = declarative_base()


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(String(64), index=True, nullable=False)
    cache_key = Column(String(64), index=True, nullable=False)
    title = Column(String(200), nullable=False)
    mode = Column(String(16))
    language = Column(String(16))
    input_text = Column(LongText, nullable=False)
    result = Column(LongText, nullable=False)  # JSON
    created_at = Column(DateTime, nullable=False,
                        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


def _make_engine():
    if config.DB_HOST:
        url = URL.create(
            "mysql+pymysql",
            username=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT,
            database=config.DB_NAME,
            query={"charset": "utf8mb4"},
        )
        # TiDB Cloud requires TLS; verify the server with the system CA store
        return create_engine(url, connect_args={"ssl": ssl.create_default_context()},
                             pool_pre_ping=True, pool_recycle=300)
    return create_engine(f"sqlite:///{config.SQLITE_PATH}",
                         connect_args={"check_same_thread": False})


engine = _make_engine()
Session = sessionmaker(bind=engine, expire_on_commit=False)
_ready = False


def init_db() -> bool:
    """Create tables if needed. Returns False (and logs) if the DB is unreachable."""
    global _ready
    try:
        Base.metadata.create_all(engine)
        _ready = True
        logger.info("Database ready: %s", "MySQL/TiDB" if config.DB_HOST else config.SQLITE_PATH)
    except Exception as e:
        _ready = False
        logger.error("Database unavailable, history and cache are disabled: %s", e)
    return _ready


def make_cache_key(request) -> str:
    payload = json.dumps({
        "v": config.CACHE_VERSION,
        "input": (request.input or "").strip(),
        "code": (request.code or "").strip(),
        "problem": (request.problem or "").strip(),
        "language": request.language or None,
    }, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get_cached(cache_key: str):
    """Return a previous result for exactly the same request, or None."""
    if not _ready:
        return None
    try:
        with Session() as s:
            row = s.scalars(select(Analysis).where(Analysis.cache_key == cache_key)
                            .order_by(Analysis.id.desc()).limit(1)).first()
            return json.loads(row.result) if row else None
    except Exception as e:
        logger.warning("Cache lookup failed: %s", e)
        return None


def save_analysis(client_id: str, cache_key: str, input_text: str, result: dict):
    """Store a result in the client's history. Returns the new id, or None."""
    if not _ready:
        return None
    title = (result.get("problem_statement") or input_text).strip().splitlines()[0][:200]
    try:
        with Session() as s:
            row = Analysis(client_id=client_id, cache_key=cache_key, title=title,
                           mode=result.get("mode"), language=result.get("language"),
                           input_text=input_text, result=json.dumps(result, ensure_ascii=False))
            s.add(row)
            s.commit()
            return row.id
    except Exception as e:
        logger.warning("Saving history failed: %s", e)
        return None


def list_history(client_id: str) -> list:
    if not _ready:
        return []
    try:
        with Session() as s:
            rows = s.scalars(select(Analysis).where(Analysis.client_id == client_id)
                             .order_by(Analysis.id.desc()).limit(config.HISTORY_LIMIT)).all()
            return [{"id": r.id, "title": r.title, "mode": r.mode, "language": r.language,
                     "created_at": r.created_at.isoformat() + "Z"} for r in rows]
    except Exception as e:
        logger.warning("Loading history failed: %s", e)
        return []


def get_analysis(client_id: str, analysis_id: int):
    if not _ready:
        return None
    with Session() as s:
        r = s.get(Analysis, analysis_id)
        if not r or r.client_id != client_id:
            return None
        return {"id": r.id, "input": r.input_text, "result": json.loads(r.result)}


def delete_analysis(client_id: str, analysis_id: int) -> bool:
    if not _ready:
        return False
    with Session() as s:
        r = s.get(Analysis, analysis_id)
        if not r or r.client_id != client_id:
            return False
        s.delete(r)
        s.commit()
        return True
