# ForgeOS Infrastructure & Configuration Review (Hjalsberg)

> Note: The request asked to save to `/tmp/hajlsberg_infra_review.md`, but this environment forbids writing to `/tmp`. This review is saved at:
> `forgeos/hjalsberg_infra_review.md`

## Repository infrastructure snapshot (observed)
- **Backend**: `apps/api` (FastAPI + SQLModel)
- **Frontend**: `apps/web` (Next.js)
- **CI/CD**: GitHub Actions in `.github/workflows/*.yml`
- **Database**: SQLite file `apps/api/forgeos.db` checked into repo; schema defined in `apps/api/models.py` (no `.sql` migrations found)
- **Notable repo hygiene**: `apps/web/node_modules/`, `apps/web/.next/`, and `apps/api/venv/` appear present in the repository tree.

---

# 1) Critical Issues

## CI workflows reference non-existent paths
- **Location**: `.github/workflows/repo-validation.yml`, `.github/workflows/ai-briefing.yml`, `.github/workflows/founder-recap.yml`
- **Severity**: **Critical**
- **Description**: Workflows run scripts under `scripts/*.py`, but there is **no** top-level `scripts/` directory. The scripts live under `apps/api/scripts/`.
- **Impact**: CI jobs will fail immediately on every run (cannot find script). Automated reporting (Slack briefings/recaps) won’t run.
- **Recommendation**: Update workflows to call `python apps/api/scripts/<script>.py` or move scripts to a top-level `scripts/` directory (and adjust import/paths accordingly).

## GitHub Pages deploy workflow likely deploys a non-static artifact
- **Location**: `.github/workflows/deploy.yml`
- **Severity**: **Critical**
- **Description**:
  - Runs `npx next build` and uploads `apps/web/.next` as the Pages artifact.
  - `apps/web/next.config.mjs` does **not** set `output: 'export'`, and there is no `next export` step.
- **Impact**: Deploys may succeed but the published site may be blank/broken because Pages expects static output (typically `out/` or a configured artifact directory).
- **Recommendation**:
  - If using static export: set `output: 'export'` in `next.config.mjs` and upload `apps/web/out`.
  - If using SSR: GitHub Pages is the wrong target; deploy to a runtime (Vercel/Fly/Render) and remove Pages workflow.

## Secrets and local state appear committed
- **Location**: `apps/api/.env`, `apps/api/forgeos.db`, `apps/api/venv/`, `apps/web/node_modules/`, `apps/web/.next/`
- **Severity**: **Critical**
- **Description**: Repo contains a committed `.env` file (typically secrets), a live SQLite DB, a Python venv, and frontend build/dependency directories.
- **Impact**:
  - High risk of credential leakage.
  - Bloated repository, slow clones, unreliable builds, and inconsistent environments.
  - Accidental production data exposure if DB isn’t sanitized.
- **Recommendation**:
  - Remove these from git history where possible (git filter-repo/BFG) and ensure `.gitignore` covers them.
  - Use `.env.example` only; do not commit `.env`.
  - Store DB outside repo (or generate in dev), and never commit `node_modules`, `.next`, `venv`.

## JWT authentication is not verified (token spoofing)
- **Location**: `apps/api/middleware/auth.py` (line ~23)
- **Severity**: **Critical**
- **Description**: `jwt.decode(token, options={"verify_signature": False})` accepts any token payload without signature verification.
- **Impact**: Anyone can forge `sub`, `org_id`, `role` and access/modify other tenants’ data.
- **Recommendation**: Verify JWTs using Clerk JWKS / issuer / audience checks (or validate via Clerk backend). If you truly validate at an edge proxy, enforce network-level isolation so the API cannot be accessed directly.

## Tenant isolation is inconsistent / bypassable in several endpoints
- **Location**: `apps/api/routers/projects.py`
- **Severity**: **Critical**
- **Description**:
  - Several handlers do not require `AuthContext` at all (`delete_folder`, `list_deliverables`, `create_deliverable`, `get_deliverable`, `update_deliverable`, `delete_deliverable`, multiple brief endpoints).
  - Multiple code paths hard-code `Project.user_id == "aaron"` and create objects without `organization_id`.
- **Impact**: Cross-tenant data exposure and write access. Also produces orphaned rows that later queries (filtered by `organization_id`) won’t return.
- **Recommendation**: Enforce auth + `organization_id` filtering in **every** read/write endpoint. Remove hard-coded user logic; require org-scoped project/folder selection.

## ORM/router schema mismatches will crash at runtime
- **Location**:
  - `apps/api/models.py` vs `apps/api/routers/search.py`
  - `apps/api/models.py` vs `apps/api/routers/calendar.py`
  - `apps/api/models.py` vs `apps/api/services/usage.py`
- **Severity**: **Critical**
- **Description**:
  - `SearchInsight` model appears to have `user_id`, not `organization_id`, but router filters on `SearchInsight.organization_id`.
  - `CalendarEvent` model lacks `organization_id`, but calendar router uses it and passes it in constructors.
  - `UsageEvent` model fields (tokens_input/tokens_output/occurred_at) do not match `services/usage.py` (metadata/cost_cents/recorded_at).
- **Impact**: Endpoints will throw exceptions and fail requests (500s) or won’t even import in some cases.
- **Recommendation**:
  - Decide the canonical multi-tenant schema (org-scoped vs user-scoped).
  - Align models and handlers; add migrations.
  - Delete dead/legacy code or gate by feature flags.

## No migrations; schema created at startup via `create_all`
- **Location**: `apps/api/database.py`, `apps/api/main.py`, `apps/api/README.md`
- **Severity**: **Critical**
- **Description**: DB schema is created on startup via `SQLModel.metadata.create_all(engine)` with no migration history.
- **Impact**:
  - Data-loss risk when schema changes (manual edits required).
  - Difficult rollbacks; non-deterministic production upgrades.
  - Concurrency issues if multiple instances start simultaneously.
- **Recommendation**: Introduce Alembic migrations (or SQLModel-compatible migration workflow). Treat schema changes as versioned migrations.

---

# 2) High Priority

## SQLite foreign keys and integrity constraints likely not enforced
- **Location**: `apps/api/database.py`, `apps/api/models.py`
- **Severity**: **High**
- **Description**: SQLite requires `PRAGMA foreign_keys=ON` per connection; current engine creation doesn’t set it.
- **Impact**: Orphaned rows, silent integrity violations (FKs declared but not enforced).
- **Recommendation**: Add a connect event listener to enable foreign keys for SQLite, or move to Postgres for production.

## Missing database constraints for uniqueness and de-duplication
- **Location**: `apps/api/models.py` (e.g., `Organization.slug`, `Membership`, `ScrapeItem.source_url`)
- **Severity**: **High**
- **Description**: Uniqueness is enforced in app code (e.g., org slug check) but not at DB level; no composite uniqueness for memberships.
- **Impact**: Race conditions allow duplicates; downstream code assumes uniqueness and may behave incorrectly.
- **Recommendation**:
  - Add `UNIQUE` constraints:
    - `organization.slug`
    - `membership(organization_id, user_id)`
    - `scrape_item(organization_id, source_url)` (if intended)

## Missing indexes on common access paths (org scoping, time ordering)
- **Location**: `apps/api/models.py`
- **Severity**: **High**
- **Description**: Only a handful of explicit indexes exist (keyword/gsc/trends/search/usage/audit/doctrine). Many likely query patterns filter by `organization_id`, `project_id`, `folder_id`, `deliverable_id`, `created_at`.
- **Impact**: Scaling bottlenecks as data grows; slow list pages and background jobs.
- **Recommendation**:
  - Add indexes for:
    - `Project(organization_id)`
    - `Folder(organization_id, project_id, parent_folder_id)`
    - `Deliverable(organization_id, folder_id, updated_at)`
    - `Brief(organization_id, project_id, deliverable_id, updated_at)`
    - `ScrapeItem(organization_id, created_at)` and/or `(organization_id, score, created_at)`
    - `ChatMessage(organization_id, session_id, created_at)`

## CORS configuration is unsafe/invalid for credentialed requests
- **Location**: `apps/api/main.py` (CORS middleware)
- **Severity**: **High**
- **Description**: `allow_origins=[..., "*"]` combined with `allow_credentials=True` is not valid and is unsafe.
- **Impact**: Browser clients may fail CORS checks; security risk if misconfigured.
- **Recommendation**: Remove `"*"` and explicitly list allowed origins, or set `allow_credentials=False` if you truly need wildcard.

## In-process scheduler will duplicate work in multi-worker deployments
- **Location**: `apps/api/main.py` (APScheduler jobs)
- **Severity**: **High**
- **Description**: Scheduler starts on FastAPI startup; with multiple processes/replicas, each instance will run the same cron/interval jobs.
- **Impact**: Duplicate scraping, duplicate Google calendar sync, increased cost and rate-limit risk.
- **Recommendation**: Run background jobs in a single dedicated worker (Celery/Arq/RQ) or an external scheduler (GitHub Actions/Cloud Scheduler) with idempotent tasks.

## Requirements are not fully pinned (non-reproducible deployments)
- **Location**: `apps/api/requirements.txt`
- **Severity**: **High**
- **Description**: Several dependencies are unversioned (e.g., `arize-otel`, `opentelemetry-sdk`, `beautifulsoup4`, `lxml`, `aiofiles`, `python-dotenv`).
- **Impact**: Builds become non-deterministic; unexpected breaking changes.
- **Recommendation**: Pin versions (or adopt Poetry/pip-tools) and consider hashes for supply-chain integrity.

---

# 3) Medium Priority

## Configuration loading depends on working directory
- **Location**: `apps/api/config.py`
- **Severity**: **Medium**
- **Description**: `env_file = ".env"` is relative to the process working directory, not the module path.
- **Impact**: Running `uvicorn` from repo root vs `apps/api` can silently load the wrong env or none.
- **Recommendation**: Use an absolute env path (e.g., `REPO_ROOT / "apps/api/.env"`) or document a strict working-directory requirement.

## Encryption keys auto-generated at runtime if missing
- **Location**: `apps/api/config.py` (`__init__`)
- **Severity**: **Medium**
- **Description**: If `ENCRYPTION_KEY` or `LLM_KEY_ENCRYPTION_SECRET` are absent, new keys are generated on boot.
- **Impact**: Encrypted data becomes undecryptable after restart; multi-instance deployments generate inconsistent keys.
- **Recommendation**: Fail fast in non-dev when required secrets are missing. Only allow auto-generation in explicit dev mode.

## Time handling is naive (UTC naive datetimes, inconsistent timezone usage)
- **Location**: `apps/api/models.py`, `apps/api/routers/briefing.py`, `apps/api/services/calendar.py`
- **Severity**: **Medium**
- **Description**: Mixed naive `datetime.utcnow()` and timezone-aware parsing in calendar sync.
- **Impact**: Subtle bugs around ordering, comparisons, and serialization.
- **Recommendation**: Store timezone-aware UTC (or enforce naive UTC everywhere consistently) and normalize all parsed datetimes.

## JSON stored as plain strings without validation
- **Location**: `apps/api/models.py` (e.g., `metadata_json`, `toggles_json`, `context_layers_json`, etc.)
- **Severity**: **Medium**
- **Description**: Many fields are `Optional[str]` but represent JSON.
- **Impact**: Corruption and unqueryable data; no schema validation; expensive app-level parsing.
- **Recommendation**: Use JSON columns in Postgres; or use SQLAlchemy JSON type where available and enforce Pydantic validation.

## Inefficient counts and stats queries
- **Location**: `apps/api/routers/search.py`
- **Severity**: **Medium**
- **Description**: Computes totals by loading all rows then `len()`.
- **Impact**: O(n) memory/time; will slow down as data grows.
- **Recommendation**: Use `select(func.count())` and indexed predicates.

---

# 4) Low Priority

## `.gitignore` has duplicates and doesn’t prevent already-committed artifacts
- **Location**: `.gitignore`, `apps/web/.gitignore`
- **Severity**: **Low**
- **Description**: Root `.gitignore` repeats `*.db` lines; `.env` is ignored but still committed.
- **Impact**: Confusing repo hygiene; new contributors may commit artifacts again.
- **Recommendation**: Clean up `.gitignore` and add repo checks (pre-commit / CI) to fail if `node_modules/`, `.next/`, `venv/`, `.env`, `*.db` are tracked.

## Slack scripts embed emoji and assume stdout preview
- **Location**: `apps/api/scripts/ai_daily_briefing.py`, `apps/api/scripts/founder_tweet_recap.py`
- **Severity**: **Low**
- **Description**: Scripts print previews and include emoji; fine, but may be noisy in Actions logs.
- **Impact**: Log noise.
- **Recommendation**: Gate preview output behind env var (e.g., `DEBUG=1`).

---

# 5) Opportunities

## Introduce proper deployment topology
- **Opportunity**: Split API, worker, and frontend deployments.
- **Recommendation**:
  - API: containerized (Docker) with Postgres.
  - Worker: background jobs (scraping/calendar sync) in a separate process.
  - Frontend: Vercel/Netlify (or static export if truly static).

## Add observability and operational guardrails
- **Location**: `apps/api/instrumentation.py`
- **Opportunity**: You already have Arize OTel wiring.
- **Recommendation**:
  - Add explicit spans for background jobs and DB operations.
  - Export metrics (queue depth, job runtimes, failures).
  - Add health endpoints for DB connectivity and scheduler state.

## Data model normalization and tenant safety
- **Opportunity**: Align all “content” tables to an explicit tenant model.
- **Recommendation**:
  - Add `organization_id` to all tables that are tenant-owned.
  - Add composite indexes `(organization_id, <fk>)`.
  - Consider row-level security patterns (in Postgres) if needed.

## Migration strategy
- **Opportunity**: Establish a deterministic schema lifecycle.
- **Recommendation**:
  - Add Alembic.
  - Generate initial migration from current SQLModel metadata.
  - Replace `create_all` at startup with `alembic upgrade head` in deploy.

---

## Appendix: Files reviewed (core infra/config)
- `.github/workflows/*.yml`
- `.gitignore`
- `apps/api/.env.example` (did not inspect `apps/api/.env` contents)
- `apps/api/requirements.txt`
- `apps/api/{config.py,database.py,models.py,main.py,instrumentation.py,cache.py}`
- `apps/api/middleware/auth.py`
- Selected routers/services: `routers/{projects.py,orgs.py,briefing.py,search.py,calendar.py}`, `services/{calendar.py,oauth.py,usage.py}`
- `apps/web/{package.json,next.config.mjs,tsconfig.json,tailwind.config.ts,postcss.config.mjs,.gitignore}`
