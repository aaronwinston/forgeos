---
name: Markdown Export Guide
description: How to export and share ForgeOS content as universal markdown files
target_platform: Universal (Markdown)
format: Pure Markdown
supported_tools: Any markdown viewer, git, docs platforms
version: 1.0.0
---

# Markdown Export Guide

Pure markdown exports provide universal compatibility and perfect for archiving, version control, and sharing via any platform.

## Why Markdown?

**Strengths:**
- Universal format (works everywhere)
- Version control friendly (git)
- Human-readable
- Platform-agnostic
- Perfect for archiving
- Easy to print or convert

**Best Use Cases:**
- Version control (git)
- Documentation sites (GitHub Pages, Notion, Confluence)
- Archiving and backup
- Sharing via email or links
- Publishing to documentation platforms
- Print-friendly exports

## Export Process

### Step 1: Select Content

Choose which files to export:
- Single files (e.g., one runbook)
- Directory (e.g., all packages)
- Complete export (everything)

### Step 2: Prepare Files

Ensure markdown is properly formatted:
- [ ] Frontmatter is complete
- [ ] Headings are properly hierarchical
- [ ] Links are relative or absolute
- [ ] Images have alt text
- [ ] Code blocks are properly formatted

### Step 3: Create Archive

Option A: Single Markdown File
```bash
# Combine multiple files
cat file1.md file2.md file3.md > combined-export.md

# With table of contents
cat header.md file1.md file2.md > combined-export.md
# Then add table of contents manually
```

Option B: Directory Export
```bash
# Copy directory structure
cp -r runbooks/ exports/runbooks/
cp -r packages/ exports/packages/
cp -r workflows/ exports/workflows/

# Create index
cat > exports/INDEX.md << 'EOF'
# ForgeOS Export

Contents:
- [Runbooks](./runbooks/)
- [Packages](./packages/)
- [Workflows](./workflows/)
EOF
```

Option C: Git Repository
```bash
# Initialize git repository
git init forgeos-export
cd forgeos-export

# Copy files
cp -r /path/to/forgeos/* .

# Commit
git add .
git commit -m "Initial ForgeOS export"

# Push to GitHub/GitLab
git remote add origin [repo-url]
git push -u origin main
```

### Step 4: Format for Target

**For GitHub:**
```markdown
# Add to README.md
- Table of contents
- Quick links
- License information
```

**For Notion:**
```
1. Export as markdown
2. Use "Upload Markdown" in Notion
3. Fix any formatting issues
4. Organize in database
```

**For Confluence:**
```
1. Export as markdown
2. Use markdown converter
3. Upload to Confluence
4. Apply confluence formatting
```

**For Print:**
```bash
# Convert to PDF
pandoc export.md -o export.pdf \
  --pdf-engine=xetex \
  --template=eisvogel

# Or use online tool: md-to-pdf.com
```

## Directory Structure for Export

### Minimal Export
```
forgeos-export/
├── README.md (index)
├── runbooks/
│   └── [runbook files]
├── packages/
│   └── [package files]
└── workflows/
    └── [QA checklists]
```

### Complete Export
```
forgeos-export/
├── README.md
├── INDEX.md
├── runbooks/
│   ├── README.md
│   ├── blog-post.md
│   ├── launch-campaign.md
│   └── ...
├── packages/
│   ├── README.md
│   └── [package files]
├── workflows/
│   ├── qa-gating.md
│   ├── qa-checklist-blog.md
│   └── ...
├── exports/
│   ├── README.md
│   └── [export guides]
├── context/
│   ├── README.md
│   └── [context files]
├── docs/
│   └── [additional documentation]
└── LICENSE
```

## Frontmatter Format

```yaml
---
name: Document Name
description: Brief description
version: 1.0.0
last_updated: 2024-12-20
type: runbook | package | checklist | guide
author: Name
tags: [tag1, tag2, tag3]
---

# Document Title

[Content]
```

## Adding Table of Contents

### Markdown TOC (Automated)

```bash
# Using doctoc
npm install -g doctoc
doctoc export.md

# Using markdown-toc
npm install -g markdown-toc
markdown-toc -i export.md
```

### Manual TOC

```markdown
# ForgeOS Export

## Contents

- [Runbooks](#runbooks)
  - [Blog Post](./runbooks/blog-post.md)
  - [Launch Campaign](./runbooks/launch-campaign.md)
- [Packages](#packages)
  - [Blog Post Package](./packages/blog-post.md)
- [Quality Assurance](#quality-assurance)
  - [QA Gating System](./workflows/qa-gating.md)

---

## Runbooks

[Runbook content]

## Packages

[Package content]

## Quality Assurance

[QA content]
```

## Linking Between Files

### Relative Links (Best for exports)
```markdown
# Internal export links
[Blog Runbook](./runbooks/blog-post.md)
[Blog QA](./workflows/qa-checklist-blog.md)

# Subdirectory links
[See also](../packages/blog-post.md#success-criteria)
```

### Absolute Links (For shared URLs)
```markdown
[Blog Runbook](https://github.com/org/repo/blob/main/runbooks/blog-post.md)
```

### Anchor Links (Within document)
```markdown
[See Success Criteria](#success-criteria)

# Later in document
## Success Criteria
```

## Markdown Formatting Best Practices

### Headings
```markdown
# H1 - Document Title (use once per file)
## H2 - Major sections
### H3 - Subsections
#### H4 - Details
```

### Emphasis
```markdown
**Bold** for important terms
*Italics* for emphasis
`Code` for technical terms
```

### Lists
```markdown
## Unordered
- Item 1
- Item 2
  - Nested item

## Ordered
1. Step 1
2. Step 2
3. Step 3

## Checkboxes
- [ ] Unchecked
- [x] Checked
```

### Code Blocks
```markdown
```yaml
# YAML example
key: value
```

```python
# Python example
def function():
    pass
```

```bash
# Bash example
echo "Hello"
```
```

### Tables
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |
```

### Blockquotes
```markdown
> This is a blockquote
> Can span multiple lines
```

### Horizontal Rule
```markdown
---
```

## Export Templates

### README Template
```markdown
# ForgeOS Content Export

Export generated: [Date]  
Version: 1.0.0  
Source: https://github.com/org/forgeos

## Quick Start

This export contains ForgeOS runbooks, packages, and quality standards.

**Start here:**
1. Read [Getting Started](./docs/getting-started.md)
2. Choose a runbook from [Runbooks](./runbooks/)
3. Apply quality standards from [QA System](./workflows/qa-gating.md)

## Structure

- **Runbooks** - Step-by-step workflows for content production
- **Packages** - Deliverable definitions and specifications
- **Workflows** - Quality assurance checklists and gating system
- **Exports** - Guides for exporting to external tools
- **Docs** - Additional documentation and guides

## Navigation

[Full Index](./INDEX.md)

## License

[License information]
```

### Index Template
```markdown
# Complete Index

## Runbooks (6 items)

1. [Blog Post Runbook](./runbooks/blog-post.md) - End-to-end blog writing
2. [Launch Campaign Runbook](./runbooks/launch-campaign.md) - Multi-channel campaigns
3. [Repurposing Campaign](./runbooks/repurposing-campaign.md) - Content reuse
4. [Content Audit](./runbooks/content-audit.md) - Quarterly reviews
5. [Strategy Brief](./runbooks/strategy-brief.md) - Strategic planning
6. [Runbook Layer README](./runbooks/README.md) - Overview

[Continues for all sections]
```

## Hosting Exported Content

### Option 1: GitHub Pages
```bash
# Create docs/ directory
mkdir docs
mv *.md docs/
mv _config.yml docs/  # Jekyll config

# Push to GitHub
git add docs/
git commit -m "Add documentation site"
git push origin main

# Enable GitHub Pages in settings
# Site available at: https://username.github.io/repo
```

### Option 2: GitHub Discussions
```
1. Copy markdown to GitHub discussions
2. Pin important threads
3. Use for team reference
4. Link from README
```

### Option 3: Personal Wiki
```bash
# Using Obsidian
1. Create vault
2. Import markdown files
3. Update links for Obsidian format
4. Use locally or publish via Obsidian Publish

# Using DocusaurusOptons
npm install docusaurus
docusaurus build
```

### Option 4: Version Control Only
```bash
# Just use git for tracking
git init
git add *.md
git commit -m "Initial import"

# Access via any markdown viewer or IDE
# Share git clone URL for distribution
```

## Maintenance

### Update Workflow
```bash
1. Export latest from source
2. Review for changes
3. Commit with descriptive message
4. Push to remote
5. Update version in frontmatter
6. Document changelog
```

### Version Control Best Practices
```bash
# Use semantic versioning
# Format: MAJOR.MINOR.PATCH

# Example commits:
git commit -m "docs: Update blog runbook (v1.1.0)"
git commit -m "fix: Correct QA checklist item (v1.0.1)"
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main --tags
```

## Sharing & Distribution

### Direct File Share
```
1. Export markdown files
2. Create zip: zip -r forgeos-export.zip *.md
3. Share via email or drive
4. Include README with instructions
```

### Repository Link
```
1. Push export to GitHub/GitLab
2. Share repository URL
3. Recipients clone or download
4. Natural version control built-in
```

### Embedded Link
```markdown
# In your documentation
[Download ForgeOS (v1.0.0)](https://github.com/org/forgeos/archive/refs/heads/main.zip)
```

### CI/CD Release
```yaml
# .github/workflows/release.yml
name: Create Release
on:
  push:
    tags:
      - 'v*'
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create archive
        run: zip -r forgeos-${{ github.ref }}.zip *.md
      - name: Create release
        uses: softprops/action-gh-release@v1
        with:
          files: forgeos-*.zip
```

## Limitations

| Issue | Solution |
|-------|----------|
| Markdown viewers vary | Stick to common markdown, test rendering |
| Images may not display | Include alt text, verify image paths |
| Complex formatting lost | Use simpler markdown, provide PDF version |
| Large files slow | Split into smaller files, link between them |
| Link maintenance | Use relative links, test all links regularly |

## Tools & Conversion

### Convert Markdown to Other Formats

```bash
# To HTML
pandoc export.md -o export.html

# To PDF
pandoc export.md -o export.pdf

# To DOCX
pandoc export.md -o export.docx

# To EPUB
pandoc export.md -o export.epub
```

## Related Documents

- [Export Layer README](./README.md)

---

**Version:** 1.0.0 | **Last Updated:** 2024-12-20
