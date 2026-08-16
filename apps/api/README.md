# ForgeOS API

FastAPI backend for ForgeOS. Serves as the interface between the markdown engine, the SQLite database, and the web frontend.

## Setup

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Installation

```bash
cd apps/api
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your configuration:

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL_GENERATION=claude-opus-4-7
MODEL_SCORING=claude-haiku-4-5
DATABASE_URL=sqlite:///./forgeos.db
ARIZE_SPACE_ID=your_space_id_here
ARIZE_API_KEY=your_arize_api_key_here
```

- `ANTHROPIC_API_KEY` — Required. Get from [console.anthropic.com](https://console.anthropic.com/)
- `MODEL_GENERATION` — Model for content generation (default: `claude-opus-4-7`)
- `MODEL_SCORING` — Model for intelligence scoring (default: `claude-haiku-4-5`)
- `ARIZE_SPACE_ID`, `ARIZE_API_KEY` — Optional. Observability tracing via Arize AX

## Running

```bash
python -m uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Check `/api/health` for a health ping.

## Rate limiting

ForgeOS API uses **slowapi** to rate limit requests to protect against DoS and brute-force attacks.

**Keying policy:**
- Authenticated requests are limited **per user** (JWT `sub`).
- Unauthenticated requests are limited **per IP**.

**Default limits (configurable via env):**
- Auth endpoints (`/api/auth/*`): `RATE_LIMIT_AUTH` (default: `10/minute`)
- Public endpoints (`/api/health`, `/api/trust/legal/*`, `/api/trust/status`): `RATE_LIMIT_PUBLIC` (default: `60/minute`)
- Internal endpoints (most authenticated endpoints): `RATE_LIMIT_INTERNAL` (default: `100/minute`)
- Expensive endpoints also have a global cap: `RATE_LIMIT_EXPENSIVE_GLOBAL` (default: `30/minute`)

When rate limited, the API returns **429 Too Many Requests** with `X-RateLimit-*` headers.

### Configuration

Add to `.env` as needed:

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STORAGE_URI=memory://
RATE_LIMIT_TRUST_X_FORWARDED_FOR=false

RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_PUBLIC=60/minute
RATE_LIMIT_INTERNAL=100/minute
RATE_LIMIT_EXPENSIVE_GLOBAL=30/minute
```

## API Overview

### Health & Status

- `GET /api/health` — Health check

### Content Organization

- `GET /api/projects` — List all projects
- `POST /api/projects` — Create a project
- `GET /api/folders` — List folders in a project
- `POST /api/folders` — Create a folder
- `GET /api/deliverables` — List deliverables
- `POST /api/deliverables` — Create a deliverable
- `GET /api/deliverables/{id}` — Get deliverable details

### Brief Management

- `GET /api/briefs` — List briefs
- `POST /api/briefs` — Create a brief
- `GET /api/briefs/{id}` — Get brief details
- `PUT /api/briefs/{id}` — Update a brief

### Chat (Interactive Mode)

- `POST /api/chat/brief` — Generate a brief from a prompt
- `POST /api/chat/generate` — Generate content using a playbook
- `GET /api/chat/stream` — Stream chat responses

### Intelligence & Briefing

- `GET /api/intelligence/feed` — Full scored intelligence feed with filters
- `POST /api/intelligence/scrape` — Trigger an immediate scrape
- `GET /api/briefing` — Curated briefing view (top-scored items from last 24h)

### Pipeline Mode (Legacy Sessions)

- `GET /api/sessions` — List pipeline runs
- `POST /api/sessions` — Create a pipeline run
- `GET /api/sessions/{id}` — Get run details
- `POST /api/sessions/{id}/run` — Execute the agent chain

### Settings & Engine Management

- `GET /api/settings/engine` — Tree view of markdown engine (`core/`, `context/`, `skills/`, `playbooks/`, `rubrics/`)
- `PUT /api/settings/engine/file` — Update an engine file (explicit save)
- `GET /api/settings/scraping-config` — Get scraper configuration
- `PUT /api/settings/scraping-config` — Update scraper sources

### File Operations

- `GET /api/files/{path}` — Read a file from the engine
- `PUT /api/files/{path}` — Write a file to the engine (explicit save)

## Database

SQLite database at `forgeos.db` (configurable via `DATABASE_URL` in `.env`). Schema is auto-migrated on startup using SQLModel.

**Key tables:**
- `project` — Top-level content projects
- `folder` — Nested organization under projects
- `deliverable` — Final content output (markdown, status, metadata)
- `brief` — Structured brief (input shape for content generation)
- `chat_session` — Conversation thread
- `chat_message` — Individual messages
- `pipeline_run` — Fire-and-forget agent chain execution (legacy Sessions)
- `scrape_item` — Scored intelligence items from web scraping
- `pipeline_step` — Intermediate outputs per agent in a pipeline run

## Scraping

The system runs a scheduled scraper twice daily (configurable via APScheduler cron). It reads from:

- **Hacker News** (Algolia API) — `hn`
- **GitHub** (topics RSS) — `github`
- **ArXiv** (RSS) — `arxiv`
- **Reddit** (JSON API) — `reddit`
- **Generic RSS feeds** — `rss`

Each scraped item is scored by `services/scoring.py` using a scoring prompt from `context/07_research/intelligence-scoring-prompt.md`. Items with score ≥7 are included in the Briefing Book; all items appear in the Intelligence feed.

**Configure scraping:**
1. Open Settings → Scraping Config
2. Edit sources, keywords, subreddits, RSS feeds
3. Scoring prompt is editable in `context/07_research/intelligence-scoring-prompt.md`
4. Trigger immediate scrape via "Refresh now" button or `/api/intelligence/scrape`

## Testing

Run tests with pytest:

```bash
pytest
```

Tests are in `tests/` (if any exist).

## Phased rollout readiness checker

Run the deterministic go/no-go checker for the 12-month rollout:

```bash
python3 apps/api/scripts/check_phase_readiness.py
```

The checker validates required readiness signals across phase gates, including key context files, API components/endpoints, and phase-aligned test files. It exits with code `0` for GO and `1` for NO-GO.

## Instrumentation

ForgeOS dogfoods Arize AX observability. Tracing is wired via `instrumentation.py`:

- Agent runs are traced with `CHAIN` spans
- Claude calls are auto-instrumented via `openinference-instrumentation-anthropic`
- Scraping jobs are traced
- Chat and pipeline endpoints are traced

Traces export to Arize if `ARIZE_SPACE_ID` and `ARIZE_API_KEY` are set. Otherwise, traces are printed to console.

## Architecture

```
apps/api/
├── main.py                  # App entry point, router registration
├── config.py                # Settings (environment variables)
├── models.py                # SQLModel definitions
├── database.py              # SQLite connection
├── cache.py                 # In-memory TTL cache
├── instrumentation.py       # Arize AX tracing setup
├── requirements.txt         # Python dependencies
├── routers/                 # Endpoint handlers
│   ├── projects.py          # /api/projects, /api/folders, /api/deliverables
│   ├── briefing.py          # /api/briefing (curated briefing view)
│   ├── chat.py              # /api/chat/* (interactive mode)
│   ├── intelligence.py      # /api/intelligence/* (full feed + scraping)
│   ├── sessions.py          # /api/sessions/* (legacy pipeline mode)
│   ├── settings.py          # /api/settings/* (engine management)
│   ├── jobs.py              # /api/jobs/* (job queue monitoring)
│   └── files.py             # /api/files/* (markdown engine file I/O)
├── services/                # Business logic
│   ├── file_engine.py       # Markdown engine abstraction
│   ├── generation.py        # Playbook execution & content generation
│   ├── scoring.py           # Intelligence item scoring
│   └── scraping.py          # Web scraper implementations
├── tasks.py                 # Celery background tasks
├── celery_app.py            # Celery configuration
├── manage_jobs.py           # Job queue management CLI
└── scripts/                 # Utilities
    ├── validate_repo_structure.py
    └── lint_skill_files.py
    └── check_phase_readiness.py
```

## Background Jobs

ForgeOS uses **Celery** with **Redis** for reliable background job processing. This provides automatic retries, monitoring, and distributed task execution.

### Quick Start

1. **Start services with Docker:**
   ```bash
   cd /path/to/forgeos
   docker-compose up -d
   ```

2. **Or run locally:**
   ```bash
   # Terminal 1: Redis
   redis-server
   
   # Terminal 2: Celery worker
   cd apps/api
   celery -A celery_app worker --loglevel=info
   
   # Terminal 3: Celery beat (scheduler)
   celery -A celery_app beat --loglevel=info
   ```

3. **Monitor at** http://localhost:5555 (Flower UI)

### Documentation

- **[CELERY_QUICKSTART.md](./CELERY_QUICKSTART.md)** - Get started in 5 minutes
- **[BACKGROUND_JOBS.md](./BACKGROUND_JOBS.md)** - Complete job queue documentation
- **[CELERY_MIGRATION.md](./CELERY_MIGRATION.md)** - Migration from APScheduler

### Scheduled Tasks

| Task | Schedule | What it does |
|------|----------|--------------|
| Intelligence Scraping | 8 AM & 6 PM | Scrape and score intelligence sources |
| Calendar Sync | Every 5 min | Poll Google Calendar for updates |
| Trends Polling | 9 AM daily | Fetch Google Trends data |
| Email/Slack Digests | 8 AM daily | Send daily notifications |
| Data Cleanup | 2 AM daily | Archive old data |
| Weekly Report | Monday 7 AM | Generate analytics reports |

See [BACKGROUND_JOBS.md](./BACKGROUND_JOBS.md) for the complete list and details.

---

For more context, see the [main README](../../README.md).

---

## Query Optimization (P4.1)

ForgeOS API implements SQLAlchemy query optimization patterns to prevent N+1 queries and improve performance.

### Patterns

#### 1. Pagination with Offset/Limit

Always paginate list endpoints to reduce memory usage and response time:

```python
from fastapi import Query
from services.query_optimization import PaginationParams, add_pagination

@router.get("/projects")
def list_projects(
    auth: AuthContext = Depends(get_current_user),
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    pagination = PaginationParams(skip=skip, limit=limit)
    query = select(Project).where(Project.organization_id == auth.org_id)
    query = add_pagination(query, pagination)
    return session.exec(query).all()
```

#### 2. Eager Loading with selectinload

Load related objects in the same query to avoid N+1 queries:

```python
from services.query_optimization import apply_eager_loading

# Bad: N+1 queries (one for briefs, one per brief for items)
briefs = session.exec(select(Brief)).all()
for brief in briefs:
    items = brief.items  # Lazy load - triggers N queries

# Good: Single query with eager loading
query = select(Brief).options(
    selectinload(Brief.scrape_items)
)
briefs = session.exec(query).all()

# Or use the helper:
query = select(Brief)
query = apply_eager_loading(query, Brief, ["scrape_items"])
```

#### 3. Optimized List Queries

Use `optimize_list_query()` for the recommended pattern:

```python
from services.query_optimization import optimize_list_query

# Single optimized call with pagination, ordering, and eager loading
projects = optimize_list_query(
    session,
    Project,
    org_id=auth.org_id,
    skip=skip,
    limit=limit,
    relationships=["folders", "briefs"],
    order_by_field=Project.created_at.desc(),
)
```

#### 4. Caching

Optional Redis caching for read-heavy endpoints:

```python
from services.query_optimization import cached_query
from config import settings

@cached_query(cache_ttl_seconds=3600, cache_enabled=settings.CACHE_ENABLED)
def get_user_projects(user_id: str, session: Session):
    return session.exec(
        select(Project).where(Project.user_id == user_id)
    ).all()
```

### Performance Benchmarks

Expected improvements with optimization:

| Query Type | Before | After | Improvement |
|-----------|--------|-------|------------|
| List 100 projects | 101 queries, 500ms | 1 query, 50ms | 10x faster |
| List items with relationships | 51 queries, 800ms | 2 queries, 80ms | 10x faster |
| Paginated list (20 items) | 1 query | 1 query | No change (already fast) |

### Monitoring Queries

Use the monitoring tools to track query performance:

```python
from monitoring import time_operation, record_db_operation

with time_operation("list_projects", attributes={"table": "project"}):
    projects = session.exec(select(Project)).all()
    record_db_operation("select", "project", count=len(projects))
```

---

## Observability & Monitoring (P4.2)

ForgeOS API provides comprehensive observability via Sentry error tracking and OpenTelemetry distributed tracing.

### Sentry Integration

Sentry captures errors and provides performance monitoring.

#### Configuration

Add to `.env`:

```env
SENTRY_DSN=https://your-key@sentry.io/your-project-id
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILE_SAMPLE_RATE=0.1
```

- `SENTRY_DSN` — Get from sentry.io; leave blank to disable
- `SENTRY_TRACES_SAMPLE_RATE` — 10% of requests sampled for performance tracing
- `SENTRY_PROFILE_SAMPLE_RATE` — 10% of traced requests include profiling data

#### What's Tracked

- **Errors**: All unhandled exceptions automatically captured
- **Performance**: Request latency, database queries, Celery tasks
- **Context**: User ID, organization ID, request ID attached to all traces
- **Slow Requests**: Alerts on endpoints >1000ms
- **Database Issues**: Slow queries (>500ms) and connection pool saturation

### Distributed Tracing

Trace requests through the entire system:

```python
from monitoring import trace_operation, time_operation

@router.get("/projects")
@trace_operation("list_projects")  # Creates named trace span
def list_projects(auth, session):
    with time_operation("db_query", attributes={"table": "projects"}):
        return session.exec(select(Project)).all()
```

### Metrics Collection

Real-time metrics on request/database performance:

```python
from monitoring import get_metrics_collector, get_request_summary

# After request completes, retrieve summary
summary = get_request_summary()
print(f"Request took {summary['total_duration_ms']}ms")
print(f"Database queries: {summary['db_query_count']}")
```

Metrics exported:

- `http_requests_total` — Total requests by endpoint/method/status
- `http_request_duration_ms` — Request latency (histogram)
- `db_queries_total` — Total database queries by operation/table
- `db_query_duration_ms` — Query latency (histogram)
- `celery_tasks_total` — Total background jobs executed
- `celery_task_duration_ms` — Job execution time
- `errors_total` — Errors by type/endpoint

### Health Check

The `/api/health` endpoint provides real-time system status:

```bash
curl http://localhost:8000/api/health
```

Response:

```json
{
  "status": "ok",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "scheduler": "ok"
  }
}
```

Status values:
- **ok** — All systems healthy
- **degraded** — Some systems down but core functions work
- **error** — Critical systems offline

### Custom Tracing

Create custom spans for internal operations:

```python
from monitoring import trace_operation, time_operation, record_db_operation

@trace_operation("generate_brief")
def generate_brief(project_id: int, session: Session):
    # Record database operation
    with time_operation("db_fetch", attributes={"entity": "project"}):
        project = session.get(Project, project_id)
        record_db_operation("select", "project", count=1)
    
    # Record expensive operation
    with time_operation("llm_call", attributes={"model": "claude-opus"}):
        brief = generate_with_llm(project)
    
    return brief
```

### Alerting

Configure alerts in Sentry dashboard:

1. **Error Rate Alert**: Trigger when error rate > 5%
2. **Latency Alert**: Trigger when p95 latency > 1000ms
3. **Resource Alert**: Trigger when DB connection pool > 90% utilized

Default thresholds (in `monitoring.py`):

- Slow database query: >500ms
- Slow endpoint: >1000ms
- Slow Celery task: >10000ms (10 seconds)

---
