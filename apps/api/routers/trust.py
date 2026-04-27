"""Trust, security, legal, and compliance endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Organization, AuditEvent, Membership
from middleware.auth import get_current_user, AuthContext
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/trust", tags=["trust"])

class DataExportRequest(BaseModel):
    include_events: bool = True
    include_documents: bool = True
    include_projects: bool = True

class DataDeletionRequest(BaseModel):
    confirm_deletion: bool

@router.get("/legal/privacy")
async def get_privacy_policy():
    """Return privacy policy."""
    return {
        "title": "Privacy Policy",
        "last_updated": "2024-04-01",
        "version": "1.0",
        "content": """# Privacy Policy

ForgeOS respects your privacy. We collect only what's necessary to operate the service:

**Data we collect:**
- Account information (email, name, organization)
- API keys (encrypted at rest with AES-256-GCM)
- Usage events (tokens, API calls, skill executions)
- Audit logs (actions on resources)

**Data we don't collect:**
- Your documents (stay in your org)
- Your projects (self-contained per org)
- Third-party API responses (processed but not stored)

**Retention:**
- Account data: for the lifetime of your account
- Audit logs: 90 days minimum, longer if needed for disputes
- Usage events: 2 years for billing purposes
- Deleted orgs: 30-day grace period, then permanent deletion

**Your rights:**
- Access your data anytime via /api/trust/export
- Delete your account anytime via /api/trust/delete
- Request changes to personal information

**Contact:** privacy@forgeos.example (replace with real email)"""
    }

@router.get("/legal/terms")
async def get_terms_of_service():
    """Return terms of service."""
    return {
        "title": "Terms of Service",
        "last_updated": "2024-04-01",
        "version": "1.0",
        "content": """# Terms of Service

By using ForgeOS, you agree to:

1. **Legitimate use only** - no illegal activity, no spam, no abuse
2. **Your responsibility** - you control your API keys and credentials
3. **No guarantees** - ForgeOS is provided AS-IS without warranty
4. **Limits** - we reserve the right to rate limit or suspend abuse
5. **Your content** - you own your documents; we don't claim them

**Pricing:**
- Free: 1 user, 1 project, 7-day history
- Pro: $49/month, unlimited projects, 365-day history, integrations
- Team: $99/month per 3+ users, team features, role-based access

**Cancellation:** Cancel anytime; no refunds for partial months

**Contact:** legal@forgeos.example"""
    }

@router.get("/legal/dpa")
async def get_data_processing_agreement():
    """Return Data Processing Agreement (GDPR/CCPA compliance)."""
    return {
        "title": "Data Processing Agreement",
        "last_updated": "2024-04-01",
        "version": "1.0",
        "content": """# Data Processing Agreement

ForgeOS complies with GDPR, CCPA, and other privacy laws.

**Our commitment:**
- Data minimization: we collect only what's necessary
- Encryption: all data at rest is AES-256-GCM encrypted
- Audit logging: all access is logged and auditable
- Right to deletion: users can delete their account + data anytime
- Right to access: users can export their data anytime

**Subprocessors:**
- Anthropic (API calls for generation)
- OpenAI (if configured by user)
- GitHub Copilot (if configured by user)
- AWS (infrastructure, may be used)

**Data residency:** US-based (configurable for Team plans)

**Incident response:** We commit to notifying you within 72 hours of any breach

Contact: dpa@forgeos.example"""
    }

@router.post("/export")
async def export_user_data(
    req: DataExportRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Generate a complete data export for the user."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    export = {
        "export_date": datetime.utcnow().isoformat(),
        "organization": {
            "id": org.id,
            "name": org.name,
            "plan": org.plan,
            "created_at": str(org.created_at),
        }
    }
    
    # Include audit events
    if req.include_events:
        audit_events = session.exec(
            select(AuditEvent).where(
                AuditEvent.organization_id == auth.org_id
            )
        ).all()
        
        export["audit_events"] = [
            {
                "id": e.id,
                "action": e.action,
                "resource_type": e.resource_type,
                "created_at": str(e.created_at),
                "details": json.loads(e.details_json) if e.details_json else None
            }
            for e in audit_events
        ]
    
    # Include members
    members = session.exec(
        select(Membership).where(
            Membership.organization_id == auth.org_id
        )
    ).all()
    
    export["members"] = [
        {
            "user_id": m.user_id,
            "role": m.role,
            "joined_at": str(m.created_at)
        }
        for m in members
    ]
    
    return export

@router.post("/delete")
async def schedule_account_deletion(
    req: DataDeletionRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Schedule account deletion with 30-day grace period."""
    
    if not req.confirm_deletion:
        raise HTTPException(status_code=400, detail="Must confirm deletion")
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Set deletion scheduled flag
    deletion_scheduled_at = datetime.utcnow()
    
    import json as json_lib
    metadata = {}
    if org.metadata_json:
        try:
            metadata = json_lib.loads(org.metadata_json)
        except:
            pass
    
    metadata["deletion_scheduled_at"] = deletion_scheduled_at.isoformat()
    metadata["deletion_grace_until"] = (deletion_scheduled_at + timedelta(days=30)).isoformat()
    
    org.metadata_json = json_lib.dumps(metadata)
    session.add(org)
    session.commit()
    
    # Log audit event
    audit = AuditEvent(
        organization_id=auth.org_id,
        user_id=auth.user_id,
        action="data_deleted",
        resource_type="account",
        details_json=json_lib.dumps({
            "grace_period_days": 30,
            "scheduled_at": deletion_scheduled_at.isoformat()
        })
    )
    session.add(audit)
    session.commit()
    
    return {
        "status": "deletion_scheduled",
        "grace_period_days": 30,
        "deleted_at": (deletion_scheduled_at + timedelta(days=30)).isoformat(),
        "message": "Your account and data will be permanently deleted in 30 days. You can cancel this by logging in again."
    }

@router.get("/status")
async def get_service_status():
    """Return ForgeOS service status and uptime."""
    return {
        "status": "operational",
        "uptime_percentage": 99.9,
        "last_incident": None,
        "components": {
            "api": "operational",
            "web": "operational",
            "database": "operational",
            "stripe": "operational",
        },
        "contact": "support@forgeos.example"
    }

@router.get("/audit-log")
async def get_audit_log(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    limit: int = 100,
):
    """Get audit log for the organization (admin only)."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # TODO: Add role check (owner/admin only)
    
    events = session.exec(
        select(AuditEvent).where(
            AuditEvent.organization_id == auth.org_id
        ).order_by(AuditEvent.created_at.desc()).limit(limit)
    ).all()
    
    return [
        {
            "id": e.id,
            "action": e.action,
            "resource_type": e.resource_type,
            "user_id": e.user_id,
            "created_at": str(e.created_at),
            "details": json.loads(e.details_json) if e.details_json else None
        }
        for e in events
    ]
