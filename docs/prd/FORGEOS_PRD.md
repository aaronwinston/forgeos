# ForgeOS — Product Requirements Document

**Owner:** Aaron Winston (Head of Content, Comms, AR — Arize AI)
**Status:** v1 in repair; v2 features scoped
**Last updated:** 2026-04-26
**Repo:** github.com/aaronwinston/forgeos (branch: `you're-looking-at-it`)

This PRD reflects the actual state of the repo as of this commit — not an aspirational redesign. Section 2 ("What is broken right now") is grounded in code reading; every claim names the file and the bug. Section 4 ("v1 must-fix") is the only section that should be touched in the next session. Everything else is context or scope for later.

---

## 1. What ForgeOS is, in one paragraph

ForgeOS is a **local-first marketing command center** that wraps a markdown-based "engine" of voice rules, skills, playbooks, and context with a Next.js cockpit. Aaron uses it to produce developer marketing for Arize AI — blogs, launches, AR responses, social, lifecycle emails — at the throughput of a small team. The markdown directories at the repo root (`context/`, `core/`, `skills/`, `playbooks/`, `rubrics/`, `briefs/`, `prompts/`) are the system's brain and remain canonical. The app reads from and writes to them. The database (SQLite via SQLModel) holds runtime state only: projects, folders, deliverables, briefs, chat sessions and messages, scrape items, and agent run state.

This PRD distinguishes two run modes that both currently exist in the codebase under conflicting names. Going forward:

- **Chat mode** — conversational, optionally producing a brief first, optionally executing a playbook to produce a deliverable. Backed by `ChatSession`, `ChatMessage`, `Brief`, `Deliverable`. Endpoints under `/api/chat/*`. This is the primary path.
- **Pipeline mode** — fire-and-forget execution of the full agent chain against a single prompt. Backed by `AgentSession`. Endpoint `/api/sessions/*`. This is the legacy "Sessions" UI from the Claude Design pass.

These two paths exist for different reasons and both should remain. They must stop being conflated in the UI copy. See §6 for the disambiguation.

---

## 2. What is broken right now (audit findings)

### 2.1 Critical bugs (showstoppers — fix first)

**Bug A: `briefing` router is imported but never registered.**
File: `apps/api/main.py` line 9 imports `briefing` along with the other routers, but lines 21–25 only call `include_router` for `projects, chat, intelligence, settings, files`. The `briefing` and `sessions` routers are never registered. Result: `GET /api/briefing` returns 404, the dashboard's Briefing Book always shows the "Start the local API" empty state even when the API is running, and the Sessions UI cannot create or run sessions. **This is the single biggest reason the app appears non-functional.** Fix: add `app.include_router(briefing.router)` and `app.include_router(sessions.router)`.

**Bug B: hardcoded model name that doesn't match what's actually available.**
Files: `apps/api/runner.py` line 60 and `apps/api/routers/briefing.py` line 116 both call `client.messages.stream(model="claude-sonnet-4-5", ...)`. The intended models per the architecture are `claude-opus-4-7` for generation and `claude-haiku-4-5` for cheap scoring. `claude-sonnet-4-5` will either error out or behave unexpectedly depending on the SDK's resolution behavior. Fix: introduce two constants in `config.py` (`MODEL_GENERATION = "claude-opus-4-7"`, `MODEL_SCORING = "claude-haiku-4-5"`) and use them everywhere a model name appears today.

**Bug C: two competing scraper implementations, neither wired to the dashboard.**
The dashboard's Briefing Book calls `getBriefing()` → `/api/briefing` (router not registered, see Bug A). That router has its own inline scrapers (`scrape_hackernews`, `scrape_github_trending`, `scrape_arxiv`) and synthesizes via Claude into a `stories` shape with `why_relevant`, `engagement_signal`, `content_angle`. Separately, `services/scraping.py` has a more robust scraper set (HN Algolia API, Reddit JSON, GitHub topics, arXiv RSS, RSS feeds), and it writes to the `ScrapeItem` table on the twice-daily scheduler. The Intelligence page reads from that table via `/api/intelligence/feed`. **These are two parallel intelligence systems that don't know about each other.** The Briefing Book never reads from the scored `ScrapeItem` data the scheduler is producing. Fix: see §4.3.

**Bug D: agent chain runs sequentially with no concurrency control or persistence of intermediate outputs.**
File: `apps/api/runner.py`. `run_agent_chain` iterates 11 agents in series, each one a streaming Claude call, and the loop streams updates to a single in-memory `asyncio.Queue` keyed by `session_id`. If the SSE consumer disconnects, the run continues but the user sees nothing. If the server restarts mid-run, all state is lost. Each agent gets the previous agent's full output as input — fine for v1, but no agent ever has access to the **brief** or the **original user prompt** after step 0. By step 5, the system is summarizing summaries. This is why output quality will drift from voice over a long chain.

**Bug E: `chat.py` imports `execute_playbook` from `services.generation` but the chat router and the runner are using two different agent-orchestration paths.**
The Chat path (`/api/chat/generate`) goes through `services.generation.execute_playbook`. The Sessions path (`/api/sessions/{id}/run`) goes through `runner.run_agent_chain`. These two functions implement the same conceptual workflow with different prompt-assembly logic, different model calls, and different output shapes. **Pick one.** The `services.generation.execute_playbook` path is the better foundation: it composes from `core/` docs, the orchestrator, and named context layers. The `runner.py` path is older. Migrate `/api/sessions/{id}/run` to call `execute_playbook` and delete `runner.py`'s `run_agent_chain`.

### 2.2 Architecture misalignments

**Misalignment 1: `AgentSession` model duplicates `Deliverable` + `Brief` + `ChatSession`.**
`AgentSession` has `title`, `type`, `audience`, `description`, `status`, `current_agent`, `progress`, `output` — all fields that should be split across `Brief` (for the input), `Deliverable` (for the output), and a new `PipelineRun` row (for the in-flight execution state). Right now an "agent session" is doing three jobs and that's why the Sessions UI doesn't compose with Projects/Folders. **Fix:** rename `AgentSession` → `PipelineRun`, link it to `brief_id` and `deliverable_id`, and let it carry only execution state (status, current_agent, progress, started_at, completed_at, error). The `output` lives on the `Deliverable`, not on the run.

**Misalignment 2: Sidebar doesn't expose Folders or Deliverables.**
`apps/web/src/components/Sidebar.tsx` shows top-level Projects only, with a click-through to `/projects/[id]`. The architecture supports nested folders and content-type-organized deliverables (Market Research → Series X funding news → Blogs/emails/press releases), but there's no UI for it. The Sidebar needs to become a real tree.

**Misalignment 3: No WYSIWYG editor over the markdown engine.**
`MarkdownEditor.tsx` exists as a single component. The Settings page should be a tree view of `context/`, `core/`, `skills/`, `playbooks/`, `rubrics/` with that editor in the right pane and explicit save (these files are load-bearing — autosave is wrong). Currently no such surface exists.

**Misalignment 4: No toggles panel.**
The brief-first flow, voice selector, audience field, skills multi-select, playbook selector, and content type are all defined in `chat.py` (`ChatRequest.toggles: dict`) but there is no UI to set them. Everything is implicit defaults. The right rail of the workspace doesn't exist.

**Misalignment 5: No streaming-to-UI for chat.**
`apps/web/src/lib/api.ts` has `streamChat()` using fetch + ReadableStream, but no page consumes it. The chat surface in the workspace is missing entirely. The Sessions page has streaming, but it's the pipeline-mode streaming, not chat.

**Misalignment 6: Empty-state copy is misleading.**
The screenshot shows "Start the local API to load your briefing feed." — but the API may already be running; the issue is that the briefing router isn't registered (Bug A). Even after Bug A is fixed, the Briefing Book is reading from a separate scraper than the Intelligence page does. Users will get two different feeds in two different surfaces with no explanation of why.

### 2.3 Context audit — files exist but are thin

| File | Size | State |
|---|---|---|
| `context/00_orchestration/forgeos-context-orchestrator.md` | 2 KB | populated (skinny but real) |
| `context/02_narrative/messaging-framework.md` | 1.4 KB | thin — needs ~10x to be useful |
| `context/02_narrative/competitive-pov.md` | 0.9 KB | thin |
| `context/02_narrative/campaign-messaging.md` | 0.7 KB | thin |
| `context/03_strategy/ar-strategy.md` | 0.9 KB | thin |
| `context/04_execution/post-launch-framework.md` | 0.9 KB | thin |
| `core/VOICE.md` | 9.8 KB | populated |
| `core/STYLE_GUIDE.md` | 1.6 KB | populated |
| `core/CLAIMS_POLICY.md` | 2.1 KB | populated |
| `skills/` (22 SKILL.md files) | — | populated |

**Reading:** the engine has voice and style nailed, but messaging/positioning/competitive POV are placeholder-scale. PMM-lead and competitive-intelligence skills will produce generic output until those grow. **This is not a v1 software fix** — Aaron flagged this is intentional for now. Listed here so the system doesn't pretend it's solved.

### 2.4 Things working better than I expected

- The 11-skill chain in `runner.py` is well-structured and the SKILL.md library is real.
- `services/file_engine.py` cleanly abstracts reading the markdown engine — this is the right shape.
- `/api/chat/brief` and `/api/chat/generate` properly compose `core/` + orchestrator + named skills + named context layers + selected scrape items into the system prompt. This is the architecturally correct path; it just needs UI.
- The intelligence scoring service (`services/scoring.py`) reads its scoring prompt from `context/07_research/intelligence-scoring-prompt.md` per the spec — a context layer Aaron can edit from the UI.
- Arize instrumentation is wired in `instrumentation.py`. ForgeOS is dogfooding Arize on itself, which is exactly right for a content system being built by the AR/comms head at Arize.
- Frontend has SWR + React Query installed (overkill — pick one, see §4) but the data-fetching foundations are sound.
- `apps/web/src/lib/api.ts` is a single typed client that mirrors the backend surface. Keep it.

---

## 3. Product principles (these decide trade-offs)

1. **Markdown engine is canonical.** The app never owns voice/skills/playbook truth. SQLite holds runtime state, never doctrine.
2. **Two run modes, clearly named.** Chat mode (interactive, brief-first by default) and Pipeline mode (one-shot full chain). Both stay. The UI never blurs them.
3. **Explicit save on doctrine files.** Anything in `core/`, `context/`, `skills/`, `playbooks/`, `rubrics/` requires a deliberate save click. Drafts and chat messages autosave.
4. **Free-tier today; paid-tier interfaces stubbed.** HN Algolia, Reddit JSON, GitHub API, arXiv RSS, generic RSS — all working. X and broad web search — adapter interface in the codebase, returns empty, swap-in path documented.
5. **Loading, empty, error — never spinners-as-default.** Every async surface needs all three. The current "Start the local API" copy is misleading; replace with diagnostic empty states that distinguish API-down vs. data-empty vs. server-error.
6. **Honest scope boundaries.** Calendar, reminders, Slack/Gmail/HubSpot integrations are v2. They render as deliberate "coming soon" cards in Settings, not broken buttons.

---

## 4. v1 — must-fix scope (this is what the next session ships)

This section is what gets done in the next Copilot CLI session. Nothing here is optional. Anything not listed here is v2.

### 4.1 Fix the showstopper bugs

- Register `briefing` and `sessions` routers in `apps/api/main.py`.
- Add `MODEL_GENERATION` and `MODEL_SCORING` to `apps/api/config.py`. Replace every hardcoded model string in `runner.py`, `routers/briefing.py`, `services/generation.py`, `services/scoring.py`.
- Verify `apps/api/.env.example` exposes both model names so they can be overridden without code changes.
- Add a `/api/health` ping in the frontend's `api.ts` and make the offline detection use it. The Briefing Book and other surfaces should distinguish "API unreachable" from "API up, no data yet" from "API errored on this call."

### 4.2 Unify the agent execution path

- Migrate `routers/sessions.py::run_session` to call `services.generation.execute_playbook` instead of `runner.run_agent_chain`.
- Delete `apps/api/runner.py` once nothing references it.
- In `services/generation.py::execute_playbook`, ensure each agent in the chain receives both:
  - the original brief (canonical source of truth for the run), and
  - the previous agent's output (the working draft).
  Not just the working draft. This fixes the "summarizing summaries" drift.
- Persist intermediate outputs per agent step into a new `pipeline_step` table so a refresh mid-run shows real progress, and so we can later analyze which agents add value vs. rubber-stamp. Schema: `id, pipeline_run_id, agent_name, input_text, output_text, started_at, completed_at, tokens_used`.

### 4.3 Unify the intelligence pipeline

- Make `/api/briefing` read from `ScrapeItem` (the scored, scheduled-scrape source of truth) instead of running its own ad-hoc scrapers.
- The "Briefing Book" on the dashboard becomes a curated/synthesized **view** of `ScrapeItem` rows scored ≥ 7 from the last 24 hours, presented with `why_relevant` and `content_angle` fields. The synthesis pass (Claude editorial-director-style call that produced those fields in the old `briefing.py`) moves to a post-scrape job in `services/scoring.py` so it runs once per scrape, not once per dashboard load.
- The Intelligence page becomes the **full feed** view of all scored items, with filters.
- One source of truth, two views. Delete the duplicate scraper code in `routers/briefing.py`.
- Add a "Refresh now" button on both surfaces that calls `/api/intelligence/scrape` (already exists) and shows progress.

### 4.4 Refactor `AgentSession` → `PipelineRun`

- Rename the model. Migrate the table.
- Add `brief_id` (FK to Brief) and `deliverable_id` (FK to Deliverable, nullable until the run completes).
- Drop `output` from this table; the output lives on the `Deliverable` row.
- Update `routers/sessions.py` to create the Brief + Deliverable + PipelineRun together when a run is initiated.
- Update the Sessions UI to show this triplet correctly: which brief drove this run, which deliverable it produced, what its execution state is.

### 4.5 Build the Workspace surface (the missing primary UI)

This is the biggest single UI gap. Create `/workspace/[deliverableId]` route with a three-pane layout:

- **Left pane: Project tree.** Real tree, not a flat list. Projects → Folders → Subfolders → Deliverables. Deliverables show a content-type lozenge (blog, email, press release, etc.) and a status dot. Right-click for new project / new folder / new deliverable. Search at top. Keyboard navigation (arrow keys, Enter to open).
- **Center pane: tabs for Chat, Editor, Brief.**
  - Chat: streaming Claude responses via `streamChat`, message history rendered with markdown and code blocks, references to skills/playbooks rendered as clickable chips. Cmd+Enter to send.
  - Editor: TipTap WYSIWYG over `Deliverable.body_md` with markdown round-trip. Explicit save button.
  - Brief: the structured brief that produced (or will produce) this deliverable. Editable inline. Saves to the `Brief` row.
- **Right pane: Toggles panel.** brief_first toggle (default on), audience text field, voice selector (opinionated/thoughtful/objective/technical/founder), skills multi-select with "auto" default, playbook selector with "auto" default, content type selector. Below the toggles: "Context in use" panel showing which context layers, skills, and intelligence items are composed into the current prompt. Each is removable with one click.

**Note on TipTap:** the package isn't yet installed. Add `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-placeholder`, and a markdown serializer (`@tiptap/extension-markdown` if available, otherwise wire `marked` + `turndown`).

### 4.6 Build the Settings/Engine editor

`/settings` becomes a tree view:

- Tree on left: `core/` files, `context/` layers (by subdirectory), `skills/` (by category), `playbooks/`, `rubrics/`.
- Editor on right: WYSIWYG markdown editor with a structured frontmatter panel above the body for files that have frontmatter (most SKILL.md files do).
- Above the editor, a "this file is referenced by N skills and M playbooks" indicator. Compute by simple grep across the markdown engine on file open.
- Save is explicit. Unsaved changes warning on navigate-away.
- Below the engine tree, a Settings tab with: scrape sources config (subreddits, RSS feeds, keywords, GitHub topics, scoring prompt link), API keys (read from .env, never written from UI), integrations stubs (Slack, Gmail, HubSpot — explicitly "v2, coming soon" cards).

### 4.7 Frontend cleanup

- **Pick one of SWR or React Query and remove the other.** Both are installed. React Query is more idiomatic for the mutation patterns this app needs. Remove SWR.
- Replace `prompt()` usage in `Sidebar.tsx` with a proper modal.
- Add a real loading state to the Sidebar tree (currently flashes empty then populates).
- Every async surface gets loading + empty + error states. No exceptions.

### 4.8 Documentation

Update the root `README.md` to reflect the new architecture (it currently still says `mktg-agents` and references the old top-level layout). Document:

- How to run `apps/api` and `apps/web`.
- How the markdown engine relates to the app and which directories are doctrine vs. runtime state.
- The two run modes (Chat vs. Pipeline) and when to use each.
- The scrape schedule and how to edit sources.
- The empty-template context layers Aaron is intentionally leaving for later.

---

## 5. v2 — explicitly scoped, not built today

These are real items on the roadmap. The next session does not touch them. They render as visual stubs in the UI where applicable so the design accommodates them.

- **Calendar / pipeline view (Airtable-style).** Multi-day view with drag-to-reschedule, status flow, dependencies. Hangs off the existing `Deliverable.status` and a new `due_date` column.
- **Reminders.** Hangs off the calendar. Local notifications first; Slack/email later.
- **Slack integration.** OAuth flow, channel selection, post-on-publish, mention-on-mention.
- **Gmail integration.** OAuth, draft creation for outreach, send-from-app.
- **HubSpot integration.** Contact sync for AR contacts, deal-stage triggers for content distribution.
- **Twitter/X scraper.** Real implementation (paid API or paid scraper). Adapter interface exists today.
- **Broad web search.** Exa or Brave or SerpAPI. Adapter interface exists today.
- **Multi-user.** Auth middleware (Auth0 or Supabase). The DB already has `user_id` columns.
- **Performance feedback loop.** GA4/UTM ingestion → which content performed → fed back into a `learnings/` markdown layer that becomes part of the composed system prompt.
- **Pipeline step instrumentation viewer.** Surface the `pipeline_step` table from §4.2 as a debug view: which agents added value, which rubber-stamped, average tokens per step, error rates. Useful for pruning the chain over time.
- **Repurposer batch view.** Take a deliverable and fan it out to N social formats in one shot.
- **Export.** Word, Google Docs, Notion, raw markdown.

---

## 6. Naming and copy decisions to lock in

The app currently mixes "Sessions," "Briefing Book," "Intelligence," "Agent Team," and "Marketing Command Center" in inconsistent ways. Lock these in:

- **Workspace** — primary UI for chat + editor + brief over a single deliverable.
- **Pipeline run** — one-shot agent chain execution (was: "Sessions"). Sidebar item: "Pipelines."
- **Intelligence** — full scored scrape feed.
- **Briefing** — top-of-dashboard curated view of high-score items from the last 24 hours.
- **Engine** — the markdown doctrine (core/, context/, skills/, playbooks/, rubrics/). Settings tab: "Engine."
- **Project / Folder / Deliverable** — the org structure.
- **Brief** — the structured intake document that drives a deliverable.

Update all UI copy, route names, and table names to match.

---

## 7. Acceptance criteria for the v1 fix session

The session is done when all of these are true:

1. `/api/health` returns 200. `/api/briefing` and `/api/sessions` return 200 (not 404).
2. Dashboard's Briefing Book renders real items from the scored `ScrapeItem` table within 3 seconds of page load. No "Start the local API" message when the API is up.
3. Intelligence page renders the full scored feed with working dismiss / use-as-context / save filters.
4. A user can: create a project, create a folder under it, create a sub-folder, create a deliverable in that sub-folder, open the workspace for that deliverable, set toggles in the right rail, send a chat message, see streaming response, save a draft to the editor.
5. A user can run a pipeline from the workspace's brief → deliverable, see streaming progress with which agent is active and at what percentage, see the final draft land in the editor.
6. Settings/Engine page renders the markdown engine as a tree, opens any file in the WYSIWYG editor, saves changes back to disk, and the change is reflected on next chat (no restart required — the file engine watcher already supports this).
7. Two integration stubs (Slack and Gmail) render as "v2, coming soon" cards. No broken buttons anywhere.
8. The two run modes (Chat and Pipeline) are clearly distinguished in the UI per §6.
9. `apps/api/runner.py` is deleted. All agent execution goes through `services/generation.py`.
10. `package.json` no longer includes both SWR and React Query.
11. The README at repo root documents the new architecture and run instructions.
12. `pytest` (if any tests are added) and `ruff`/`black` pass on the API. `next lint` passes on the web app.

If any of these is not true, the session is not done.

---

## 8. Out of scope for this PRD

- New skills, new playbooks, new context layers, new rubrics. The engine is sufficient for v1.
- Any model other than Claude (no OpenAI fallback, no local model).
- Any deployment beyond `localhost`. Web deployment is a v2 concern.
- Any auth. Single-user, hardcoded `user_id="aaron"`.
- Mobile responsiveness beyond "doesn't break." The cockpit is a desktop-first product.
