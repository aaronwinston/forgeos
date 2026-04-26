# ForgeOS

AI-native editorial and marketing operating system for Arize AI.

**Two layers:**
1. **The Engine** — a markdown knowledge base of voice, skills, playbooks, and standards
2. **The Cockpit** — a local web app that wraps the engine with chat, editing, intelligence, and generation

---

## Architecture

```
mktg-agents/
  context/          # Curated knowledge base (8 layers, 00_orchestration to 07_research)
  core/             # Shared standards (voice, style, claims policy, brand)
  skills/           # Specialist agent skill definitions
  playbooks/        # Sequenced production workflows
  rubrics/          # Quality scoring rubrics
  briefs/           # Intake brief templates
  prompts/          # Reusable prompt templates
  examples/         # Reference quality tiers
  tests/            # Sample briefs and expected outputs
  workflows/        # Workflow documentation
  apps/
    api/            # FastAPI backend — file engine, CRUD, chat streaming, scraping
    web/            # Next.js 14 frontend — dashboard, intelligence, settings, project workspace
  packages/
    shared/         # Shared TypeScript types (v2)
```

## How to run

### Prerequisites
- Python 3.11+
- Node.js 18+
- An Anthropic API key

### Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
python -m uvicorn main:app --reload --port 8000
```

On first run, seed the database:
```bash
python scripts/seed_demo.py
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000.

---

## The markdown engine

The markdown files at the repo root are the system's brain. The app reads and writes to them. They remain the source of truth.

**Start every agent session with:**
```
Read context/00_orchestration/forgeos-context-orchestrator.md first.
Then check the relevant context files for this task before drafting.
```

---

## Validation

```bash
cd apps/api
source venv/bin/activate
python scripts/validate_repo_structure.py
python scripts/lint_skill_files.py
```

---

## v2 roadmap
- Calendar / pipeline view
- Slack, Gmail, HubSpot integrations
- Multi-user auth
- Twitter/X scraper (interface exists, implementation stubbed)
- Broad web search (interface exists, implementation stubbed)
