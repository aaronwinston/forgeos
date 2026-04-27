---
title: Getting Started with ForgeOS Production System
description: Quick start guide for using ForgeOS production workflows
version: 1.0.0
last_updated: 2024-12-20
---

# Getting Started with ForgeOS Production System

The ForgeOS Production System provides 6 layers of structure for managing content production workflows at scale.

## What You'll Find

- **Runbooks** - Step-by-step workflows for 5 major content types
- **Packages** - Deliverable specifications and success criteria  
- **QA Checklists** - Quality assurance gates for each stage
- **Export Guides** - Share content with Claude, ChatGPT, Cursor, Copilot, or Markdown
- **Lifecycle Tracker** - Track content from planning through archive

## Choose Your Starting Point

### Scenario 1: Write a Blog Post

**Time:** 3-5 business days | **Complexity:** Medium | **New?** Start here

1. Open: [Blog Post Runbook](../runbooks/blog-post.md)
2. Follow the 5-step workflow (Research → Draft → Edit → Refine → SEO)
3. Use: [Blog QA Checklist](../workflows/qa-checklist-blog.md) before publishing
4. Reference: [Blog Post Package](../packages/blog-post.md) for deliverables

**Key timeline:**
- Research & Outline: 1 day
- First Draft: 1.5 days
- Editorial Review: 1 day
- Author Refinement: 0.5 days
- SEO Optimization: 0.5 days
- **Total: 3-4 days**

### Scenario 2: Launch a Product/Feature Campaign

**Time:** 4-6 weeks | **Complexity:** High | **New?** Read first

1. Open: [Launch Campaign Runbook](../runbooks/launch-campaign.md)
2. Review: [Campaign Package](../packages/launch-campaign.md) for scope
3. Follow the 4-phase workflow (Strategy → Content → Integration → Launch)
4. Use: [Campaign QA Checklist](../workflows/qa-checklist-campaign.md)
5. Track: [Content Lifecycle Tracker](../workflows/content-lifecycle.md)

**Key phases:**
- Phase 1 (Strategy): Weeks 1-2
- Phase 2 (Content): Weeks 3-4
- Phase 3 (Integration): Week 5
- Phase 4 (Launch): Week 6+

**Components created:**
- Landing page + announcement email
- Blog post + email series
- 20+ social posts across 4 platforms
- Display ads + PR materials
- Webinar/demo content

### Scenario 3: Quarterly Content Review & Optimization

**Time:** 2-3 weeks per cycle | **Complexity:** Medium | **New?** Good follow-up task

1. Open: [Content Audit Runbook](../runbooks/content-audit.md)
2. Inventory all published content
3. Score performance on 5+ dimensions
4. Create optimization roadmap
5. Use: [Analytics QA Checklist](../workflows/qa-checklist-analytics.md)

**Key activities:**
- Performance audit (3-5 days)
- Analysis & scoring (5-7 days)
- Optimization planning (3-5 days)
- Implementation (rolling, 90 days)

**Expected outcomes:**
- Top 50 content pieces identified
- 80% improvement on bottom 30%
- 15%+ traffic lift (organic)

---

## The Six Layers (Quick Overview)

### Layer 1: Runbooks
**"How do I do this?"**

Found in: `runbooks/`

Available runbooks:
- [Blog Post](../runbooks/blog-post.md) - End-to-end blog writing
- [Launch Campaign](../runbooks/launch-campaign.md) - Multi-channel campaigns
- [Repurposing](../runbooks/repurposing-campaign.md) - Content reuse & adaptation
- [Content Audit](../runbooks/content-audit.md) - Quarterly optimization
- [Strategy Brief](../runbooks/strategy-brief.md) - Strategic planning

Each runbook includes:
- Step-by-step workflow
- Agent sequence and responsibilities
- Input/output specifications
- Example timeline
- Success criteria

### Layer 2: Packages
**"What should this deliverable include?"**

Found in: `packages/`

Available packages:
- [Blog Post](../packages/blog-post.md) - Complete blog + social derivatives
- [Campaign](../packages/launch-campaign.md) - Multi-channel package
- [Analyst Report](../packages/analyst-report.md) - Research report bundle
- [Social Campaign](../packages/social-campaign.md) - Social media package
- [Repurposing Bundle](../packages/repurposing-bundle.md) - Format adaptations

Each package defines:
- Core content component(s)
- Derivative content
- Distribution channels
- Success metrics
- Resource requirements

### Layer 3: QA System
**"Is this ready to publish?"**

Found in: `workflows/`

Quality gates:
- [QA Gating Overview](../workflows/qa-gating.md) - The system
- [Blog Checklist](../workflows/qa-checklist-blog.md)
- [Campaign Checklist](../workflows/qa-checklist-campaign.md)
- [Social Checklist](../workflows/qa-checklist-social.md)
- [Analytics Checklist](../workflows/qa-checklist-analytics.md)
- [Positioning Checklist](../workflows/qa-checklist-positioning.md)

Apply checklists:
- Component QA (before phase handoff)
- Workflow QA (end of phase)
- Integration QA (cross-channel)
- Compliance QA (pre-publication)

### Layer 4: Export Layer
**"How do I use this in Claude/ChatGPT/Cursor?"**

Found in: `exports/`

Export guides:
- [Claude Context](../exports/claude-context.md) - 200K context window
- [Cursor Context](../exports/cursor-context.md) - IDE integration
- [Copilot Context](../exports/copilot-context.md) - GitHub native
- [ChatGPT Custom GPTs](../exports/chatgpt-context.md) - Quick setup
- [Markdown Export](../exports/markdown-export.md) - Universal format

Choose based on:
- **Claude:** Large strategic tasks, full packages
- **ChatGPT:** Quick reviews, team collaboration
- **Cursor:** Development/technical workflows
- **Copilot:** GitHub-native team processes
- **Markdown:** Archiving, version control

### Layer 5: Lifecycle Tracker
**"Where is this content in its lifecycle?"**

Found in: `workflows/content-lifecycle.md`

Track content through:
1. Planning
2. Production
3. QA & Validation
4. Scheduled for Publication
5. Published/Active
6. Optimization
7. Maintenance
8. Archived/Declined

Use for:
- Status tracking
- Performance monitoring
- Optimization trigger identification
- Refresh scheduling

---

## Recommended Learning Path

### Week 1: Understand the System

1. Read: [Production System README](../README.md) (10 min)
2. Skim: [Runbook Layer Overview](../runbooks/README.md) (15 min)
3. Skim: [Package Layer Overview](../packages/README.md) (15 min)
4. Skim: [QA System Overview](../workflows/qa-gating.md) (10 min)

**Time: ~50 minutes**

### Week 2: Execute Your First Workflow

Pick ONE scenario from above and execute it:

- **Simple:** Blog Post (3-4 days)
- **Medium:** Repurposing Campaign (2-3 weeks)  
- **Complex:** Launch Campaign (4-6 weeks)

Use the runbook step-by-step. Reference the QA checklist before publishing.

**Time: Variable (3 days to 6 weeks)**

### Week 3+: Build Your System

1. Document your content types (beyond the 5 templates)
2. Create new runbooks for your workflows
3. Build custom packages for your team
4. Set up export profiles for your tools
5. Configure your lifecycle tracker

---

## Common Questions

### "Which runbook should I use?"

Use this matrix:

| Goal | Runbook |
|------|---------|
| Create one piece of content | Blog Post |
| Launch new product/feature | Launch Campaign |
| Adapt existing content | Repurposing Campaign |
| Improve content portfolio | Content Audit |
| Make strategic decision | Strategy Brief |

### "What's the difference between runbooks and packages?"

- **Runbook:** The process ("How do I write this?")
- **Package:** The deliverable ("What does this include?")

Use together: Follow the runbook's process to create the package's deliverables.

### "When do I use QA checklists?"

After each major phase:
1. **After writing:** Component QA
2. **After drafting:** Workflow QA
3. **Before launch:** Integration QA
4. **Before publish:** Compliance QA

### "How do I export to Claude or ChatGPT?"

1. Open export guide: `exports/claude-context.md` or `exports/chatgpt-context.md`
2. Copy relevant runbook/package markdown
3. Paste into Claude or ChatGPT
4. Ask: "Walk me through this workflow step by step"

### "Can I modify these documents?"

**Yes!** They're templates. Customize them for your team:
- Add your brand guidelines
- Adjust timelines to your pace
- Add/remove process steps
- Create new runbooks for your workflows

### "How do I track content status?"

Use `workflows/content-lifecycle.md`:
- Simple: Google Sheets with status column
- Medium: GitHub Issues for each content piece
- Advanced: Airtable or CMS with workflow automation

---

## Real-World Example: Blog Post

Here's how it flows from start to publish:

### Day 1: Planning
- [ ] Topic approved
- [ ] Audience identified
- [ ] Timeline confirmed (3-4 days)
- [ ] Runbook referenced: `blog-post.md`

### Day 2: Research & Draft
- [ ] Researcher completes outline (1 day)
- [ ] Writer completes first draft (1.5 days)
- [ ] Component QA: Runbook section 1-2 reviewed

### Day 3-4: Review & Refinement
- [ ] Editor reviews draft (1 day)
- [ ] Writer refines with feedback (0.5 days)
- [ ] Workflow QA: Runbook sections 3-4 reviewed

### Day 4-5: Optimization
- [ ] SEO Optimizer applies standards (0.5 days)
- [ ] Integration QA: Cross-channel alignment checked
- [ ] Blog QA Checklist applied (full review)

### Day 5: Publication
- [ ] Compliance review passed ✓
- [ ] Published to blog ✓
- [ ] Social content scheduled ✓
- [ ] Analytics tracking configured ✓

### Weeks 2-12: Active & Maintenance
- [ ] Track: `content-lifecycle.md` status = "Active"
- [ ] Monitor performance weekly
- [ ] Optimize if needed
- [ ] Review at 3, 6, 12 months for refresh

---

## Next Steps

1. **Choose your first task** from the three scenarios above
2. **Open the runbook** for that task
3. **Start at step 1** and follow through to completion
4. **Use the QA checklist** before publication
5. **Track in lifecycle tracker** and iterate

You now have everything you need to execute professional content workflows.

**Questions?** Check the README in each directory (`runbooks/`, `packages/`, `workflows/`, `exports/`).

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
