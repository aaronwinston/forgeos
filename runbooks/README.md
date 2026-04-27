---
name: Runbook Layer
description: Standard operating procedures for content production workflows
version: 1.0.0
last_updated: 2024-12-20
layer: runbooks
---

# Runbook Layer

The Runbook Layer defines **step-by-step workflows** for recurring content production tasks. Each runbook orchestrates multiple agents to accomplish a specific deliverable.

## Purpose

Runbooks:
- Standardize content production processes
- Reduce decision-making overhead
- Enable consistent quality across deliverables
- Serve as training documents for new team members
- Provide templates for agent coordination

## Common Runbooks

### Core Runbooks

1. **blog-post.md** - Complete blog post production workflow
   - Research → Outline → Draft → Review → Publish
   - Timeline: 3-5 business days
   - Key agents: Research, Writer, Editor

2. **launch-campaign.md** - Product/feature launch coordination
   - Planning → Content creation → Distribution → Measurement
   - Timeline: 2-4 weeks
   - Key agents: Strategist, Writer, Analyst, Distribution

3. **repurposing-campaign.md** - Multi-format content reuse
   - Source material audit → Format adaptation → Distribution
   - Timeline: 1-2 weeks
   - Key agents: Analyst, Formatter, Writer

4. **content-audit.md** - Quarterly content review and optimization
   - Inventory → Analysis → Recommendations → Implementation
   - Timeline: 2-3 weeks
   - Key agents: Analyst, Strategist

5. **strategy-brief.md** - Strategic planning document creation
   - Research → Synthesis → Draft → Validation
   - Timeline: 1-2 weeks
   - Key agents: Researcher, Analyst, Writer

## How Agents Use Runbooks

### Standard Workflow Pattern

1. **Initialization** - Agent receives runbook with context and inputs
2. **Phase Execution** - Agent executes assigned workflow steps
3. **Handoff** - Agent passes outputs to next agent in sequence
4. **QA Validation** - Output validated against runbook specs
5. **Completion** - Final deliverable archived with runbook reference

### File Structure

Each runbook markdown file includes:

```yaml
---
name: Runbook Name
description: Brief description
agents_required: [Agent1, Agent2, Agent3]
context_required: [Context Type 1, Context Type 2]
estimated_duration: X days
success_metrics: [Metric1, Metric2]
version: 1.0.0
---
```

### Usage Example

```bash
# Agent receives runbook with inputs
forgeos run-runbook blog-post.md \
  --topic "AI Safety in Production" \
  --audience "Technical Leaders" \
  --context "current_research"

# Output includes:
# - Generated content artifact
# - Execution timeline
# - QA checklist status
```

## Runbook Components

### 1. Frontmatter
- Name, description, version
- Required agents and context
- Estimated duration
- Success metrics

### 2. Overview
- Purpose and scope
- When to use this runbook
- Dependencies and prerequisites

### 3. Workflow Steps
- Step-by-step instructions
- Agent assignments
- Input/output specifications
- Handoff criteria

### 4. Agent Sequence
- Ordered list of agents
- Responsibility boundaries
- Communication requirements

### 5. Timeline
- Typical duration per step
- Critical path identification
- Parallel execution opportunities

### 6. Input/Output Specs
- Required inputs
- Output format and structure
- Quality standards

### 7. Troubleshooting
- Common issues
- Recovery procedures
- Escalation paths

## Integration Points

### With Context Index
- Runbooks reference context types needed
- Context loaded automatically at start
- Updates triggered by context changes

### With Agents
- Agents implement runbook steps
- Agent capabilities determine feasibility
- Fallback procedures if agent unavailable

### With Packages
- Runbooks produce outputs consumed by packages
- Multiple runbooks may feed one package
- Package layer coordinates final delivery

### With QA System
- Each step has QA checkpoint
- QA checklists aligned with runbook phases
- Sign-off required before handoff

## Creating New Runbooks

### Template

```markdown
---
name: Runbook Name
description: What this runbook accomplishes
agents_required: [Agent A, Agent B]
context_required: [Context Type]
estimated_duration: X days
success_metrics: [Metric]
version: 1.0.0
---

## Overview
- Purpose
- When to use
- Prerequisites

## Workflow
1. **Step Name** (Agent Name)
   - Details
   - Input: X
   - Output: Y
   
2. **Next Step** (Agent Name)
   - Details

## Inputs
- Required input 1
- Required input 2

## Outputs
- Deliverable 1
- Deliverable 2

## Timeline
- Phase 1: X days
- Phase 2: Y days
```

### Guidelines

- Keep steps atomic and testable
- Be specific about inputs/outputs
- Include realistic timelines
- Reference relevant QA checklists
- Link to supporting documentation
- Update version when modified

## Runbook Lifecycle

1. **Draft** - Created, not yet approved
2. **Active** - In use by agents
3. **Updated** - Modified based on feedback
4. **Archived** - Replaced by newer version
5. **Deprecated** - No longer recommended

## Related Documentation

- [Context Index](../context/README.md) - Context types available
- [Agents Index](../agents/INDEX.md) - Agent capabilities
- [Packages Layer](../packages/README.md) - Deliverable bundles
- [QA Checklist System](../workflows/qa-gating.md) - Quality gates

---

**Last Updated:** 2024-12-20  
**Maintained By:** Content Operations Team
