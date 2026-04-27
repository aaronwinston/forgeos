---
title: Agent Index
description: Registry of all ForgeOS agents and their roles
updated: 2024
---

# Agent Index

This index documents all agents in the ForgeOS system. Agents are specialized AI skills that handle specific editorial and operational tasks.

## Overview

- **Total Agents**: 25
- **Categories**: Editorial, Foundation, Quality, Specialization
- **Purpose**: Route content and operations tasks to the right specialized agent

## Quick Reference Table

| Agent | Category | Role | Primary Inputs | Use Cases |
|-------|----------|------|---|---|
| content-ops-manager | Editorial | Use this skill to manage intake, prioritization, publishing workflow, stakeholde... | Request, or, brief | Handling content intake from stakeholders |
| copy-chief | Editorial | Use this skill for final line editing, clarity, concision, brand voice, structur... | Draft, Target, channel | A draft needs final polish before review |
| editorial-director | Editorial | Use this skill to define strategy, audience, angle, narrative, positioning, and ... | Topic, or, brief | Starting a new blog post or content asset |
| managing-editor | Editorial | Use this skill to turn ideas, briefs, and drafts into production-ready editorial... | Content, idea, or | Planning an editorial calendar |
| ai-researcher | Foundation | Use this skill to research AI engineering trends, technical topics, market movem... | Topic, or, research | Researching a technical topic before drafting |
| dev-copywriter | Foundation | Use this skill to draft developer-focused blogs, technical explainers, product e... | Content, brief, Target | Drafting a developer blog post |
| dev-reviewer | Foundation | Use this skill to review drafts for developer fluency, technical clarity, specif... | Draft, Target, audience | Reviewing a blog draft for developer fluency |
| founder-x-recap | Foundation | Use this skill to summarize founder or executive X activity into useful recaps, ... | Founder, or, executive | Summarizing founder tweets or posts from the past 12 to 24 hours |
| claims-risk-reviewer | Quality | Use this skill to review risky, unsupported, overbroad, regulated, customer, par... | Draft, Source, material | Reviewing any content before publication |
| dev-campaign-reviewer | Quality | Use this skill to review developer-facing ads, landing pages, launch copy, video... | Draft, asset, or | Reviewing ad copy |
| final-publish-reviewer | Quality | Use this skill for final pre-publication review covering quality, claims, approv... | Final, draft, All | Any content asset before publication |
| narrative-consistency-reviewer | Quality | Use this skill to review whether an asset aligns with company narrative, categor... | Draft, Core, narrative | Reviewing content for narrative alignment before publication |
| analyst-relations-writer | Specialization | Use this skill to respond to analyst notes, prepare briefings, and shape analyst... | Analyst, note, or | Responding to an analyst note or inquiry |
| competitive-intelligence | Specialization | Use this skill to provide competitive framing, differentiation analysis, and mar... | Content, brief,, draft, | Starting any content task — check if competitive context is relevant before anything is written |
| content-repurposer | Specialization | Use this skill to turn one source asset into channel-specific derivatives withou... | Source, asset, (blog, | Turning a blog post into social, email, and sales content |
| customer-story-producer | Specialization | Use this skill to evaluate case study potential, shape customer narratives, and ... | Customer, name, or | Evaluating whether a customer situation has case study potential |
| dev-ad-writer | Specialization | Use this skill to write developer-facing ad copy for technical products, especia... | Product, or, feature | Writing paid social ads for developers |
| executive-comms-writer | Specialization | Use this skill to draft founder and executive communications that are technical,... | Executive, name, and | Drafting a founder LinkedIn post or thread |
| launch-comms-writer | Specialization | Use this skill to write product, feature, integration, and partner launch copy a... | Launch, brief, Product | Writing a product or feature launch announcement |
| lifecycle-email-writer | Specialization | Use this skill to write onboarding, nurture, product education, launch, and acti... | Email, type, and | Writing onboarding email sequences |
| pmm-lead | Specialization | Use this skill to define or review product positioning, messaging hierarchy, cat... | Content, brief, or | Developing or reviewing a content brief for launches, thought leadership, analyst responses, or case studies |
| seo-strategist | Specialization | Use this skill to improve discoverability without weakening content quality or d... | Draft, or, brief | Optimizing a blog post for search |
| social-editor | Specialization | Use this skill to create LinkedIn, X, founder, executive, and company social cop... | Source, asset, (blog, | Turning a blog post into social variants |
| technical-fact-checker | Specialization | Use this skill to review technical, product, architecture, benchmark, and implem... | Draft, with, technical | Reviewing technical claims in a blog post or launch copy |
| workflow-extractor | Specialization | Use this skill to turn product features, screenshots, docs, or rough notes into ... | Product, screenshots, or | The user has feature notes but needs campaign concepts |


## Agents by Category

### Editorial (4 agents)

Editorial agents handle content strategy, planning, and production workflows.


#### Content-Ops-Manager

**Role**: Use this skill to manage intake, prioritization, publishing workflow, stakeholder handoffs, and content calendar decisions.

**Primary Inputs**: Request or brief Deadline Stakeholders Channel Campaign or launch context Required approvals Current stage

**Use Cases**:
- Handling content intake from stakeholders
- Prioritizing content requests against calendar and capacity
- Creating publishing checklists for specific asset types

#### Copy-Chief

**Role**: Use this skill for final line editing, clarity, concision, brand voice, structure, grammar, and polish.

**Primary Inputs**: Draft Target channel Audience Voice guidance from core/VOICE.md Known claims or constraints Desired level of edit (light polish vs. heavy revision)

**Use Cases**:
- A draft needs final polish before review
- Copy is too long or unfocused
- Voice is inconsistent across sections

#### Editorial-Director

**Role**: Use this skill to define strategy, audience, angle, narrative, positioning, and editorial direction before drafting begins.

**Primary Inputs**: Topic or brief Audience Business goal Source material Product context Desired channel Timing or campaign context Any known constraints

**Use Cases**:
- Starting a new blog post or content asset
- Pressure-testing an idea before investing in drafting
- Turning messy input into a clear strategy

#### Managing-Editor

**Role**: Use this skill to turn ideas, briefs, and drafts into production-ready editorial plans with owners, stages, and review paths.

**Primary Inputs**: Content idea or brief Deadline Channel Stakeholders Review requirements Source material status Launch or campaign timing

**Use Cases**:
- Planning an editorial calendar
- Turning a content idea into a production plan
- Identifying missing inputs before drafting


### Foundation (4 agents)

Foundation agents provide core writing, research, and development capabilities.


#### Ai-Researcher

**Role**: Use this skill to research AI engineering trends, technical topics, market movement, competitor narratives, developer pain points, and source material for content.

**Primary Inputs**: Topic or research question Target audience Source links or documents Desired output type Time sensitivity Known company POV, if available

**Use Cases**:
- Researching a technical topic before drafting
- Preparing a blog or launch brief
- Creating a daily or weekly AI briefing

#### Dev-Copywriter

**Role**: Use this skill to draft developer-focused blogs, technical explainers, product education, and practical content for AI builders.

**Primary Inputs**: Content brief Target audience Core message Source material Product or technical notes Desired format and length Required CTA

**Use Cases**:
- Drafting a developer blog post
- Writing a technical explainer
- Turning a brief into a first draft

#### Dev-Reviewer

**Role**: Use this skill to review drafts for developer fluency, technical clarity, specificity, usefulness, and anti-hype positioning.

**Primary Inputs**: Draft Target audience Intended channel Source material Product or technical constraints Known claims that need caution

**Use Cases**:
- Reviewing a blog draft for developer fluency
- Removing hype and vague claims
- Making copy more useful to builders

#### Founder-X-Recap

**Role**: Use this skill to summarize founder or executive X activity into useful recaps, themes, and content opportunities.

**Primary Inputs**: Founder or executive posts (text or links) Time period Target channel Desired output type Known company priorities or campaigns

**Use Cases**:
- Summarizing founder tweets or posts from the past 12 to 24 hours
- Identifying recurring POVs worth amplifying
- Creating a weekly founder social recap


### Quality (4 agents)

Quality agents review, validate, and ensure content meets standards.


#### Claims-Risk-Reviewer

**Role**: Use this skill to review risky, unsupported, overbroad, regulated, customer, partner, benchmark, or competitive claims before publication.

**Primary Inputs**: Draft Source material Approval status of any customer, partner, or analyst references Known legal or compliance constraints

**Use Cases**:
- Reviewing any content before publication
- Auditing a launch announcement for risky claims
- Checking analyst materials for unsupported assertions

#### Dev-Campaign-Reviewer

**Role**: Use this skill to review developer-facing ads, landing pages, launch copy, video scripts, and campaign concepts for technical credibility, workflow clarity, and conversion quality.

**Primary Inputs**: Draft asset or campaign copy Screenshots or product UI Intended audience Channel or format Character limits Product claims or docs Desired conversion

**Use Cases**:
- Reviewing ad copy
- Reviewing landing pages
- Reviewing video scripts or storyboards

#### Final-Publish-Reviewer

**Role**: Use this skill for final pre-publication review covering quality, claims, approvals, metadata, links, CTA, and distribution readiness.

**Primary Inputs**: Final draft All previous review outputs Claims and approval status Metadata (title, slug, meta description) CTA and links Distribution plan

**Use Cases**:
- Any content asset before publication
- After all other reviews have been completed
- Before final handoff to publishing or distribution

#### Narrative-Consistency-Reviewer

**Role**: Use this skill to review whether an asset aligns with company narrative, category strategy, voice, and messaging system.

**Primary Inputs**: Draft Core narrative or messaging system Recent published content for reference Campaign or category context

**Use Cases**:
- Reviewing content for narrative alignment before publication
- Checking launch copy against company positioning
- Auditing a new content series for strategic consistency


### Specialization (13 agents)

Specialization agents handle domain-specific content creation and strategy.


#### Analyst-Relations-Writer

**Role**: Use this skill to respond to analyst notes, prepare briefings, and shape analyst relations narratives.

**Primary Inputs**: Analyst note or inquiry Company POV and talking points Product capabilities and roadmap context Customer proof points (with approval status) Competiti

**Use Cases**:
- Responding to an analyst note or inquiry
- Preparing a briefing document for an analyst meeting
- Shaping the company's narrative in analyst contexts

#### Competitive-Intelligence

**Role**: Use this skill to provide competitive framing, differentiation analysis, and market context at any stage of content production. Designed to be invoked proactively throughout the editorial process, not just as a final gate.

**Primary Inputs**: Content brief, draft, or task description (required) `context/02_narrative/competitive-pov.md` — curated competitive research files (primary source; a

**Use Cases**:
- Starting any content task — check if competitive context is relevant before anything is written
- A brief or draft touches differentiation, category claims, or market positioning
- A draft makes a claim that a competitor also makes (neutralize it or sharpen it)

#### Content-Repurposer

**Role**: Use this skill to turn one source asset into channel-specific derivatives without losing accuracy or voice.

**Primary Inputs**: Source asset (blog, announcement, report) Target channels Audience for each channel CTA for each channel Length constraints

**Use Cases**:
- Turning a blog post into social, email, and sales content
- Creating a newsletter module from a longer asset
- Extracting pull quotes and key ideas from a source

#### Customer-Story-Producer

**Role**: Use this skill to evaluate case study potential, shape customer narratives, and prepare interview guides.

**Primary Inputs**: Customer name or description Known use case or deployment context Technical details Results or outcomes (if known) Approval status Sales or customer t

**Use Cases**:
- Evaluating whether a customer situation has case study potential
- Shaping the narrative approach for a customer story
- Preparing interview questions for a customer conversation

#### Dev-Ad-Writer

**Role**: Use this skill to write developer-facing ad copy for technical products, especially CLI, IDE, agent, API, observability, infrastructure, and AI developer tools.

**Primary Inputs**: Product or feature being marketed Target developer audience Workflow or use case Product UI, docs, or source truth Channel and character limits Desire

**Use Cases**:
- Writing paid social ads for developers
- Writing Meta, Reddit, LinkedIn, or X ad copy
- Creating static ad headlines

#### Executive-Comms-Writer

**Role**: Use this skill to draft founder and executive communications that are technical, credible, and voice-sensitive.

**Primary Inputs**: Executive name and voice notes Source material (research, launch details, personal experience) Target channel and audience Desired tone and length Cla

**Use Cases**:
- Drafting a founder LinkedIn post or thread
- Writing an executive byline or op-ed
- Preparing executive talking points for an event or interview

#### Launch-Comms-Writer

**Role**: Use this skill to write product, feature, integration, and partner launch copy across all required formats.

**Primary Inputs**: Launch brief Product details and technical notes Primary message and secondary messages Target audience Channels and formats needed Executive quote re

**Use Cases**:
- Writing a product or feature launch announcement
- Drafting launch blog intro and body copy
- Writing email and social launch variants

#### Lifecycle-Email-Writer

**Role**: Use this skill to write onboarding, nurture, product education, launch, and activation emails.

**Primary Inputs**: Email type and goal Target audience and lifecycle stage Source content or product details CTA Tone guidance Known constraints

**Use Cases**:
- Writing onboarding email sequences
- Drafting nurture or educational emails
- Writing product launch emails

#### Pmm-Lead

**Role**: Use this skill to define or review product positioning, messaging hierarchy, category narrative, and feature-to-benefit translation before or during content production.

**Primary Inputs**: Content brief or draft (required) `core/CONTEXT.md` — Arize AI product knowledge (required) `core/BRAND_VOICE.md` and `core/CONTENT_STRATEGY.md` (requ

**Use Cases**:
- Developing or reviewing a content brief for launches, thought leadership, analyst responses, or case studies
- Reviewing a draft to determine if it reflects correct positioning and messaging hierarchy
- Defining the category narrative before a new content push or campaign

#### Seo-Strategist

**Role**: Use this skill to improve discoverability without weakening content quality or developer credibility.

**Primary Inputs**: Draft or brief Target audience Intended channel Any known keywords or search terms Competitor content to consider

**Use Cases**:
- Optimizing a blog post for search
- Recommending title options for SEO and click-through
- Writing meta descriptions

#### Social-Editor

**Role**: Use this skill to create LinkedIn, X, founder, executive, and company social copy from source assets.

**Primary Inputs**: Source asset (blog, announcement, research) Target channels Founder or executive voice notes Company account tone CTA or link

**Use Cases**:
- Turning a blog post into social variants
- Writing founder or executive LinkedIn posts
- Creating X threads or standalone posts

#### Technical-Fact-Checker

**Role**: Use this skill to review technical, product, architecture, benchmark, and implementation claims for accuracy before publication.

**Primary Inputs**: Draft with technical claims highlighted Product documentation or technical notes Source material (papers, docs, code) Known constraints or caveats

**Use Cases**:
- Reviewing technical claims in a blog post or launch copy
- Checking product behavior descriptions against known capabilities
- Verifying code accuracy and idiom

#### Workflow-Extractor

**Role**: Use this skill to turn product features, screenshots, docs, or rough notes into concrete developer workflows that can power ads, landing pages, demos, docs, and launch content.

**Primary Inputs**: Product screenshots or UI notes Product docs or source truth Audience Desired campaign or content format Any known commands, APIs, or UI actions Desir

**Use Cases**:
- The user has feature notes but needs campaign concepts
- The user has screenshots but the story is unclear
- The user needs ad workflows or demo scripts


## Common Agent Chains

### Blog Post Workflow

1. Editorial Director — Define strategy and angle
2. AI Researcher — Research topic and gather sources
3. Dev Copywriter — Draft content
4. Dev Reviewer — Review for technical accuracy
5. Copy Chief — Final editing
6. Final Publish Reviewer — Pre-publication check

### Product Launch Workflow

1. Editorial Director — Define launch narrative
2. Launch Comms Writer — Draft launch announcement
3. Claims Risk Reviewer — Validate product claims
4. Copy Chief — Polish messaging
5. Final Publish Reviewer — Approval

### Content Repurposing Workflow

1. Editorial Director — Define channel and angle
2. Content Repurposer — Adapt content
3. Copy Chief — Refine for channel
4. Final Publish Reviewer — Check quality

## Using the Agent Index

To route a task:

1. **Identify the type of work**: Strategy, research, writing, review, or operations
2. **Check the category**: Find agents suited to that work type
3. **Review primary inputs**: Ensure you have what the agent needs
4. **Follow the chain**: Use recommended skill sequences from the workflow section
5. **Pass outputs forward**: Each agent's output becomes the next agent's input

## Adding New Agents

When adding new agents to ForgeOS:

1. Create a skill directory in `skills/{category}/{agent-name}/`
2. Create `SKILL.md` with frontmatter and role documentation
3. Add to `skills/index.json`
4. Run the index generation script to update this file and `registry.yaml`
5. Update this INDEX.md with the new agent description

## References

- [Skills Directory](../skills/)
- [Registry YAML](./registry.yaml)
- [Skill Format](../skills/README.md)
