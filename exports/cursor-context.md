---
name: Cursor Context Export
description: Guide for exporting ForgeOS content to Cursor IDE
target_platform: Cursor
context_window: 8000-32000
format: Markdown + IDE Configuration
supported_versions: Cursor 0.25+
version: 1.0.0
---

# Cursor Context Export Guide

Cursor integrates AI directly into the development environment, making it ideal for technical runbooks, implementation guides, and architecture documentation.

## Why Cursor?

**Strengths:**
- IDE integration (AI alongside code)
- Codebase awareness and context
- Natural for technical workflows
- Quick access during development
- Perfect for implementation tasks

**Best Use Cases:**
- Technical runbooks and implementation guides
- Coding standards and best practices
- Architecture documentation
- Development workflow guides
- Code review guidelines

## Export Format

### Directory Structure

```
.cursor/
├── knowledge/
│   ├── runbooks/
│   │   ├── blog-post.md
│   │   ├── launch-campaign.md
│   │   └── ...
│   ├── packages/
│   │   ├── blog-post.md
│   │   └── ...
│   ├── workflows/
│   │   ├── qa-checklist-blog.md
│   │   └── ...
│   ├── README.md
│   └── INDEX.md
└── config.json
```

### Configuration File (.cursor/config.json)

```json
{
  "knowledge": {
    "enabled": true,
    "path": ".cursor/knowledge",
    "priority": "high"
  },
  "context": {
    "includePackageJson": true,
    "includeGitignore": true
  },
  "instructions": {
    "codeStyle": ".cursor/knowledge/code-style.md",
    "workflowGuides": ".cursor/knowledge/runbooks",
    "qualityStandards": ".cursor/knowledge/workflows"
  },
  "systemPrompt": "You have access to project knowledge in .cursor/knowledge. Reference these guides when helping with implementation tasks."
}
```

### Manifest File (.cursor/knowledge/INDEX.md)

```markdown
# Cursor Knowledge Base

Generated from ForgeOS on [Date]

## Quick Start
1. Ask Cursor for help with specific tasks
2. Reference relevant runbooks from menu
3. Apply quality standards from QA checklists
4. Use code examples and templates provided

## Contents

### Runbooks
- [Blog Post](./runbooks/blog-post.md) - Blog writing workflow
- [Launch Campaign](./runbooks/launch-campaign.md) - Campaign coordination
- [Strategy Brief](./runbooks/strategy-brief.md) - Strategic planning

### Packages
- [Blog Post Package](./packages/blog-post.md)
- [Launch Campaign Package](./packages/launch-campaign.md)
- [Analyst Report Package](./packages/analyst-report.md)

### Quality Assurance
- [QA Gating System](./workflows/qa-gating.md)
- [Blog QA Checklist](./workflows/qa-checklist-blog.md)
- [Campaign QA Checklist](./workflows/qa-checklist-campaign.md)

## How to Use

### Ask Cursor for Help
```
"I'm following the blog-post runbook. What's the first step?"
```
Cursor will reference the runbook automatically.

### Request Specific Templates
```
"Create a blog post outline using the blog-post package template."
```

### Apply Quality Standards
```
"Review this content against the blog QA checklist."
```

### Get Workflow Guidance
```
"Walk me through the campaign workflow."
```
```

## Installation Steps

### 1. Create Directory Structure
```bash
mkdir -p .cursor/knowledge/{runbooks,packages,workflows}
```

### 2. Export Files
```bash
# Export runbooks
cp runbooks/*.md .cursor/knowledge/runbooks/

# Export packages  
cp packages/*.md .cursor/knowledge/packages/

# Export workflows
cp workflows/*.md .cursor/knowledge/workflows/

# Create manifest
cp INDEX.md .cursor/knowledge/
```

### 3. Add Configuration
```bash
# Create config.json
cat > .cursor/config.json << 'EOF'
{
  "knowledge": {
    "enabled": true,
    "path": ".cursor/knowledge",
    "priority": "high"
  }
}
EOF
```

### 4. Commit to Version Control
```bash
git add .cursor/
git commit -m "Add ForgeOS knowledge base"
```

## Usage Examples

### Example 1: Content Writing Workflow
```
User: "I need to write a blog post about API security. 
Walk me through using the blog-post runbook."

Cursor: [References blog-post.md runbook]
1. Research & Outline (Researcher) - 1 day
2. First Draft (Writer) - 1.5 days
3. Editor Review (Editor) - 1 day
4. Author Refinement (Writer) - 0.5 days
5. SEO Optimization (SEO Optimizer) - 0.5 days

[Provides detailed guidance for each step]
```

### Example 2: Quality Review
```
User: [Pastes blog post text]
"Review this against the blog QA checklist."

Cursor: [References qa-checklist-blog.md]

**Grammar & Language** ✓
✓ No spelling errors
✓ No grammar mistakes
✓ Proper punctuation

**Writing Quality** ⚠️
⚠️ Readability score 75 (target >80)
→ Recommendation: Shorten some sentences
[Specific suggestions]
```

### Example 3: Implementation Guidance
```
User: "I'm working on the campaign launch. What's next?"

Cursor: [References launch-campaign.md runbook]
Based on the workflow, you're in Phase [X].
Next step: [From runbook]
Timeline: [Expected duration]
Success criteria: [From runbook]
```

### Example 4: Template Generation
```
User: "Generate the input specifications for our campaign."

Cursor: [References packages/launch-campaign.md]
[Generates YAML/JSON spec based on package definitions]
```

## Integration with Development

### Git-Based Workflow
```bash
# Check in knowledge base with code
git add .cursor/knowledge/
git commit -m "Update ForgeOS knowledge base"

# Update when ForgeOS changes
git pull origin main
```

### Team Collaboration
```bash
# Everyone on team gets same context
git clone [repo]
# .cursor/knowledge/ automatically available

# Reference shared guidelines
"Following our documented standards, here's the implementation..."
```

### CI/CD Integration
```yaml
# .github/workflows/update-knowledge.yml
name: Update Cursor Knowledge
on:
  push:
    paths:
      - 'runbooks/**'
      - 'packages/**'
      - 'workflows/**'
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Sync knowledge base
        run: cp -r {runbooks,packages,workflows} .cursor/knowledge/
      - name: Commit changes
        run: git add .cursor && git commit -m "Update Cursor knowledge"
```

## Best Practices

### Documentation
- Keep knowledge base synchronized with source
- Update timestamp when exported
- Maintain clear file structure
- Use consistent naming

### Context Management
- Export only relevant documents to each project
- Group related workflows together
- Use comments to explain connections
- Link to external docs (don't duplicate)

### Team Usage
- Document how to access knowledge base
- Provide examples of common questions
- Share tips for getting best results
- Update as standards evolve

## Optimization Tips

### Reducing File Size
- Use minimal export profile
- Exclude heavy assets (images)
- Reference external docs
- Compress with summary sections

### Improving Cursor Accuracy
- Add specific project context
- Include code examples from your projects
- Reference quality standards explicitly
- Ask Cursor to cite which document it's using

### Troubleshooting
- Ensure .cursor/knowledge paths are accessible
- Check file permissions
- Restart Cursor if files updated
- Verify config.json syntax

## Keyboard Shortcuts

```
Ctrl+K          Open chat
Cmd+K (Mac)     Open chat

@runbooks       Reference specific runbook
@packages       Reference specific package
@workflows      Reference QA checklist
@todo           Generate task list
```

## Example Cursor Commands

```
# Implement workflow
"Implement the [runbook-name] workflow for this project"

# Code from template
"Generate code using the [package-name] template"

# Quality review  
"Review this against [qa-checklist-name]"

# Process improvement
"Suggest process improvements using [runbook-name]"

# Documentation
"Write documentation following [runbook-name]"
```

## Related Documents

- [Export Layer README](./README.md)
- [Claude Context Export](./claude-context.md)
- [Copilot Context Export](./copilot-context.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
