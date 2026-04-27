---
name: Claude Context Export
description: Guide for exporting ForgeOS content to Claude (Anthropic)
target_platform: Claude
context_window: 200000
format: Markdown + System Prompts
supported_versions: Claude 3 Opus, Claude 3 Sonnet
version: 1.0.0
---

# Claude Context Export Guide

Claude's 200K token context window makes it ideal for exporting comprehensive ForgeOS packages, full runbooks, and complete campaign briefs.

## Why Claude?

**Strengths:**
- Largest context window (200K tokens = ~150,000 words)
- Excellent at complex reasoning and synthesis
- Great for analyzing relationships across documents
- Supports long narratives and detailed examples
- Strong at following detailed instructions

**Best Use Cases:**
- Complete campaign packages (end-to-end export)
- Multi-runbook workflows
- Comprehensive research briefs
- Cross-document analysis
- Strategic planning and synthesis

## Export Format

### Structure

```markdown
# [Document Title]

**Source:** ForgeOS  
**Exported:** [Date]  
**Version:** [Version]  

## Overview
[Brief description of content]

## Related Documents
[List of related documents in this export]

---

## [Main Content Sections]

[Full content, preserving all formatting]

---

## Related Context
[Links to related ForgeOS documents not included in export]

---

**Export Notes:**
[Any customizations or special instructions]
```

### System Prompt Template

```
You are an AI assistant with access to ForgeOS content.

## Your Role
You have been provided with the following ForgeOS materials:
- [List materials]

## Context
These materials contain:
- Runbooks for content production workflows
- Package definitions for deliverable bundles
- Quality assurance checklists
- Strategic guidelines and frameworks

## How to Use This Information
1. Reference specific runbooks when discussing workflows
2. Recommend appropriate packages for different content goals
3. Apply quality standards from QA checklists
4. Provide examples from the included materials
5. Cross-reference related documents

## Important Guidelines
- Always cite source from ForgeOS materials when relevant
- Maintain brand voice and tone from guidelines
- Follow quality standards defined in checklists
- Suggest appropriate runbooks/packages for tasks
- Flag when something falls outside documented processes

## Questions to Ask
When users request help with content:
1. What is the business objective?
2. What is the target audience?
3. What timeline/resources available?
4. What packages or runbooks apply?
5. What quality standards apply?
```

## Typical Exports to Claude

### Export 1: Single Runbook
**Size:** ~3,000-5,000 tokens  
**Use:** Implement specific workflow  
**Include:**
- Runbook content
- Related QA checklist
- Input/output specs
- Example timeline

**Example:**
```
$ export-to-claude runbooks/blog-post.md \
  --include qa-checklist-blog.md \
  --format minimal
```

### Export 2: Campaign Package
**Size:** ~8,000-12,000 tokens  
**Use:** Execute complete campaign  
**Include:**
- Campaign package
- Related runbook
- QA checklist
- Success criteria

**Example:**
```
$ export-to-claude packages/launch-campaign.md \
  --include runbooks/launch-campaign.md \
  --include workflows/qa-checklist-campaign.md \
  --format standard
```

### Export 3: Complete Campaign Kit
**Size:** ~25,000-35,000 tokens  
**Use:** Comprehensive campaign management  
**Include:**
- Campaign package
- All related runbooks
- All related QA checklists
- Context bundles (audience, market, brand)

**Example:**
```
$ export-to-claude packages/launch-campaign.md \
  --include-all-related \
  --format full \
  --with-context brand-voice,target-audience
```

### Export 4: Strategic Analysis
**Size:** ~15,000-25,000 tokens  
**Use:** Strategic planning and synthesis  
**Include:**
- Strategy brief runbook
- Related context (market, competitive)
- QA checklist for positioning
- Example strategy briefs

**Example:**
```
$ export-to-claude runbooks/strategy-brief.md \
  --include context/market-research.md \
  --include context/competitive-analysis.md \
  --format full
```

## Preparation Steps

1. **Identify Content**
   - Select primary document(s)
   - List related documents to include
   - Determine export scope

2. **Gather Materials**
   - Export markdown file(s)
   - Collect visual assets (if any)
   - Prepare metadata

3. **Create System Prompt**
   - Customize template above
   - Add specific instructions
   - Include context from ForgeOS

4. **Format for Claude**
   - Use proper markdown structure
   - Ensure headings are clear
   - Include table of contents for large exports
   - Add navigation links

5. **Test Export**
   - Paste into Claude conversation
   - Test system prompt
   - Verify formatting
   - Check token count

## Usage Patterns with Claude

### Pattern 1: Review & Feedback
```
User: "I've written a blog post. Here's [export blog-post.md and 
qa-checklist-blog.md]. Please review it against the quality standards."

Claude: [Uses QA checklist to evaluate blog post systematically]
```

### Pattern 2: Workflow Execution
```
User: "I need to create a launch campaign for our new product. 
Here are [export launch-campaign package and runbook]. Can you help 
me structure the work?"

Claude: [Uses runbook to create step-by-step plan, references package for 
deliverables]
```

### Pattern 3: Content Synthesis
```
User: "I need to create a strategy brief about entering the European 
market. Here are [export strategy-brief runbook and related research 
context]. Help me structure the analysis."

Claude: [Uses runbook methodology + research context to guide analysis]
```

### Pattern 4: Continuous Assistance
```
User: [Pastes complete campaign kit] "Walk me through executing this 
campaign step by step."

Claude: [Uses full context to provide detailed guidance throughout workflow]
```

## Optimization Tips

### Token Efficiency
- Export minimal + standard profiles rather than full for routine use
- Use full profile only for comprehensive strategic work
- Reference external links for related docs (don't include)

### Conversation Management
- Start with system prompt + primary document
- Add related documents as needed in conversation
- Use Claude's memory for multi-turn conversations

### Better Outputs
- Provide specific context upfront (audience, constraints, goals)
- Ask Claude to reference specific checklists or sections
- Request structured outputs (templates, tables, step-by-step)

### Quality Assurance
- Ask Claude to cite which QA items it's checking
- Request traceability back to original checklists
- Have Claude suggest improvements using standard criteria

## Example Conversation

```
User: [Pastes: blog-post.md + qa-checklist-blog.md + system prompt]

System Prompt: You are an editor evaluating blog posts using the ForgeOS 
quality standards...

---

User: "I'm planning to write a blog post about AI in marketing. Walk me 
through the process using the blog-post runbook."

Claude: "Based on the blog-post runbook, here's the 5-step workflow:

1. **Research & Outline** (Researcher) - 1 day
   - Conduct topic research
   - Create 5-7 section outline
   - Gather sources
   [Continues with full breakdown from runbook]

2. **First Draft** (Writer) - 1.5 days
   [Details from runbook]

[Continues for all 5 steps]"

---

User: "I've completed my draft. Here it is: [Pastes draft]"

Claude: "Let me evaluate this against the QA checklist...

**Grammar & Language** ✓
- No spelling errors
- Tone matches brand voice
- Sentence structure varied
[Details for each item in checklist]

**SEO Optimization** - Minor issues
- Meta description could be more compelling
- Add 2-3 internal links (currently has 2)
[Specific recommendations]"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Content truncated | Reduce export scope, export related docs separately |
| Formatting issues | Check markdown syntax, use backticks for code blocks |
| Claude forgets context | Re-paste system prompt and primary doc if conversation gets long |
| Token count too high | Use minimal export profile, exclude heavy assets |
| Claude gives wrong guidance | Verify system prompt was included, paste checklist again |

## Related Documents

- [Export Layer README](./README.md)
- [ChatGPT Context Export](./chatgpt-context.md)
- [Cursor Context Export](./cursor-context.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
