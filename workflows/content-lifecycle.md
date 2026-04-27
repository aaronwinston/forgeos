---
name: Content Lifecycle Tracker
description: Framework for tracking content status and lifecycle stages
version: 1.0.0
last_updated: 2024-12-20
layer: workflows
---

# Content Lifecycle Tracker

The Content Lifecycle Tracker defines **status stages** for content throughout production and distribution lifecycle.

## Lifecycle Stages

### 1. Planning
- [ ] Concept approved
- [ ] Objectives defined
- [ ] Timeline established
- [ ] Resources allocated

### 2. Production
- [ ] Content creation started
- [ ] Drafts in progress
- [ ] Supporting assets created
- [ ] Quality reviews scheduled

### 3. QA & Validation
- [ ] Component QA passed
- [ ] Workflow QA passed
- [ ] Compliance review passed
- [ ] Approvals obtained

### 4. Scheduled for Publication
- [ ] Publishing scheduled
- [ ] Distribution plan finalized
- [ ] Analytics configured
- [ ] Team notified

### 5. Published/Active
- [ ] Live on platform(s)
- [ ] Promotion underway
- [ ] Engagement monitoring
- [ ] Performance tracking

### 6. Optimization
- [ ] Performance reviewed
- [ ] Improvements identified
- [ ] Updates deployed
- [ ] Metrics tracked

### 7. Maintenance
- [ ] Regular reviews
- [ ] Updates as needed
- [ ] Links verified
- [ ] Freshness maintained

### 8. Declined/Archived
- [ ] Content deprecated
- [ ] Replaced by newer version
- [ ] Redirects configured
- [ ] Historical record retained

## Status Transitions

```
Planning
   ↓
Production → [Revisions]
   ↓
QA & Validation → [Revisions]
   ↓
Scheduled
   ↓
Published/Active
   ├─→ Optimization
   │   └─→ Maintenance
   │       └─→ Archived
   └─→ Declined
```

## Tracking Template

### Spreadsheet Columns

| ID | Title | Type | Status | Owner | Published | Views | Engagement | Next Review |
|----|-------|------|--------|-------|-----------|-------|------------|-------------|
| cp-001 | Blog Title | Blog | Active | Author | Date | X | Y% | Date |

### Metadata per Content Piece

```yaml
id: cp-001
title: "Blog Post Title"
type: "blog | campaign | social | report | other"
format: "blog | video | infographic | social | email"
publish_date: "2024-01-15"
last_updated: "2024-01-20"
owner: "Name"
status: "active | archived | scheduled | draft"

metrics:
  views: 150
  engagement_rate: 3.2%
  avg_time_on_page: 2:15
  conversions: 5
  
next_action: "Schedule optimization update"
next_review_date: "2024-02-15"
```

## Key Status Definitions

### Planning
Content is being scoped and approved. Work hasn't started yet.

### Production  
Content is being created. Drafts exist, reviews ongoing.

### QA & Validation
Content is being reviewed against quality standards. No publication until approved.

### Scheduled for Publication
Content approved, publication date scheduled, distribution plan ready.

### Published/Active
Content is live. Promotion underway, performance tracked.

### Optimization
Content underperforming or has improvements identified. Updates in progress.

### Maintenance
Content is mature, stable. Regular checks for freshness, link validity.

### Archived/Declined
Content deprecated, replaced by newer version, or decided not to publish.

## Lifecycle by Content Type

### Blog Post Lifecycle
1. Planning (1-2 days)
2. Production (3-5 days) 
3. QA (1-2 days)
4. Scheduled (1 week before publish)
5. Published (day 1)
6. Active (weeks 1-4)
7. Maintenance (months 2-12+)
8. Optimized/Archived (6-12 months)

### Campaign Lifecycle
1. Planning (1-2 weeks)
2. Production (3-4 weeks)
3. QA (1-2 weeks)
4. Scheduled (1-2 weeks pre-launch)
5. Published (launch day)
6. Active (4-6 weeks)
7. Optimization (ongoing during active)
8. Closed (post-campaign analysis)

### Social Post Lifecycle
1. Planning (1 day)
2. Production (1 day)
3. QA (< 1 day)
4. Scheduled (1-2 days pre-post)
5. Published (post day)
6. Active (1-7 days)
7. Engagement monitoring (optional)

## Tracking Methods

### Method 1: Spreadsheet (Simple)
- Google Sheets, Excel, or Airtable
- Columns: ID, Title, Type, Status, Owner, Dates, Metrics
- Updated manually
- Shareable with team

### Method 2: Issue Tracker (Development)
- GitHub Issues, Jira, or Linear
- Each content piece = issue
- Status = issue status
- Comments = updates
- Automated workflows

### Method 3: Content Management System
- Built-in lifecycle tracking
- Automatic status transitions
- Approval workflows
- Publishing calendar

### Method 4: Custom Database
- Airtable, Notion, or custom app
- Flexible schema
- Custom workflows
- Reporting and dashboards

## Review Frequency by Status

| Status | Review Frequency |
|--------|-----------------|
| Planning | Weekly |
| Production | Bi-weekly |
| QA | Daily |
| Scheduled | 3x week |
| Active | Daily |
| Optimization | Weekly |
| Maintenance | Monthly |

## Metrics to Track

### During Production
- Completion %
- QA review status
- On-schedule indicator

### During Publication
- Publishing status
- Distribution completion %
- Promotion activity

### During Active Phase
- Views/impressions
- Engagement rate
- Click-through rate
- Conversion rate
- Time on page
- Bounce rate

### Quarterly
- Total content inventory
- Performance distribution
- ROI/cost-per-result
- Optimization opportunities

## Automation Opportunities

### Automatic Status Updates
```
- Status changes when moved between project columns
- Approval signatures trigger status advancement
- Scheduled posts auto-advance on publish date
- Analytics triggers optimization flag
```

### Reporting
```
- Daily: Items completing QA
- Weekly: Performance summary
- Monthly: Portfolio analysis
- Quarterly: Strategic review
```

### Alerts
```
- Red flag: Content >6 months old without update
- Warning: Performance declining
- Info: Anniversary of publication (consider refreshing)
- Action needed: Scheduled item approaching publish date
```

## Related Documents

- [QA Gating System](./qa-gating.md)
- [Content Audit Runbook](../runbooks/content-audit.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
