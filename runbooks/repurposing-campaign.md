---
name: Content Repurposing Campaign
description: Workflow for auditing, adapting, and redistributing existing content across multiple formats and channels
agents_required: [Analyst, Content Formatter, Strategist, Distribution Manager]
context_required: [Content Inventory, Format Specifications, Distribution Channels, Target Audience Segments]
estimated_duration: 2-3 weeks
success_metrics: [Content Reuse Ratio >80%, Format Adaptation Quality Pass, Distribution Completion 100%, Engagement Target Met]
version: 1.0.0
qa_checklist: qa-checklist-repurposing.md
---

## Overview

This runbook defines the process for identifying high-performing content, adapting it to new formats, and redistributing it to untapped channels and audiences. It maximizes ROI on existing content investments.

**When to use:** Quarterly content recycling, off-peak periods, expanding into new channels, extending campaign reach

**Prerequisites:**
- Content performance data available (6+ months)
- Distribution channel strategy defined
- Format specifications documented
- Audience segment profiles created

## Workflow Steps

### Phase 1: Audit & Selection (3-5 days)

#### Step 1.1: Content Performance Audit (Analyst)
**Duration:** 2-3 days

**Responsibilities:**
- Analyze content performance metrics
- Identify top-performing pieces (engagement, reach, conversion)
- Assess repurposing potential for each piece
- Create priority ranking

**Inputs:**
- Historical performance data (6+ months)
- Content inventory
- Success metrics definitions
- Audience analytics

**Outputs:**
- Audit report (top 10-15 candidates)
- Performance ranking spreadsheet
- Repurposing recommendation by content type
- Format adaptation suggestions

**QA Gate:** Audit methodology verified, recommendations reviewed for validity

#### Step 1.2: Repurposing Strategy Development (Strategist)
**Duration:** 1-2 days

**Responsibilities:**
- Select 5-8 pieces for repurposing
- Identify target formats for each piece
- Map audience segments to formats
- Define channel distribution plan
- Create adaptation specifications

**Inputs:**
- Audit report with recommendations
- Distribution channel capabilities
- Audience segment profiles
- Format specification templates

**Outputs:**
- Repurposing plan (5-8 pieces)
- Format mapping document
- Channel distribution matrix
- Detailed adaptation specifications per piece

**QA Gate:** Strategy reviewed for feasibility and audience alignment

### Phase 2: Content Adaptation (1-2 weeks)

#### Step 2.1: Format Adaptation (Content Formatter)
**Duration:** 2-3 days per piece (concurrent for multiple pieces)

**Responsibilities:**
- Adapt original content to specified formats
- Maintain core message while optimizing for format
- Add format-specific enhancements (graphics, timestamps, etc.)
- Quality check for format compliance

**Inputs:**
- Original content pieces
- Format specifications
- Style guides
- Visual asset library

**Outputs:**
- Adapted content in each format:
  - Slide presentations (PowerPoint, Google Slides)
  - Infographics/visual summaries
  - Video scripts and captions
  - Social media threads
  - Email series
  - Podcast episode scripts
  - Interactive elements (quizzes, calculators)

**QA Gate:** Format specifications met, brand consistency maintained, content accuracy verified

#### Step 2.2: Enhancement & SEO Optimization (Strategist + Formatter)
**Duration:** 1-2 days

**Responsibilities:**
- Add original insights or updated data to repurposed content
- Optimize for SEO (if applicable)
- Create channel-specific CTAs and links
- Ensure proper attribution and sourcing

**Inputs:**
- Adapted content pieces
- Current market data
- SEO guidelines
- CTA templates

**Outputs:**
- Enhanced content with updates
- SEO-optimized metadata (titles, descriptions, keywords)
- Channel-specific variant copies
- Asset checklist for each piece

**QA Gate:** Enhancement value assessed, SEO standards met, CTAs appropriate

### Phase 3: Distribution Planning & Execution (5-7 days)

#### Step 3.1: Distribution Sequencing (Distribution Manager)
**Duration:** 2-3 days

**Responsibilities:**
- Create distribution calendar
- Coordinate timing across channels
- Establish publication workflows
- Set up tracking and monitoring

**Inputs:**
- Adapted content assets
- Channel distribution matrix
- Distribution capability documentation
- Existing content calendar

**Outputs:**
- Distribution calendar (4-6 weeks)
- Channel-specific publishing instructions
- Tracking setup document
- Performance monitoring specifications

**QA Gate:** Calendar validated, no conflicts with existing content, tracking configured

#### Step 3.2: Publication & Distribution (Distribution Manager + Analyst)
**Duration:** 4-6 weeks (ongoing)

**Responsibilities:**
- Publish content to all scheduled channels
- Monitor initial performance
- Optimize distribution timing based on early performance
- Document publication log

**Inputs:**
- Distribution calendar
- Final adapted assets
- Channel access credentials
- Monitoring thresholds

**Outputs:**
- Publication completion log
- Performance monitoring report
- Optimization recommendations
- Final distribution summary

**QA Gate:** 100% publication completion, tracking verified, baseline performance captured

## Content Format Reference

### Blog → Derived Formats

**Original:** "The Future of AI in Marketing" (2,000-word blog post)

**Adapted to:**
1. **Infographic** - 5-key-points visual summary
2. **LinkedIn Series** - 5-part thread with engagement hooks
3. **Slide Deck** - 15-slide presentation
4. **Podcast Script** - 20-minute episode with host notes
5. **Social Clips** - 3-5 short video scripts (15-30 seconds each)
6. **Email Series** - 3-part educational series

### Whitepaper → Derived Formats

**Original:** "Market Analysis: Enterprise Software 2024" (30-page whitepaper)

**Adapted to:**
1. **Executive Summary** - 2-page brief version
2. **Infographic Series** - 3 visual summaries of key findings
3. **Video Explainer** - 5-minute overview with screen sharing
4. **Webinar Outline** - 60-minute presentation structure
5. **Social Campaign** - 10-post series highlighting key statistics
6. **Podcast Episodes** - 2-3 standalone episodes on key topics

## Agent Sequence

```
Analyst (Audit)
├─ Strategist (Strategy Planning)
    └─ Content Formatter (Adaptation)
        └─ Strategist (Enhancement)
            └─ Distribution Manager (Sequencing)
                └─ Distribution Manager + Analyst (Publication & Monitoring)
```

## Input Specifications

```yaml
content_inventory: file
  content_piece_id: string
  original_url: string
  publish_date: date
  performance_metrics: object
    views: number
    engagement_rate: number
    conversions: number

format_specifications: file
  format_name: string
  channel: array[string]
  required_elements: array[string]
  optional_elements: array[string]
  technical_specs: object

distribution_channels: array[string]
  linkedin
  twitter
  instagram
  email
  podcast
  youtube
  tiktok
  medium

audience_segments: array[object]
  segment_name: string
  characteristics: array[string]
  preferred_formats: array[string]
```

## Output Specifications

```yaml
audit_report:
  top_candidates: array[object]
    content_id: string
    original_performance: object
    repurposing_score: number
    recommended_formats: array[string]

repurposing_plan:
  selected_pieces: array[string]
  format_mapping: object
  timeline: array[object]
  resource_requirements: object

adapted_content: array[object]
  original_id: string
  format: string
  adapted_content: file
  status: enum[draft, approved, published]
  publication_date: date

distribution_log:
  piece_id: string
  channel: string
  publication_url: string
  publication_date: date
  initial_metrics: object
```

## Timeline Example

**Campaign:** Repurpose Q4 Top 10 Content  
**Start Date:** Monday, January 8, 2024

| Phase | Duration | Key Activities | Owner | Timeline |
|-------|----------|---------------|-------|----------|
| Audit | 3 days | Identify top performers, scoring | Analyst | Jan 8-10 |
| Strategy | 2 days | Select pieces, map formats, plan distribution | Strategist | Jan 10-11 |
| Adaptation | 7 days | Convert to 5+ formats per piece | Formatter | Jan 11-18 |
| Enhancement | 3 days | Add updates, SEO optimization | Strategist | Jan 18-20 |
| Sequencing | 2 days | Create calendar, setup tracking | Distribution Mgr | Jan 20-21 |
| Publication | 30 days | Publish sequentially across channels | Distribution Mgr | Jan 22-Feb 20 |
| Monitoring | 30 days | Track performance, optimize | Analyst | Jan 22-Feb 20 |

## Format Adaptation Guidelines

### Blog Post to Infographic
- Identify 3-5 key statistics or conclusions
- Simplify language, use visual hierarchy
- Target length: fits on 1 standard infographic
- Add branding, colors, and icons

### Blog Post to Social Thread
- Break into 5-8 connected posts
- Add engagement hooks and questions
- Include clear CTAs
- Optimize for platform (hashtags, mentions, emojis)

### Blog Post to Email Series
- Break into 3-4 email sequence
- Add personalization opportunities
- Create subject lines that stand alone
- Include strong email-specific CTAs

### Blog Post to Video Script
- Create 15-30 second script for social, 3-5 minute for YouTube
- Use conversational language, reduce jargon
- Add visual cues and B-roll descriptions
- Include on-screen text/captions

## Success Metrics

| Metric | Target |
|--------|--------|
| Content Reuse Ratio | 80% of eligible content repurposed |
| Format Adaptation Quality | 95%+ brand consistency, message accuracy |
| Distribution Completion | 100% scheduled publication rate |
| Engagement Improvement | 10%+ engagement vs original content baseline |
| Channel Expansion | 3+ new channels reached per piece |
| Time Efficiency | 60% faster than creating new content |

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Outdated information | Review all content for current accuracy, add update dates |
| Format fit issues | Include fallback format if primary format not feasible |
| Audience misalignment | Validate audience-channel-format combinations with sample |
| Brand inconsistency | Strict adherence to style guides, approval checkpoints |

## Troubleshooting

**Issue:** Original content underperforms in new formats
- **Solution:** Assess audience fit, test messaging variations, consider alternative formats or audiences

**Issue:** Format adaptation takes longer than expected
- **Solution:** Simplify format specs, increase team allocation, reduce number of concurrent pieces

**Issue:** New channel distribution underperforms
- **Solution:** Analyze audience composition, adjust posting time/frequency, test different CTAs

## Related Documents

- [Content Inventory](../context/content-inventory.md)
- [Channel Strategy](../context/channel-strategy.md)
- [Repurposing Bundle Package](../packages/repurposing-bundle.md)
- [Content Lifecycle Tracker](../workflows/content-lifecycle.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
