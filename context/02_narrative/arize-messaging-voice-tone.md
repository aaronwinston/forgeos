---

title: Arize Messaging, Voice, and Tone Guide
slug: arize-messaging-voice-tone
layer: narrative
type: voice_and_messaging_system
use_for:

* enforcing tone and writing quality
* guiding messaging consistency
* reviewing generated content
  avoid:
* treating as product source of truth
* copying boilerplate blindly without context

---

# Arize Messaging, Voice, and Tone Guide

## 🔑 Agent Context

This document defines:

* how Arize **sounds**
* how Arize **structures messaging**
* how to distinguish **credible developer content from generic AI marketing**

It should be used as a **filter**, not a generator.

Always combine with:

* messaging framework (`context/02_narrative/`)
* strategy docs (`context/03_strategy/`)
* execution frameworks (`context/04_execution/`)

---

# 🧠 The One-Sentence Test

Before publishing:

> Would a senior AI engineer read this and think:
> “These people have actually shipped agents to production”?

If not → rewrite.

---

# 🧩 Core Messaging

## Positioning

Arize is the AI engineering platform for teams shipping reliable AI agents and LLM applications.

## Core Story

Observability shows you problems.
Evaluation measures them.
The improvement loop fixes them.

## Narrative Arc

1. Demos are easy
2. Production is hard
3. You need observability + evaluation + improvement
4. Arize provides the full loop

---

# 👤 Audience Model

### Primary: AI engineers

* care about debugging, reliability, production systems
* want specifics, not abstractions

### Secondary:

* PMs → outcomes, clarity
* startup devs → speed, simplicity
* enterprise buyers → reliability, scale, governance

---

# 🧱 Messaging Themes

Every piece should anchor to at least one:

1. Demo → production gap
2. Evaluation for agents
3. Observability + eval + improvement loop
4. Open ecosystem (Phoenix, AX)
5. Agent tooling (Alyx)
6. Independence + open standards

---

# 🧠 Voice Principles

## 1. Practitioner, not pundit

Write like someone who shipped the system.

## 2. Calm authority, not hype

No exaggerated claims. Show outcomes.

## 3. Teach, don’t sell

Content should stand alone as useful.

## 4. Show specifics

Name tools, numbers, functions, states.

## 5. Talk to equals

Assume a smart, technical reader.

---

# ⚠️ What to Avoid

Never use:

* “unlock”, “empower”, “leverage”
* “revolutionary”, “game-changing”
* “AI-powered”, “next-gen”
* generic “solutions” language
* PR-style announcements (“excited to share…”)

---

# ✍️ Writing Rules

## Do

* Lead with a real problem
* Show failure → then fix
* Use concrete examples
* Include code, logs, or outputs
* Admit what didn’t work

## Don’t

* Start with features
* Be abstract
* Over-explain basics
* Hide complexity

---

# 🧾 Blog Structure (Preferred Pattern)

1. Hook (specific claim or tension)
2. TL;DR
3. What broke
4. What didn’t work
5. What worked
6. What this unlocked
7. Reusable pattern

---

# 🧠 Key Insight

> Specificity = credibility

Examples beat claims:

* numbers
* tools
* traces
* PRs
* real workflows

---

# ⚖️ Competitive Tone Rule

* Lead with category, not competitors
* If comparing → focus on architecture and outcomes
* Never dunk

---

# 🧭 Agent Instructions

When generating content:

1. Remove hype language
2. Add specific proof (tools, metrics, workflows)
3. Replace abstract claims with concrete examples
4. Ensure tone is calm, technical, and credible
5. Validate using the “one-sentence test”

This file should always be applied as a **final pass filter** before output.
