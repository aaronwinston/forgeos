from fastapi import Depends, HTTPException, status, Header, Request
from typing import Optional
import jwt

from audit import set_audit_context
from personal_mode import is_personal, PERSONAL_USER_ID, PERSONAL_ORG_ID, PERSONAL_USER_ROLE

class AuthContext:
    def __init__(self, user_id: str, org_id: str, role: str):
        self.user_id = user_id
        self.org_id = org_id
        self.role = role

def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(None),
) -> AuthContext:
    """Extract and validate auth token from httpOnly cookie or Authorization header.
    
    In personal mode, returns a hardcoded user context without validation.
    """
    
    # Personal mode: bypass auth entirely
    if is_personal():
        ctx = AuthContext(user_id=PERSONAL_USER_ID, org_id=PERSONAL_ORG_ID, role=PERSONAL_USER_ROLE)
        request.state.auth = ctx
        set_audit_context(
            user_id=PERSONAL_USER_ID,
            org_id=PERSONAL_ORG_ID,
            request_method=request.method,
            request_path=request.url.path,
        )
        return ctx
    
    # Multi-tenant mode: validate JWT
    # Try to get token from httpOnly cookie first (preferred method)
    token = request.cookies.get("auth_token")
    
    # Fallback to Authorization header for backward compatibility during migration
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    try:
        # Decode with verification using JWT_SECRET_KEY
        from config import settings
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id or not isinstance(user_id, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        org_id = payload.get("org_id")
        if not org_id or not isinstance(org_id, str):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid organization claim")
        
        role = payload.get("role", "member")
        if not isinstance(role, str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid role claim")

        ctx = AuthContext(user_id=user_id, org_id=org_id, role=role)
        request.state.auth = ctx
        set_audit_context(
            user_id=user_id,
            org_id=org_id,
            request_method=request.method,
            request_path=request.url.path,
        )
        return ctx
        
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

def require_org_owner(auth: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Require owner role."""
    if auth.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires owner role")
    return auth

def require_org_admin(auth: AuthContext = Depends(get_current_user)) -> AuthContext:
    """Require admin or owner role."""
    if auth.role not in ("admin", "owner"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires admin role")
    return auth


