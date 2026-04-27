from __future__ import annotations

from pathlib import Path
import re
import sqlite3
from typing import Optional

from sqlalchemy import event
from sqlmodel import Session, create_engine

from config import settings


def _is_sqlite_url(database_url: str) -> bool:
    return database_url.startswith("sqlite://")


def _sqlite_db_path(database_url: str) -> Path:
    # Supported forms:
    #   sqlite:///./forgeos.db
    #   sqlite:////absolute/path.db
    if not database_url.startswith("sqlite:///"):
        raise ValueError(f"Unsupported SQLite URL: {database_url}")

    raw = database_url[len("sqlite:///") :]
    # Absolute path is represented as leading '/'
    p = Path(raw)
    if not p.is_absolute():
        # Resolve relative paths against apps/api/ so behavior is consistent
        p = Path(__file__).parent / p
    return p


def _configure_sqlite_engine(eng) -> None:
    @event.listens_for(eng, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


_engine_kwargs = {}
if _is_sqlite_url(settings.DATABASE_URL):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, echo=False, **_engine_kwargs)

if _is_sqlite_url(settings.DATABASE_URL):
    _configure_sqlite_engine(engine)


def get_session():
    with Session(engine) as session:
        yield session


def _parse_schema_blocks(sql_text: str) -> dict[str, str]:
    """Parse blocks in a migration SQL file.

    Blocks are delimited by lines like: -- table: <name>
    """
    blocks: dict[str, list[str]] = {}
    current: Optional[str] = None

    for line in sql_text.splitlines():
        m = re.match(r"^--\s*table:\s*(\w+)\s*$", line)
        if m:
            current = m.group(1)
            blocks.setdefault(current, [])
            continue
        if current is None:
            continue
        blocks[current].append(line)

    return {k: "\n".join(v).strip() for k, v in blocks.items()}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    cur = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)
    )
    return cur.fetchone() is not None


def _first_org_id(conn: sqlite3.Connection) -> Optional[str]:
    if not _table_exists(conn, "organization"):
        return None
    row = conn.execute("SELECT id FROM organization ORDER BY created_at LIMIT 1").fetchone()
    return row[0] if row else None


def _ensure_default_org(conn: sqlite3.Connection) -> str:
    """Guarantee there is at least one organization row for backfilling org_id."""
    org_id = _first_org_id(conn)
    if org_id:
        return org_id

    default_id = "default-org"
    conn.execute(
        "INSERT INTO organization (id, name, slug, plan, created_at, updated_at) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
        (default_id, "Default Org", "default", "free"),
    )
    return default_id


def _copy_table(
    conn: sqlite3.Connection,
    table: str,
    old_table: str,
    default_org_id: Optional[str],
):
    new_cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    old_cols = conn.execute(f"PRAGMA table_info({old_table})").fetchall()

    new_names = [r[1] for r in new_cols]
    old_names = {r[1] for r in old_cols}

    insert_cols: list[str] = []
    select_exprs: list[str] = []
    params: list[object] = []

    for col in new_names:
        if col in old_names:
            # Avoid propagating NULLs into new NOT NULL columns with very simple fallbacks.
            if col in {"updated_at"}:
                insert_cols.append(col)
                if "created_at" in old_names:
                    select_exprs.append(f"COALESCE({col}, created_at, datetime('now'))")
                else:
                    select_exprs.append(f"COALESCE({col}, datetime('now'))")
            elif col in {"created_at"}:
                insert_cols.append(col)
                select_exprs.append(f"COALESCE({col}, datetime('now'))")
            else:
                insert_cols.append(col)
                select_exprs.append(col)
        elif col == "organization_id":
            insert_cols.append(col)
            if not default_org_id:
                raise RuntimeError(
                    f"Cannot backfill organization_id for {table} without an organization"
                )
            select_exprs.append("?")
            params.append(default_org_id)
        else:
            # Leave as DB default / nullable
            pass

    if not insert_cols:
        return

    sql = (
        f"INSERT INTO {table} ({', '.join(insert_cols)}) "
        f"SELECT {', '.join(select_exprs)} FROM {old_table}"
    )
    conn.execute(sql, params)


def _rebuild_table(
    conn: sqlite3.Connection,
    table: str,
    schema_sql: str,
    default_org_id: Optional[str],
):
    if not _table_exists(conn, table):
        conn.executescript(schema_sql)
        return

    old = f"{table}__old_0001"
    if _table_exists(conn, old):
        conn.execute(f"DROP TABLE {old}")

    conn.execute(f"ALTER TABLE {table} RENAME TO {old}")
    conn.executescript(schema_sql)

    # Backfill org_id (or other new columns) by copying rows.
    _copy_table(conn, table, old, default_org_id)

    conn.execute(f"DROP TABLE {old}")


def _apply_migration_0001(conn: sqlite3.Connection, sql_path: Path):
    sql_text = sql_path.read_text(encoding="utf-8")
    blocks = _parse_schema_blocks(sql_text)

    # Rebuild order (parents first)
    table_order = [
        "organization",
        "membership",
        "project",
        "folder",
        "deliverable",
        "brief",
        "chatsession",
        "chatmessage",
        "scrapeitem",
        "pipelinerun",
        "pipelinestep",
        "calendarintegration",
        "calendarevent",
        "calendarsynclog",
        "keywordcluster",
        "gscquery",
        "trendsdata",
        "searchinsight",
        "runtimecredential",
        "usageevent",
        "featureflag",
        "auditevent",
        "doctrineversion",
    ]

    # organization must exist first to backfill org_id into legacy rows.
    _rebuild_table(conn, "organization", blocks["organization"], default_org_id=None)
    default_org_id = _ensure_default_org(conn)

    for t in table_order[1:]:
        if t not in blocks:
            continue
        _rebuild_table(conn, t, blocks[t], default_org_id=default_org_id)


def run_migrations(database_url: Optional[str] = None) -> None:
    """Apply SQL migrations.

    Currently supports SQLite only.
    """
    url = database_url or settings.DATABASE_URL
    if not _is_sqlite_url(url):
        return

    db_path = _sqlite_db_path(url)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    migrations_dir = Path(__file__).parent / "migrations"
    migrations_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys=OFF")
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT (datetime('now')))"
        )

        version = "0001_initial_constraints"
        already = conn.execute(
            "SELECT 1 FROM schema_migrations WHERE version=?", (version,)
        ).fetchone()
        if already:
            return

        sql_path = migrations_dir / f"{version}.sql"
        if not sql_path.exists():
            raise FileNotFoundError(f"Missing migration file: {sql_path}")

        conn.execute("BEGIN")
        _apply_migration_0001(conn, sql_path)
        conn.execute("INSERT INTO schema_migrations(version) VALUES (?)", (version,))
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.execute("PRAGMA foreign_keys=ON")
        conn.close()


def create_db_and_tables():
    # Import all models to ensure they're registered (and for create_all fallback)
    import models  # noqa: F401

    # Run Alembic migrations for version-controlled schema changes
    try:
        from migration_runner import run_pending_migrations
        run_pending_migrations()
    except Exception as e:
        # Fall back to the legacy migration system if Alembic fails
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Alembic migration failed, falling back to legacy migrations: {e}")
        run_migrations()
