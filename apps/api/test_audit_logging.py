import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from main import app
from database import engine
from models import AuditLog, Organization, Membership

pytestmark = pytest.mark.integration

client = TestClient(app)


def make_token(user_id: str, org_id: str, role: str = "admin") -> str:
    import jwt
    from config import settings

    payload = {"sub": user_id, "org_id": org_id, "role": role}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


def create_test_org() -> tuple[str, str]:
    org_id = str(uuid.uuid4())
    user_id = f"user_{uuid.uuid4().hex[:8]}"

    with Session(engine) as session:
        org = Organization(id=org_id, name="Audit Org", slug=f"audit-{org_id[:8]}")
        session.add(org)
        session.commit()

        membership = Membership(
            id=str(uuid.uuid4()),
            user_id=user_id,
            organization_id=org_id,
            role="admin",
        )
        session.add(membership)
        session.commit()

    return org_id, user_id


def test_audit_log_records_create_update_delete(caplog):
    org_id, user_id = create_test_org()
    token = make_token(user_id, org_id)

    caplog.set_level("INFO")

    # CREATE
    r = client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "P1", "description": "d"},
    )
    assert r.status_code == 200
    project_id = r.json()["id"]

    # UPDATE
    r = client.put(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "P2", "description": "d2"},
    )
    assert r.status_code == 200

    # DELETE
    r = client.delete(
        f"/api/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200

    with Session(engine) as session:
        rows = session.exec(
            select(AuditLog)
            .where(AuditLog.organization_id == org_id)
            .where(AuditLog.table_name == "project")
            .order_by(AuditLog.created_at.asc())
        ).all()

    ops = [r.operation for r in rows]
    assert "CREATE" in ops
    assert "UPDATE" in ops
    assert "DELETE" in ops

    # Ensure context is present
    for row in rows:
        assert row.user_id == user_id
        assert row.organization_id == org_id

    # Request logging emitted
    request_logs = [rec.message for rec in caplog.records if rec.name == "forgeos.request"]
    assert any('"path": "/api/projects"' in m for m in request_logs)


def test_audit_log_endpoint_lists_rows():
    org_id, user_id = create_test_org()
    token = make_token(user_id, org_id, role="admin")

    client.post(
        "/api/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "P1", "description": "d"},
    )

    r = client.get(
        "/api/audit-log",
        headers={"Authorization": f"Bearer {token}"},
        params={"table_name": "project", "limit": 10},
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert any(item["table_name"] == "project" for item in data)
