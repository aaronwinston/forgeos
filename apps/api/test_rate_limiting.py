import uuid

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from config import settings
from database import engine
from main import app
from models import Membership, Organization

pytestmark = pytest.mark.rate_limit

client = TestClient(app)


def _limit_count(limit: str) -> int:
    # supports "10/minute", "100/minute" etc.
    return int(limit.split("/", 1)[0].strip())


@pytest.fixture(autouse=True)
def reset_rate_limiter_storage():
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


def _create_org_and_user() -> tuple[str, str]:
    org_id = str(uuid.uuid4())
    user_id = f"user_{uuid.uuid4().hex[:8]}"
    with Session(engine) as session:
        org = Organization(id=org_id, name="Test Org", slug=f"test-org-{org_id[:8]}")
        session.add(org)
        session.commit()

        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=org_id,
            role="owner",
        )
        session.add(membership)
        session.commit()

    return org_id, user_id


def _make_token(user_id: str, org_id: str, role: str = "member") -> str:
    payload = {"sub": user_id, "org_id": org_id, "role": role}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def test_auth_endpoints_are_rate_limited():
    max_ok = _limit_count(settings.RATE_LIMIT_AUTH)

    last = None
    for i in range(max_ok + 1):
        last = client.post(
            "/api/auth/signin",
            json={"email": f"test{i}@example.com", "password": "pw"},
        )

    assert last is not None
    assert last.status_code == 429
    assert "X-RateLimit-Limit" in last.headers


def test_public_endpoints_are_rate_limited():
    max_ok = _limit_count(settings.RATE_LIMIT_PUBLIC)

    last = None
    for _ in range(max_ok + 1):
        last = client.get("/api/health")

    assert last is not None
    assert last.status_code == 429
    assert "X-RateLimit-Limit" in last.headers


def test_internal_endpoints_are_rate_limited_per_user():
    org_id, user_id = _create_org_and_user()
    token = _make_token(user_id, org_id)

    max_ok = _limit_count(settings.RATE_LIMIT_INTERNAL)

    last = None
    for _ in range(max_ok + 1):
        last = client.get("/api/projects", headers={"Authorization": f"Bearer {token}"})

    assert last is not None
    assert last.status_code == 429
    assert "X-RateLimit-Limit" in last.headers


def test_expensive_endpoints_have_global_cap():
    org_id, user_id = _create_org_and_user()
    token = _make_token(user_id, org_id)

    max_ok = _limit_count(settings.RATE_LIMIT_EXPENSIVE_GLOBAL)

    last = None
    for _ in range(max_ok + 1):
        last = client.post(
            "/api/trust/export",
            headers={"Authorization": f"Bearer {token}"},
            json={"include_events": False, "include_documents": False, "include_projects": False},
        )

    assert last is not None
    assert last.status_code == 429
    assert "X-RateLimit-Limit" in last.headers
