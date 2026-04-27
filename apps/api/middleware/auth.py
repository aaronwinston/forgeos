from fastapi import Depends, HTTPException, status, Header
from typing import Optional
import jwt

class AuthContext:
    def __init__(self, user_id: str, org_id: str, role: str):
        self.user_id = user_id
        self.org_id = org_id
        self.role = role

def get_current_user(
    authorization: Optional[str] = Header(None),
) -> AuthContext:
    """Extract and validate auth token from Authorization header."""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    
    try:
        # Decode without verification (Clerk token validation happens at edge)
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        org_id = payload.get("org_id")
        if not org_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization")
        
        role = payload.get("role", "member")
        
        return AuthContext(user_id=user_id, org_id=org_id, role=role)
        
    except jwt.DecodeError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
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


