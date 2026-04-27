---
name: Blog Post Production
description: End-to-end workflow for creating and publishing a blog post
agents_required: [Researcher, Writer, Editor, SEO Optimizer]
context_required: [Brand Voice, Content Calendar, Target Audience, Topic Research]
estimated_duration: 3-5 business days
success_metrics: [Grammar/Spelling Score >95%, SEO Readability Pass, Editorial Approval, Schedule Compliance]
version: 1.0.0
qa_checklist: qa-checklist-blog.md
---

## Overview

This runbook orchestrates the complete blog post production process from ideation through publication. It ensures consistency, quality, and brand alignment across all published content.

**When to use:** Creating standalone articles, research pieces, or thought leadership content

**Prerequisites:**
- Topic approved in editorial calendar
- Target audience identified
- Brand voice guidelines reviewed

## Workflow Steps

### 1. Research & Outline (Researcher)
**Duration:** 1 day

**Responsibilities:**
- Conduct topic research
- Identify key arguments and supporting evidence
- Create structured outline
- Gather source materials and citations

**Inputs:**
- Topic name
- Target audience description
- Desired article length (800-2000 words)
- Success criteria from editorial calendar

**Outputs:**
- Detailed outline (5-7 main sections)
- Source materials document
- Key statistics and citations
- Handoff notes for writer

**QA Gate:** Outline reviewed for completeness and accuracy

### 2. First Draft (Writer)
**Duration:** 1.5 days

**Responsibilities:**
- Write article following outline
- Maintain brand voice and tone
- Include citations and links
- Incorporate SEO keywords naturally

**Inputs:**
- Outline from Researcher
- Brand voice guidelines
- SEO keyword targets
- Source materials

**Outputs:**
- Full draft article (1500-2000 words)
- Internal comments on sections needing review
- Embedded citations

**QA Gate:** Draft checked for completeness and coherence

### 3. Editor Review & Revision (Editor)
**Duration:** 1 day

**Responsibilities:**
- Review for grammar, clarity, and style
- Ensure brand voice consistency
- Improve readability and flow
- Add/remove content for balance

**Inputs:**
- Full draft from Writer
- Brand guidelines
- Previous published articles for style reference

**Outputs:**
- Edited version with track changes
- Detailed editorial comments
- Fact-check summary
- Revised draft ready for author review

**QA Gate:** Grammar/spelling score >95%, all changes justified

### 4. Author Review & Refinement (Writer)
**Duration:** 0.5 days

**Responsibilities:**
- Review editorial changes
- Resolve editor comments
- Finalize content with corrections

**Inputs:**
- Edited draft with comments
- Editorial feedback

**Outputs:**
- Final author-approved draft
- Comment resolution log

**QA Gate:** Author sign-off obtained

### 5. SEO & Meta Optimization (SEO Optimizer)
**Duration:** 0.5 days

**Responsibilities:**
- Optimize meta description
- Review keyword distribution
- Ensure readability score acceptable
- Create social preview text

**Inputs:**
- Final draft
- SEO keyword targets
- Article title

**Outputs:**
- Optimized meta description (155 chars)
- Social media preview text
- Final SEO score report
- Publishing checklist

**QA Gate:** SEO readability pass, keyword integration acceptable

## Agent Sequence

```
Researcher → Writer → Editor → Writer (refinement) → SEO Optimizer → Published
```

## Input Specifications

```yaml
topic_name: string
target_audience: string
desired_length: "800-2000 words"
seo_keywords: array[string]
publish_date: date
internal_notes: string
```

## Output Specifications

```yaml
blog_post:
  title: string
  slug: string
  content: markdown
  meta_description: string
  seo_score: number (0-100)
  word_count: number
  
publication_assets:
  social_preview_text: string
  featured_image_alt_text: string
  internal_links: array[object]
  
metadata:
  author: string
  publish_date: date
  tags: array[string]
  category: string
```

## Timeline Example

**Topic:** "Scaling ML Teams in 2024"  
**Publish Date:** Friday, January 10, 2024

| Phase | Owner | Start | Duration | Notes |
|-------|-------|-------|----------|-------|
| Research | Researcher | Tue, Jan 2 | 1 day | Complete by Wed evening |
| Draft | Writer | Wed, Jan 3 | 1.5 days | Submit for review Thu evening |
| Editorial Review | Editor | Fri, Jan 4 | 1 day | Return with comments Fri afternoon |
| Author Refinement | Writer | Mon, Jan 7 | 0.5 days | Resolve comments by Mon afternoon |
| SEO Optimization | SEO Optimizer | Mon, Jan 7 | 0.5 days | Publish ready Tue morning |
| Publishing | Publisher | Tue, Jan 8 | 1 day | Live by Wed morning |

## Troubleshooting

**Issue:** Topic requires more research than anticipated
- **Solution:** Contact Researcher immediately, adjust timeline, request extended deadline if needed

**Issue:** Editor and Writer disagree on direction
- **Solution:** Schedule 30-min sync call, Editor makes final call on structural changes

**Issue:** Final draft exceeds SEO readability standards
- **Solution:** Editor and Writer collaborate to simplify, shorten sentences, remove jargon

**Issue:** Publishing date approaches and article incomplete
- **Solution:** Escalate to Editorial Lead for deadline adjustment or deprioritization decision

## Related Documents

- [QA Checklist for Blog Posts](../workflows/qa-checklist-blog.md)
- [Content Calendar](../context/)
- [Brand Voice Guidelines](../context/)
- [Blog Post Package](../packages/blog-post.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
