from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from models import Organization, Membership
from database import get_session
from middleware.auth import get_current_user, require_org_owner, AuthContext
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/api/orgs", tags=["organizations"])

class OrgCreate(BaseModel):
    name: str
    slug: str

class OrgResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    trial_ends_at: str = None
    created_at: str

@router.post("/", response_model=OrgResponse)
async def create_org(
    org_create: OrgCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a new organization."""
    
    # Check if slug is unique
    existing = session.exec(
        select(Organization).where(Organization.slug == org_create.slug)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    org = Organization(
        id=str(uuid.uuid4()),
        name=org_create.name,
        slug=org_create.slug,
        plan="free",
    )
    session.add(org)
    
    membership = Membership(
        id=str(uuid.uuid4()),
        user_id=auth.user_id,
        organization_id=org.id,
        role="owner",
    )
    session.add(membership)
    session.commit()
    session.refresh(org)
    
    return OrgResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        trial_ends_at=str(org.trial_ends_at) if org.trial_ends_at else None,
        created_at=str(org.created_at),
    )

@router.get("/{org_id}", response_model=OrgResponse)
async def get_org(
    org_id: str,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get organization details."""
    
    # Verify user is member
    membership = session.exec(
        select(Membership)
        .where(Membership.user_id == auth.user_id)
        .where(Membership.organization_id == org_id)
    ).first()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    org = session.exec(select(Organization).where(Organization.id == org_id)).first()
    
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return OrgResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        trial_ends_at=str(org.trial_ends_at) if org.trial_ends_at else None,
        created_at=str(org.created_at),
    )

@router.get("/")
async def list_orgs(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all organizations user is member of."""
    
    memberships = session.exec(
        select(Membership).where(Membership.user_id == auth.user_id)
    ).all()
    
    org_ids = [m.organization_id for m in memberships]
    
    if not org_ids:
        return []
    
    orgs = session.exec(
        select(Organization).where(Organization.id.in_(org_ids))
    ).all()
    
    return [
        OrgResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            plan=org.plan,
            trial_ends_at=str(org.trial_ends_at) if org.trial_ends_at else None,
            created_at=str(org.created_at),
        )
        for org in orgs
    ]
