---
name: Content Audit & Optimization
description: Systematic quarterly review, analysis, and optimization of existing content across all channels
agents_required: [Analyst, Strategist, Writer, Editor]
context_required: [Content Inventory, Performance Data, SEO Rankings, Audience Behavior, Competitive Analysis]
estimated_duration: 2-3 weeks per cycle
success_metrics: [Audit Coverage >90%, Optimization Plan Created, 80%+ Implementation Rate, Traffic Lift Target Met]
version: 1.0.0
qa_checklist: qa-checklist-content-audit.md
---

## Overview

This runbook defines the process for systematically reviewing all published content, analyzing performance, identifying improvement opportunities, and executing optimization campaigns. Typically run quarterly or semi-annually.

**When to use:** Regular cadence (quarterly), in response to algorithm changes, during off-peak content creation periods, before major campaign launches

**Prerequisites:**
- 6+ months of performance data available
- Analytics infrastructure in place
- SEO tracking tools configured
- Content management system accessible

## Workflow Steps

### Phase 1: Inventory & Data Collection (3-5 days)

#### Step 1.1: Content Inventory Audit (Analyst)
**Duration:** 2-3 days

**Responsibilities:**
- Catalog all published content (blog, pages, resources, guides)
- Verify accuracy of metadata
- Collect content asset metadata (publish date, author, topic, format)
- Identify orphaned or duplicate content
- Document current publishing locations

**Inputs:**
- Content management system access
- Site crawl/sitemap data
- Analytics account access

**Outputs:**
- Complete content inventory spreadsheet:
  - URL
  - Title
  - Publish date
  - Last update date
  - Primary topic/keyword
  - Content type
  - Current location(s)
  - Performance metrics stub

**QA Gate:** Inventory completeness verified (>90% coverage)

#### Step 1.2: Performance Data Compilation (Analyst)
**Duration:** 2-3 days (concurrent)

**Responsibilities:**
- Extract 12-month performance metrics per piece
- Gather SEO data (rankings, organic traffic, backlinks)
- Collect engagement metrics (bounce rate, time on page, scroll depth)
- Consolidate conversion/goal data
- Calculate performance trends

**Inputs:**
- Google Analytics data
- Search Console data
- Email engagement data (if applicable)
- Social analytics
- Conversion data

**Outputs:**
- Performance dataset:
  - Organic traffic (12-month)
  - Bounce rate and scroll depth
  - Average time on page
  - Conversions/goals
  - Top keywords and rankings
  - Backlink count
  - Traffic trend (increasing/declining/flat)
  - Revenue attributed (if tracked)

**QA Gate:** Data accuracy spot-checked, gaps identified and documented

### Phase 2: Analysis & Scoring (5-7 days)

#### Step 2.1: Content Performance Analysis (Analyst)
**Duration:** 3-4 days

**Responsibilities:**
- Score content on multiple dimensions:
  - Traffic performance (vs. benchmark)
  - Engagement quality (bounce rate, time on page)
  - Conversion effectiveness
  - SEO health (rankings, backlinks)
  - Freshness (time since last update)
  - Format quality (mobile optimization, readability)
- Create performance tiers (Top, Middle, Low)
- Identify underperforming content by type
- Analyze traffic trends and decline patterns
- Benchmark against industry standards

**Inputs:**
- Inventory spreadsheet
- Performance dataset
- Historical benchmarks
- Content type standards

**Outputs:**
- Scoring model and results
- Performance tier breakdown
- Traffic analysis report
- Content type performance comparison
- Trend analysis (growth vs. decline)
- Top opportunities for improvement list

**QA Gate:** Scoring methodology reviewed, outliers investigated

#### Step 2.2: Optimization Opportunity Assessment (Strategist + Analyst)
**Duration:** 2-3 days

**Responsibilities:**
- Categorize content by improvement opportunity:
  - Quick wins (minor updates → significant impact)
  - Content refresh (update data, add new sections)
  - Format changes (convert to different format)
  - Restructure/rewrite (major content overhaul)
  - Repurpose (adapt to new channel)
  - Archive/Delete (no longer relevant)
- Assess keyword gaps and expansion opportunities
- Identify cross-linking opportunities
- Recommend consolidation (merge similar topics)
- Suggest new content gaps to fill

**Inputs:**
- Performance scoring results
- Current keyword rankings
- Traffic analysis
- Competitive analysis
- Audience research

**Outputs:**
- Optimization opportunity matrix:
  - Content ID
  - Current performance tier
  - Recommended action
  - Expected impact
  - Effort estimate
  - Priority score
- Gap analysis and new content recommendations
- Cross-linking opportunities map
- Consolidation recommendations

**QA Gate:** Recommendations reviewed for feasibility and impact potential

### Phase 3: Optimization Planning (3-5 days)

#### Step 3.1: Optimization Roadmap Creation (Strategist)
**Duration:** 2-3 days

**Responsibilities:**
- Prioritize optimization opportunities (impact vs. effort matrix)
- Create implementation timeline (3-month rolling window)
- Allocate resources (Writer, Editor, Designer)
- Identify quick wins for immediate execution
- Plan rollout sequence

**Inputs:**
- Optimization opportunity matrix
- Resource availability
- Content calendar
- Budget constraints

**Outputs:**
- Optimization roadmap:
  - Batch 1 (Quick wins: 5-7 pieces)
  - Batch 2 (Medium effort: 5-7 pieces)
  - Batch 3 (Major revamps: 2-3 pieces)
  - Timeline and resource allocation
- Resource requirements summary
- Expected impact projection
- Implementation checklist

**QA Gate:** Roadmap feasibility assessed, stakeholder approval obtained

#### Step 3.2: Detailed Optimization Specifications (Writer + Strategist)
**Duration:** 1-2 days

**Responsibilities:**
- Create detailed optimization briefs for each piece in Batch 1
- Document specific changes needed:
  - Keywords to add/strengthen
  - Sections to add/remove/rewrite
  - Data to update
  - Format improvements
  - Internal/external links to add
  - Visual enhancements

**Inputs:**
- Optimization roadmap
- SEO analysis
- Performance data
- Competitive analysis
- Current content

**Outputs:**
- Optimization brief per piece (template):
  - Current URL and stats
  - Recommended title/meta changes
  - Keyword targets (primary + secondary)
  - Content changes needed
  - New sections to add
  - Data/statistics to update
  - Internal linking opportunities
  - Visual improvements
  - Timeline estimate
  - Success metrics post-optimization

**QA Gate:** Briefs reviewed for completeness and accuracy

### Phase 4: Optimization Execution (Ongoing)

#### Step 4.1: Content Updates (Writer + Editor)
**Duration:** Ongoing per timeline

**Responsibilities:**
- Execute optimization briefs in priority order
- Update content with new/improved sections
- Refresh data and statistics
- Optimize for keywords naturally
- Improve structure and readability
- Add internal links

**Inputs:**
- Optimization briefs
- Current content
- Research and data sources
- Style guides

**Outputs:**
- Updated content versions
- Update log (what was changed and why)
- Keyword optimization report
- Internal linking additions

**QA Gate:** Content reviewed for quality, accuracy, keyword integration

#### Step 4.2: Performance Monitoring (Analyst)
**Duration:** Ongoing (3-4 weeks post-update)

**Responsibilities:**
- Monitor ranking changes
- Track traffic impact
- Analyze engagement improvements
- Document results in tracking spreadsheet
- Adjust approach if needed

**Inputs:**
- Updated content URLs
- Performance baseline
- Analytics setup

**Outputs:**
- Performance monitoring report:
  - Ranking changes (4 weeks post-update)
  - Traffic impact vs. baseline
  - Engagement metric changes
  - Conversion impact (if applicable)
  - ROI analysis
- Lessons learned and insights
- Recommendations for similar content

**QA Gate:** Results documented, insights extracted

## Audit Scorecard Template

| Content ID | Title | Type | Traffic | Engagement | Conversions | SEO Health | Freshness | Overall Score | Tier | Recommendation |
|------------|-------|------|---------|------------|-------------|-----------|-----------|---------------|------|-----------------|
| cp-001 | Blog Post | Blog | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 3.4/5 | Top | Maintain + Refresh Data |
| cp-002 | Guide | Guide | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐ | 1.2/5 | Low | Consider Archive |
| cp-003 | Resource | Resource | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | 3.0/5 | Middle | Major Refresh |

## Optimization Action Categories

### 🎯 Quick Wins (2-4 hours each)
- Update statistics and data
- Add new research or case studies
- Refresh publication date (last updated)
- Add/improve internal links
- Update CTAs

### ⚙️ Content Refreshes (4-8 hours each)
- Add new section with recent developments
- Improve structure and readability
- Rewrite introduction/summary
- Add visual elements
- Update examples

### 🔄 Major Revamps (8-16 hours each)
- Complete rewrite for keyword optimization
- Significant structural changes
- Consolidate with related content
- Format conversion (e.g., guide to interactive tool)
- Add interactive elements

## Agent Sequence

```
Analyst (Inventory + Data Collection)
├─ Analyst (Performance Analysis)
    └─ Strategist + Analyst (Opportunity Assessment)
        └─ Strategist (Roadmap Planning)
            └─ Writer + Strategist (Optimization Specs)
                └─ Writer + Editor (Content Updates)
                    └─ Analyst (Performance Monitoring)
```

## Timeline Example

**Audit Cycle:** Q1 2024 (January-March)

| Phase | Week | Key Activities | Owner |
|-------|------|----------------|-------|
| Inventory | W1 | Audit inventory, collect data | Analyst |
| Analysis | W2-3 | Analyze performance, identify opportunities | Analyst, Strategist |
| Planning | W3-4 | Create roadmap, write briefs | Strategist, Writer |
| Execution | W4-12 | Execute optimization batches | Writer, Editor |
| Monitoring | Ongoing | Track performance improvements | Analyst |

## Success Metrics

| Metric | Target |
|--------|--------|
| Audit Coverage | >90% of published content |
| Optimization Plan Completion | 100% planning phase |
| Implementation Rate | 80%+ of planned content updated within 90 days |
| Average Traffic Lift | +15% organic traffic post-optimization |
| Ranking Improvements | +5 positions average on target keywords |
| Engagement Improvement | +10% average time on page |
| Bounce Rate Reduction | -5% bounce rate |

## Content Archival Criteria

Archive content if:
- Zero traffic for 12+ months
- Ranking on no keywords with search volume
- Outdated/inaccurate information that's difficult to update
- Duplicate of higher-performing content on same topic
- No strategic value for SEO or audience engagement

## Related Documents

- [Content Inventory](../context/content-inventory.md)
- [Performance Benchmarks](../context/performance-benchmarks.md)
- [SEO Guidelines](../context/)
- [Content Lifecycle Tracker](../workflows/content-lifecycle.md)
- [QA Checklist for Content Audit](../workflows/qa-checklist-audit.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
