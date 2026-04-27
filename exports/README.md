---
name: Export Layer
description: Framework for exporting ForgeOS content to external AI tools and platforms
version: 1.0.0
last_updated: 2024-12-20
layer: exports
---

# Export Layer

The Export Layer enables **seamless export** of ForgeOS content, context, and packages to external AI platforms and tools. It preserves structure, relationships, and context during export.

## Purpose

Exports:
- Enable use of ForgeOS content in external tools
- Preserve context and relationships
- Maintain brand consistency across platforms
- Simplify knowledge transfer to AI assistants
- Create platform-specific format adaptations

## Supported Export Targets

### 1. Claude (Anthropic)
**Best For:** Deep analysis, long-context tasks, research synthesis  
**Format:** Markdown + system prompts  
**Context Window:** 200K tokens (Claude 3 Opus)  
**Key Features:** Long context, complex reasoning  

**Export What:**
- Runbooks and workflows
- Research briefs and analyses
- Content packages
- Context bundles

### 2. Cursor (IDE-Integrated AI)
**Best For:** Code-related content, technical documentation, implementation  
**Format:** Markdown + codebase structure  
**Context Window:** 8-32K tokens (configurable)  
**Key Features:** IDE integration, codebase awareness  

**Export What:**
- Technical runbooks
- Implementation guides
- Code documentation
- Architecture decisions

### 3. Copilot (GitHub)
**Best For:** Development workflows, GitHub-native tasks, enterprise integration  
**Format:** Markdown + GitHub context  
**Context Window:** 8-32K tokens  
**Key Features:** GitHub integration, enterprise support  

**Export What:**
- Development runbooks
- Documentation
- GitHub project context
- Workflow definitions

### 4. ChatGPT (OpenAI)
**Best For:** General-purpose use, broad audience, accessibility  
**Format:** Markdown + system prompts  
**Context Window:** 8K-128K tokens (GPT-4)  
**Key Features:** Wide availability, good reasoning  

**Export What:**
- Content packages
- Runbooks (general)
- Briefing documents
- FAQ content

### 5. Markdown (Universal)
**Best For:** Archiving, sharing, documentation, print  
**Format:** Pure Markdown with metadata  
**Context Window:** Unlimited (static files)  
**Key Features:** Platform-agnostic, version control friendly  

**Export What:**
- Full content packages
- Runbook collections
- Context bundles
- Documentation archives

## Export Profiles

### Standard Export Profile

Includes:
- Core content document
- Metadata (title, author, date, version)
- Linked resources (referenced documents)
- Visual assets (images, diagrams)
- Internal cross-references converted to external links

### Minimal Export Profile

Includes:
- Core content only
- Basic metadata
- Essential links
- No heavy assets (smaller file size)

### Full Export Profile

Includes:
- Core content
- All linked documents
- All visual assets
- Complete metadata
- Supporting materials
- Appendices and references

### Context-Preserving Profile

Includes:
- Core content
- Related context from Context Index
- Runbook dependencies
- Agent information
- Cross-references
- Relationship map

## Export Features by Platform

| Feature | Claude | Cursor | Copilot | ChatGPT | Markdown |
|---------|--------|--------|---------|---------|----------|
| System Prompts | ✓ | ✓ | ✓ | ✓ | N/A |
| Code Examples | ✓ | ✓ | ✓ | ✓ | ✓ |
| Markdown Tables | ✓ | ✓ | ✓ | ✓ | ✓ |
| Mermaid Diagrams | ✓ | ✓ | ✓ | Partial | ✓ |
| Long Documents | ✓ | Partial | Partial | ✓ | ✓ |
| Images/Visuals | ✓ | ✓ | ✓ | ✓ | ✓ |
| PDF Attachments | Partial | ✓ | ✓ | Partial | N/A |
| Cross-References | ✓ | ✓ | ✓ | ✓ | ✓ |
| Version Control | N/A | ✓ | ✓ | N/A | ✓ |

## Export Workflow

### Step 1: Select Content
- Choose which content/packages to export
- Define export scope (minimal/standard/full)
- Select target platform

### Step 2: Prepare Content
- Gather linked documents
- Collect visual assets
- Create metadata
- Generate system prompts (if applicable)

### Step 3: Format for Target
- Convert to platform-specific format
- Optimize for platform constraints (token limits, etc.)
- Add platform-specific instructions
- Test rendering/functionality

### Step 4: Bundle & Deliver
- Create export package (file or zip)
- Include manifest/readme
- Test in target platform
- Deliver to user

### Step 5: Version & Archive
- Store export template for future use
- Version control export scripts
- Document any customizations
- Archive as needed

## Context Preservation Strategy

### What Gets Preserved

1. **Semantic Structure**
   - Document hierarchy (H1, H2, H3)
   - Section relationships
   - Cross-reference links

2. **Content Relationships**
   - Runbook dependencies
   - Package components
   - Agent interactions
   - Context requirements

3. **Metadata**
   - Document title, author, date
   - Version information
   - Classification tags
   - Related documents

4. **Visual Context**
   - Charts and diagrams
   - Screenshots and examples
   - Process flows
   - Hierarchies

### Preservation Techniques

**Markdown Formatting:** Standard markdown for universal compatibility

**Frontmatter:** YAML frontmatter for metadata (supported in most tools)

**Comments:** HTML comments for non-visible instructions/context

**Tables:** Markdown tables for structured data

**Code Blocks:** Code syntax highlighting for examples

**Mermaid Diagrams:** Flowcharts, sequence diagrams, timelines

**Cross-References:** Internal links converted to tool-specific format

## Export Templates

### Blog Post Export Template
```markdown
---
source: ForgeOS Blog Post Package
title: [Title]
author: [Author]
date: [Date]
tags: [Tags]
length: [Word count]
---

# [Title]

[Featured image]

[Blog post content]

## Related Resources
- [Link 1]
- [Link 2]

---
Exported from ForgeOS [Date]
```

### Campaign Package Export Template
```markdown
---
source: ForgeOS Campaign Package
name: [Campaign Name]
date: [Date]
channels: [List]
duration: [Duration]
budget: [Budget]
---

# [Campaign Name]

[Campaign overview]

## Content Components
- [Component 1]
- [Component 2]

## Timeline
[Timeline table]

## Success Metrics
[Metrics]

---
Exported from ForgeOS [Date]
```

### Runbook Export Template
```markdown
---
source: ForgeOS Runbook
name: [Runbook Name]
agents: [Agent list]
duration: [Duration]
date: [Date]
---

# [Runbook Name]

[Runbook content]

## Workflow
[Detailed steps]

## Templates
[Applicable templates]

---
Exported from ForgeOS [Date]
```

## Export Best Practices

### Before Exporting
- [ ] Confirm export scope and profile
- [ ] Verify all links are current
- [ ] Check visual assets are included
- [ ] Review metadata accuracy
- [ ] Test export in target tool

### During Export
- [ ] Use consistent formatting
- [ ] Preserve all relationships
- [ ] Include clear navigation
- [ ] Add table of contents (for long documents)
- [ ] Maintain version information

### After Export
- [ ] Test in target platform
- [ ] Verify rendering/formatting
- [ ] Check all links work
- [ ] Confirm images display correctly
- [ ] Validate AI tool can process content

### Sharing Exports
- [ ] Include readme/instructions
- [ ] Document export date and version
- [ ] Provide source link (back to ForgeOS)
- [ ] Note any customizations
- [ ] Specify how to report issues

## Integration with External Tools

### Claude Integration
- Copy markdown content into conversation
- Use system prompts for context
- Reference cross-documents in conversation
- Leverage 200K context window for large packages

### Cursor Integration
- Store in `.cursor/context` directory
- Reference in project configuration
- Use code examples directly
- Version control exports in git

### Copilot Integration
- Store in `.copilot/knowledge` directory
- Reference in agent prompts
- Use for agent training
- Version with repository

### ChatGPT Integration
- Create custom GPT with exported content
- Use as knowledge base
- Enable RAG for direct reference
- Share GPT with others

## Export Limitations & Considerations

**Token Limits:**
- ChatGPT (8K): Limit exports to <2K tokens
- GPT-4 (128K): Can handle full packages
- Claude (200K): Can handle very large packages
- Cursor (8-32K): Suitable for medium-sized exports

**Formatting Support:**
- Mermaid diagrams may not render in all tools
- LaTeX equations need tool-specific format
- Complex HTML won't render in plain markdown
- Some platforms don't support YAML frontmatter

**Data Privacy:**
- Don't export confidential content to public tools
- Verify tool privacy policies
- Use private GPTs/instances where available
- Redact sensitive information if needed

**Link Handling:**
- External links should remain unchanged
- Internal links converted to tool format or descriptive text
- Broken links should be identified before export
- Link preview generation depends on tool

## Related Documents

- [Export Adapter Templates](./claude-context.md)
- [Export Adapter: Cursor](./cursor-context.md)
- [Export Adapter: Copilot](./copilot-context.md)
- [Export Adapter: ChatGPT](./chatgpt-context.md)
- [Markdown Export Guide](./markdown-export.md)

---

**Last Updated:** 2024-12-20  
**Maintained By:** Operations Team
