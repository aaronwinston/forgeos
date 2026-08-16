---
title: Agent Evaluation Category Map
slug: agent-evaluation-category-map
layer: narrative
type: category-framing
use_for:
  - category narrative
  - analyst and thought leadership prep
  - messaging consistency across teams
avoid:
  - uncited market claims
  - collapsing distinct categories into one term
---

# Agent Evaluation Category Map

## Purpose

Frame how the market is moving from observability to eval-driven development, then to agent-native evaluation. Use this map to keep messaging consistent and claims-safe.

## Category progression

### 1) AI observability (foundation)

What it solves:
- Visibility into model, retrieval, tool, and pipeline behavior
- Root-cause analysis for failures in production

Core question:
- "What happened in this run?"

### 2) Eval-driven development (operational loop)

What it adds:
- Systematic scoring against quality criteria
- Experiments across versions on shared datasets
- Regression checks before rollout

Core question:
- "Did this change improve quality on defined criteria?"

### 3) Agent-native evaluation (emerging frontier)

What it expands:
- Evaluation of multi-step agent behavior, not just final output
- Step-level checks for planning, tool use, retrieval, and handoff logic
- Continuous validation for long-running and stateful workflows

Core question:
- "Can this agent make reliable decisions across steps and contexts?"

## Terminology bridge

Use this bridge so teams can move from familiar observability terms to agent evaluation language.

| Familiar term | Bridge phrasing | Agent-native term |
|---|---|---|
| Trace debugging | Trace + scoring loop | Behavioral evaluation |
| Error analysis | Failure pattern + rubric | Reliability criteria |
| QA checks | Dataset + evaluator pipeline | Regression gates |
| Prompt test | Prompt + tool-path validation | Policy and trajectory eval |
| Run logs | Structured execution record | Decision graph evidence |

## Messaging constraints

### What we can say safely

- The workflow is moving from inspection to measured improvement.
- Agent quality requires both observability and evaluation.
- Teams need step-level evidence, not only final-answer scoring.

### What needs evidence before publish

- Any claim that Arize defines or owns the category
- Any market share, ranking, or "leader" statement
- Any benchmark claim versus named alternatives
- Any quantitative business outcome claim

### What we do not say

- "Observability is obsolete"
- "Evaluation replaces observability"
- "One metric proves agent quality"
- "Fully autonomous agents are production-safe by default"

## Narrative spine for external content

1. Start with production pain: teams can see failures but still struggle to prevent recurrence.
2. Introduce eval-driven development: score, compare, and gate changes on real traces.
3. Expand to agent-native evaluation: assess decisions across steps, tools, and context shifts.
4. Close with proof expectations: traces, rubrics, experiments, and regression evidence.

## Asset-level guidance

- Website and SEO pages: prioritize practical workflow language over category debate language.
- Analyst content: use explicit category progression and source-backed definitions.
- Product launches: tie each claim to a concrete artifact (trace view, eval config, experiment result).
