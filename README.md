Brought to you by LLMs and espresso. Buyer beware. 

# mktg-agents

`mktg-agents` is an AI-native editorial, content, communications, analyst relations, and developer marketing operating system.

It is designed for teams building technical content for developers, engineering leaders, AI builders, and enterprise buyers.

---

## What this repo is for

Use this repository to produce:

- Developer blog posts and technical explainers
- Product launch copy
- Partnership announcements
- Founder-led social posts
- Analyst relations responses
- Case study briefs
- Customer story outlines
- SEO content briefs
- Lifecycle emails
- Research briefings
- Campaign messaging
- Repurposed social and newsletter assets

---

## What this repo is not

This is not a generic content bot. This is not a prompt dump. This is not a replacement for product, engineering, legal, comms, or customer approval.

This repo is a structured system of specialized agents that work like a high-performing editorial team.

---

## Core idea

```
core       = shared standards
skills     = specialist agents
playbooks  = workflows
rubrics    = quality bar
```

Additional layers:

```
briefs     = intake
prompts    = reusable commands
examples   = training data
scripts    = automation
workflows  = repeatable execution
tests      = quality checks
```

---

## Recommended default workflow

For most developer-facing content:

```
brief
→ editorial-director
→ ai-researcher
→ dev-copywriter
→ dev-reviewer
→ technical-fact-checker
→ seo-strategist
→ copy-chief
→ claims-risk-reviewer
→ final-publish-reviewer
→ social-editor
→ content-ops-manager
```

---

## How to use this repo with Copilot CLI or Claude Code

### 1. Clone the repo

```bash
git clone https://github.com/aaronwinston/mktg-agents.git
cd mktg-agents
```

### 2. Ask your agent to orient itself

```
Read README.md, core/VOICE.md, core/STYLE_GUIDE.md, core/CONTENT_STRATEGY.md, and skills/README.md.
Explain how this repo is organized and recommend the right workflow for the task I give you next.
```

### 3. Start with a brief

```
Use briefs/blog-brief-template.md to create a complete content brief for a blog post about [topic].
Ask only for missing information that materially changes the strategy.
```

### 4. Run a playbook

```
Use playbooks/blog-production.md to produce this blog.
Follow the skill chain exactly.
Use core/VOICE.md, core/STYLE_GUIDE.md, core/CLAIMS_POLICY.md, and rubrics/developer-fluency.md as quality standards.
```

### 5. Call a specific skill

```
Use skills/editorial/editorial-director/SKILL.md to pressure-test this angle.
```

```
Use skills/specialization/technical-fact-checker/SKILL.md to review the technical claims in this draft.
```

```
Use skills/specialization/social-editor/SKILL.md to turn this blog into LinkedIn, X, and founder-led posts.
```

### 6. Run final quality review

```
Use skills/quality/final-publish-reviewer/SKILL.md and prompts/final-publish-check.md to review this asset for readiness.
```

---

## Skill categories

### Foundation
`ai-researcher` · `dev-copywriter` · `dev-reviewer` · `founder-x-recap`

### Editorial
`editorial-director` · `managing-editor` · `copy-chief` · `content-ops-manager`

### Specialization
`technical-fact-checker` · `seo-strategist` · `launch-comms-writer` · `social-editor` · `customer-story-producer` · `analyst-relations-writer` · `executive-comms-writer` · `lifecycle-email-writer` · `content-repurposer`

### Quality
`claims-risk-reviewer` · `narrative-consistency-reviewer` · `final-publish-reviewer`

---

## Quality bar

Every publishable asset should be scored against:

- `rubrics/editorial-quality.md`
- `rubrics/technical-accuracy.md`
- `rubrics/developer-fluency.md`
- `rubrics/brand-fit.md`
- `rubrics/distribution-readiness.md`

---

## Voice rules

Always follow `core/VOICE.md` and `core/STYLE_GUIDE.md`.

Short version:
- Be useful before being persuasive.
- Use technical specifics.
- Avoid generic AI marketing language.
- Avoid unsupported claims.
- Avoid em dashes.
- Prefer workflows, examples, and proof.
- Treat developers as smart.
- Explain what the product actually does.

---

## Claims policy

Before publishing, every factual claim must be categorized. See `core/CLAIMS_POLICY.md`.

---

## Validation

```bash
python scripts/validate_repo_structure.py
python scripts/lint_skill_files.py
python scripts/generate_skill_index.py
```
