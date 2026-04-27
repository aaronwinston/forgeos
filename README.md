<img width="1082" height="607" alt="Screenshot 2026-04-26 at 9 18 56 PM" src="https://github.com/user-attachments/assets/e712f82b-f49a-47f8-9cef-37784dafd509" />


# **ForgeOS: Mission control for content.**
 
A local-first marketing operating system. You point it at your voice, your messaging, your competitive POV. It points back at the work.
 
Most AI writing tools start with a chat box. That's a search bar with extra steps. ForgeOS starts with a knowledge base. The chat box is downstream of it.
 
---
 
## What this is
 
Two layers, one product.
 
**The engine** is a markdown brain at the repo root. Voice rules, claims policy, skills, playbooks, context layers, rubrics. You own these files. You edit them in your editor of choice or in the app. The agents read them before they read your prompt.
 
**The cockpit** is a Next.js app you run on localhost. Dashboard, briefing, projects, deliverables, chat, pipeline runs, engine editor. It writes back to the same markdown files. Your `git log` is the audit trail.
 
The whole system is built on a single bet: that the gap between AI-generated slop and content that sounds like you came out of it is almost entirely a function of what's in the system prompt before the user types anything. So the engine is canonical. The cockpit is in service to it.

## The name is earned, not invented.

A forge is where raw material becomes something shaped and useful. The ore goes in rough. It comes out with form and purpose. The smith doesn't replace the material — she reveals what it was always capable of being.

That is what this system is for. Not to replace the thinking. To give the thinking somewhere to go.

Every marketer who uses ForgeOS brings their own ore: their company's story, their product's actual capabilities, their audience's real fears and real questions. The system provides the heat, the tools, the structure, and the quality bar. What comes out is content that sounds like it was written by someone with judgment — because the judgment was encoded into the system before the agents touched anything.
 
---
 
## Why I built this
 
I do a lot of work, and my job demands a small team's worth of output from one person (me). The available tools either generated faster slop or organized slower slop. Neither solved the actual problem.

So I slopped up my own tool (you're looking at it). 
 
The actual problem I was trying to solve? every output needs voice, point of view, and technical fluency that doesn't survive a generic prompt. Loading those things into context manually, every time, doesn't scale. Saving prompts in a Notion doc doesn't scale either, because prompts decay and Notion isn't a runtime.
 
ForgeOS is what happens when you treat your editorial standards as code, version them, and put a runtime in front of them.
 
---
 
## Two ways to work
 
**Chat mode.** Conversational. Optional brief-first flow that asks you only what materially changes the output, then composes a brief, then runs the relevant playbook to produce a deliverable. This is where most of the work happens.
 
**Pipeline mode.** Fire-and-forget. One prompt enters, eleven specialist agents work it in sequence, a finished draft comes out the other side. For when you know what you want and want it batched.
 
Both modes draw from the same engine. Both write back to the same deliverables. Pick the one that fits the moment.
 
---
 
## The engine
 
The markdown directories at the repo root are the source of truth. Every agent reads from them. The app writes back to them.
 
```
core/         Voice, style, claims policy, editorial principles, brand standards
context/      Eight composable layers from philosophy through research
skills/       Twenty-two specialist agent definitions, organized by category
playbooks/    Sequenced workflows that orchestrate skills for each content type
rubrics/      Quality bars used during review and scoring
briefs/       Intake brief templates per content type
prompts/      Reusable prompt fragments composed into the system prompt
```
 
`core/` is doctrine. `context/` is composable. `skills/` are the actors. `playbooks/` are the choreography. `rubrics/` are the bar. Each layer is editable. None of them are sacred.
 
**A note on what's intentionally thin.** Several files in `context/02_narrative/`, `context/03_strategy/`, and `context/04_execution/` ship as placeholders. That's deliberate, not unfinished. The shape is right; the content needs to be your company's, not a generic template.
 
---
 
## The cockpit
 
```
Dashboard       Daily briefing curated from HN, Reddit, GitHub, and arXiv
Workspace       Three pane editor with chat, brief, and WYSIWYG over the deliverable
Pipelines       Fire-and-forget runs of the eleven-agent chain
Intelligence    Full scored feed of everything the scrapers surfaced
Projects        Nested projects, folders, deliverables organized by content type
Settings        Engine editor, runtime keys, scrape config, integrations
```
 
Everything streams. Chat tokens stream. Pipeline progress streams. The dashboard updates without a refresh.
 
The right rail in the workspace shows which context layers, skills, and intelligence items are composed into the current prompt. You can see exactly what the agent sees. You can also remove anything you don't want in the prompt with one click.
 
---
 
## The eleven agents
 
Each pipeline run executes this chain in order. Each agent reads its own `SKILL.md` before running, so its behavior is fully inspectable and editable.
 
```
editorial-director       Frames the narrative, sets the strategy
ai-researcher            Pulls sources, validates context
dev-copywriter           Writes the draft
dev-reviewer             Tightens copy, fixes structure
technical-fact-checker   Verifies technical claims
seo-strategist           Optimizes for search without losing the voice
copy-chief               Final editorial pass
claims-risk-reviewer     Flags unsupported or risky claims
final-publish-reviewer   Last sanity check before publish
social-editor            Derives social from the long form
content-ops-manager      Distribution and repurposing plan
```
 
Eleven specialists running on rails. Change the skill file, change the agent. Add a skill, add a step.
 
---
 
## The briefing
 
Every morning the system reads what the internet is talking about and tells you what's worth your attention.
 
Sources: Hacker News (Algolia API), Reddit JSON, GitHub trending, arXiv RSS, plus a configurable list of blog feeds. Twice a day on a cron. Every item gets scored by Claude Haiku against a prompt at `context/07_research/intelligence-scoring-prompt.md`. Items scoring seven or higher land in the dashboard's briefing card.
 
You edit the scoring prompt the same way you edit any other context layer. The system gets sharper as your taste does.
 
---
 
## Run it
 
**Prerequisites**
 
- Python 3.9 or newer
- Node.js 18 or newer
- An [Anthropic API key](https://console.anthropic.com/)
**Backend**
 
```bash
cd apps/api
python -m venv venv
source venv/bin/activate              # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```
 
Open `.env` and add your key:
 
```
ANTHROPIC_API_KEY=sk-ant-...
```
 
Start the API:
 
```bash
python -m uvicorn main:app --reload --port 8000
```
 
Confirm it's up:
 
```bash
curl http://localhost:8000/api/health
```
 
**Frontend**
 
```bash
cd apps/web
npm install
npm run dev
```
 
Open `http://localhost:3000`. Empty states are real. If the API is down the app says so and tells you how to start it. Nothing breaks. Nothing red.
 
**First run**
 
```bash
cd apps/api
python scripts/seed_demo.py
```
 
Seeds a project, a folder, a brief, and a deliverable so the cockpit has something to render while you wait for your first scrape to finish.
 
---
 
## How to use it
 
**Make something.**
 
1. Click **Let's build** on the dashboard.
2. Pick guided (chat walks you through the brief) or YOLO (one prompt, no questions).
3. Set toggles in the right rail: audience, voice, content type, which skills to invoke. Auto is fine for most things.
4. Confirm or edit the brief.
5. Watch the chain run in real time. Open the deliverable when it lands.
**Edit your voice.**
 
`core/VOICE.md` in any editor. Or Settings → Engine → Voice in the app. Save explicitly. The next chat will use the new version. No restart needed.
 
**Add a skill.**
 
```
skills/{category}/{agent-name}/SKILL.md
```
 
Frontmatter at the top, prose below. Reference it from a playbook or invoke it directly from the workspace toggles. The lint will tell you if the structure is wrong.
 
```bash
python scripts/lint_skill_files.py
python scripts/validate_repo_structure.py
```
 
**Refresh the briefing.**
 
Click refresh on the dashboard. Or hit `POST /api/intelligence/scrape`. The synthesis pass that produces the curated briefing runs once per scrape, not once per page load, so the dashboard is fast.
 
---
 
## Architecture
 
```
forgeos/
├── core/                       Voice, style, claims, editorial principles
├── context/                    Eight composable context layers
│   ├── 00_orchestration/       Routing rules for the engine
│   ├── 01_philosophy/          Developer marketing principles
│   ├── 02_narrative/           Messaging, competitive POV, campaign messaging
│   ├── 03_strategy/            Content strategy, AR strategy
│   ├── 04_execution/           Launch playbooks, post-launch frameworks
│   ├── 05_patterns/            Proven content patterns
│   ├── 06_influence/           Analyst relations
│   └── 07_research/            Market research, intelligence scoring prompt
├── skills/                     Twenty-two agent definitions
│   ├── editorial/              Director, copy chief, content-ops manager
│   ├── foundation/             Researcher, copywriter, reviewer
│   ├── specialization/         SEO, social, fact-checker, repurposer, more
│   └── quality/                Claims risk, publish readiness
├── playbooks/                  Workflow definitions
├── rubrics/                    Scoring rubrics
├── briefs/                     Intake templates
├── prompts/                    Composable prompt fragments
└── apps/
    ├── api/                    FastAPI backend
    │   ├── main.py             Entry, router registration, scheduler
    │   ├── routers/            chat, projects, sessions, intelligence, files
    │   ├── services/           generation, scraping, scoring, file_engine
    │   ├── models.py           Project, Folder, Deliverable, Brief, ScrapeItem
    │   ├── database.py         SQLite via SQLModel
    │   └── instrumentation.py  Arize AX (OpenTelemetry)
    └── web/                    Next.js 14
        └── src/
            ├── app/            Routes
            ├── components/     UI, layout, dashboard, workspace
            └── lib/            API client, types, utilities
```
 
No cloud database. No auth service. No Redis. No Vercel. SQLite on disk. Static frontend. One API key. One person can run it.
 
---
 
## Tech stack
 
| Layer | Technology |
|---|---|
| Backend | FastAPI, Python 3.9+ |
| Database | SQLite via SQLModel |
| Models | Anthropic Claude (Opus 4.7 for generation, Haiku 4.5 for scoring) |
| Frontend | Next.js 14, TypeScript |
| Styling | Tailwind CSS |
| Data | React Query |
| Observability | Arize AX |
 
ForgeOS is instrumented end to end with Arize AX. Every model call, every retrieval, every chain step is traced. The system that helps you write about agent observability is itself observable. That's not a coincidence.
 
---
 
## What's next
 
The roadmap moves in three directions. Not all at once.
 
**Near term.** Calendar with bidirectional Google sync. The "Let's build" guided flow as the default entry point. Content strategy upload that routes documents to the right context layer. Sentence case across the entire UI. Light and dark themes that earn their pixels.
 
**Medium term.** Search intelligence. Google Search Console plus Trends plus the existing scrape pipeline, joined by a daily LLM pass that tells you where the gaps are. Real per-skill model routing once a second LLM provider is wired. A skill marketplace where the engine becomes shareable.
 
**Longer term.** Multi-tenancy. Auth. Team plans. Billing. The version of this that other people pay for.
 
The PRDs that govern each of these live in the repo at `FORGEOS_PRD.md`, `FORGEOS_PHASE_PLAN.md`, and `FORGEOS_COMMERCIALIZATION_PRD.md`. Read them before opening a PR.
 
---
 
## Contributing
 
I'm one person building this between other work. The roadmap is real and the gaps are real.
 
- **Frontend.** The cockpit is functional. It is not yet excellent.
- **Backend.** The agent runner, the scrape pipeline, the engine watcher all have meaningful improvements queued up.
- **AI engineering.** Evals, scoring calibration, parallelism, smarter context composition. All open problems.
- **Technical writers.** The engine is the product. Good writers who understand AI tooling matter as much as good engineers here.
- **Marketers who code.** This tool is built for people like you. Your feedback shapes everything.
Open an issue. Start a discussion. The best contributions usually start with a conversation.
 
---
 
## License
 
MIT. Use it, fork it, build on it. If it helps you, tell me.
