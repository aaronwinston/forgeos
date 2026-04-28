# Social Post Generator Tool

A command-line tool to generate developer-focused social media posts for the Arize Observe 2026 campaign with agent feedback loops messaging and ownership keywords.

## Installation

```bash
# Install as a global command (make it executable)
chmod +x social-post-generator.sh
sudo ln -s $(pwd)/social-post-generator.sh /usr/local/bin/social-post

# Or use directly
./social-post-generator.sh [command] [options]
```

## Usage

### Generate LinkedIn Post
```bash
social-post --platform linkedin --week 1 --topic problem_awareness --keyword agent_harness

social-post --platform linkedin --week 2 --topic framework --keyword harness_engineering

social-post --platform linkedin --week 1 --topic speaker_spotlight --company Cursor
```

### Generate Twitter/X Post
```bash
social-post --platform twitter --theme evals_fail_production --type thread --length 3

social-post --platform twitter --theme multi_agent_failures --type thread

social-post --platform twitter --theme agent_costs --type single
```

### Generate Email Subject
```bash
social-post --platform email --week 1 --segment warm_users

social-post --platform email --week 3 --segment cold_list

social-post --platform email --week 6 --segment all
```

### Generate In-Product Banner
```bash
social-post --platform banner --phase 1

social-post --platform banner --phase 4
```

### List Keywords
```bash
social-post --keywords
```

## Options

### LinkedIn Posts
- `--week` (1-5): Campaign week
- `--topic`: problem_awareness, speaker_spotlight, framework, founder_pov, multi_agent, before_after, tool_calling, memory_architecture, cost_analysis, weekly_roundup
- `--keyword` (required): agent_harness, harness_engineering, architecture_patterns, orchestration_layer, multi_agent_design, memory_architecture, tool_calling_architecture
- `--speaker`: Speaker name (for spotlight posts)
- `--company`: Company name (for spotlight/case study)

### Twitter Posts
- `--theme`: evals_fail_production, multi_agent_failures, agent_costs, tool_calling, agent_learning, orchestration, urgency
- `--type`: single or thread
- `--length` (2-5): Number of tweets in thread (if type=thread)

### Email Subjects
- `--week` (1-6): Campaign week
- `--segment`: warm_users, cold_list, partners, all

### Banner Copy
- `--phase` (1-4): Banner phase
  - 1: Problem Awareness (May 1-10)
  - 2: Framework Introduction (May 11-20)
  - 3: Social Proof (May 21-31)
  - 4: Urgency (Jun 1-3)

## Examples

```bash
# Generate Week 1 problem awareness post
social-post --platform linkedin --week 1 --topic problem_awareness --keyword agent_harness

# Generate a 3-tweet thread about why evals fail
social-post --platform twitter --theme evals_fail_production --type thread --length 3

# Generate email subject for cold segment, week 2
social-post --platform email --week 2 --segment cold_list

# Generate urgency banner copy
social-post --platform banner --phase 4

# Show all 7 ownership keywords
social-post --keywords
```

## Output

Returns JSON with:
- `post`: The generated content (string or array of strings for threads)
- `platform`: Platform type
- `tips`: Posting tips for optimal engagement
- `metadata`: Week, topic, segment, etc.

Example:
```json
{
  "post": "your agent passed evals...",
  "platform": "LinkedIn",
  "week": 1,
  "topic": "problem_awareness",
  "tips": [
    "Post Tuesday or Thursday between 8am-10am PT",
    "Thread keywords naturally throughout",
    "Lead with problem, not event"
  ]
}
```

## Integration

### With Copilot CLI
Use as a skill in Copilot CLI:
```bash
copilot
/skills
# social-post-generator should appear in available skills
```

### Python/Node Integration
The tool outputs valid JSON, so you can pipe it to jq or use in scripts:

```bash
# Capture a LinkedIn post
POST=$(social-post --platform linkedin --week 1 --topic framework --keyword harness_engineering | jq -r '.post')

# Copy to clipboard (macOS)
social-post --platform twitter --theme agent_costs --type thread | jq -r '.post[]' | pbcopy

# Save to file
social-post --platform linkedin --week 2 --topic founder_pov | jq '.post' > linkedin_post.txt
```

## Key Design Principles

1. **Problem-First**: Every post leads with a problem developers face
2. **Feedback Loops**: All content threads back to the core message
3. **Ownership Keywords**: 7 keywords are naturally integrated:
   - agent harness
   - harness engineering
   - AI agent architecture patterns
   - orchestration layer
   - multi-agent system design
   - agent memory architecture
   - tool calling architecture
4. **Developer Tone**: Short sentences, specific pain points, technical depth
5. **Consistency**: Same narrative across all channels

## Content Strategy Alignment

All posts are aligned with:
- **Campaign goal**: 1,100 registrations for Arize Observe 2026
- **Timeline**: May 1 - June 4 (38 days)
- **Messaging arc**: Problem → Framework → Authority → Urgency
- **Audience**: AI builders, engineering leads, technical developers

## Updates & Maintenance

To update post content, edit the templates in:
```
~/.copilot/extensions/social-post-generator.js
```

Then reload:
```bash
social-post --reload
```

Or restart Copilot CLI:
```bash
copilot --restart
```

---

**Last Updated**: April 28, 2026
**Created for**: Arize Observe 2026 Campaign
**Campaign dates**: May 1 - June 4, 2026
**Tool version**: 1.0.0
