from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import Session, select
from database import get_session
from models import (
    Project,
    Folder,
    Deliverable,
    Brief,
    ScrapeItem,
    ConversionTaxonomyDefinition,
    DeliverableConversionOutcomeSnapshot,
    DeliverableCTAExperiment,
)
from middleware.auth import get_current_user, AuthContext
from pydantic import BaseModel, validator
from typing import Optional, Any, Dict
from datetime import datetime, timezone
import json
import re
from monitoring import time_operation, trace_operation
from services.query_optimization import PaginationParams, add_pagination
from services.publishing import PublishPayload, build_publish_bundle

router = APIRouter(prefix="/api", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.get("/projects")
@trace_operation("list_projects")
def list_projects(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List projects for authenticated user's organization with pagination."""
    with time_operation("db_query", attributes={"table": "project", "operation": "list"}):
        pagination = PaginationParams(skip=skip, limit=limit)
        query = select(Project).where(Project.organization_id == auth.org_id)
        query = add_pagination(query, pagination)
        return session.exec(query).all()

@router.post("/projects")
def create_project(
    data: ProjectCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = Project(
        name=data.name,
        description=data.description,
        organization_id=auth.org_id,
        user_id=auth.user_id,
    )
    session.add(p)
    session.commit()
    session.refresh(p)
    return p

@router.get("/projects/{project_id}")
def get_project(
    project_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@router.put("/projects/{project_id}")
def update_project(
    project_id: int,
    data: ProjectCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    p.name = data.name
    if data.description is not None:
        p.description = data.description
    session.add(p)
    session.commit()
    session.refresh(p)
    return p

@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(p)
    session.commit()
    return {"ok": True}

class FolderCreate(BaseModel):
    project_id: int
    parent_folder_id: Optional[int] = None
    name: str

@router.get("/projects/{project_id}/folders")
def list_folders(
    project_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify project belongs to org
    p = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return session.exec(
        select(Folder).where(
            (Folder.project_id == project_id) & (Folder.organization_id == auth.org_id)
        )
    ).all()

@router.get("/folders/{folder_id}")
def get_folder(
    folder_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    f = session.exec(
        select(Folder).where(
            (Folder.id == folder_id) & (Folder.organization_id == auth.org_id)
        )
    ).first()
    if not f:
        raise HTTPException(status_code=404, detail="Folder not found")
    return f

@router.post("/folders")
def create_folder(
    data: FolderCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify project belongs to org
    p = session.exec(
        select(Project).where(
            (Project.id == data.project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    
    f = Folder(
        project_id=data.project_id,
        parent_folder_id=data.parent_folder_id,
        name=data.name,
        organization_id=auth.org_id,
    )
    session.add(f)
    session.commit()
    session.refresh(f)
    return f

@router.delete("/folders/{folder_id}")
def delete_folder(
    folder_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    f = session.exec(
        select(Folder).where(
            (Folder.id == folder_id) & (Folder.organization_id == auth.org_id)
        )
    ).first()
    if not f:
        raise HTTPException(status_code=404, detail="Folder not found")
    session.delete(f)
    session.commit()
    return {"ok": True}

class DeliverableCreate(BaseModel):
    folder_id: Optional[int] = None
    content_type: str
    title: str
    status: str = "draft"
    body_md: Optional[str] = None
    metadata_json: Optional[str] = None

class DeliverableUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    body_md: Optional[str] = None
    metadata_json: Optional[str] = None


class PublishBundleResponse(BaseModel):
    platform: str
    deliverable_id: int
    payload: PublishPayload
    adapter_payload: Dict[str, Any]


EVENT_KEY_RE = re.compile(r"^[a-z0-9:_-]+$")
CTA_VARIANT_RE = re.compile(r"^[A-Za-z0-9 _-]+$")


class ConversionTaxonomyCreate(BaseModel):
    event_key: str
    funnel_stage: str
    definition: str
    primary_cta: Optional[str] = None
    success_metric: Optional[str] = None

    @validator("event_key")
    def validate_event_key(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not EVENT_KEY_RE.match(normalized):
            raise ValueError("event_key must use lowercase letters, numbers, colon, dash, or underscore")
        return normalized

    @validator("funnel_stage", "definition")
    def validate_required_text(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("value cannot be empty")
        return value.strip()


class ConversionOutcomeSnapshotCreate(BaseModel):
    period_label: str
    visitors: Optional[int] = None
    conversions: Optional[int] = None
    conversion_rate: Optional[float] = None
    observed_outcome: Optional[str] = None
    notes: Optional[str] = None
    recorded_at: Optional[datetime] = None

    @validator("period_label")
    def validate_period_label(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("period_label is required")
        return value.strip()

    @validator("visitors", "conversions")
    def validate_non_negative_int(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 0:
            raise ValueError("value must be non-negative")
        return value

    @validator("conversion_rate")
    def validate_conversion_rate(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and (value < 0 or value > 1):
            raise ValueError("conversion_rate must be between 0 and 1")
        return value


class DeliverableCTAExperimentCreate(BaseModel):
    experiment_key: str
    variant_label: str
    hypothesis: Optional[str] = None
    observed_outcome: Optional[str] = None
    status: str = "active"
    impressions: Optional[int] = None
    conversions: Optional[int] = None
    conversion_rate: Optional[float] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    @validator("experiment_key")
    def validate_experiment_key(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not EVENT_KEY_RE.match(normalized):
            raise ValueError("experiment_key must use lowercase letters, numbers, colon, dash, or underscore")
        return normalized

    @validator("variant_label")
    def validate_variant_label(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("variant_label is required")
        if not CTA_VARIANT_RE.match(normalized):
            raise ValueError("variant_label has unsupported characters")
        return normalized

    @validator("status")
    def validate_status(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"active", "paused", "completed"}:
            raise ValueError("status must be active, paused, or completed")
        return normalized

    @validator("impressions", "conversions")
    def validate_non_negative_metrics(cls, value: Optional[int]) -> Optional[int]:
        if value is not None and value < 0:
            raise ValueError("value must be non-negative")
        return value

    @validator("conversion_rate")
    def validate_experiment_conversion_rate(cls, value: Optional[float]) -> Optional[float]:
        if value is not None and (value < 0 or value > 1):
            raise ValueError("conversion_rate must be between 0 and 1")
        return value


def _get_org_deliverable(
    session: Session,
    org_id: str,
    deliverable_id: int,
) -> Deliverable:
    deliverable = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) & (Deliverable.organization_id == org_id)
        )
    ).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return deliverable


def _serialize_taxonomy(item: ConversionTaxonomyDefinition) -> Dict[str, Any]:
    return {
        "id": item.id,
        "deliverable_id": item.deliverable_id,
        "content_type": item.content_type,
        "event_key": item.event_key,
        "funnel_stage": item.funnel_stage,
        "definition": item.definition,
        "primary_cta": item.primary_cta,
        "success_metric": item.success_metric,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


def _serialize_snapshot(item: DeliverableConversionOutcomeSnapshot) -> Dict[str, Any]:
    return {
        "id": item.id,
        "deliverable_id": item.deliverable_id,
        "period_label": item.period_label,
        "visitors": item.visitors,
        "conversions": item.conversions,
        "conversion_rate": item.conversion_rate,
        "observed_outcome": item.observed_outcome,
        "notes": item.notes,
        "recorded_at": item.recorded_at.isoformat(),
        "created_at": item.created_at.isoformat(),
    }


def _serialize_cta_experiment(item: DeliverableCTAExperiment) -> Dict[str, Any]:
    return {
        "id": item.id,
        "deliverable_id": item.deliverable_id,
        "experiment_key": item.experiment_key,
        "variant_label": item.variant_label,
        "hypothesis": item.hypothesis,
        "observed_outcome": item.observed_outcome,
        "status": item.status,
        "impressions": item.impressions,
        "conversions": item.conversions,
        "conversion_rate": item.conversion_rate,
        "started_at": item.started_at.isoformat() if item.started_at else None,
        "ended_at": item.ended_at.isoformat() if item.ended_at else None,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }

@router.get("/folders/{folder_id}/deliverables")
def list_deliverables(
    folder_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify folder belongs to org
    folder = session.exec(
        select(Folder).where(
            (Folder.id == folder_id) & (Folder.organization_id == auth.org_id)
        )
    ).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    return session.exec(
        select(Deliverable).where(
            (Deliverable.folder_id == folder_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).all()

@router.post("/deliverables")
def create_deliverable(
    data: DeliverableCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get or create default folder if not specified
    if not data.folder_id:
        project = session.exec(
            select(Project).where(
                (Project.user_id == auth.user_id) & (Project.organization_id == auth.org_id)
            )
        ).first()
        if not project:
            project = Project(
                user_id=auth.user_id,
                organization_id=auth.org_id,
                name="Default Project"
            )
            session.add(project)
            session.commit()
            session.refresh(project)
        
        folder = session.exec(
            select(Folder).where(
                (Folder.project_id == project.id) & (Folder.organization_id == auth.org_id)
            )
        ).first()
        if not folder:
            folder = Folder(
                project_id=project.id,
                organization_id=auth.org_id,
                name="Deliverables"
            )
            session.add(folder)
            session.commit()
            session.refresh(folder)
        folder_id = folder.id
    else:
        # Verify folder belongs to org
        folder = session.exec(
            select(Folder).where(
                (Folder.id == data.folder_id) & (Folder.organization_id == auth.org_id)
            )
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        folder_id = data.folder_id
    
    d = Deliverable(
        folder_id=folder_id,
        organization_id=auth.org_id,
        content_type=data.content_type,
        title=data.title,
        status=data.status,
        body_md=data.body_md,
        metadata_json=data.metadata_json,
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    return d

@router.get("/deliverables/{deliverable_id}")
def get_deliverable(
    deliverable_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    d = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    return d


@router.get("/deliverables/{deliverable_id}/conversion-loop")
def get_deliverable_conversion_loop(
    deliverable_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    deliverable = _get_org_deliverable(session, auth.org_id, deliverable_id)

    taxonomy = session.exec(
        select(ConversionTaxonomyDefinition)
        .where(
            (ConversionTaxonomyDefinition.organization_id == auth.org_id)
            & (ConversionTaxonomyDefinition.deliverable_id == deliverable.id)
        )
        .order_by(ConversionTaxonomyDefinition.created_at.desc())
    ).all()
    snapshots = session.exec(
        select(DeliverableConversionOutcomeSnapshot)
        .where(
            (DeliverableConversionOutcomeSnapshot.organization_id == auth.org_id)
            & (DeliverableConversionOutcomeSnapshot.deliverable_id == deliverable.id)
        )
        .order_by(DeliverableConversionOutcomeSnapshot.recorded_at.desc())
    ).all()
    experiments = session.exec(
        select(DeliverableCTAExperiment)
        .where(
            (DeliverableCTAExperiment.organization_id == auth.org_id)
            & (DeliverableCTAExperiment.deliverable_id == deliverable.id)
        )
        .order_by(DeliverableCTAExperiment.created_at.desc())
    ).all()

    return {
        "deliverable_id": deliverable.id,
        "content_type": deliverable.content_type,
        "taxonomy_definitions": [_serialize_taxonomy(row) for row in taxonomy],
        "conversion_outcomes": [_serialize_snapshot(row) for row in snapshots],
        "cta_experiments": [_serialize_cta_experiment(row) for row in experiments],
    }


@router.post("/deliverables/{deliverable_id}/conversion-taxonomy")
def create_conversion_taxonomy_definition(
    deliverable_id: int,
    payload: ConversionTaxonomyCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    deliverable = _get_org_deliverable(session, auth.org_id, deliverable_id)
    row = ConversionTaxonomyDefinition(
        organization_id=auth.org_id,
        deliverable_id=deliverable.id,
        created_by_user_id=auth.user_id,
        content_type=deliverable.content_type,
        event_key=payload.event_key,
        funnel_stage=payload.funnel_stage,
        definition=payload.definition,
        primary_cta=payload.primary_cta.strip() if payload.primary_cta else None,
        success_metric=payload.success_metric.strip() if payload.success_metric else None,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(row)
    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Conversion taxonomy event_key already exists for this deliverable",
        ) from exc
    session.refresh(row)
    return _serialize_taxonomy(row)


@router.post("/deliverables/{deliverable_id}/conversion-outcomes")
def create_conversion_outcome_snapshot(
    deliverable_id: int,
    payload: ConversionOutcomeSnapshotCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    deliverable = _get_org_deliverable(session, auth.org_id, deliverable_id)
    row = DeliverableConversionOutcomeSnapshot(
        organization_id=auth.org_id,
        deliverable_id=deliverable.id,
        created_by_user_id=auth.user_id,
        period_label=payload.period_label,
        visitors=payload.visitors,
        conversions=payload.conversions,
        conversion_rate=payload.conversion_rate,
        observed_outcome=payload.observed_outcome.strip() if payload.observed_outcome else None,
        notes=payload.notes.strip() if payload.notes else None,
        recorded_at=payload.recorded_at or datetime.now(timezone.utc),
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return _serialize_snapshot(row)


@router.get("/deliverables/{deliverable_id}/conversion-outcomes")
def list_conversion_outcome_snapshots(
    deliverable_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    deliverable = _get_org_deliverable(session, auth.org_id, deliverable_id)
    rows = session.exec(
        select(DeliverableConversionOutcomeSnapshot)
        .where(
            (DeliverableConversionOutcomeSnapshot.organization_id == auth.org_id)
            & (DeliverableConversionOutcomeSnapshot.deliverable_id == deliverable.id)
        )
        .order_by(DeliverableConversionOutcomeSnapshot.recorded_at.desc())
    ).all()
    return [_serialize_snapshot(row) for row in rows]


@router.post("/deliverables/{deliverable_id}/cta-experiments")
def create_deliverable_cta_experiment(
    deliverable_id: int,
    payload: DeliverableCTAExperimentCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    deliverable = _get_org_deliverable(session, auth.org_id, deliverable_id)
    row = DeliverableCTAExperiment(
        organization_id=auth.org_id,
        deliverable_id=deliverable.id,
        created_by_user_id=auth.user_id,
        experiment_key=payload.experiment_key,
        variant_label=payload.variant_label,
        hypothesis=payload.hypothesis.strip() if payload.hypothesis else None,
        observed_outcome=payload.observed_outcome.strip() if payload.observed_outcome else None,
        status=payload.status,
        impressions=payload.impressions,
        conversions=payload.conversions,
        conversion_rate=payload.conversion_rate,
        started_at=payload.started_at,
        ended_at=payload.ended_at,
        updated_at=datetime.now(timezone.utc),
    )
    session.add(row)
    try:
        session.commit()
    except Exception as exc:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="CTA experiment variant already exists for this deliverable",
        ) from exc
    session.refresh(row)
    return _serialize_cta_experiment(row)


@router.get("/deliverables/{deliverable_id}/cta-experiments")
def list_deliverable_cta_experiments(
    deliverable_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    deliverable = _get_org_deliverable(session, auth.org_id, deliverable_id)
    rows = session.exec(
        select(DeliverableCTAExperiment)
        .where(
            (DeliverableCTAExperiment.organization_id == auth.org_id)
            & (DeliverableCTAExperiment.deliverable_id == deliverable.id)
        )
        .order_by(DeliverableCTAExperiment.created_at.desc())
    ).all()
    return [_serialize_cta_experiment(row) for row in rows]

@router.put("/deliverables/{deliverable_id}")
def update_deliverable(
    deliverable_id: int,
    data: DeliverableUpdate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    d = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    update_data = data.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(d, k, v)
    d.updated_at = datetime.now(timezone.utc)
    session.add(d)
    session.commit()
    session.refresh(d)
    return d

@router.delete("/deliverables/{deliverable_id}")
def delete_deliverable(
    deliverable_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    d = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    session.delete(d)
    session.commit()
    return {"ok": True}


@router.get("/deliverables/{deliverable_id}/publish-bundle", response_model=PublishBundleResponse)
def get_deliverable_publish_bundle(
    deliverable_id: int,
    platform: str = Query("wordpress"),
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    deliverable = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    try:
        bundle = build_publish_bundle(deliverable, platform=platform)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Deliverable metadata_json must be valid JSON")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return PublishBundleResponse(
        platform=bundle.platform,
        deliverable_id=bundle.deliverable_id,
        payload=bundle.payload,
        adapter_payload=bundle.adapter_payload,
    )

class BriefCreate(BaseModel):
    project_id: Optional[int] = None
    deliverable_id: Optional[int] = None
    title: Optional[str] = None
    brief_md: str
    toggles_json: Optional[str] = None

@router.post("/briefs")
def create_brief(
    data: BriefCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Get or create default project if not specified
    if not data.project_id:
        project = session.exec(
            select(Project).where(
                (Project.user_id == auth.user_id) & (Project.organization_id == auth.org_id)
            )
        ).first()
        if not project:
            project = Project(
                user_id=auth.user_id,
                organization_id=auth.org_id,
                name="Default Project"
            )
            session.add(project)
            session.commit()
            session.refresh(project)
        project_id = project.id
    else:
        # Verify project belongs to org
        project = session.exec(
            select(Project).where(
                (Project.id == data.project_id) & (Project.organization_id == auth.org_id)
            )
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project_id = data.project_id
    
    # Verify deliverable if provided
    if data.deliverable_id:
        deliverable = session.exec(
            select(Deliverable).where(
                (Deliverable.id == data.deliverable_id) & (Deliverable.organization_id == auth.org_id)
            )
        ).first()
        if not deliverable:
            raise HTTPException(status_code=404, detail="Deliverable not found")
    
    b = Brief(
        project_id=project_id,
        organization_id=auth.org_id,
        user_id=auth.user_id,
        deliverable_id=data.deliverable_id,
        title=data.title or "Untitled Brief",
        brief_md=data.brief_md,
        toggles_json=data.toggles_json,
    )
    session.add(b)
    session.commit()
    session.refresh(b)
    return b

@router.get("/briefs/{brief_id}")
def get_brief(
    brief_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    b = session.exec(
        select(Brief).where(
            (Brief.id == brief_id) & (Brief.organization_id == auth.org_id)
        )
    ).first()
    if not b:
        raise HTTPException(status_code=404, detail="Brief not found")
    return b

@router.get("/projects/{project_id}/briefs")
def list_project_briefs(
    project_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify project belongs to org
    project = session.exec(
        select(Project).where(
            (Project.id == project_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return session.exec(
        select(Brief).where(
            (Brief.project_id == project_id) & (Brief.organization_id == auth.org_id)
        )
    ).all()

@router.get("/deliverables/{deliverable_id}/brief")
def get_deliverable_brief(
    deliverable_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # Verify deliverable belongs to org
    deliverable = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    b = session.exec(
        select(Brief).where(
            (Brief.deliverable_id == deliverable_id) & (Brief.organization_id == auth.org_id)
        )
    ).first()
    if not b:
        return None
    return b


class WorkspaceFromItemRequest(BaseModel):
    scrape_item_id: int
    title: str
    content_type: str = "blog"


@router.post("/workspace/from-briefing-item")
def workspace_from_briefing_item(
    data: WorkspaceFromItemRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Create a Deliverable + Brief with a ScrapeItem pre-attached as context,
    then return the deliverable ID for workspace navigation.
    """
    # Verify scrape item belongs to org
    item = session.exec(
        select(ScrapeItem).where(
            (ScrapeItem.id == data.scrape_item_id) & (ScrapeItem.organization_id == auth.org_id)
        )
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Briefing item not found")

    # Get or create the default inbox project + folder
    project = session.exec(
        select(Project).where(
            (Project.user_id == auth.user_id) & (Project.organization_id == auth.org_id)
        )
    ).first()
    if not project:
        project = Project(
            user_id=auth.user_id,
            organization_id=auth.org_id,
            name="Default Project"
        )
        session.add(project)
        session.commit()
        session.refresh(project)

    folder = session.exec(
        select(Folder).where(
            (Folder.project_id == project.id) & (Folder.organization_id == auth.org_id)
        )
    ).first()
    if not folder:
        folder = Folder(
            project_id=project.id,
            organization_id=auth.org_id,
            name="Inbox"
        )
        session.add(folder)
        session.commit()
        session.refresh(folder)

    # Create deliverable
    deliverable = Deliverable(
        folder_id=folder.id,
        organization_id=auth.org_id,
        content_type=data.content_type,
        title=data.title,
        status="draft",
    )
    session.add(deliverable)
    session.commit()
    session.refresh(deliverable)

    # Create brief with the scrape item pre-loaded as intelligence context
    brief = Brief(
        project_id=project.id,
        organization_id=auth.org_id,
        user_id=auth.user_id,
        deliverable_id=deliverable.id,
        title=data.title,
        brief_md="",
        intelligence_items_json=json.dumps([data.scrape_item_id]),
    )
    session.add(brief)
    session.commit()

    # Mark item as surfaced
    item.surfaced_to_user_at = datetime.now(timezone.utc)
    session.add(item)
    session.commit()

    return {"deliverable_id": deliverable.id, "brief_id": brief.id}


class CalendarEventCreate(BaseModel):
    deliverable_id: int
    title: str
    description: Optional[str] = None
    start_at: datetime
    end_at: datetime


@router.post("/calendar/events")
def create_calendar_event(
    data: CalendarEventCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create a calendar event linked to a deliverable.
    
    Event is created locally immediately and synced to Google Calendar asynchronously.
    Frontend receives event ID and sync status right away.
    """
    from services.calendar import create_event_atomic
    
    # Verify deliverable belongs to org
    deliverable = session.exec(
        select(Deliverable).where(
            (Deliverable.id == data.deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    try:
        event = create_event_atomic(
            title=data.title,
            start_at=data.start_at,
            end_at=data.end_at,
            deliverable_id=data.deliverable_id,
            description=data.description,
        )
        return {
            "status": "created",
            "event": event,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar event: {str(e)}")


@router.get("/calendar/events/{deliverable_id}")
def get_calendar_event(
    deliverable_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get calendar event for a deliverable."""
    from models import CalendarEvent
    
    # Verify deliverable belongs to org
    deliverable = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    event = session.exec(
        select(CalendarEvent).where(
            (CalendarEvent.deliverable_id == deliverable_id) & (CalendarEvent.organization_id == auth.org_id)
        )
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="No calendar event for this deliverable")
    
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "start_at": event.start_at.isoformat(),
        "end_at": event.end_at.isoformat(),
        "status": event.status,
        "google_event_id": event.google_event_id,
        "synced_to_google_at": event.synced_to_google_at.isoformat() if event.synced_to_google_at else None,
        "last_synced_at": event.last_synced_at.isoformat() if event.last_synced_at else None,
    }


@router.put("/calendar/events/{event_id}")
def update_calendar_event(
    event_id: int,
    data: CalendarEventCreate,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Update a calendar event."""
    from models import CalendarEvent
    from services.calendar import sync_to_google
    
    event = session.exec(
        select(CalendarEvent).where(
            (CalendarEvent.id == event_id) & (CalendarEvent.organization_id == auth.org_id)
        )
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    # Verify deliverable still belongs to org
    deliverable = session.exec(
        select(Deliverable).where(
            (Deliverable.id == data.deliverable_id) & (Deliverable.organization_id == auth.org_id)
        )
    ).first()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")
    
    event.title = data.title
    event.description = data.description
    event.start_at = data.start_at
    event.end_at = data.end_at
    event.updated_at = datetime.now(timezone.utc)
    session.add(event)
    session.commit()
    
    sync_to_google(event_id)
    
    return {
        "status": "updated",
        "event_id": event_id,
    }


@router.delete("/calendar/events/{event_id}")
def delete_calendar_event(
    event_id: int,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete a calendar event (archives it, doesn't hard-delete)."""
    from models import CalendarEvent
    
    event = session.exec(
        select(CalendarEvent).where(
            (CalendarEvent.id == event_id) & (CalendarEvent.organization_id == auth.org_id)
        )
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    
    event.status = "archived"
    event.updated_at = datetime.now(timezone.utc)
    session.add(event)
    session.commit()
    
    return {"status": "archived", "event_id": event_id}
