---
name: founder-x-recap
description: "INVOKE THIS SKILL when the user wants a recap, summary, or digest of what a founder has been posting or saying on X (Twitter). Fetches recent tweets and replies from a given X handle, summarizes the key themes and notable posts, and optionally posts the recap to Slack."
---

# Founder X Recap Skill

Use this skill when the user wants a **summary of what a founder has been tweeting** — including original tweets and replies.

## What this skill does

1. Fetches recent tweets and replies from a given X handle (default: `@aparnadhinak`)
2. Groups and summarizes the content by theme
3. Highlights notable posts (high-engagement, announcements, strong opinions)
4. Optionally posts the recap to Slack

## Steps

### Step 1: Fetch tweets

Use `web_fetch` to pull the Nitter RSS feed for the target profile:

```
https://nitter.privacyredirect.com/{handle}/rss
```

If that instance is down, try these fallbacks in order:
- `https://nitter.poast.org/{handle}/rss`
- `https://nitter.1d4.us/{handle}/rss`
- `https://xcancel.com/{handle}/rss`

Parse the RSS XML to extract:
- Post text (strip HTML tags)
- Post date/time
- Whether it's a reply (title starts with "R to") or original tweet
- Retweet count and like count if available

Only include posts from the **last 12 hours** for a twice-daily recap.

### Step 2: Summarize

Organize findings into this structure:

**🧵 Original Tweets** — what they posted themselves  
**💬 Replies & Conversations** — who they're engaging with and on what topics  
**🔥 Most Notable** — highest engagement or most interesting post  
**📌 Key Themes** — 2-4 bullet points on recurring topics or signals

Keep the recap concise — aim for under 300 words total.

### Step 3: Format for Slack

Use this Slack message format:

```
📣 *Founder Recap: @{handle}* — {date} {time window}

🧵 *Original Tweets*
{list}

💬 *Key Conversations*
{list}

🔥 *Most Notable*
{post}

📌 *Themes*
• {theme 1}
• {theme 2}
• {theme 3}
```

### Step 4: Post to Slack (if requested)

POST to the Slack webhook URL stored in the environment variable `SLACK_WEBHOOK_URL`.

## Default configuration

| Setting | Value |
|---------|-------|
| X handle | `aparnadhinak` |
| Time window | Last 12 hours |
| Slack channel | Set via webhook |

## Usage examples

- "Run the founder recap for @aparnadhinak"
- "What has Aparna been tweeting about today?"
- "Give me a digest of @aparnadhinak's posts and post it to Slack"
