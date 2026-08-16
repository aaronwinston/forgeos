# ForgeOS documentation map

This directory contains all operational, strategic, and deployment documentation.

## 📍 Navigation guide

### Getting started with deployment
- **[VERCEL_DEPLOYMENT.md](./deployment/VERCEL_DEPLOYMENT.md)** — How to deploy `apps/web` to Vercel and connect to the backend API

### Strategic & product docs
- **[prd/FORGEOS_PRD.md](./prd/FORGEOS_PRD.md)** — Product roadmap, feature planning, and technical strategy
- **[prd/FORGEOS_COMMERCIALIZATION_PRD.md](./prd/FORGEOS_COMMERCIALIZATION_PRD.md)** — Commercialization plan, team structure, and go-to-market

### Production system
- **[getting-started-production-system.md](./getting-started-production-system.md)** — Running ForgeOS as a production content system for your team
- **[playbooks/](./playbooks/)** — Step-by-step workflows for content types
- **[content-planning/](./content-planning/)** — Content strategy and planning resources
- **[events/](./events/)** — Event tracking and lifecycle documentation

### Archive (historical reference)
- **[archive/](./archive/)** — Legacy status reports, review writeups, and implementation snapshots

Historical docs are preserved for context but are not the current source of truth. Current operations reference the active sections above.

---

## 🏗️ What lives where

### In the main repo root
- `core/` — Voice, style, claims policy, editorial standards (doctrine, not editable)
- `context/` — Eight composable context layers (the knowledge base engine)
- `skills/` — Agent definitions (specialists that run on the engine)
- `playbooks/` — Orchestration workflows (how skills sequence together)
- `rubrics/` — Quality scoring and evaluation standards
- `briefs/` — Intake templates per content type
- `prompts/` — Composable prompt fragments

### In this `docs/` directory
- Deployment guides (how to run ForgeOS for yourself)
- Product requirements (what we're building and why)
- Strategic docs (vision, roadmap, commercialization)
- Historical docs (archive for context and audit trail)

---

## 🚀 Quick links

- **Want to run ForgeOS locally?** Start with the main [README.md](../README.md)
- **Want to deploy to production?** See [deployment/VERCEL_DEPLOYMENT.md](./deployment/VERCEL_DEPLOYMENT.md)
- **Want to use ForgeOS as a content system?** See [getting-started-production-system.md](./getting-started-production-system.md)
- **Want to understand the roadmap?** See [prd/FORGEOS_PRD.md](./prd/FORGEOS_PRD.md)
