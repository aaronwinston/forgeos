import os
import tempfile
import sqlite3
from pathlib import Path

# Must be set before importing the app so scheduler.start() is skipped at startup
os.environ.setdefault("TESTING", "1")

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import jwt

from config import settings
from database import get_session
from main import app
from models import Organization, Membership


@pytest.fixture(scope="session")
def test_db_path():
    """Create a temporary test database."""
    # Use a consistent test db in .test_dbs directory
    db_dir = Path(__file__).parent.parent / ".test_dbs"
    db_dir.mkdir(exist_ok=True)
    db_path = db_dir / "test.db"
    yield str(db_path)


@pytest.fixture(scope="function")
def test_db(test_db_path):
    """Create a fresh test database for each test."""
    # Delete previous test db to start fresh
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Create new engine for this test
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    # Create all tables
    SQLModel.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    engine.dispose()


@pytest.fixture
def test_session(test_db):
    """Create a test database session."""
    connection = test_db.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def test_org(test_session) -> Organization:
    """Create a test organization."""
    org = Organization(
        id="test-org-1",
        name="Test Organization",
        slug="test-org",
    )
    test_session.add(org)
    test_session.commit()
    test_session.refresh(org)
    return org


@pytest.fixture
def test_user(test_session, test_org) -> tuple[str, str]:
    """Create a test user and return (user_id, org_id)."""
    user_id = "test-user-1"
    membership = Membership(
        id="test-member-1",
        user_id=user_id,
        organization_id=test_org.id,
        role="member",
    )
    test_session.add(membership)
    test_session.commit()
    return user_id, test_org.id


@pytest.fixture
def test_admin_user(test_session, test_org) -> tuple[str, str]:
    """Create a test admin user and return (user_id, org_id)."""
    user_id = "test-admin-1"
    membership = Membership(
        id="test-admin-member-1",
        user_id=user_id,
        organization_id=test_org.id,
        role="admin",
    )
    test_session.add(membership)
    test_session.commit()
    return user_id, test_org.id


@pytest.fixture
def test_owner_user(test_session, test_org) -> tuple[str, str]:
    """Create a test owner user and return (user_id, org_id)."""
    user_id = "test-owner-1"
    membership = Membership(
        id="test-owner-member-1",
        user_id=user_id,
        organization_id=test_org.id,
        role="owner",
    )
    test_session.add(membership)
    test_session.commit()
    return user_id, test_org.id


@pytest.fixture
def test_token(test_user):
    """Create a valid JWT token for test_user."""
    user_id, org_id = test_user
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": "member",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


@pytest.fixture
def test_admin_token(test_admin_user):
    """Create a valid JWT token for test_admin_user."""
    user_id, org_id = test_admin_user
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": "admin",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


@pytest.fixture
def test_owner_token(test_owner_user):
    """Create a valid JWT token for test_owner_user."""
    user_id, org_id = test_owner_user
    payload = {
        "sub": user_id,
        "org_id": org_id,
        "role": "owner",
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return token


@pytest.fixture
def client(test_db):
    """Override the app dependency to use test database."""
    def override_get_session():
        with Session(test_db) as session:
            yield session
    
    app.dependency_overrides[get_session] = override_get_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test."""
    limiter = getattr(app.state, "limiter", None)
    if limiter is None:
        yield
        return
    
    storage = getattr(limiter, "_storage", None)
    if storage is not None:
        for method_name in ("reset", "clear", "flushall"):
            if hasattr(storage, method_name):
                getattr(storage, method_name)()
                break
        else:
            internal = getattr(storage, "storage", None)
            if hasattr(internal, "clear"):
                internal.clear()
    
    yield
    
    # Reset again after test
    storage = getattr(limiter, "_storage", None)
    if storage is not None:
        for method_name in ("reset", "clear", "flushall"):
            if hasattr(storage, method_name):
                getattr(storage, method_name)()
                break
        else:
            internal = getattr(storage, "storage", None)
            if hasattr(internal, "clear"):
                internal.clear()
