#!/usr/bin/env python3
"""
Founder Tweet Recap
Fetches recent tweets from a founder's X profile via Nitter RSS,
summarizes them using an LLM, and posts the digest to Slack.
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

HANDLE = os.getenv("X_HANDLE", "aparnadhinak")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "12"))

NITTER_INSTANCES = [
    "https://nitter.privacyredirect.com",
    "https://nitter.poast.org",
    "https://nitter.1d4.us",
    "https://xcancel.com",
]


# ---------------------------------------------------------------------------
# Fetch RSS
# ---------------------------------------------------------------------------

def fetch_rss(handle: str) -> str:
    for base in NITTER_INSTANCES:
        url = f"{base}/{handle}/rss"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                content = resp.read().decode("utf-8")
                if "<rss" in content or "<feed" in content:
                    print(f"✓ Fetched RSS from {base}", file=sys.stderr)
                    return content
        except Exception as e:
            print(f"  ✗ {base} failed: {e}", file=sys.stderr)
    raise RuntimeError("All Nitter instances failed. Try again later.")


def parse_rss(xml_content: str, lookback_hours: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    root = ET.fromstring(xml_content)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    items = root.findall(".//item")
    posts = []

    for item in items:
        title = (item.findtext("title") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date_str = item.findtext("pubDate") or ""
        link = item.findtext("link") or ""

        # Parse date
        try:
            pub_date = parsedate_to_datetime(pub_date_str)
        except Exception:
            continue

        if pub_date < cutoff:
            continue

        # Strip HTML tags from description
        text = re.sub(r"<[^>]+>", "", description).strip()
        text = re.sub(r"\s+", " ", text)

        is_reply = title.lower().startswith("r to")

        posts.append({
            "title": title,
            "text": text,
            "url": link,
            "date": pub_date.strftime("%b %d %H:%M UTC"),
            "is_reply": is_reply,
        })

    return posts


# ---------------------------------------------------------------------------
# Summarize
# ---------------------------------------------------------------------------

def summarize(posts: list[dict], handle: str) -> str:
    if not posts:
        return f"No posts from @{handle} in the last {LOOKBACK_HOURS} hours."

    originals = [p for p in posts if not p["is_reply"]]
    replies = [p for p in posts if p["is_reply"]]

    def fmt_post(p: dict) -> str:
        return f"• {p['text'][:200]}{'…' if len(p['text']) > 200 else ''} ({p['date']}) {p['url']}"

    lines = []

    if originals:
        lines.append("🧵 *Original Tweets*")
        for p in originals[:5]:
            lines.append(fmt_post(p))

    if replies:
        lines.append("\n💬 *Key Conversations*")
        for p in replies[:5]:
            lines.append(fmt_post(p))

    if posts:
        lines.append("\n📌 *Quick Stats*")
        lines.append(f"• {len(originals)} original tweet(s), {len(replies)} repl(ies) in the last {LOOKBACK_HOURS}h")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Slack
# ---------------------------------------------------------------------------

def post_to_slack(message: str, handle: str, webhook_url: str) -> None:
    now = datetime.now(timezone.utc).strftime("%b %d, %Y %H:%M UTC")
    payload = {
        "text": f"📣 *Founder Recap: @{handle}* — {now}\n\n{message}",
        "unfurl_links": False,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.status
    if status != 200:
        raise RuntimeError(f"Slack returned HTTP {status}")
    print("✓ Posted to Slack", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"Fetching tweets for @{HANDLE} (last {LOOKBACK_HOURS}h)…", file=sys.stderr)

    xml_content = fetch_rss(HANDLE)
    posts = parse_rss(xml_content, LOOKBACK_HOURS)

    print(f"Found {len(posts)} post(s) in window.", file=sys.stderr)

    summary = summarize(posts, HANDLE)
    print("\n--- RECAP ---")
    print(summary)
    print("-------------\n")

    if SLACK_WEBHOOK_URL:
        post_to_slack(summary, HANDLE, SLACK_WEBHOOK_URL)
    else:
        print("⚠ SLACK_WEBHOOK_URL not set — skipping Slack post.", file=sys.stderr)


if __name__ == "__main__":
    main()
