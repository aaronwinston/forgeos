---
name: ChatGPT Context Export
description: Guide for exporting ForgeOS content to ChatGPT and Custom GPTs
target_platform: ChatGPT
context_window: 8000-128000
format: Markdown + System Prompts
supported_versions: ChatGPT Plus, GPT-4
version: 1.0.0
---

# ChatGPT Context Export Guide

ChatGPT's broad accessibility makes it ideal for quick consultations, team collaboration, and creating reusable Custom GPTs.

## Why ChatGPT?

**Strengths:**
- Widely available (web, mobile, API)
- Simple to use (no special setup)
- Create Custom GPTs for reuse
- Share with non-technical team members
- Good reasoning and writing abilities

**Best Use Cases:**
- Quick content consultation
- Team feedback and brainstorming
- Creating Custom GPTs for specific roles
- Knowledge sharing with external teams
- Testing and iteration

## Export Formats

### 1. Direct Conversation Export

Paste markdown content directly into ChatGPT conversation.

**Steps:**
1. Copy markdown from runbook/package/checklist
2. Open ChatGPT conversation
3. Paste content
4. Add your question/request
5. Let ChatGPT provide guidance

### 2. Custom GPT Creation

Build specialized GPTs for specific domains.

**Custom GPT Template:**
```
Name: ForgeOS Content Assistant
Description: Helps create content following ForgeOS standards and runbooks
Instructions:
  You have been provided ForgeOS content creation runbooks, packages, and QA checklists.
  
  When helping with content creation:
  1. Reference specific runbooks for workflows
  2. Apply QA standards from checklists
  3. Use package definitions for deliverables
  4. Suggest improvements based on standards
  
  Always cite which document you're referencing.
  
Knowledge Files:
  - All runbooks (PDF or markdown)
  - All packages (PDF or markdown)
  - All QA checklists (PDF or markdown)
  
Capabilities:
  - Guide content creation workflows
  - Review content against standards
  - Suggest process improvements
  - Recommend appropriate tools/templates
```

## Export Process

### Export 1: Single Document

```
Steps:
1. Copy markdown from source file
2. Open ChatGPT
3. Paste content
4. Add system message: 
   "You have access to [document name]. Use it to answer my questions."
5. Ask your question
```

### Export 2: Complete Knowledge Base

```
Steps:
1. Combine files: cat runbooks/*.md packages/*.md workflows/*.md > combined.md
2. Create Custom GPT
3. Upload combined.md as knowledge file
4. Add system prompt (see template above)
5. Share link with team
```

### Export 3: Conversation Starter

```
Steps:
1. Copy runbook for task
2. Paste into ChatGPT
3. Ask: "Walk me through this workflow step by step"
4. ChatGPT provides guidance with examples
5. Continue conversation as needed
```

## Custom GPT Examples

### Example 1: Blog Writer Assistant

```
Name: Blog Writer Assistant (ForgeOS)
Description: Helps write and review blog posts using ForgeOS standards

System Prompt:
"You are a blog writing assistant using ForgeOS blog-post runbook and QA standards.

When helping with blogs:
1. Guide through the 5-step workflow (Research, Draft, Edit, Refine, SEO)
2. Apply grammar and tone standards
3. Check SEO optimization
4. Review against blog QA checklist
5. Provide specific improvements

Always reference specific steps from runbook and checklist items."

Knowledge Files:
- runbooks/blog-post.md
- packages/blog-post.md
- workflows/qa-checklist-blog.md
```

### Example 2: Campaign Manager

```
Name: Campaign Manager (ForgeOS)
Description: Helps plan and execute multi-channel campaigns

System Prompt:
"You are a campaign planning assistant using ForgeOS campaign workflows.

When helping with campaigns:
1. Break down launch-campaign.md into executable phases
2. Create timeline and milestones
3. Recommend content components from package
4. Apply quality standards from campaign checklist
5. Suggest optimizations based on patterns

Reference specific sections from runbooks and packages."

Knowledge Files:
- runbooks/launch-campaign.md
- packages/launch-campaign.md
- workflows/qa-checklist-campaign.md
```

### Example 3: Content Strategist

```
Name: Content Strategist (ForgeOS)
Description: Strategic planning and content portfolio management

System Prompt:
"You are a content strategist using ForgeOS frameworks.

Available workflows:
- Content audit (quarterly review)
- Strategic positioning (planning)
- Content repurposing (maximizing ROI)

When helping with strategy:
1. Apply relevant runbook methodology
2. Reference data from audit findings
3. Suggest packages and formats
4. Create implementation roadmaps
5. Define success metrics

Always root recommendations in runbooks."

Knowledge Files:
- runbooks/content-audit.md
- runbooks/repurposing-campaign.md
- runbooks/strategy-brief.md
- packages/analyst-report.md
```

## Usage Examples

### Scenario 1: Quick Content Review

```
User: [Pastes blog post]
"Review this blog post against the ForgeOS blog QA checklist. 
What needs improvement?"

ChatGPT: [References qa-checklist-blog.md]
**Grammar & Language** ✓
- No spelling errors
- Tone matches brand voice
- Sentence structure varied

**Writing Quality** ⚠️
- Readability could be higher
- [Specific recommendations]

[Continues through checklist items]
```

### Scenario 2: Workflow Guidance

```
User: "I need to create a launch campaign. Walk me through 
the process using the ForgeOS runbook."

ChatGPT: [References launch-campaign.md]
"The launch-campaign runbook has 4 phases:

Phase 1: Strategic Planning (Weeks 1-2)
- Campaign strategy development
- Creative brief creation
[Details from runbook]

Phase 2: Content Creation (Weeks 3-4)
[Continues for all phases]"
```

### Scenario 3: Template Generation

```
User: "Generate an email template for a campaign launch 
email using the campaign package specs."

ChatGPT: [References packages/launch-campaign.md]
[Generates email HTML based on package specifications]
```

### Scenario 4: Team Brainstorming

```
User: [Shares link to Custom GPT]
"Here's our content assistant. Use it to brainstorm 
campaign ideas for Q4."

Team Members: [Access Custom GPT]
- Ask about audience targeting
- Request content recommendations
- Review against quality standards
- Get timeline estimates
```

## Creating Custom GPT

### Steps

1. **Open ChatGPT Settings**
   - Click "Explore" in ChatGPT
   - Select "Create a GPT"

2. **Configure Basic Info**
   - Name: [GPT Name]
   - Description: [What it does]
   - Instructions: [System prompt from template above]

3. **Upload Knowledge Files**
   - Click "Upload files"
   - Select markdown or PDF files
   - ForgeOS files recommended:
     - Relevant runbooks
     - Relevant packages
     - Relevant QA checklists

4. **Set Capabilities**
   - Enable: Web Browsing (optional)
   - Enable: Code Interpreter (optional)
   - Enable: File Upload (recommended)

5. **Create & Share**
   - Click "Create"
   - Test with sample questions
   - Copy link to share with team

## Sharing Custom GPTs

### Internal Team Use
```
1. Create Custom GPT (see above)
2. Share link in team Slack/email
3. Team members access via ChatGPT Plus subscription
4. No additional setup needed
```

### External Collaboration
```
1. Create Custom GPT
2. Publish as "Anyone with link"
3. Share link with external partners/clients
4. They don't need ChatGPT subscription to use
```

### Client Delivery
```
1. Create Custom GPT with your company branding
2. Remove sensitive internal content
3. Upload client-specific examples
4. Share as deliverable/training tool
```

## Best Practices

### Conversation Flow
- Start with context (what you're trying to achieve)
- Ask for step-by-step guidance
- Reference specific documents
- Request templates and examples
- Save good conversations (pin to custom GPT)

### Custom GPT Maintenance
- Update knowledge files quarterly
- Test regularly with sample questions
- Refine system prompt based on usage
- Document common issues and improvements
- Share best practices with team

### Team Adoption
- Create team-specific Custom GPTs
- Provide training on how to use
- Share example questions
- Encourage team to contribute improvements
- Track usage and feedback

## Limitations

| Limitation | Workaround |
|-----------|-----------|
| Context window (8-128K) | Split large documents, reference external links |
| Cannot modify uploaded files | Keep knowledge files outside Chat, update manually |
| No real-time sync | Periodically update knowledge files |
| Limited to text input | Use API for programmatic access if needed |

## Advanced Usage

### API Access (Developers)

```python
import openai

# Use Custom GPT via API
client = openai.OpenAI()

response = client.chat.completions.create(
  model="gpt-4",
  messages=[
    {
      "role": "system",
      "content": "You have access to ForgeOS runbooks..."
    },
    {
      "role": "user",
      "content": "Walk me through the blog post workflow"
    }
  ]
)
```

### Zapier Integration (No-Code)

```
1. Set up Zapier
2. Create trigger (e.g., "New Slack message with @gpt-assist")
3. Add ChatGPT action with your Custom GPT
4. Route response back to Slack
5. Team can get instant assistance in Slack
```

## Related Documents

- [Export Layer README](./README.md)
- [Claude Context Export](./claude-context.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
