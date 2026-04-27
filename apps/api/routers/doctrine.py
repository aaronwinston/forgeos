"""Engine doctrine versioning and health endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select, desc
from database import get_session
from models import DoctrineVersion, Organization
from middleware.auth import get_current_user, AuthContext
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import hashlib

router = APIRouter(prefix="/api/doctrine", tags=["doctrine"])

class SaveDoctrineRequest(BaseModel):
    file_path: str
    content: str

class DoctrineVersionResponse(BaseModel):
    id: str
    file_path: str
    content: str
    content_hash: str
    saved_by_user_id: str
    created_at: str

class HealthStatus(BaseModel):
    file_path: str
    word_count: int
    completeness_score: int  # 0-100
    status: str  # empty, thin, complete
    last_updated: Optional[str] = None

def compute_completeness(word_count: int, file_path: str) -> tuple[int, str]:
    """Compute completeness score and status based on word count."""
    # Recommended ranges per file type
    minimums = {
        "core/VOICE.md": (500, "Voice guide needs 500+ words"),
        "context/02_narrative/messaging-framework.md": (1500, "Messaging should be 1500+ words"),
        "core/CLAIMS_POLICY.md": (300, "Claims policy needs 300+ words"),
    }
    
    # Find matching recommendation
    min_words = 100  # default
    for pattern, (threshold, _) in minimums.items():
        if pattern in file_path:
            min_words = threshold
            break
    
    if word_count == 0:
        return 0, "empty"
    elif word_count < min_words:
        return int((word_count / min_words) * 50), "thin"
    else:
        return min(100, 50 + int((word_count - min_words) / min_words * 50)), "complete"

@router.post("/save")
async def save_doctrine(
    req: SaveDoctrineRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Save a doctrine file and create a version."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if team plan with lock
    existing_locked = session.exec(
        select(DoctrineVersion).where(
            (DoctrineVersion.organization_id == auth.org_id) &
            (DoctrineVersion.file_path == req.file_path) &
            (DoctrineVersion.locked_by_user_id != None)
        ).order_by(desc(DoctrineVersion.created_at))
    ).first()
    
    if existing_locked and existing_locked.locked_by_user_id != auth.user_id:
        raise HTTPException(status_code=403, detail="This file is locked by another user")
    
    # Compute hash
    content_hash = hashlib.sha256(req.content.encode()).hexdigest()
    
    # Create version
    version = DoctrineVersion(
        organization_id=auth.org_id,
        file_path=req.file_path,
        content=req.content,
        content_hash=content_hash,
        saved_by_user_id=auth.user_id,
    )
    session.add(version)
    session.commit()
    session.refresh(version)
    
    return DoctrineVersionResponse(
        id=version.id,
        file_path=version.file_path,
        content=version.content,
        content_hash=version.content_hash,
        saved_by_user_id=version.saved_by_user_id,
        created_at=str(version.created_at)
    )

@router.get("/versions/{file_path}")
async def get_doctrine_versions(
    file_path: str,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get version history for a doctrine file."""
    
    versions = session.exec(
        select(DoctrineVersion).where(
            (DoctrineVersion.organization_id == auth.org_id) &
            (DoctrineVersion.file_path == file_path)
        ).order_by(desc(DoctrineVersion.created_at)).limit(50)
    ).all()
    
    return [
        DoctrineVersionResponse(
            id=v.id,
            file_path=v.file_path,
            content=v.content,
            content_hash=v.content_hash,
            saved_by_user_id=v.saved_by_user_id,
            created_at=str(v.created_at)
        )
        for v in versions
    ]

@router.get("/versions/{file_path}/{version_id}")
async def get_doctrine_version(
    file_path: str,
    version_id: str,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get a specific version of a doctrine file."""
    
    version = session.exec(
        select(DoctrineVersion).where(
            (DoctrineVersion.id == version_id) &
            (DoctrineVersion.organization_id == auth.org_id) &
            (DoctrineVersion.file_path == file_path)
        )
    ).first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    return DoctrineVersionResponse(
        id=version.id,
        file_path=version.file_path,
        content=version.content,
        content_hash=version.content_hash,
        saved_by_user_id=version.saved_by_user_id,
        created_at=str(version.created_at)
    )

@router.post("/restore/{file_path}/{version_id}")
async def restore_doctrine_version(
    file_path: str,
    version_id: str,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Restore a previous version of a doctrine file."""
    
    # Get the target version
    target_version = session.exec(
        select(DoctrineVersion).where(
            (DoctrineVersion.id == version_id) &
            (DoctrineVersion.organization_id == auth.org_id) &
            (DoctrineVersion.file_path == file_path)
        )
    ).first()
    
    if not target_version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Create a new version with the restored content
    restored = DoctrineVersion(
        organization_id=auth.org_id,
        file_path=target_version.file_path,
        content=target_version.content,
        content_hash=target_version.content_hash,
        saved_by_user_id=auth.user_id,
    )
    session.add(restored)
    session.commit()
    session.refresh(restored)
    
    return DoctrineVersionResponse(
        id=restored.id,
        file_path=restored.file_path,
        content=restored.content,
        content_hash=restored.content_hash,
        saved_by_user_id=restored.saved_by_user_id,
        created_at=str(restored.created_at)
    )

@router.get("/health")
async def get_engine_health(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get engine health status for all files (actual filesystem scan)."""
    
    from services.doctrine_health import DoctrineHealthService
    
    # In personal mode, scan actual filesystem
    service = DoctrineHealthService(repo_root=".")
    report = service.get_health_report()
    
    return {
        "total_files": report["total_files"],
        "placeholder_count": report["placeholder_count"],
        "thin_count": report["thin_count"],
        "files": report["files"],
        "highest_leverage_file": service.get_highest_leverage_thin_file(),
        "timestamp": report["timestamp"],
        "cached": report["cached"]
    }

@router.post("/cleanup-old-versions")
async def cleanup_old_versions(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Clean up doctrine versions older than 90 days. (Admin task)"""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Delete versions older than 90 days
    cutoff = datetime.utcnow() - timedelta(days=90)
    old_versions = session.exec(
        select(DoctrineVersion).where(
            (DoctrineVersion.organization_id == auth.org_id) &
            (DoctrineVersion.created_at < cutoff)
        )
    ).all()
    
    for v in old_versions:
        session.delete(v)
    
    session.commit()
    return {"deleted_count": len(old_versions)}
