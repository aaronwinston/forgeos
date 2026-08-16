import os
from pathlib import Path

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, create_engine

import database
from models import Organization, Project

pytestmark = pytest.mark.integration


@pytest.fixture()
def constraint_db_engine():
    base_dir = Path(__file__).parent
    db_dir = base_dir / ".test_dbs"
    db_dir.mkdir(exist_ok=True)

    db_path = db_dir / "constraints.db"
    if db_path.exists():
        db_path.unlink()

    url = f"sqlite:///{db_path}"
    database.run_migrations(url)

    engine = create_engine(url, connect_args={"check_same_thread": False})
    database._configure_sqlite_engine(engine)

    try:
        yield engine
    finally:
        try:
            db_path.unlink()
        except FileNotFoundError:
            pass


def test_unique_org_slug_enforced(constraint_db_engine):
    with Session(constraint_db_engine) as session:
        org1 = Organization(name="Acme", slug="acme", plan="free")
        org2 = Organization(name="Acme2", slug="acme", plan="free")
        session.add(org1)
        session.commit()

        session.add(org2)
        with pytest.raises(IntegrityError):
            session.commit()


def test_foreign_key_project_org_enforced(constraint_db_engine):
    with Session(constraint_db_engine) as session:
        bad_project = Project(organization_id="does-not-exist", user_id="u1", name="P1")
        session.add(bad_project)
        with pytest.raises(IntegrityError):
            session.commit()


def test_check_constraint_org_plan_enforced(constraint_db_engine):
    with Session(constraint_db_engine) as session:
        bad_org = Organization(name="Bad", slug="bad-slug", plan="enterprise")
        session.add(bad_org)
        with pytest.raises(IntegrityError):
            session.commit()
