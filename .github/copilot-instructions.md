# Copilot Instructions for mktg-agents

This repo is an AI-native editorial operating system for Arize AI's content, developer marketing, communications, and analyst relations work. Read this file before doing anything else.

---

## Who you are working for

**Aaron Winston** — Head of content, comms, AR, and developer marketing at Arize AI. Former GitHub (5 years), where he led the GitHub Blog, Octoverse, and how GitHub talked about AI to developers. He is a technical storyteller and developer marketing insider. He writes for smart developers, not for general audiences.

---

## What this repo produces

- Developer blog posts and technical explainers
- Product launch copy
- Analyst relations responses
- Case studies and customer stories
- Founder-led social content
- SEO briefs
- Lifecycle emails
- Research summaries
- Campaign messaging
- Repurposed and distributed assets

---

## How to orient yourself every session

Before doing any writing work, read these files:

1. `core/VOICE.md` — Aaron's voice and style. This is the source of truth.
2. `core/STYLE_GUIDE.md` — Specific rules and banned language.
3. `core/CLAIMS_POLICY.md` — What claims require sourcing, legal review, or caution.
4. `core/CONTEXT.md` — Arize AI product knowledge, terminology, key narratives.
5. `skills/README.md` — Index of all available skills.

Then check the `context/` directory for curated files relevant to the task:

- `context/my-writing/` — Aaron's published writing. Read before drafting anything in his voice.
- `context/arize/` — Internal product knowledge. Read before writing about any Arize product or feature.
- `context/audience/` — ICP and persona docs. Read to calibrate technical depth and tone.
- `context/approved-messaging/` — Locked copy. Pull exact phrasing from here instead of generating new variants.
- `context/research/` — Source material. Use when the task involves citing, summarizing, or referencing external work.

See `context/README.md` for the full guide on what each folder contains and how to use it.

---

## Default behavior rules

### Always
- Follow `core/VOICE.md` exactly. Match Aaron's voice — technical, narrative-first, people-centered.
- Use `core/CLAIMS_POLICY.md` before asserting any performance claim, competitive claim, or customer outcome.
- Reference `core/CONTEXT.md` for all Arize AI product details. Do not guess at product names, features, or positioning.
- Suggest the right playbook from `playbooks/` if asked to produce a content type.
- Score drafts against the relevant rubric before calling them done.
- Be specific. Real names, real numbers, real workflow steps — not abstractions.

### Never
- Use banned words: unlock, unleash, revolutionary, game-changing, seamless, next-generation, leverage, utilize, cutting-edge, transformative, powerful, robust, excited to announce, thrilled to share, delighted.
- Use em dashes.
- Write marketing copy that talks about AI like it's magic.
- Make competitive claims without citation.
- Make performance or outcome claims without sourcing.
- Write in passive voice unless Aaron explicitly signals a formal context.
- Add fluff sentences that don't add information.
- Start body paragraphs with "In today's world" or "In the rapidly evolving landscape."

### For developer content specifically
- Write for AI engineers, ML engineers, and developers building with LLMs — not for business executives.
- Explain what the product actually does, step by step.
- Use code examples where relevant.
- Acknowledge complexity — don't oversimplify.
- Reference `core/DEVELOPER_FLUENCY.md` for technical depth standards.

---

## Skill selection guide

If someone gives you a task, recommend or use the appropriate skill:

| Task | Skill |
|------|-------|
| Evaluate angle, narrative, or strategy | `skills/editorial/editorial-director` |
| Draft developer blog or explainer | `skills/foundation/dev-copywriter` |
| Technical accuracy review | `skills/specialization/technical-fact-checker` |
| SEO brief or keyword strategy | `skills/specialization/seo-strategist` |
| Launch copy or PR | `skills/specialization/launch-comms-writer` |
| Social posts from a draft | `skills/specialization/social-editor` |
| Analyst response or brief | `skills/specialization/analyst-relations-writer` |
| Customer story | `skills/specialization/customer-story-producer` |
| Executive quote or comms | `skills/specialization/executive-comms-writer` |
| Lifecycle email | `skills/specialization/lifecycle-email-writer` |
| Repurpose a piece for other channels | `skills/specialization/content-repurposer` |
| Check claims risk | `skills/quality/claims-risk-reviewer` |
| Final readiness check | `skills/quality/final-publish-reviewer` |
| Daily AI research summary | `skills/foundation/ai-researcher` |

---

## Workflow shorthand

For a blog post:
```
brief → editorial-director → dev-copywriter → dev-reviewer → technical-fact-checker → seo-strategist → copy-chief → claims-risk-reviewer → final-publish-reviewer → social-editor
```

For a product launch:
```
brief → editorial-director → launch-comms-writer → dev-reviewer → technical-fact-checker → claims-risk-reviewer → copy-chief → final-publish-reviewer → social-editor → content-repurposer
```

For an analyst response:
```
brief → editorial-director → analyst-relations-writer → technical-fact-checker → claims-risk-reviewer → executive-comms-writer → final-publish-reviewer
```

Full playbooks are in `playbooks/`.

---

## Quality bar

A draft is not done until it passes:
- `rubrics/editorial-quality.md`
- `rubrics/technical-accuracy.md`
- `rubrics/developer-fluency.md` (for dev-facing content)
- `rubrics/brand-fit.md`

Run `scripts/run_editorial_check.py [file]` to check a draft.

---

## Adding new samples

Aaron's writing samples live in `examples/excellent/`. When new published work is added, it becomes part of the voice reference for all writing tasks. Reference those files when calibrating tone and structure.

---

## Repo validation

```bash
python3 scripts/validate_repo_structure.py
python3 scripts/lint_skill_files.py
python3 scripts/generate_skill_index.py
```
