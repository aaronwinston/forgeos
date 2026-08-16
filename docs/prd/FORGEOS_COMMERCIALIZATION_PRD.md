# ForgeOS — commercialization PRD

**Owner:** Aaron Winston
**Status:** post-phase-1 plan — everything required to take ForgeOS from solo tool to product
**Constraint:** $0 in recurring subscriptions. Free APIs only. Three agent runtimes: Anthropic SDK, OpenAI (API + Codex CLI), GitHub Copilot SDK.
**Companion to:** `FORGEOS_PRD.md` (phase 1 — repair, must ship first)
**Last updated:** 2026-04-26

This PRD supersedes `FORGEOS_PHASE_PLAN.md` and adds everything required to charge money: auth, billing, multi-tenancy, onboarding, support, and the legal/operational layer. It assumes phase 1 has shipped and the acceptance criteria in `FORGEOS_PRD.md` §7 are green.

The PRD is organized into **modules**, not phases. Each module is independently shippable. They are sequenced in recommended build order. The dependency graph is in §1 so parallel work is possible.

---

## 0. Product positioning

**What ForgeOS is:** a marketing operating system for AI-native developer tools companies. The cockpit a head of content/PMM/comms uses to run their function — daily intelligence, brief-driven production, calendar, search insight, voice governance — all in one place.

**ICP:** heads of content/PMM/comms at Series A–C developer tools companies (AI infra, LLM ops, agent platforms, dev observability). 50–500 person companies. Selling to engineers. Currently running their function on Notion + Airtable + Google Docs + a half-dozen Chrome tabs.

**Wedge:** every output has a point of view because the system is grounded in your voice, your messaging, your competitive POV. Not a generic AI writing tool. A house-style enforcer with eyes on the world.

**Pricing (shipped at v1 launch, not deferred):**

| Tier | Price | What's included |
|---|---|---|
| Free | $0 | 1 user, 1 project, BYO Anthropic key required, 7-day briefing history, no integrations, ForgeOS branding on shareables |
| Pro | $49/user/mo | Unlimited projects, full briefing history, all integrations, BYO keys for any/all of Anthropic + OpenAI + Copilot SDK, custom branding on shareables |
| Team | $99/user/mo, 3-user min | Pro + shared engine across team, multi-user collab, role-based access, audit log, priority support, SSO |

**The BYO-keys-from-day-one model is what makes "$0 subscription budget" compatible with "I want to charge money."** ForgeOS never pays for LLM tokens. Users pay their providers directly. ForgeOS charges for the cockpit, the engine, the integrations, the orchestration. This is unusual and it is correct for this product. See §8.

All three tiers ship simultaneously at launch. The free tier's job is acquisition; the paid tiers are the business.

---

## 1. Module dependency graph

```
M1: Auth & multi-tenancy ─┬─> M2: Billing & metering ─┐
                          │                            │
                          ├─> M3: Onboarding flow ─────┤
                          │                            │
                          ├─> M4: Engine doctrine ─────┤
                          │                            ├─> Public launch
                          ├─> M5: Mission control ─────┤
                          │   (subsumes phase 2)       │
                          │                            │
                          ├─> M6: Calendar (phase 3) ──┤
                          │                            │
                          ├─> M7: Search intel (ph 4)──┤
                          │                            │
                          ├─> M8: Multi-runtime ───────┤
                          │                            │
                          └─> M9: Trust & support ─────┘
```

M1 unblocks everything. M2 and M9 are launch-blockers. M3–M8 can be built in parallel after M1 lands. Order below is the recommended single-developer sequence.

---

## 2. M1 — auth and multi-tenancy

### 2.1 What it does

Turns ForgeOS from a single-user local app into a multi-tenant web app where every row belongs to an organization, and every user belongs to one or more organizations.

### 2.2 Tech choices (all free)

- **Auth provider:** Clerk (free up to 10,000 MAU) for email/password, Google OAuth, GitHub OAuth, magic links, MFA. Drop-in Next.js integration. SOC 2 Type II compliant out of the box, which matters for §9.
- **Why not Supabase Auth or Auth0:** Supabase free tier caps at 50K MAU but bundles a database we don't need. Auth0 free tier is 7,500 MAU but its DX for Next.js is worse. Clerk wins on both axes.
- **Why not roll our own:** rolling auth is the single most common reason a B2B SaaS ships compromised. Don't.

### 2.3 Data model changes

Add to schema:

- `organization` — `id, name, slug, created_at, plan (free|pro|team), trial_ends_at`
- `membership` — `id, user_id, organization_id, role (owner|admin|member), created_at`
- Every existing table (`project`, `folder`, `deliverable`, `brief`, `chat_session`, `chat_message`, `scrape_item`, `pipeline_run`, `pipeline_step`, `calendar_event`, `gsc_query`, `trends_data`, `search_insight`) gets an `organization_id` foreign key and an index on it. Every query is scoped to the current org.
- The hardcoded `user_id="aaron"` from phase 1 is removed. Auth middleware injects the real `user_id` and `organization_id` from the Clerk session.

### 2.4 Tenant isolation

- Every `SELECT` query in every router gets `WHERE organization_id = :current_org_id`. Build this into the `get_session` dependency — it returns a session that auto-filters by org.
- Cross-tenant data exposure is the single worst bug class for B2B SaaS. Add a row-level test fixture: create two orgs, two users, attempt to read across orgs, assert 404. Run on every PR.

### 2.5 Org switcher UI

- Top-left of the sidebar: org name + dropdown. Dropdown shows all orgs the user is a member of, plus "Create new organization."
- Switching orgs reloads the entire app state. No bleed.

### 2.6 Acceptance criteria

1. New user signs up with email or Google in <30 seconds.
2. New user gets a default organization on signup, slug derived from email domain.
3. User can be in multiple organizations and switch between them.
4. User in org A cannot read, write, or even enumerate any data from org B. Verified by integration test.
5. The hardcoded `aaron` user is deleted from the codebase.

---

## 3. M2 — billing and metering

### 3.1 What it does

Charges users money. Tracks LLM usage. Enforces tier limits.

### 3.2 Tech choices (all free to start)

- **Stripe:** the only real choice. Free to integrate, takes 2.9% + 30¢ per transaction. No monthly fee. Use Stripe Checkout for new subscriptions and Stripe Customer Portal for self-serve plan management — both are hosted by Stripe, so we don't build payment forms.
- **Webhooks:** Stripe webhooks to a `/api/billing/webhook` endpoint. Sync subscription state into our `organization.plan` field on every event.

### 3.3 Data model changes

- `organization` gets: `stripe_customer_id`, `stripe_subscription_id`, `subscription_status (active|past_due|canceled|trialing)`, `current_period_end`.
- New table `usage_event` — `id, organization_id, user_id, event_type, tokens_input, tokens_output, runtime (anthropic|openai|copilot), cost_usd_estimate, occurred_at`. Every LLM call writes one row. Used for metering, not billing — see §3.5 on the BYO-keys model.
- New table `feature_flag` — `id, organization_id, flag_name, enabled, expires_at`. Used to gate features per org during rollout, not for tier enforcement.

### 3.4 Tier enforcement

Tier checks live in a single `apps/api/services/entitlements.py` module:

```python
def check_entitlement(org: Organization, feature: str) -> EntitlementCheck:
    # returns allowed: bool, reason: str, upgrade_path: str
```

Every router that gates a feature calls this. Features gated:

- `unlimited_projects` (free: 1, pro/team: unlimited)
- `briefing_history_days` (free: 7, pro/team: unlimited)
- `integrations.calendar` (pro/team only)
- `integrations.gsc` (pro/team only)
- `multi_runtime` (pro/team only — free is Anthropic only)
- `team_features` (team only — shared engine, audit log, SSO)

When a free user hits a paywall, the UI shows a contextual upgrade prompt with a one-click "upgrade to Pro" that drops them in Stripe Checkout.

### 3.5 The BYO-keys model

This is the entire reason ForgeOS can be a $0-cost-of-goods business.

- Every user adds their own Anthropic, OpenAI, and Copilot SDK keys in Settings → Runtimes.
- Keys are encrypted at rest using AES-256-GCM with a key from `LLM_KEY_ENCRYPTION_SECRET` env var. Stored in a `runtime_credential` table per organization (per user on Free, per org on Pro/Team).
- Every LLM call uses the user's key. ForgeOS never holds a master key.
- Free tier requires at minimum an Anthropic key. The signup flow asks for it before letting the user run their first session.
- Pro/Team tiers can add OpenAI and Copilot SDK keys to enable multi-runtime routing (M8).

The `usage_event` table is for the user's transparency (we show them their estimated spend per provider per month) and for our analytics — not for billing them. Stripe charges the flat per-seat subscription. Whatever they spend on tokens is between them and the provider.

This model has tradeoffs. It is the right one for $0 budget. Not opining further per your instruction.

### 3.6 Free trial

- 14-day Pro trial on signup, no credit card required. After 14 days, drop to Free unless they upgrade.
- Trial state is stored on `organization.trial_ends_at`. Entitlements check honors trial.

### 3.7 Acceptance criteria

1. User can upgrade Free → Pro in Stripe Checkout in <60 seconds.
2. Subscription cancellations downgrade the org within 5 minutes of the webhook.
3. Past-due subscriptions show a banner but don't immediately revoke access (7-day grace).
4. Every LLM call writes a `usage_event` row with token counts and cost estimate.
5. Settings → Usage page shows real-time spend per runtime per month, broken down per project.
6. Team plan enforces 3-user minimum at checkout and at member-add time.

---

## 4. M3 — onboarding flow

### 4.1 What it does

Takes a new user from signup to first usable session in under 5 minutes. The onboarding sets up the engine, not just the account.

### 4.2 The flow

1. **Signup** (Clerk) — email + password or Google.
2. **Org bootstrap** — name your company, pick a slug. We pre-fill from the email domain.
3. **The engine setup wizard** — this is the key step most onboardings skip and it's why most AI writing tools produce slop:
   - "Tell us about your company" — paste a one-paragraph elevator pitch. We extract messaging pillars via Claude and write `context/02_narrative/messaging-framework.md`.
   - "Upload your existing voice" — drop 3–5 examples of writing you want the system to match (links, PDFs, or pasted text). We analyze and seed `core/VOICE.md`.
   - "Who do you compete with?" — list 3–5 competitors with one-line takes on each. We seed `context/02_narrative/competitive-pov.md`.
   - "What do you absolutely not say?" — anti-claims, banned phrases, regulated topics. Seeds `core/CLAIMS_POLICY.md`.
   - At every step there's a "skip for now, I'll fill this in later" button that uses sensible defaults. The system works without these but works dramatically better with them.
4. **Connect your runtime** — paste at least an Anthropic key. The signup is not complete until this is done. Validate the key with a single low-cost test call before saving.
5. **Pick a starter project** — three templates: "Product launch," "Weekly newsletter," "AR program." Each creates a project with relevant folders and a sample brief. Or skip and start from blank.
6. **Land in dashboard** — first briefing is generating in the background. Show a progress indicator: "Analyzing your space — this takes about 90 seconds."

### 4.3 Re-onboarding

If a user signed up before doing the engine setup, the dashboard shows a persistent "complete your setup" widget until each step is done. Output quality is conditional on these being filled in, so the product itself motivates completion.

### 4.4 Acceptance criteria

1. Median time from signup to first briefing visible: <5 minutes.
2. Median time from signup to first deliverable shipped: <15 minutes.
3. Engine setup wizard can be completed at signup or returned to later without losing state.
4. Anthropic key is validated in real time before save.
5. User cannot reach the workspace without at least an Anthropic key configured.

---

## 5. M4 — engine doctrine

### 5.1 What it does

Productizes the markdown engine for non-Aaron users. The engine that's currently a power-user feature becomes the central differentiator.

### 5.2 What changes from phase 1

Phase 1's engine editor is a tree of files with a WYSIWYG editor. That's right for Aaron. It's wrong for a customer who has never seen this kind of system before.

For commercialization, the engine surface gains:

- **Engine health dashboard:** at the top of Settings → Engine, a panel showing what's populated, what's empty, and what's thin. Think of it like a "completeness score" but specific: "Your messaging framework is 280 words. Most teams' frameworks are 1,500–3,000 words for best results. [Edit messaging framework]"
- **Templates:** every empty file in `context/` and `core/` ships with a real template inside the file (commented out so it doesn't pollute prompts). The user opens the file and sees the structure they should fill in.
- **Examples library:** Settings → Engine → Examples shows three real (anonymized) populated engines from companies in the user's space. Clicking an example loads it into a sandbox where they can adapt it. We seed this with anonymized templates inspired by 5 real dev tools companies' public messaging (Vercel, Supabase, Linear, Sentry, Honeycomb-style — derived from public materials, not their internal docs).
- **Engine versioning:** every save to a doctrine file creates a version. Users can roll back. Implementation: a `doctrine_version` table — `id, organization_id, file_path, content_hash, content, saved_by_user_id, saved_at`. Old versions garbage-collected after 90 days.
- **Engine sharing (Team plan):** the engine is shared across the organization on Team plans. Edits are visible to all members with role-based permissions. Owners can lock specific files (e.g., VOICE.md) so only they can edit.

### 5.3 Skill marketplace (free)

- Settings → Engine → Skills → "Browse skills" shows community-shared skills.
- Aaron's existing 22 skills are seeded as the official starter set.
- Users can install/clone any skill into their engine. They can also fork and customize.
- Users can publish their own skills back to the marketplace (opt-in).
- This is `git`-like, not a database — every skill is a markdown file with frontmatter. Sharing is a Pull Request to a public github repo we host (`forgeos-skills`), reviewed by us before merge for v1, opened to community moderation later.
- This is free because it lives on GitHub and uses GitHub's hosting, not ours.

### 5.4 Acceptance criteria

1. New user opens the engine and immediately sees what's populated and what isn't.
2. Every empty doctrine file has a useful template inside.
3. Saving a doctrine file creates a version. Rolling back works.
4. On Team plans, engine edits are visible to all members in real time.
5. Users can install a skill from the marketplace in <30 seconds.

---

## 6. M5 — mission control

This module subsumes everything from `FORGEOS_PHASE_PLAN.md` phase 2 — the daily briefing, the "Let's build" guided flow, content strategy upload, sentence case, design polish — and adds what's required to make it commercially defensible.

### 6.1 The daily briefing (productized)

Phase 1 ships the briefing reading from `ScrapeItem`. This module makes it the killer feature.

- **Email digest:** every morning at 7am local time, send an email with the top 5 briefing items. Customers can disable. Free using Resend's free tier (3,000 emails/month, 100/day) or AWS SES (62,000 emails/month free if you stay in EC2; ForgeOS doesn't run on EC2 so use Resend).
- **Slack digest:** same content, posted to a Slack channel of the user's choice. Slack incoming webhook is free. Setup: paste a webhook URL in Settings → Notifications.
- **Briefing API:** `GET /api/briefing/today` returns JSON. Pro/Team can pull this into their own systems. Documented in §9.5.
- **Calibration:** users rate briefing items 👍/👎. The scoring prompt automatically adjusts based on aggregated feedback per organization (the prompt itself stays static, but a per-org "user preferences" addendum is appended to the scoring prompt and updated nightly).

### 6.2 The "Let's build" flow (commercial version)

Phase 2's guided + YOLO modes ship as specified. Commercial additions:

- **Brief library:** every brief is saved and searchable. Org-wide on Team plan.
- **Brief templates:** users can save a brief as a template. Picking a template pre-fills the guided flow.
- **Multi-deliverable from one brief:** after a brief is approved, the system asks "what do you want from this?" with checkboxes for blog, social, newsletter, press release, AR briefing, etc. It generates all selected outputs in parallel from the same brief, each through its own playbook. Critical for time-to-value.
- **Approval gates:** Team plan only. After the deliverable is generated, it enters a review state. Owners/admins approve before "publish ready" status. Notifications via Slack/email.

### 6.3 Content strategy upload (productized)

The phase 2 upload flow ships as specified. Commercial additions:

- **Bulk import:** drag-and-drop multiple files. The system uses Claude to classify each file (messaging? voice example? competitive intel? past content?) and routes to the right destination. User confirms before save.
- **Notion sync:** one-way sync from a Notion workspace into the engine. User connects Notion via OAuth (free), picks pages or a database, and ForgeOS pulls them as context layers. Resyncs daily.
- **Google Drive sync:** same as Notion, for Google Drive folders.

Both Notion and Google Drive integrations are free APIs. They're the most-requested integrations in this category and shipping both gates of "no, you don't have to leave your existing system."

### 6.4 Visual design (commercial bar)

Phase 2's design polish ships. Commercial bar additions:

- **Branded shareables:** when a user shares a deliverable preview link, it renders with their organization's logo and accent color (Pro/Team only). Free tier shows ForgeOS branding. Logo upload + color picker in Settings → Branding.
- **Dark/light theme respects system preference** by default, with manual override.
- **Print stylesheet** for deliverables — clean white background, black text, no chrome — so a "print to PDF" produces a usable document.
- **Mobile read-only view:** the workspace doesn't need to be editable on mobile, but the dashboard, briefing, and deliverable viewer should look right on a phone. Aaron will check the briefing from bed; commercial users will too.

### 6.5 Acceptance criteria

1. A user receives a useful email digest every morning. Open rates >40% within first month signal it's working.
2. The "Let's build" flow takes a user from blank intent to finished deliverable in <10 minutes for a typical blog post.
3. One brief produces 3–5 deliverable variants in parallel without re-prompting.
4. Bulk-import 10 files → all classified and routed correctly with one user confirmation.
5. Notion sync runs daily without user intervention after initial setup.
6. Branded shareable preview link renders the user's org branding correctly.

---

## 7. M6 — calendar

This module is `FORGEOS_PHASE_PLAN.md` phase 3 with multi-tenancy applied.

Everything in phase 3 ships as specified, with these commercial additions:

- **Per-org dedicated Google Calendar:** each org gets its own dedicated calendar in the connected Google account, named "ForgeOS — [org name]."
- **Tier gate:** integration is Pro/Team only. Free users see the calendar UI with a paywall.
- **Team calendar (Team plan):** all members see the same calendar. Per-event ownership controls who can edit.
- **iCal export:** every org's calendar has a public-but-unguessable iCal URL for read-only subscription from any calendar app. Useful for executives who want visibility but don't want to log in.
- **Conflict detection:** if a deliverable's `due_date` slips past the calendar event, surface a warning on the dashboard.

Acceptance criteria from phase 3 §3.5 plus: tier gate enforced, team calendar permissions verified by integration test, iCal feed is per-org and unguessable.

---

## 8. M7 — search intelligence

This module is `FORGEOS_PHASE_PLAN.md` phase 4 with multi-tenancy applied. All free.

Everything in phase 4 ships as specified. Commercial additions:

- **GSC integration is Pro/Team only.** Free users see a paywall.
- **Per-property tracking:** Pro can track one property. Team can track up to 10 (e.g., main domain + docs subdomain + each major product page).
- **Competitor tracking via free SERP scraping:** ForgeOS does daily lightweight SERP scrapes for the user's tracked queries against their declared competitors. Implementation: a single Playwright/Puppeteer instance pulling the top 10 results for ~50 queries/day per org, respecting Google's robots.txt and using human-paced timing. This stays under any single-org rate limit. At scale across many orgs we'd hit limits — at that point the scrape moves to a queue with multiple residential IPs (Bright Data has a free tier for low volume) or we punt to "your IP, your scraping" via a self-hosted scraper option for Team plans.
- **Twitter/X scraping via Codex CLI:** OpenAI's Codex CLI can drive a headless browser and execute scraping flows against X with login. Pro/Team users provide their own X account credentials (encrypted at rest, same vault as runtime keys), and ForgeOS uses Codex to drive the scrape on a schedule. This is the user's account, the user's session, the user's risk — same model as BYO LLM keys. The free path that wasn't possible without their account is possible with it.
- **Conversational pulse → keyword expansion:** for every conversational topic surfaced from social, ForgeOS uses Claude (paid by user's key) to generate 5–10 related search queries. These get added to GSC tracking automatically (Pro/Team) so the user starts seeing data on those queries within a week.

Acceptance criteria from phase 4 §4.6 plus: GSC tier gate, X scraping via Codex CLI works end-to-end, competitor SERP tracking populates daily.

---

## 9. M8 — multi-runtime

### 9.1 What it does

Three agent runtimes: Anthropic, OpenAI (API + Codex CLI), Copilot SDK. Per-skill routing. Per-skill model selection within each runtime. Cost transparency.

### 9.2 The runtime adapter

The phase 2 `apps/api/services/llm.py` adapter is extended:

```python
class RuntimeAdapter(Protocol):
    name: str  # "anthropic" | "openai" | "copilot"

    async def stream_message(
        self,
        system: str,
        messages: list[dict],
        model: str,
        max_tokens: int,
        tools: list[dict] = None,
    ) -> AsyncGenerator[StreamEvent, None]: ...

    def list_models(self) -> list[ModelInfo]:
        # returns models available with this runtime + their per-Mtok pricing
        ...

    def estimate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float: ...
```

Concrete implementations:

- **AnthropicAdapter:** wraps the Anthropic Python SDK. Models surfaced: Claude Opus 4.7, Claude Sonnet 4.6, Claude Haiku 4.5.
- **OpenAIAdapter:** wraps the OpenAI Python SDK for chat completions, plus a Codex CLI subprocess wrapper for agentic flows that need shell/file/browser access. Models surfaced for chat: GPT-5, GPT-5-mini, o3, o4-mini. The Codex CLI integration is exposed as a separate "agentic skill" type — see §9.4.
- **CopilotAdapter:** wraps the Copilot SDK. Surfaces Copilot's agentic runtime as an option for skills that benefit from Copilot's specific orchestration model — particularly the technical-fact-checker and dev-reviewer skills, which want code-aware reasoning.

### 9.3 Per-skill routing

Settings → Engine → Skills, each skill has a "Runtime configuration" panel:

- Default runtime: Anthropic
- Default model: Claude Opus 4.7 (for editorial agents) or Sonnet 4.6 (for utility agents) or Haiku 4.5 (for scoring)
- Override runtime: pick Anthropic / OpenAI / Copilot
- Override model: dynamic dropdown based on selected runtime

The runtime adapter's `list_models()` populates the model dropdown. ForgeOS doesn't hardcode model lists — when a provider releases a new model, it appears in the dropdown the next day.

When a runtime/model is selected for a skill, the system prompts the user during selection: "This will use [your OpenAI key]. Estimated cost per execution: $0.04. Continue?" The estimate uses average input/output tokens for that skill from historical `usage_event` data.

### 9.4 Codex CLI as an agentic runtime tier

Codex isn't just another model. It's a runtime that can drive shell commands, edit files, and execute multi-step agentic workflows. Within ForgeOS, certain skills can be marked as "agentic" — they execute via Codex CLI in a sandboxed subprocess instead of via a chat completion.

Use cases:

- **The competitive-intelligence skill** running a real scrape session: Codex CLI navigates a competitor's blog, downloads recent posts, summarizes positioning shifts, returns structured findings.
- **The technical-fact-checker skill** verifying a code claim: Codex CLI clones a repo mentioned in the brief, runs a reproduction, reports whether the claim holds.
- **The repurposer skill** taking a long-form deliverable and producing 12 social variants, written to disk and previewable in the workspace.

Implementation: ForgeOS spawns a `codex` subprocess with a constrained working directory (per-session sandbox), passes a structured task prompt, captures stdout/stderr, parses results back into the `pipeline_step` table. The user sees a "live agent" panel in the workspace showing what Codex is doing in real time.

Codex requires the user's OpenAI key. Same BYO model.

### 9.5 Copilot SDK for code-aware skills

Copilot SDK's agentic runtime is best-in-class for skills that reason about code. Three ForgeOS skills route to Copilot by default when a user has a Copilot SDK key:

- **technical-fact-checker** — verifies code samples, API references, version claims.
- **dev-reviewer** — checks technical accuracy of dev marketing copy.
- **example-curator** — finds the best public code examples to support a claim in a draft.

Implementation: Copilot SDK is wired through the `RuntimeAdapter` interface. The agentic flows are encoded as Copilot SDK agent definitions in `apps/api/services/copilot_agents/`. Users with a Copilot SDK key in their runtime credentials see these skills automatically upgrade to Copilot-powered. Without a key, they fall back to Claude.

### 9.6 Cost transparency

- Settings → Usage shows current month's spend per runtime per project per skill.
- Every chat message shows estimated cost in a small chip below the message: "$0.04 · Claude Opus 4.7."
- Every pipeline run shows total cost on completion.
- Monthly digest email includes spend summary.

### 9.7 Acceptance criteria

1. User can configure any of the 22 skills to run on any of the three runtimes.
2. Codex CLI subprocess execution works for at least 3 skills end-to-end.
3. Copilot SDK powers technical-fact-checker, dev-reviewer, and example-curator when a Copilot key is configured.
4. Cost estimates appear before every paid action and are within 15% of actual cost on average.
5. Settings → Usage shows accurate per-runtime spend.

---

## 10. M9 — trust and support

### 10.1 What it does

Everything required for a B2B buyer to actually pay.

### 10.2 Legal and policy

- **Terms of service.** Generated from a free template (Termly, GetTerms.io, or hand-rolled from open templates). Reviewed by a lawyer before launch — the only line item that costs money, but it's a one-time ~$500–1500 expense, not a subscription. Excluded from the $0 constraint per your instruction to do everything for free anyway, so: use Termly's free tier, accept the boilerplate is generic, plan to upgrade later.
- **Privacy policy.** Same model. Must specifically address: encryption at rest, BYO-keys handling (we never see plaintext keys after submission), data retention (90 days for soft-deleted, indefinite for active), data export rights (see §10.4), data deletion rights (see §10.4), subprocessor list (Clerk, Stripe, Resend, our cloud host).
- **DPA (data processing addendum).** Required for European customers. Standard template, customer-signed. Free templates exist.
- **Cookie policy and consent banner.** Required for European customers. Free via Cookiebot's free tier (up to 100 subpages) or self-rolled.
- **Acceptable use policy.** Defines what users can and can't do — no spam, no harassment, no IP infringement, no scraping at rates that violate target sites' ToS (relevant for §8's competitor scraping and X scraping).
- **AI disclosure.** Specifically: outputs are AI-generated, users are responsible for verifying claims, ForgeOS does not warrant accuracy. This is in the ToS and shown at signup.

### 10.3 Security baseline

- **Data encryption at rest:** all PII and all credentials encrypted via AES-256-GCM. Already specified for runtime credentials in M2; extend to email addresses and any uploaded content.
- **Data encryption in transit:** TLS 1.3 everywhere, HSTS headers, no HTTP fallback.
- **Audit log:** new table `audit_event` — `id, organization_id, user_id, action, resource_type, resource_id, ip_address, user_agent, occurred_at`. Logs every doctrine edit, every settings change, every credential add/remove, every member add/remove. Visible to admins on Team plan.
- **Session security:** Clerk handles sessions. Configure for 7-day idle timeout, require MFA for admin actions.
- **Vulnerability disclosure:** publish `/security` page with a contact email and our response SLA. Free.
- **Backups:** daily SQLite backups to S3 (we move off SQLite to Postgres for production — see §11). Restore tested monthly.

### 10.4 Data rights

- **Export:** `/api/export` returns a zip of all the org's data — markdown engine files, deliverables, briefs, calendar events, scrape items. Customers can leave with their data.
- **Deletion:** Settings → Danger Zone → "Delete organization" — soft-deletes for 30 days, then hard-deletes on a daily job. Email confirmation required.
- **Retention:** chat messages older than 1 year are auto-archived for Pro/Team, deleted for Free.

### 10.5 Support surfaces

- **In-app help:** every page has a help icon that opens contextual docs.
- **Documentation site:** `docs.forgeos.com` (or whatever the domain is). Static site built with Mintlify (free for open source, $150/mo for commercial — use a free alternative like Docusaurus, Astro Starlight, or Nextra for $0).
- **Support email:** `support@forgeos.com` routes to Aaron's inbox until volume justifies a help desk. Free.
- **Status page:** `status.forgeos.com` via UptimeRobot (free tier — 50 monitors, 5-minute checks). Public.
- **Changelog:** every meaningful release noted at `/changelog` in-app and on the marketing site.

### 10.6 Marketing site requirements

Outside this PRD's scope, but the app must support:

- Marketing-site signup CTA → app signup flow (Clerk handles this).
- Marketing-site demo content → an `/demo` route in the app showing a curated read-only example workspace.
- SEO-friendly public deliverable preview links — `/p/[slug]` renders a deliverable as a public page if the user enabled sharing.

### 10.7 Acceptance criteria

1. ToS, Privacy, DPA, Cookie, AUP, AI Disclosure all live and linked from signup, settings, and footer.
2. Audit log shows every doctrine edit, member change, and credential add for the last 90 days.
3. Customer can export all their data in one click and the export is valid (re-importable in dev).
4. Customer can delete their org with 30-day grace.
5. Status page is public and shows real uptime data.
6. `/security` page lives.

---

## 11. Production deployment

The current local-only architecture (FastAPI + SQLite + Next.js) needs to become deployable. All free.

### 11.1 Infrastructure choices

- **Frontend:** Vercel free tier. Plenty for v1 (100 GB bandwidth/month).
- **Backend:** Fly.io free tier (3 small VMs, 3GB persistent volume) or Railway free trial that converts to ~$5/mo — Fly is the $0 choice. Run the FastAPI app on Fly.
- **Database:** Postgres via Neon free tier (3 GB storage, no compute hour limit on the free plan as of 2026). Migrate from SQLite to Postgres on launch — SQLite doesn't survive serverless deploys reliably.
- **Object storage:** Cloudflare R2 free tier (10 GB storage, no egress fees) for uploaded content strategy docs, branded logos, doctrine version snapshots.
- **Background jobs:** the APScheduler approach from phase 1 doesn't survive serverless. Replace with a small dedicated job worker on Fly — same monorepo, different process. Free.
- **Queue:** for now, Postgres-backed via `pg-boss` or similar. No Redis. When volume justifies, move to Upstash Redis free tier.
- **Email:** Resend free tier (3,000/month, 100/day) for transactional + digests.
- **Logs and monitoring:** Sentry free tier (5K errors/month) for errors. Logfire free tier or stdout-to-Fly for app logs. UptimeRobot for uptime.
- **CDN:** Cloudflare free tier in front of everything. Free.

### 11.2 SQLite → Postgres migration

- Export current SQLite via SQLModel's metadata.
- Recreate schema in Postgres with appropriate type adjustments (TEXT → VARCHAR/TEXT, JSON columns → JSONB).
- One-time migration script for existing local data.
- Update `database.py` to use Postgres connection string. SQLModel handles the rest.

### 11.3 Domain and email

- Domain: register `forgeos.com` (or whatever's available). One-time ~$10–15/year. Excluded from $0 subscription budget by stretch.
- Email: Cloudflare Email Routing (free) for `support@`, `hello@`, etc. forwarding to Aaron's existing email. SPF/DKIM/DMARC set up via Cloudflare DNS.

### 11.4 Acceptance criteria

1. Production deploy of `apps/web` on Vercel succeeds. Build time <5 minutes.
2. Production deploy of `apps/api` on Fly succeeds. Worker process runs scheduled jobs.
3. Postgres migration runs cleanly. All phase-1 data survives.
4. Custom domain serves the app over HTTPS.
5. Status page reflects real uptime within 1 hour of deploy.

---

## 12. Launch criteria

ForgeOS is ready to take its first paying customer when **all** of these are true:

1. M1–M9 acceptance criteria are met.
2. 5 friends-and-family beta users have paid for Pro for at least 30 days each.
3. Day-30 retention of paid users >70%.
4. Median NPS from beta users >40.
5. Zero P0 bugs open. <10 P1 bugs.
6. Documentation covers every feature.
7. Status page shows >99% uptime over the prior 30 days.
8. Support email is responsive within 24 hours and below 10 open tickets.
9. The marketing site exists and has a functional signup flow.
10. Aaron has used ForgeOS as his daily driver for at least 60 days and has shipped >20 pieces of content through it.

#10 is the most important. If Aaron isn't dogfooding it daily, neither will paying customers.

---

## 13. Out of scope

- Mobile app (native iOS/Android). PWA is acceptable.
- Self-hosted/on-prem deployment. Cloud only.
- Real-time collaborative editing (Google-Docs-style). Multi-user works, but two people editing the same brief at the same time produces last-write-wins. Real CRDT-based collab is a v2 problem.
- White-label reseller. Pro and Team have branded shareables; full white-label (custom domain per customer, hide ForgeOS entirely) is v2.
- HIPAA, SOC 2 Type II, ISO 27001. Soft commitments to security practice, but no formal compliance. Required for enterprise — that's v2.
- Native HubSpot integration. Stays as a stub. v2.
- Native Salesforce integration. v2.
- Marketplace revenue share for skill creators. v2.

---

## 14. The order to actually build this

If this PRD looks like a lot, that's because it is. Here's the order:

1. **M1 (auth/multi-tenancy)** — week 1. Nothing else works without it.
2. **M2 (billing + BYO keys)** — week 2. The BYO keys part is what makes the rest financially viable.
3. **M9 (trust/legal + production deploy)** — week 3. Get the legal floor and the deployment story done before adding features. Boring but launch-blocking.
4. **M3 (onboarding)** — week 4. Now there's an app worth onboarding into.
5. **M4 (engine doctrine productized)** — week 5.
6. **M5 (mission control)** — weeks 6–7. The biggest module by surface area.
7. **M6 (calendar)** — week 8.
8. **M7 (search intel)** — week 9.
9. **M8 (multi-runtime)** — week 10.
10. **Beta** — weeks 11–14.
11. **Launch** — week 15.

15 weeks of focused weekend work is not a small lift. Adjust expectations accordingly.
