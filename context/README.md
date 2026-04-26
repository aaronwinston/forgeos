# context/

This directory is where you drop files that give agents richer, more specific knowledge before they do any work.

All agents in this repo are instructed to check the relevant subdirectory before producing output. The more you put here, the less correcting you do later.

---

## Directory structure

```
context/
  my-writing/        # Your published work — blog posts, social, talks, newsletters
  arize/             # Arize AI product docs, internal positioning, feature notes
  audience/          # Who you're writing for — ICPs, personas, community intel
  research/          # Papers, articles, external sources agents can cite or reference
  approved-messaging/ # Locked copy — taglines, product descriptions, legal-cleared claims
```

---

## How to add files

Drop any file type into the right folder. Markdown works best — agents read it cleanly. PDFs and plain text also work. Name files clearly.

**Good file names:**
- `my-writing/github-blog-animated-ascii-banner.md`
- `arize/phoenix-product-overview-2025.md`
- `audience/ai-engineer-icp.md`
- `research/attention-is-all-you-need.md`
- `approved-messaging/arize-ax-taglines-approved.md`

**Bad file names:**
- `draft.md`
- `notes.txt`
- `final_final_v3.md`

---

## What goes where

### `my-writing/`
Paste in or link to your published writing. Blog posts, LinkedIn posts, Twitter threads, talks, newsletter editions, anything you've shipped that represents how you think and write.

Agents use these to:
- Match your voice precisely (not just rules — actual patterns)
- Understand your point of view on a topic before drafting
- Check their output against real examples

**Tip:** Include a one-line header at the top of each file with the source and date.
```
<!-- Source: GitHub Blog | Published: 2024-11-14 -->
```

---

### `arize/`
Internal product knowledge that isn't on the public docs site. Release notes, positioning briefs, feature overviews, customer use cases (approved), roadmap context (non-confidential).

Agents use these to:
- Write about features accurately, with the right terminology
- Avoid outdated or incorrect product descriptions
- Reference the right level of maturity for a feature

---

### `audience/`
Who you're writing for — written out. Persona docs, ICP definitions, community observations, interview notes, survey data, anything that describes your readers.

Agents use these to:
- Calibrate technical depth correctly
- Write to the right level of sophistication
- Avoid alienating the audience with wrong assumptions

---

### `research/`
Papers, articles, blog posts, or source material you want agents to be able to cite, reference, or synthesize. Drop the full text or a detailed summary.

Agents use these to:
- Ground claims in real sources
- Summarize findings accurately
- Recommend relevant reading in content

---

### `approved-messaging/`
Final, locked copy. Taglines, product one-liners, boilerplate descriptions, legal-cleared claims, partnership language. Anything that should not be improvised.

Agents use these to:
- Pull exact approved phrasing instead of generating new variants
- Check that drafted copy doesn't contradict approved language
- Hold the line on claims that have been through review

---

## How agents should use this directory

When producing any content, agents should:

1. Check `context/my-writing/` — read any relevant samples to calibrate voice
2. Check `context/arize/` — confirm product details before writing about Arize
3. Check `context/audience/` — confirm who they're writing for
4. Check `context/approved-messaging/` — pull exact phrasing where it exists
5. Check `context/research/` — if the topic has relevant sources there, use them

**Instruction to include in any task prompt:**
```
Before writing, read context/README.md and check the relevant subdirectories for
files that inform this task. Use my-writing/ to match voice, arize/ for product
accuracy, approved-messaging/ for any locked copy, and audience/ to calibrate depth.
```

---

## Maintenance

- Add new writing to `my-writing/` after anything publishes
- Update `arize/` when products or features change significantly
- Archive outdated files by prefixing with `_archive-`
- Don't leave placeholder files here — delete them when you replace them with real content
