---
name: QA Gating System
description: Quality assurance gates and rubric application workflow for content production
version: 1.0.0
last_updated: 2024-12-20
layer: workflows
---

# QA Gating System

The QA Gating System defines **quality checkpoints** throughout content production workflows. Each gate ensures content meets quality standards before progressing to the next phase or publication.

## Purpose

QA Gates:
- Maintain consistent quality standards
- Reduce rework and revisions
- Build customer confidence
- Catch issues before publication
- Establish accountability

## Gate Levels

### Level 1: Component QA (Per-Piece Review)
**When:** Each content component completed  
**Owner:** Content creator's manager or peer reviewer  
**Criteria:** Format specs, grammar, accuracy, brand alignment  
**Duration:** 30-60 minutes  
**Pass Rate Target:** >90%  

**Applies to:**
- Individual blog posts
- Social media posts
- Email copy
- Video scripts

### Level 2: Workflow QA (End of Phase)
**When:** Workflow phase completed  
**Owner:** Designated QA reviewer (editor, strategist)  
**Criteria:** Completeness, quality, integration readiness  
**Duration:** 1-2 hours  
**Pass Rate Target:** >85%  

**Applies to:**
- After writer drafts blog (before editor)
- After designer creates graphics (before distribution)
- After email sequences created (before sending)

### Level 3: Integration QA (Cross-Channel)
**When:** All components ready for distribution  
**Owner:** Distribution manager or operations lead  
**Criteria:** Consistency across channels, timing coordination, tracking setup  
**Duration:** 2-4 hours  
**Pass Rate Target:** >95%  

**Applies to:**
- Launch campaigns (final check)
- Social media campaigns (all platforms aligned)
- Multi-channel packages

### Level 4: Compliance QA (Pre-Publication)
**When:** Content ready to publish/distribute  
**Owner:** Legal/compliance (if applicable), brand manager  
**Criteria:** Legal compliance, brand guidelines, accessibility  
**Duration:** 30-60 minutes  
**Pass Rate Target:** 100%  

**Applies to:**
- All public-facing content
- Promotional content
- Content with claims or data

## QA Workflow Process

### Standard Workflow

```
Content Created
    ↓
Component QA (Level 1) ← Fails: Return for revision
    ↓
Phase Complete
    ↓
Workflow QA (Level 2) ← Fails: Return for revision
    ↓
Ready for Distribution
    ↓
Integration QA (Level 3) ← Fails: Revisit coordination
    ↓
Compliance Review (Level 4) ← Fails: Address issues
    ↓
✓ APPROVED FOR PUBLICATION
    ↓
Distribute/Publish
    ↓
Post-Publication Review (Ongoing)
```

### Fast-Track (Low-Risk Content)

For social media, blog comments, minor updates:
- Component QA only (Level 1)
- Compliance check if needed
- Publication

## QA Checklist Structure

Each QA checklist includes:

### Pre-Checklist Section
- Context and objective
- Content type and scope
- Approval path
- Timeline

### Main Checklist
- 7-12 primary quality criteria
- Supporting sub-items where needed
- Checkbox format with N/A option
- Comments field for issues

### Sign-Off Section
- Reviewer name and date
- Approval authority
- Sign-off statement
- Issues documented (if any)

### Escalation Path
- When to escalate issues
- Escalation contacts
- Timeline for resolution

## Applying QA Rubrics

### Rubric Selection
Each content type has a primary rubric:
- **Blog posts** → Blog QA Checklist
- **Campaigns** → Campaign QA Checklist  
- **Social content** → Social QA Checklist
- **Analytics** → Analytics QA Checklist
- **Positioning** → Positioning QA Checklist

### Rubric Usage

**During Production:**
- Reviewer references checklist during review
- Notes items that don't meet standard
- Provides feedback for improvement
- Tracks revision cycles

**At Quality Gate:**
- Checklist serves as formal validation
- Signed-off by approving authority
- Issues document in comments
- Sign-off date recorded

**Post-Publication:**
- Checklist retained with content record
- Used for trend analysis (common issues)
- Baseline for retraining if needed

## Quality Standards by Dimension

### 1. Grammar & Language
- **Standard:** >95% accuracy (spell check + human review)
- **Tool:** Grammarly, human editor
- **Gate:** Before editor handoff

### 2. Brand Alignment
- **Standard:** Voice, tone, visual style consistent
- **Criteria:** Voice guidelines, style guide, previous examples
- **Gate:** Before distribution

### 3. Accuracy & Verification
- **Standard:** 100% for facts, figures, quotes (spot-checked)
- **Process:** Source verification, data validation
- **Gate:** Before publication

### 4. Technical Quality
- **Standard:** Mobile responsive, fast loading, no broken links
- **Testing:** Cross-browser, cross-device
- **Gate:** Before publication

### 5. Accessibility
- **Standard:** WCAG 2.0 AA compliant
- **Criteria:** Alt text, captions, contrast ratio, keyboard navigation
- **Gate:** Before publication

### 6. Completeness
- **Standard:** 100% of required components present
- **Criteria:** As defined in runbook/package
- **Gate:** Before distribution

## Tracking & Reporting

### QA Metrics to Track

**By Checklist:**
- Pass rate (% of items passing on first try)
- Average revision cycles
- Common failure points
- Time to approval

**By Content Type:**
- Blog: Average revisions per post
- Social: Approval time
- Campaign: Integration issues

**By Reviewer:**
- Consistency of standards
- Approval speed
- Escalation frequency

### QA Dashboard (Monthly)
- Pass rate trend (target: >85%)
- Average revisions (target: <1.5 cycles)
- Time to approval (target: <24 hours)
- Top failure categories
- Training needs identified

### Quality Improvement Loop

1. **Identify:** Analyze QA data for patterns
2. **Root Cause:** Why are common issues occurring?
3. **Training:** Update guidelines or provide training
4. **Implement:** Apply changes
5. **Measure:** Track improvement in metrics
6. **Repeat:** Quarterly review cycle

## QA Tool Recommendations

### Content Review Tools
- **Grammarly:** Grammar, spelling, style
- **Copyscape:** Plagiarism detection
- **Hemingway Editor:** Readability analysis
- **Google Lighthouse:** Technical SEO

### Accessibility Testing
- **WAVE:** Web accessibility evaluation tool
- **Color Contrast Analyzer:** Contrast ratios
- **Lighthouse:** Accessibility audit

### Checklist Management
- **Google Forms/Sheets:** Simple checklists
- **Notion/Airtable:** Trackable database
- **Loom:** Video feedback

## Related QA Checklists

This system includes 5 specific QA checklists:

1. **qa-checklist-blog.md** - Blog post content
2. **qa-checklist-campaign.md** - Multi-channel campaigns
3. **qa-checklist-social.md** - Social media content
4. **qa-checklist-analytics.md** - Analytics and data
5. **qa-checklist-positioning.md** - Strategic positioning

Each checklist is tailored to the specific content type and includes Level 1-4 gates.

## QA Best Practices

### Reviewer Selection
- Never review own work (peer review)
- Vary reviewers (reduces bias)
- Assign by expertise (editor for copy, designer for visuals)

### Timing
- Allow 24 hours between creation and review (fresh eyes)
- Schedule reviews before deadlines
- Build review time into timeline

### Feedback Quality
- Be specific: "Headline unclear" vs. "This doesn't work"
- Provide examples: Show similar, better version
- Explain why: Help creator understand standard
- Suggest solutions: Easier to implement feedback

### Escalation Handling
- Document issue clearly
- Provide escalation contact
- Set timeline for resolution
- Follow up on closure

## Common QA Issues & Solutions

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| Grammar errors | Rushed writing | Build in buffer time, use Grammarly |
| Brand inconsistency | Unclear guidelines | Provide style guide, examples |
| Broken links | Manual entry | Use hyperlink management tools |
| Missing alt text | Forgotten in process | Add to template requirements |
| Timeline misses | Late handoffs | Build review into timeline |
| Duplicate messaging | Poor coordination | Communication plan, asset sharing |

## Continuous Improvement

### Quarterly QA Review
- Analyze data from all checklists
- Identify top 3 issue categories
- Plan training or process improvements
- Update guidelines if needed
- Share learnings with team

### Annual QA Audit
- Full process review
- Benchmark against industry standards
- Update checklist templates
- Training plan for next year
- Resource planning

## Related Documents

- [Blog QA Checklist](./qa-checklist-blog.md)
- [Campaign QA Checklist](./qa-checklist-campaign.md)
- [Social QA Checklist](./qa-checklist-social.md)
- [Analytics QA Checklist](./qa-checklist-analytics.md)
- [Positioning QA Checklist](./qa-checklist-positioning.md)
- [Content Lifecycle Tracker](./content-lifecycle.md)

---

**Last Updated:** 2024-12-20  
**Maintained By:** Quality Assurance Team
