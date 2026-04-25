# mktg-agents
Agents to improve workflows + increase mktg throughput.

## Skills

| Skill | Description |
|-------|-------------|
| [`founder-x-recap`](./skills/founder-x-recap/SKILL.md) | Twice-daily digest of a founder's X posts + replies, posted to Slack |
| [`dev-reviewer`](./skills/dev-reviewer/SKILL.md) | Senior software developer who reviews technical writing and code |
| [`ai-researcher`](./skills/ai-researcher/SKILL.md) | Expert AI engineer who briefs on latest research + reviews AI content |
| [`dev-copywriter`](./skills/dev-copywriter/SKILL.md) | World-class copywriter with deep software dev knowledge |

All writing skills reference [`skills/VOICE.md`](./skills/VOICE.md) — Aaron's personal voice guide.

## Setup

### Slack Webhook
Add your Slack incoming webhook URL as a GitHub Actions secret named `SLACK_WEBHOOK_URL`.  
[Create a webhook →](https://api.slack.com/messaging/webhooks)

### Running manually
```bash
SLACK_WEBHOOK_URL=your_webhook python scripts/founder_tweet_recap.py
```
