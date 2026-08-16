# ForgeOS Consolidated Improvement Plan
**Synthesized from three independent code reviews (Wozniak, Gates, Hjalsberg)**

**Date:** 2024  
**Status:** Ready for Implementation  
**Overall Production Readiness:** ❌ **NOT READY** (10 critical security issues)

---

## Executive Summary

ForgeOS is an AI-native editorial/marketing platform combining a **FastAPI backend**, **Next.js frontend**, and **GitHub-hosted infrastructure**. The codebase shows functional early-stage development but has **critical security vulnerabilities, architectural gaps, and missing production infrastructure** that must be fixed before public deployment.

### Key Findings Across All Reviews

| Category | Count | Status |
|----------|-------|--------|
| **Critical Issues** | 15 | 🔴 BLOCKING DEPLOYMENT |
| **High Priority** | 28 | 🟠 MUST FIX |
| **Medium Priority** | 22 | 🟡 IMPROVE |
| **Low Priority** | 10+ | 🟢 NICE-TO-HAVE |
| **Opportunities** | 20+ | 💡 FUTURE |

### Top 10 Critical Issues (Blocking Deployment)

1. **JWT signature verification disabled** - Any token accepted, complete auth bypass
2. **Tenant isolation failures** - Cross-org data leakage on multiple endpoints
3. **Hardcoded user ID "aaron"** - All users share search/trends/GSC data
4. **API keys exposed in endpoints** - ENCRYPTION_KEY leakage = credential theft
5. **CORS wildcard with credentials** - CSRF/session hijacking vulnerability
6. **Missing org_id filters** - Delete operations bypass tenant isolation
7. **CI/CD workflows broken** - Reference non-existent paths, fail on every run
8. **GitHub Pages deployment broken** - Next.js deployed without static export
9. **Auth tokens in localStorage** - XSS vulnerability exposes all tokens
10. **Secrets and DB committed** - Repository contains .env files, forgeos.db, venv/node_modules

### Overall Code Quality Metrics
- **API Security:** 2/10 (Critical flaws)
- **Frontend Security:** 3/10 (Exposed tokens, no CSP)
- **Infrastructure:** 2/10 (CI broken, secrets in repo)
- **Test Coverage:** 0% (No tests anywhere)
- **Database Design:** 5/10 (Missing indexes, migrations, constraints)
- **Production Readiness:** 1/10 (Multiple blocking issues)

### Estimated Effort
- **Phase 1 (Critical Fixes):** 2-3 weeks
- **Phase 2 (Infrastructure):** 2-3 weeks
- **Phase 3 (Frontend):** 2-3 weeks
- **Phase 4 (Optimization):** 2-3 weeks
- **Total to Production:** 8-12 weeks

---

## Phase 1: Critical Security Fixes (Weeks 1-3)

**MUST COMPLETE BEFORE ANY PRODUCTION DEPLOYMENT**

### P1.1: Enable JWT Signature Verification
**File:** `apps/api/middleware/auth.py` (line 23)  
**Severity:** 🔴 CRITICAL  
**Effort:** 2 hours  
**Impact:** Complete auth bypass → authenticated API

**Current Code:**
```python
payload = jwt.decode(token, options={"verify_signature": False})
```

**Solution:**
- Implement proper JWT verification using Clerk's public keys
- Validate token expiration, issuer, and audience
- Create JWKS endpoint client or use Clerk SDK
- Add token refresh logic with proper error handling

**Acceptance Criteria:**
- [ ] JWT signature verification enabled
- [ ] Invalid/forged tokens rejected with 401
- [ ] Token expiration enforced
- [ ] Unit tests verify verification works
- [ ] Clerk integration tested end-to-end

---

### P1.2: Fix All Tenant Isolation Issues
**Files:**
- `apps/api/routers/projects.py` (lines 164, 187, 191, 228, 249)
- `apps/api/routers/briefing.py` (all endpoints)
- `apps/api/routers/chat.py` (session access)
- `apps/api/models.py` (hardcoded user_id "aaron")

**Severity:** 🔴 CRITICAL  
**Effort:** 3-4 days  
**Impact:** Cross-org data access → isolated tenants

**Issues to Fix:**
1. `delete_folder()` - Add `auth: AuthContext = Depends(get_current_user)` + org filter
2. `list_deliverables()` - Add organization_id WHERE clause
3. `create_deliverable()` - Verify auth and org ownership
4. `get_deliverable()` - Filter by org_id
5. `delete_deliverable()` - Verify user can delete
6. Remove hardcoded `user_id = "aaron"` defaults in models
7. Add org_id filter to ALL queries reading/writing user data

**Solution Pattern:**
```python
# For every read/write endpoint:
@router.get("/deliverables/{deliverable_id}")
def get_deliverable(
    deliverable_id: int, 
    auth: AuthContext = Depends(get_current_user),  # ADD THIS
    session: Session = Depends(get_session)
):
    deliverable = session.exec(
        select(Deliverable).where(
            (Deliverable.id == deliverable_id) &
            (Deliverable.organization_id == auth.org_id)  # ADD THIS
        )
    ).first()
    if not deliverable:
        raise HTTPException(404)
    return deliverable
```

**Acceptance Criteria:**
- [ ] All endpoints require auth context
- [ ] All queries filter by organization_id
- [ ] Integration test verifies Org A cannot access Org B data
- [ ] No hardcoded "aaron" user_id remains
- [ ] Search/trends/GSC services scoped to org_id

---

### P1.3: Fix CORS Configuration
**File:** `apps/api/main.py` (lines 13-19)  
**Severity:** 🔴 CRITICAL  
**Effort:** 1 hour  
**Impact:** Wildcard CORS → restricted origins

**Current Code:**
```python
allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
allow_credentials=True,
```

**Solution:**
```python
allow_origins=[
    "http://localhost:3000",  # Dev
    "http://localhost:3001",  # Dev
    "https://forgeos.app",    # Production
    "https://app.forgeos.app" # Production
],
allow_credentials=True,
```

**Acceptance Criteria:**
- [ ] Remove "*" from allow_origins
- [ ] Define explicit origin whitelist
- [ ] Test CORS with external origin (should fail)
- [ ] Test CORS with whitelisted origin (should work)

---

### P1.4: Secure API Key Endpoint
**File:** `apps/api/routers/settings.py`  
**Severity:** 🔴 CRITICAL  
**Effort:** 4 hours  
**Impact:** Exposed credentials → vault-managed secrets

**Issues:**
- `/api/settings/api-keys` returns encrypted keys to frontend
- ENCRYPTION_KEY in config.py can be compromised
- No secret rotation

**Solution:**
1. Remove API key retrieval endpoint from frontend
2. Implement backend-to-backend secret exchange only
3. Use AWS Secrets Manager or HashiCorp Vault
4. Never return keys to frontend (show masked values only)
5. Add secret rotation schedule

**Acceptance Criteria:**
- [ ] /api/settings/api-keys returns masked keys only
- [ ] Secrets stored in AWS Secrets Manager (dev: environment vars)
- [ ] Key rotation implemented (monthly schedule)
- [ ] Audit logs track secret access
- [ ] Credentials rotated before production launch

---

### P1.5: Remove Committed Secrets & Dependencies
**Files:**
- `.gitignore` - Ensure .env, .db, venv/, node_modules/ ignored
- `.github/workflows/*.yml` - Remove/redact sensitive paths
- `apps/api/.env` - Remove from git history
- `apps/api/forgeos.db` - Remove from git history
- `apps/api/venv/` - Remove from git history
- `apps/web/node_modules/`, `apps/web/.next/` - Remove from git history

**Severity:** 🔴 CRITICAL  
**Effort:** 2-3 hours (including git cleanup)  
**Impact:** Secrets in repo → clean git history

**Solution:**
```bash
# 1. Update .gitignore
echo "*.env" >> .gitignore
echo "*.db" >> .gitignore
echo "venv/" >> .gitignore
echo "node_modules/" >> .gitignore
echo ".next/" >> .gitignore

# 2. Remove from git history (one-time cleanup)
git filter-repo --invert-paths --path .env
git filter-repo --invert-paths --path forgeos.db
git filter-repo --invert-paths --path apps/api/venv/
git filter-repo --invert-paths --path apps/web/node_modules/

# 3. Rotate all credentials that were ever committed
# - Clerk API keys
# - Anthropic/OpenAI API keys
# - Database credentials
# - Any other secrets
```

**Acceptance Criteria:**
- [ ] .gitignore covers all sensitive paths
- [ ] Git history cleaned (use git filter-repo)
- [ ] Repository size reduced significantly
- [ ] All credentials rotated
- [ ] Pre-commit hook added to prevent re-commits

---

### P1.6: Fix CI/CD Workflow Paths
**Files:** `.github/workflows/repo-validation.yml`, `.github/workflows/ai-briefing.yml`, `.github/workflows/founder-recap.yml`  
**Severity:** 🔴 CRITICAL  
**Effort:** 1 hour  
**Impact:** Broken CI → working automation

**Issues:**
- Scripts referenced as `scripts/*.py` but live in `apps/api/scripts/`
- GitHub Pages deploy broken (no static export step)

**Solution:**
```yaml
# Before:
- run: python scripts/ai_daily_briefing.py

# After:
- run: python apps/api/scripts/ai_daily_briefing.py
```

**For Pages deploy:**
```yaml
# Add to deploy.yml:
- run: cd apps/web && npm run build
- run: npx next export  # Add this step
- uses: actions/upload-pages-artifact@v2
  with:
    path: 'apps/web/out'  # Upload static export, not .next
```

**Acceptance Criteria:**
- [ ] Workflows reference correct script paths
- [ ] CI/CD runs without errors
- [ ] Pages deployment produces static HTML
- [ ] Slack briefing workflow runs successfully

---

### P1.7: Secure Frontend Auth Storage
**Files:** `apps/web/src/lib/api.ts`, `apps/web/src/components/ProtectedRoute.tsx`  
**Severity:** 🔴 CRITICAL  
**Effort:** 1-2 days  
**Impact:** localStorage tokens → httpOnly cookies

**Current Issue:**
```typescript
const token = localStorage.getItem('auth_token');
```

**Solution (use Clerk or httpOnly cookies):**
1. **Recommended:** Migrate to Clerk's built-in session management
   - Use `@clerk/nextjs` package (already in dependencies)
   - Clerk handles token storage securely in httpOnly cookies
   - No frontend token manipulation needed

2. **If custom auth needed:**
   - Use httpOnly cookies (not accessible to JavaScript)
   - Backend sets `Set-Cookie: auth_token=...; HttpOnly; Secure; SameSite=Strict`
   - Frontend never directly accesses token
   - CSRF protection via SameSite cookie attribute

**Acceptance Criteria:**
- [ ] Tokens stored in httpOnly cookies
- [ ] localStorage auth_token references removed
- [ ] Clerk integration working (or secure cookie flow)
- [ ] XSS attack cannot steal tokens
- [ ] CSRF protection enabled

---

### P1.8: Fix Database & Schema Issues
**Files:**
- `apps/api/database.py` - Enable foreign key constraints
- `apps/api/models.py` - Add organization_id to all tenant-owned tables
- `apps/api/main.py` - Replace create_all with migrations

**Severity:** 🔴 CRITICAL  
**Effort:** 2-3 days  
**Impact:** Orphaned rows → enforced referential integrity

**Issues:**
1. SQLite foreign keys not enforced (PRAGMA not set)
2. No schema migrations (create_all on startup)
3. Missing unique constraints (org slug, memberships)
4. Missing indexes on org_id, created_at

**Solution:**
```python
# database.py - Enable foreign keys
def get_engine():
    engine = create_engine(DATABASE_URL)
    
    # Enable foreign keys for SQLite
    if "sqlite" in DATABASE_URL:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    return engine

# OR migrate to PostgreSQL for production:
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/forgeos")
```

**Acceptance Criteria:**
- [ ] Foreign key constraints enforced
- [ ] All tenant-owned tables have organization_id
- [ ] Unique constraints on org.slug, membership(org_id, user_id)
- [ ] Indexes on organization_id, created_at
- [ ] Schema migration strategy implemented (Alembic)
- [ ] create_all replaced with alembic upgrade head

---

## Phase 2: Core Infrastructure (Weeks 4-6)

**Foundation improvements for scaling and reliability**

### P2.1: Implement Database Migrations (Alembic)
**Files:** `apps/api/database.py`, new `apps/api/alembic/`  
**Severity:** 🟠 HIGH  
**Effort:** 2 days  
**Impact:** Deterministic schema changes, rollback capability

**Solution:**
```bash
# Initialize Alembic
cd apps/api
alembic init alembic

# Generate migration from current schema
alembic revision --autogenerate -m "Initial schema"

# Replace startup create_all:
# FROM: SQLModel.metadata.create_all(engine)
# TO: subprocess.run(["alembic", "upgrade", "head"])
```

**Acceptance Criteria:**
- [ ] Alembic initialized and configured
- [ ] Initial migration generated from SQLModel metadata
- [ ] Startup runs alembic upgrade head
- [ ] Test migration on fresh database
- [ ] Rollback tested

---

### P2.2: Add Database Indexes
**File:** `apps/api/models.py`  
**Severity:** 🟠 HIGH  
**Effort:** 1 day  
**Impact:** Sub-second queries → 100ms queries

**Missing Indexes:**
```python
# Add to each model with organization scoping:
__table_args__ = (
    Index('idx_org', 'organization_id'),
    Index('idx_org_created', 'organization_id', 'created_at'),
    Index('idx_org_project', 'organization_id', 'project_id'),
    Index('idx_org_session', 'organization_id', 'session_id'),
)

# For items requiring score/ranking:
__table_args__ = (
    Index('idx_org_score_created', 'organization_id', 'score', 'created_at'),
)
```

**Acceptance Criteria:**
- [ ] Index on organization_id for all tenant tables
- [ ] Composite indexes (org_id, created_at) for list/search
- [ ] Composite indexes (org_id, score, created_at) for ranking
- [ ] EXPLAIN plan verified for 10+ common queries
- [ ] No sequential scans on tables >1000 rows

---

### P2.3: Implement Request Logging & Audit Trail
**Files:** New `apps/api/middleware/logging.py`, models for AuditEvent  
**Severity:** 🟠 HIGH  
**Effort:** 2 days  
**Impact:** Complete audit trail for compliance, debugging

**Solution:**
```python
# middleware/logging.py
async def logging_middleware(request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    log_entry = {
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "user_id": auth.user_id if auth else None,
        "org_id": auth.org_id if auth else None,
        "duration_ms": process_time * 1000,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(json.dumps(log_entry))
    return response

# For audit events (sensitive operations):
@router.post("/projects")
def create_project(...):
    project = Project(...)
    session.add(project)
    session.flush()
    
    # Log audit event
    audit = AuditEvent(
        organization_id=auth.org_id,
        user_id=auth.user_id,
        action="create_project",
        resource_type="Project",
        resource_id=project.id,
        details={"name": project.name},
        timestamp=datetime.utcnow()
    )
    session.add(audit)
    session.commit()
    return project
```

**Acceptance Criteria:**
- [ ] Request logging middleware installed
- [ ] All requests logged with request_id, user_id, org_id, status, duration
- [ ] Sensitive operations logged to AuditEvent table
- [ ] Request IDs in error responses for tracking
- [ ] Logs exportable for compliance (GDPR, SOC2)

---

### P2.4: Fix Scheduled Jobs Architecture
**Files:** `apps/api/main.py`  
**Severity:** 🟠 HIGH  
**Effort:** 2-3 days  
**Impact:** Single scheduler → distributed job queue

**Current Issues:**
- In-process APScheduler duplicates jobs in multi-worker deployments
- No error recovery or retry logic
- Background jobs can block API

**Solution (Phase 1 - immediate fix):**
```python
# Disable APScheduler in multi-worker setups
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "false").lower() == "true"

if ENABLE_SCHEDULER:
    # Only run scheduler in dedicated worker
    scheduler.start()
else:
    # Add health check instead
    logger.info("Scheduler disabled (use dedicated worker)")
```

**Solution (Phase 2 - better approach):**
- Move to Celery or Temporal for background jobs
- Scheduled tasks trigger via GitHub Actions
- Idempotent task implementation
- Retry with exponential backoff

**Acceptance Criteria:**
- [ ] Scheduler runs only on dedicated worker (or disabled in API)
- [ ] All scheduled jobs have error handling and retry logic
- [ ] Failed jobs logged and alertable
- [ ] Task idempotence verified (safe to retry)
- [ ] Monitor job queue depth and duration

---

### P2.5: Add Rate Limiting
**Files:** `apps/api/main.py`, new middleware  
**Severity:** 🟠 HIGH  
**Effort:** 1 day  
**Impact:** DOS protection, fair usage

**Solution:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # Use Redis for production
    default_limits=["1000/hour"]
)
app.state.limiter = limiter

# Apply to endpoints
@router.post("/chat/stream")
@limiter.limit("10/minute")  # 10 messages per minute per user
async def chat_stream(req: ChatRequest, auth: AuthContext = Depends(get_current_user)):
    ...

# Per-organization limits
@router.get("/projects")
@limiter.limit("100/minute")  # Higher for API
def list_projects(auth: AuthContext = Depends(get_current_user)):
    ...
```

**Acceptance Criteria:**
- [ ] Rate limits implemented on all endpoints
- [ ] Per-user limits (e.g., 10/min for chat, 100/min for API)
- [ ] Per-IP limits for unauthenticated endpoints (1000/hour)
- [ ] Proper 429 response with Retry-After header
- [ ] Limits tuned for production traffic

---

### P2.6: Implement Secrets Management
**Files:** `apps/api/config.py`  
**Severity:** 🟠 HIGH  
**Effort:** 2 days  
**Impact:** Hardcoded secrets → vault-managed

**Solution (Development):**
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Required in production
    ANTHROPIC_API_KEY: str  # No default
    OPENAI_API_KEY: str
    CLERK_SECRET_KEY: str
    DATABASE_URL: str
    ENCRYPTION_KEY: str
    
    # Validate required fields
    @field_validator('ANTHROPIC_API_KEY')
    @classmethod
    def api_key_required(cls, v):
        if not v:
            raise ValueError('ANTHROPIC_API_KEY is required')
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache
def get_settings():
    return Settings()
```

**For Production:**
```bash
# Use AWS Secrets Manager
export ANTHROPIC_API_KEY=$(aws secretsmanager get-secret-value \
  --secret-id forgeos/anthropic-key \
  --query SecretString --output text)
```

**Acceptance Criteria:**
- [ ] All secrets required at startup (fail fast)
- [ ] .env.example with placeholder values
- [ ] AWS Secrets Manager integration for production
- [ ] Secret rotation every 90 days
- [ ] No secrets in error messages or logs

---

### P2.7: Add Configuration Validation
**File:** `apps/api/config.py`  
**Severity:** 🟠 HIGH  
**Effort:** 4 hours  
**Impact:** Invalid configs caught at startup

**Solution:**
```python
from pydantic import BaseSettings, field_validator, HttpUrl

class Settings(BaseSettings):
    DATABASE_URL: str  # Validate format
    API_URL: HttpUrl  # Validate URL
    ANTHROPIC_API_KEY: str = Field(min_length=20)
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_db_url(cls, v):
        if not v.startswith(('sqlite://', 'postgresql://')):
            raise ValueError('Invalid DATABASE_URL')
        return v
    
    @field_validator('LOG_LEVEL')
    @classmethod
    def valid_log_level(cls, v):
        if v not in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            raise ValueError(f'Invalid LOG_LEVEL: {v}')
        return v
```

**Acceptance Criteria:**
- [ ] All required settings validated at startup
- [ ] Invalid configuration caught with clear error message
- [ ] Type validation (URL, port number, enum values)
- [ ] Length validation for keys (min 20 chars for API keys)
- [ ] Documented in .env.example

---

## Phase 3: Frontend Hardening (Weeks 7-9)

**Security, reliability, and user experience improvements**

### P3.1: Implement Error Boundaries
**Files:** `apps/web/app/layout.tsx`, new `apps/web/src/components/ErrorBoundary.tsx`  
**Severity:** 🔴 CRITICAL  
**Effort:** 4 hours  
**Impact:** Graceful error handling → error recovery

**Solution:**
```typescript
'use client';
import { Component, ReactNode } from 'react';

class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean; error?: Error }
> {
  state = { hasError: false };

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Send to error tracking (Sentry)
    if (typeof window !== 'undefined') {
      console.error('Error boundary caught:', error, info);
      // Sentry.captureException(error);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1>Something went wrong</h1>
            <p>{this.state.error?.message}</p>
            <button onClick={() => window.location.href = '/'}>
              Return to dashboard
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// In layout.tsx:
export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ErrorBoundary>{children}</ErrorBoundary>
      </body>
    </html>
  );
}
```

**Acceptance Criteria:**
- [ ] ErrorBoundary component wraps entire app
- [ ] Errors logged to Sentry/error service
- [ ] User-friendly error message displayed
- [ ] Refresh button allows recovery
- [ ] No white screen of death

---

### P3.2: Fix Authentication & Add CSRF Protection
**Files:** `apps/web/src/lib/api.ts`, `apps/web/middleware.ts` (create if needed)  
**Severity:** 🔴 CRITICAL  
**Effort:** 1-2 days  
**Impact:** localStorage → httpOnly cookies, CSRF protection

**Solution:**
1. Migrate to Clerk authentication (already in dependencies)
2. Use httpOnly cookies for session tokens
3. Implement CSRF protection

```typescript
// Use Clerk's middleware for Next.js 14
// middleware.ts
import { clerkMiddleware } from "@clerk/nextjs";

export const config = {
  matcher: ["/((?!.+\\.[\\w]+$|_next).*)", "/", "/(api|trpc)(.*)"],
};

export default clerkMiddleware();

// Remove localStorage auth token handling
// Use Clerk's useAuth hook instead
import { useAuth } from "@clerk/nextjs";

export function MyComponent() {
  const { getToken } = useAuth();
  
  const apiFetch = async (path: string) => {
    const token = await getToken();
    const res = await fetch(`${API_BASE}${path}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.json();
  };
}
```

**Acceptance Criteria:**
- [ ] Clerk authentication integrated
- [ ] Auth tokens in httpOnly cookies (not localStorage)
- [ ] CSRF tokens sent with POST/PUT/DELETE
- [ ] Clerk middleware protects all routes
- [ ] Login/logout flow working

---

### P3.3: Add Input Validation & Sanitization
**Files:** All form components, new `apps/web/src/lib/validation.ts`  
**Severity:** 🔴 CRITICAL  
**Effort:** 2-3 days  
**Impact:** No injection attacks, data quality

**Solution:**
```typescript
// lib/validation.ts
import { z } from 'zod';
import DOMPurify from 'isomorphic-dompurify';

// Define schemas for all forms
export const createProjectSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().max(1000).optional(),
  tags: z.array(z.string()).max(10),
});

export type CreateProjectInput = z.infer<typeof createProjectSchema>;

// Sanitize HTML content
export function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html);
}

// In components:
import { createProjectSchema } from '@/lib/validation';

export function NewProjectForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const input = Object.fromEntries(formData);
    
    // Validate
    const result = createProjectSchema.safeParse(input);
    if (!result.success) {
      setErrors(result.error.flatten().fieldErrors);
      return;
    }
    
    // Submit validated data
    createProject(result.data);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input name="name" maxLength={255} required />
      {errors.name && <span className="error">{errors.name}</span>}
    </form>
  );
}
```

**Acceptance Criteria:**
- [ ] Zod schemas defined for all forms
- [ ] Client-side validation before submit
- [ ] User-friendly error messages
- [ ] HTML content sanitized with DOMPurify
- [ ] Server-side validation double-checks data

---

### P3.4: Fix API URL Hardcoding
**Files:** `apps/web/src/lib/api.ts`, all components with hardcoded URLs  
**Severity:** 🔴 CRITICAL  
**Effort:** 4 hours  
**Impact:** localhost URLs → environment-based

**Solution:**
```typescript
// lib/api.ts - Single source of truth
const API_BASE = process.env.NEXT_PUBLIC_API_URL || (() => {
  if (typeof window !== 'undefined') {
    return window.location.origin.replace(':3000', ':8000');
  }
  return 'http://localhost:8000';
})();

export const apiClient = {
  projects: {
    list: () => apiFetch('/api/projects'),
    create: (data) => apiFetch('/api/projects', { method: 'POST', body: JSON.stringify(data) }),
  },
  orgs: {
    list: () => apiFetch('/api/orgs'),
  },
  // ... all endpoints
};

// .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

// .env.production
NEXT_PUBLIC_API_URL=https://api.forgeos.app
```

**Acceptance Criteria:**
- [ ] All API URLs use API_BASE constant
- [ ] No hardcoded localhost URLs in code
- [ ] Environment variables properly set per environment
- [ ] Production API URL configured
- [ ] Tests use mocked API endpoints

---

### P3.5: Implement Content Security Policy (CSP)
**File:** `apps/web/next.config.mjs`  
**Severity:** 🟠 HIGH  
**Effort:** 1 day  
**Impact:** XSS protection, defense in depth

**Solution:**
```typescript
// next.config.mjs
const headers = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-inline' https://cdn.clerk.com;
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
      font-src 'self' data:;
      connect-src 'self' http://localhost:8000 https://api.forgeos.app;
      frame-ancestors 'none';
    `.replace(/\n/g, ' '),
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
];

/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [{ source: '/:path*', headers }];
  },
};

export default nextConfig;
```

**Acceptance Criteria:**
- [ ] CSP header configured
- [ ] XSS test: inline script blocked
- [ ] External scripts restricted to whitelist
- [ ] Unsafe-inline removed once trusted-types in place
- [ ] Security headers on all responses

---

### P3.6: Add Loading States & Optimistic UI
**Files:** Components using API calls (LetsBuildModal.tsx, etc.)  
**Severity:** 🟠 HIGH  
**Effort:** 2-3 days  
**Impact:** Poor perceived performance → instant feedback

**Solution (React Query):**
```typescript
import { useMutation, useQuery } from '@tanstack/react-query';

export function ProjectList() {
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: apiClient.projects.list,
  });

  if (isLoading) return <ProjectSkeleton count={5} />;
  if (error) return <ErrorMessage error={error} />;
  
  return projects.map(p => <ProjectCard key={p.id} project={p} />);
}

export function CreateProjectButton() {
  const queryClient = useQueryClient();
  
  const createMutation = useMutation({
    mutationFn: (data) => apiClient.projects.create(data),
    onMutate: async (newProject) => {
      // Optimistically update UI
      await queryClient.cancelQueries({ queryKey: ['projects'] });
      const previousProjects = queryClient.getQueryData(['projects']);
      
      queryClient.setQueryData(['projects'], (old) => [
        ...old,
        { ...newProject, id: 'optimistic-id' }
      ]);
      
      return { previousProjects };
    },
    onError: (error, newProject, context) => {
      // Rollback on error
      queryClient.setQueryData(['projects'], context.previousProjects);
    },
    onSuccess: () => {
      // Refresh projects list
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    }
  });

  return (
    <button onClick={() => createMutation.mutate(newProjectData)}>
      {createMutation.isPending ? 'Creating...' : 'Create Project'}
    </button>
  );
}
```

**Acceptance Criteria:**
- [ ] React Query integrated
- [ ] Loading states show spinners/skeletons
- [ ] Optimistic updates on mutations
- [ ] Error states handled gracefully
- [ ] Rollback works on failed mutations

---

### P3.7: Add Accessibility (a11y)
**Files:** All components  
**Severity:** 🟠 HIGH (ethical obligation)  
**Effort:** 3-4 days  
**Impact:** 15% of users can access app

**Quick Wins:**
```typescript
// Use semantic HTML
<button>Delete</button>  // Instead of <div onClick>

// Add ARIA labels
<button aria-label="Delete project">
  <TrashIcon />
</button>

// Link labels
<a href="/projects" aria-label="View all projects">Projects</a>

// Form accessibility
<label htmlFor="project-name">Project Name</label>
<input id="project-name" required />

// Focus management
<div
  role="dialog"
  aria-labelledby="dialog-title"
  aria-modal="true"
  onKeyDown={(e) => e.key === 'Escape' && closeModal()}
>
  <h2 id="dialog-title">Create Project</h2>
  {/* Auto-focus first input */}
  <input autoFocus />
</div>
```

**Acceptance Criteria:**
- [ ] Semantic HTML used
- [ ] All interactive elements have aria-labels
- [ ] Form inputs properly labeled
- [ ] Focus visible and manageable
- [ ] axe-core audit passes (0 violations)
- [ ] Screen reader tested (VoiceOver/NVDA)

---

### P3.8: Lazy Load & Code Split Components
**Files:** `apps/web/src/` - all heavy components  
**Severity:** 🟠 HIGH  
**Effort:** 1-2 days  
**Impact:** 5MB bundle → 2MB initial load

**Solution:**
```typescript
import dynamic from 'next/dynamic';

// Lazy load modals and heavy components
export const LetsBuildModal = dynamic(() => import('@/components/LetsBuildModal'), {
  loading: () => <ModalSkeleton />,
  ssr: false, // Don't render on server
});

export const CalendarView = dynamic(() => import('@/components/CalendarView'), {
  loading: () => <Skeleton height={400} />,
  ssr: true, // Can render on server
});

// Route-based code splitting (automatic with Next.js)
// Each page in app/ directory is its own chunk

// Usage:
import { LetsBuildModal } from '@/components';

export function Dashboard() {
  const [showModal, setShowModal] = useState(false);
  
  return (
    <>
      <button onClick={() => setShowModal(true)}>Build</button>
      {showModal && <LetsBuildModal onClose={() => setShowModal(false)} />}
    </>
  );
}
```

**Acceptance Criteria:**
- [ ] Heavy components (>50KB) dynamically imported
- [ ] Modals lazy loaded (only on demand)
- [ ] Route-based code splitting verified
- [ ] Bundle size <2MB initial (measured with next/bundle-analyzer)
- [ ] Lighthouse Performance score >80

---

## Phase 4: Optimization & Testing (Weeks 10-12)

**Performance, reliability, and test coverage**

### P4.1: Add Database Query Optimization
**Files:** `apps/api/services/`, `apps/api/routers/`  
**Severity:** 🟠 HIGH  
**Effort:** 2-3 days  
**Impact:** Slow queries → fast responses

**Issues to Fix:**
1. N+1 queries in briefing endpoints
2. SELECT * patterns should be specific columns
3. Missing pagination on list endpoints

**Solution:**
```python
# Before: N+1 queries
briefs = session.exec(select(Brief)).all()  # 1 query
for brief in briefs:
    items = session.exec(select(ScrapeItem).where(...)).all()  # N queries

# After: Single query with join
briefs = session.exec(
    select(Brief).options(
        joinedload(Brief.scrape_items)
    )
).all()  # 1 query total

# Add pagination
@router.get("/projects")
def list_projects(
    auth: AuthContext = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    projects = session.exec(
        select(Project)
        .where(Project.organization_id == auth.org_id)
        .offset(skip)
        .limit(limit)
    ).all()
    return projects
```

**Acceptance Criteria:**
- [ ] N+1 queries eliminated (use EXPLAIN to verify)
- [ ] All queries use specific column selection (no SELECT *)
- [ ] Pagination implemented on list endpoints
- [ ] Query response times <100ms for common queries
- [ ] Database CPU usage <50% under normal load

---

### P4.2: Add Observability & Monitoring
**Files:** `apps/api/instrumentation.py`, new observability setup  
**Severity:** 🟠 HIGH  
**Effort:** 2 days  
**Impact:** Blindness → visibility into production

**Solution (using existing Arize setup):**
```python
# Already have instrumentation.py, enhance it:
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc import trace_exporter, metric_exporter

# Create spans for database operations
tracer = trace.get_tracer(__name__)

@router.get("/projects")
def list_projects(auth: AuthContext = Depends(get_current_user)):
    with tracer.start_as_current_span("list_projects") as span:
        span.set_attribute("organization_id", auth.org_id)
        span.set_attribute("user_id", auth.user_id)
        
        with tracer.start_as_current_span("db_query") as db_span:
            projects = session.exec(
                select(Project).where(...)
            ).all()
        
        span.set_attribute("project_count", len(projects))
    
    return projects

# Add metrics
metrics_meter = metrics.get_meter(__name__)
request_counter = metrics_meter.create_counter("http_requests")
request_duration = metrics_meter.create_histogram("http_duration_ms")

# Health checks
@router.get("/health")
def health():
    return {
        "status": "ok",
        "database": check_database(),
        "scheduler": check_scheduler(),
    }
```

**Acceptance Criteria:**
- [ ] Traces captured for all endpoints
- [ ] Database query spans created
- [ ] Metrics exported (request count, latency, errors)
- [ ] Health endpoint implemented
- [ ] Dashboards in Arize/DataDog configured
- [ ] Alerts on high error rate (>5%), p95 latency >1s

---

### P4.3: Implement Comprehensive Testing
**Files:** `apps/api/tests/`, `apps/web/__tests__/`  
**Severity:** 🟠 HIGH  
**Effort:** 5-7 days (ongoing)  
**Impact:** 0% coverage → 70%+ coverage

**API Testing (pytest):**
```python
# tests/test_projects.py
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

class TestProjectTenantIsolation:
    def test_user_cannot_access_other_org_project(self):
        # Create two users in different orgs
        org1 = create_org("org1")
        org2 = create_org("org2")
        user1 = create_user(org1)
        user2 = create_user(org2)
        
        # User1 creates project
        project = client.post(
            "/api/projects",
            headers=get_auth_header(user1),
            json={"name": "Secret Project"}
        ).json()
        
        # User2 tries to access project
        response = client.get(
            f"/api/projects/{project['id']}",
            headers=get_auth_header(user2)
        )
        assert response.status_code == 404

class TestAuth:
    def test_invalid_jwt_rejected(self):
        response = client.get(
            "/api/projects",
            headers={"Authorization": "Bearer INVALID_TOKEN"}
        )
        assert response.status_code == 401
```

**Frontend Testing (React Testing Library):**
```typescript
// __tests__/components/ProjectCard.test.tsx
import { render, screen } from '@testing-library/react';
import { ProjectCard } from '@/components/ProjectCard';

describe('ProjectCard', () => {
  it('renders project name', () => {
    const project = { id: 1, name: 'Test Project' };
    render(<ProjectCard project={project} />);
    expect(screen.getByText('Test Project')).toBeInTheDocument();
  });
  
  it('calls onDelete when delete button clicked', async () => {
    const onDelete = jest.fn();
    render(<ProjectCard project={{...}} onDelete={onDelete} />);
    await userEvent.click(screen.getByRole('button', { name: /delete/i }));
    expect(onDelete).toHaveBeenCalled();
  });
});
```

**E2E Testing (Playwright):**
```typescript
// e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('user can log in', async ({ page }) => {
  await page.goto('http://localhost:3000');
  await page.click('text=Sign In');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('text=Sign In');
  await expect(page).toHaveURL('http://localhost:3000/dashboard');
});
```

**Acceptance Criteria:**
- [ ] API test coverage >70%
- [ ] All tenant isolation cases tested
- [ ] All critical endpoints tested
- [ ] Frontend component tests for main components
- [ ] E2E tests for critical user flows
- [ ] CI/CD runs tests on every commit
- [ ] Coverage reports generated

---

### P4.4: Implement Rate Limiting Testing
**Files:** `apps/api/tests/test_rate_limiting.py`  
**Severity:** 🟠 HIGH  
**Effort:** 1 day  
**Impact:** DOS vulnerability → protected endpoints

**Solution:**
```python
def test_rate_limiting():
    # Send 11 requests (limit is 10/minute)
    responses = []
    for i in range(11):
        response = client.post(
            "/api/chat/stream",
            headers=get_auth_header(user),
            json={"message": "test"}
        )
        responses.append(response.status_code)
    
    # First 10 should succeed, 11th should be rate limited
    assert responses[:10] == [200] * 10
    assert responses[10] == 429  # Too Many Requests
    assert 'Retry-After' in client.headers
```

**Acceptance Criteria:**
- [ ] Rate limiting enforced on all endpoints
- [ ] 429 response with Retry-After header
- [ ] Per-user limits work correctly
- [ ] Per-IP limits work for unauthenticated endpoints
- [ ] Rate limit headers include remaining/reset

---

### P4.5: Performance Testing & Optimization
**Files:** `apps/api/`, `apps/web/`  
**Severity:** 🟠 HIGH  
**Effort:** 2-3 days  
**Impact:** Unknown performance → measurable baselines

**Load Testing:**
```bash
# Using k6
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 100 },
    { duration: '1m30s', target: 100 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  const response = http.get('http://localhost:8000/api/projects');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
}
```

**Frontend Performance (Lighthouse):**
```bash
npx lighthouse http://localhost:3000/dashboard --output-path=report.html
# Target: Performance >80, LCP <2.5s, CLS <0.1
```

**Acceptance Criteria:**
- [ ] Load test: 100 concurrent users, <2% error rate
- [ ] API response time p95 <500ms
- [ ] Database CPU <70% under load
- [ ] Frontend Lighthouse score >80
- [ ] LCP (Largest Contentful Paint) <2.5s
- [ ] CLS (Cumulative Layout Shift) <0.1

---

### P4.6: Security Testing
**Files:** `apps/api/tests/test_security.py`  
**Severity:** 🟠 HIGH  
**Effort:** 2 days  
**Impact:** Unknown vulnerabilities → tested security

**Solution:**
```python
class TestSecurityHeaders:
    def test_csrf_protection(self):
        response = client.post("/api/projects", json={...})
        # Should require CSRF token or SameSite cookie
        assert response.status_code in [200, 403]  # Not 200 without token

class TestInputValidation:
    def test_sql_injection_blocked(self):
        response = client.get(
            "/api/projects?name='; DROP TABLE projects; --"
        )
        assert response.status_code == 422  # Validation error
        
    def test_xss_sanitized(self):
        response = client.post(
            "/api/projects",
            json={"name": "<script>alert('xss')</script>"}
        )
        # Should sanitize or reject
        project = response.json()
        assert '<script>' not in project['name']

class TestAuth:
    def test_expired_token_rejected(self):
        token = create_expired_token()
        response = client.get(
            "/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
```

**Acceptance Criteria:**
- [ ] CSRF tests pass
- [ ] SQL injection tests pass
- [ ] XSS tests pass
- [ ] Auth expiration tested
- [ ] CORS restrictions tested
- [ ] Rate limiting tested
- [ ] Security headers verified

---

## Dependencies & Blockers

### Execution Dependencies

**Critical Path (must complete in order):**
1. **P1.1-P1.4** (JWT, tenant isolation, CORS, secrets) → Foundation for all others
2. **P2.1-P2.3** (Migrations, indexes, logging) → Infrastructure stability
3. **P3.1-P3.2** (Error boundaries, auth) → Frontend reliability
4. **P4.1-P4.3** (Query optimization, testing) → Production readiness

### Cross-Cutting Dependencies

| Item | Depends On | Blocks |
|------|-----------|--------|
| P1.8 (DB migrations) | P1.2 (tenant isolation) | P2.1, P2.2 |
| P2.4 (scheduled jobs) | P1.1 (JWT verification) | All background tasks |
| P3.2 (frontend auth) | P1.1 (JWT verification) | All API calls |
| P4.3 (testing) | P1-P3 complete | Production deployment |

### External Blockers

- **Clerk integration** - Already in dependencies, need API keys
- **AWS Secrets Manager** - For production deployments
- **Database migration** - SQLite → PostgreSQL for production

---

## Success Criteria by Phase

### Phase 1: Critical Security Fixes ✅
- [ ] All 10 critical security issues fixed and tested
- [ ] JWT signature verification enabled
- [ ] All tenant isolation tests pass (no cross-org access)
- [ ] CORS only allows whitelisted origins
- [ ] No secrets in git history
- [ ] No tokens in localStorage
- [ ] CI/CD workflows passing
- [ ] Database foreign keys enforced

### Phase 2: Core Infrastructure ✅
- [ ] Database migrations working (Alembic)
- [ ] All critical indexes created
- [ ] Request logging & audit trail functional
- [ ] Rate limiting preventing DOS
- [ ] Scheduled jobs have error handling
- [ ] Configuration validation working
- [ ] Secrets managed securely
- [ ] Health checks passing

### Phase 3: Frontend Hardening ✅
- [ ] Error boundaries catch all errors
- [ ] Input validation on all forms
- [ ] API URLs environment-based
- [ ] CSP headers blocking XSS
- [ ] Authentication flow working with Clerk
- [ ] Loading states show for all async operations
- [ ] Accessibility audit passes
- [ ] Bundle size <2MB initial

### Phase 4: Optimization & Testing ✅
- [ ] All N+1 queries fixed
- [ ] Database queries <100ms
- [ ] Test coverage >70%
- [ ] All critical user flows E2E tested
- [ ] Load test: 100 users, <2% error rate
- [ ] Lighthouse score >80
- [ ] Security tests passing
- [ ] Monitoring/observability working

---

## Production Deployment Checklist

**DO NOT DEPLOY TO PRODUCTION UNTIL ALL ITEMS CHECKED:**

### Security
- [ ] All CRITICAL issues fixed (Phase 1)
- [ ] JWT signature verification enabled
- [ ] Tenant isolation verified for all endpoints
- [ ] CORS whitelist configured for production domains
- [ ] Secrets in AWS Secrets Manager
- [ ] SSL/TLS certificates valid
- [ ] Security headers in place (CSP, X-Frame-Options, etc.)
- [ ] Rate limiting active
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak sensitive info

### Infrastructure
- [ ] Database migrations tested
- [ ] Backups configured and tested
- [ ] Monitoring/alerting active
- [ ] Health checks passing
- [ ] Load balancer configured (if needed)
- [ ] CDN configured for static assets
- [ ] Logging aggregation working (ELK/Datadog)

### Testing
- [ ] Test coverage >70%
- [ ] All critical endpoints tested
- [ ] E2E tests for main user flows
- [ ] Load testing completed (100+ users)
- [ ] Security testing completed
- [ ] Browser compatibility tested (Chrome, Firefox, Safari, Edge)

### Documentation
- [ ] API documented (OpenAPI/Swagger)
- [ ] Deployment runbook written
- [ ] Incident response plan documented
- [ ] Data handling policy documented
- [ ] Backup/recovery procedures documented

### Operations
- [ ] On-call rotation established
- [ ] Incident response team trained
- [ ] Dashboard/alerting configured
- [ ] Log retention policy set
- [ ] Runbooks for common scenarios

---

## Timeline Estimate

| Phase | Week | Focus | Status |
|-------|------|-------|--------|
| **P1** | 1-3 | Critical security fixes | 🔴 Start here |
| **P2** | 4-6 | Core infrastructure | ⏳ After P1 |
| **P3** | 7-9 | Frontend hardening | ⏳ After P2 |
| **P4** | 10-12 | Testing & optimization | ⏳ After P3 |
| **Deploy** | Week 13+ | Production launch | 🚀 After all phases |

**Realistic Estimate: 12-16 weeks to production-ready**

---

## Risk Assessment

### High-Risk Items (most likely to slip)
1. **Database migration** - Complex if schema changes required
2. **Testing implementation** - Large effort if starting from 0%
3. **Performance optimization** - May require architectural changes
4. **Tenant isolation verification** - Time-consuming to test all endpoints

### Mitigation Strategies
- Allocate 2+ engineers for parallel work on P1-P4
- Start with highest-risk items first
- Daily standup to catch blockers early
- Allocate 20% buffer for unexpected issues

---

## Maintenance & Ongoing

### Post-Launch (Month 1+)
- Monitor error rates and latency
- Review logs for security incidents
- Test backup/recovery procedures
- Update dependencies monthly
- Security patches immediately

### Quarterly Reviews
- Performance optimization (based on real-world usage)
- Feature flag rollout
- Test coverage maintenance (target: >80%)
- Security audit
- Infrastructure capacity planning

---

## References

- **Wozniak API Review:** 85 issues across 54+ Python files
- **Gates Web Review:** Issues across 79 TypeScript/TSX components
- **Hjalsberg Infrastructure Review:** CI/CD, database, deployment issues

---

**Plan Status:** Ready for implementation  
**Last Updated:** 2024  
**Next Review:** After Phase 1 completion
