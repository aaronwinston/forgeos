---
name: Copilot Context Export
description: Guide for exporting ForgeOS content to GitHub Copilot
target_platform: GitHub Copilot
context_window: 8000-32000
format: Markdown + Copilot Configuration
supported_versions: Copilot 1.0+
version: 1.0.0
---

# Copilot Context Export Guide

GitHub Copilot integration enables AI assistance within development workflows and GitHub-native tools, perfect for enterprise teams using GitHub.

## Why Copilot?

**Strengths:**
- GitHub integration (issues, PRs, discussions)
- Enterprise support and SSO
- Works in VS Code, JetBrains, Neovim
- Repository-aware context
- Team collaboration features

**Best Use Cases:**
- Development workflow automation
- GitHub-native task creation
- PR and issue guidance
- Team process documentation
- Enterprise deployment workflows

## Export Format

### Directory Structure

```
.copilot/
├── knowledge/
│   ├── runbooks.md
│   ├── packages.md
│   ├── workflows.md
│   └── context-index.md
├── system-prompts/
│   ├── development.md
│   ├── content.md
│   └── team.md
└── config.yml
```

### Configuration File (.copilot/config.yml)

```yaml
knowledge:
  enabled: true
  base_path: ".copilot/knowledge"
  refresh_interval: "daily"

system_prompts:
  development: ".copilot/system-prompts/development.md"
  content: ".copilot/system-prompts/content.md"
  team: ".copilot/system-prompts/team.md"

context:
  include_readme: true
  include_package_json: true
  include_manifests: true

integration:
  github_issues: true
  github_prs: true
  github_discussions: true
```

## Installation Steps

### 1. Export Knowledge Base

```bash
# Create directory structure
mkdir -p .copilot/knowledge
mkdir -p .copilot/system-prompts

# Combine runbooks, packages, workflows
cat runbooks/README.md runbooks/*.md > .copilot/knowledge/runbooks.md
cat packages/README.md packages/*.md > .copilot/knowledge/packages.md
cat workflows/*.md > .copilot/knowledge/workflows.md
cat context/*.md > .copilot/knowledge/context-index.md
```

### 2. Add System Prompts

See example system prompts below.

### 3. Configure Copilot

Copy config.yml template above to .copilot/config.yml

### 4. Commit to Repository

```bash
git add .copilot/
git commit -m "Add Copilot knowledge base from ForgeOS"
git push origin main
```

## System Prompt Examples

### Development System Prompt

```markdown
# Development Workflow

You are an AI assistant helping with development tasks.

## Available Resources
- Runbooks: Development, testing, deployment workflows
- Packages: Deliverable specifications and requirements
- Quality Standards: QA checklists and validation steps

## Your Role
1. Reference relevant runbooks when explaining workflows
2. Apply quality standards from QA checklists
3. Provide code examples from documentation
4. Suggest process improvements
5. Help automate repetitive tasks

## Key References
- See .copilot/knowledge/runbooks.md for workflow guidance
- See .copilot/knowledge/workflows.md for quality standards
- Reference specific packages for deliverable specs
```

### Content System Prompt

```markdown
# Content Creation Workflow

You are an AI assistant for content creation and marketing.

## Available Resources
- Runbooks: Blog, campaign, social workflows
- Packages: Content deliverable definitions
- Quality Standards: Content QA checklists

## Your Role
1. Guide through content creation workflows
2. Apply quality standards and best practices
3. Reference templates and examples
4. Suggest content optimization
5. Help plan campaigns

## Key References
- Blog post runbook: .copilot/knowledge/runbooks.md
- Campaign package: .copilot/knowledge/packages.md
- QA standards: .copilot/knowledge/workflows.md
```

## Usage Patterns

### In GitHub Issues

```
/copilot "Help me implement the launch campaign workflow"

Copilot references: launch-campaign.md runbook
└─ Provides step-by-step guidance
└─ Links to campaign package
└─ Suggests milestone structure
```

### In Pull Requests

```
/copilot "Review this against the blog QA checklist"

Copilot references: qa-checklist-blog.md
└─ Checks grammar and formatting
└─ Verifies SEO optimization
└─ Applies quality standards
```

### In Discussions

```
/copilot "What's our process for launching features?"

Copilot references: launch-campaign.md runbook
└─ Explains full workflow
└─ Links to related documentation
└─ Provides timeline expectations
```

## Team Features

### Shared Context
```bash
# All team members get same knowledge base
# Add to onboarding checklist:
1. Clone repository
2. .copilot/knowledge/ available automatically
3. Reference @runbooks, @packages, @workflows in comments
```

### Workflow Automation
```yaml
# .github/workflows/knowledge-sync.yml
name: Sync ForgeOS Knowledge
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
      - name: Update knowledge base
        run: |
          cat runbooks/*.md > .copilot/knowledge/runbooks.md
          cat packages/*.md > .copilot/knowledge/packages.md
          cat workflows/*.md > .copilot/knowledge/workflows.md
      - name: Commit
        run: |
          git config user.name "Knowledge Bot"
          git config user.email "bot@example.com"
          git add .copilot/knowledge/
          git commit -m "Update Copilot knowledge base" || true
          git push
```

## Commands

```
/copilot [question]         Ask about anything
@runbooks                   Reference runbooks
@packages                   Reference packages
@workflows                  Reference QA checklists
/help                       Get help with commands
/knowledge                  List available knowledge base
```

## Integration Examples

### Issue Template with Copilot

```markdown
---
name: Content Creation Task
about: Create a new piece of content
title: '[Content] '
labels: content
---

## Content Details
- **Type:** Blog / Social / Campaign / Other
- **Topic:** 
- **Audience:** 
- **Timeline:** 

## Process Guidance
/copilot reference runbook for [Content Type]

## QA Checklist
See QA checklist in .copilot/knowledge/ before completion

---
/copilot
```

### PR Template with Quality Gates

```markdown
## Changes
[Description]

## Quality Assurance
- [ ] Follows relevant runbook (reference: _____)
- [ ] Passes QA checklist (checked against: _____)
- [ ] Brand standards met
- [ ] Links tested

## Quality Check
/copilot review against [checklist-name]

---
```

## Best Practices

### Knowledge Base Maintenance
- Keep synchronized with source (weekly)
- Document export date
- Version control all changes
- Test in development environment first

### Team Communication
- Reference knowledge base in discussions
- Link to specific checklists in issues
- Share common questions in team notes
- Update documentation as standards evolve

### Productivity Tips
- Use Copilot for repetitive workflows
- Automate knowledge base updates
- Create templates for common tasks
- Share successful patterns with team

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Copilot doesn't reference knowledge | Check .copilot/config.yml, restart VS Code |
| Knowledge base outdated | Run knowledge-sync workflow manually |
| Team can't access knowledge | Verify .copilot/ committed to main branch |
| Copilot gives wrong guidance | Check system prompt, provide more context |

## Related Documents

- [Export Layer README](./README.md)
- [Claude Context Export](./claude-context.md)
- [Cursor Context Export](./cursor-context.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
