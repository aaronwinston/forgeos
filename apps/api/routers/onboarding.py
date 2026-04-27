"""Onboarding flow endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from database import get_session
from models import Organization, Project, Folder
from middleware.auth import get_current_user, AuthContext
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import anthropic

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])

# Request models
class CompanyPitchRequest(BaseModel):
    pitch: str

class VoiceExampleRequest(BaseModel):
    examples: List[str]

class CompetitorsRequest(BaseModel):
    competitors: List[dict]  # {name: str, description: str}

class ClaimsRequest(BaseModel):
    claims: List[str]

class StarterProjectRequest(BaseModel):
    template: Optional[str] = None  # "product-launch", "newsletter", "ar-program", or None

class OnboardingStateRequest(BaseModel):
    completed_steps: List[str]

# Response models
class ExtractedMessaging(BaseModel):
    messaging_pillars: List[str]
    placeholder_framework: str

class AnalyzedVoice(BaseModel):
    tone: str
    vocabulary: str
    patterns: str
    placeholder_voice_md: str

class CompetitiveAnalysis(BaseModel):
    competitive_pov: str

@router.post("/extract-messaging")
async def extract_messaging(
    req: CompanyPitchRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Extract messaging pillars from company pitch."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Call Claude to analyze the pitch
    client = anthropic.Anthropic()
    
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this company pitch and extract 3-5 core messaging pillars. 
Also create a brief messaging framework template.

Pitch: {req.pitch}

Return JSON:
{{
  "messaging_pillars": ["pillar1", "pillar2", ...],
  "placeholder_framework": "## Messaging Framework\\n\\n[Content]"
}}"""
                }
            ]
        )
        
        content = message.content[0].text
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        
        result = json.loads(json_match.group())
        return ExtractedMessaging(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-voice")
async def analyze_voice(
    req: VoiceExampleRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Analyze voice examples and extract tone/style."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    client = anthropic.Anthropic()
    
    try:
        examples_text = "\n\n".join([f"Example {i+1}:\n{ex}" for i, ex in enumerate(req.examples)])
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze these writing examples and identify:
1. Overall tone (e.g., "formal", "conversational", "technical")
2. Vocabulary patterns (technical terms, jargon level, etc)
3. Writing patterns (sentence structure, metaphors, etc)
4. A placeholder VOICE.md file for them to customize

Examples:
{examples_text}

Return JSON:
{{
  "tone": "...",
  "vocabulary": "...",
  "patterns": "...",
  "placeholder_voice_md": "## Voice Guide\\n\\n[Content]"
}}"""
                }
            ]
        )
        
        content = message.content[0].text
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        
        result = json.loads(json_match.group())
        return AnalyzedVoice(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-competitors")
async def analyze_competitors(
    req: CompetitorsRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Analyze competitors and create competitive POV."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    client = anthropic.Anthropic()
    
    try:
        competitors_text = "\n".join([f"- {c.get('name')}: {c.get('description')}" for c in req.competitors])
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Based on these competitors, create a competitive point of view and differentiation strategy.

Competitors:
{competitors_text}

Return JSON:
{{
  "competitive_pov": "## Competitive POV\\n\\n[Analysis of competitive landscape and our positioning]"
}}"""
                }
            ]
        )
        
        content = message.content[0].text
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON found in response")
        
        result = json.loads(json_match.group())
        return CompetitiveAnalysis(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/create-starter-project")
async def create_starter_project(
    req: StarterProjectRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Create a starter project from template."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    templates = {
        "product-launch": {
            "name": "Product Launch Campaign",
            "description": "Pre-flight checklist + multi-channel messaging",
            "folders": ["messaging", "content", "assets"]
        },
        "newsletter": {
            "name": "Weekly Newsletter",
            "description": "Curated insights + internal updates",
            "folders": ["drafts", "calendar", "archive"]
        },
        "ar-program": {
            "name": "ARR Growth Program",
            "description": "Tier-based nurture sequences",
            "folders": ["tier-1", "tier-2", "tier-3"]
        }
    }
    
    if req.template and req.template not in templates:
        raise HTTPException(status_code=400, detail="Invalid template")
    
    # Create project
    if req.template:
        template = templates[req.template]
        project_name = template["name"]
        folders = template["folders"]
    else:
        project_name = "My Project"
        folders = []
    
    project = Project(
        name=project_name,
        organization_id=auth.org_id,
        description=templates.get(req.template, {}).get("description", "")
    )
    session.add(project)
    session.flush()  # Get the project ID
    
    # Create folders
    for folder_name in folders:
        folder = Folder(
            name=folder_name,
            project_id=project.id,
            organization_id=auth.org_id
        )
        session.add(folder)
    
    session.commit()
    session.refresh(project)
    
    return {
        "project_id": project.id,
        "name": project.name,
        "template": req.template,
        "created_at": str(project.created_at)
    }

@router.put("/state")
async def update_onboarding_state(
    req: OnboardingStateRequest,
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Update onboarding completion state."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Store completed steps as JSON
    org.onboarding_completed_steps = json.dumps(req.completed_steps)
    org.updated_at = datetime.utcnow()
    session.add(org)
    session.commit()
    
    return {
        "completed_steps": req.completed_steps,
        "all_steps": [
            "company_pitch",
            "voice_examples",
            "competitors",
            "claims_policy",
            "runtime_key",
            "starter_project"
        ]
    }

@router.get("/state")
async def get_onboarding_state(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Get current onboarding state."""
    
    org = session.get(Organization, auth.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    completed_steps = []
    if org.onboarding_completed_steps:
        try:
            completed_steps = json.loads(org.onboarding_completed_steps)
        except:
            pass
    
    return {
        "completed_steps": completed_steps,
        "all_steps": [
            "company_pitch",
            "voice_examples",
            "competitors",
            "claims_policy",
            "runtime_key",
            "starter_project"
        ]
    }
