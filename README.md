# mktg-agents
Agents to improve workflows + increase mktg throughput.

## Skills

| Skill | Description |
|-------|-------------|
| [`founder-x-recap`](./skills/founder-x-recap/SKILL.md) | Twice-daily digest of a founder's X posts + replies, posted to Slack |

## Setup

### Slack Webhook
Add your Slack incoming webhook URL as a GitHub Actions secret named `SLACK_WEBHOOK_URL`.  
[Create a webhook →](https://api.slack.com/messaging/webhooks)

### Running manually
```bash
SLACK_WEBHOOK_URL=your_webhook python scripts/founder_tweet_recap.py
```
