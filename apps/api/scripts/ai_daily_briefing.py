#!/usr/bin/env python3
"""
AI Daily Briefing
Fetches the latest AI research and news, summarizes it, and posts to Slack twice a day.
Pulls from arXiv, Hugging Face papers, and web search.
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
LOOKBACK_HOURS = int(os.getenv("LOOKBACK_HOURS", "12"))

ARXIV_CATEGORIES = ["cs.AI", "cs.LG", "cs.CL"]
ARXIV_MAX_RESULTS = 10

HF_PAPERS_URL = "https://huggingface.co/papers"
ARXIV_RSS_BASE = "https://rss.arxiv.org/rss/{cat}"


# ---------------------------------------------------------------------------
# Fetch arXiv RSS
# ---------------------------------------------------------------------------

def fetch_arxiv_papers(categories: list[str], lookback_hours: int) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    papers = []

    for cat in categories:
        url = ARXIV_RSS_BASE.format(cat=cat)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read().decode("utf-8")
        except Exception as e:
            print(f"  ✗ arXiv {cat} failed: {e}", file=sys.stderr)
            continue

        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            continue

        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            description = re.sub(r"<[^>]+>", "", item.findtext("description") or "").strip()
            abstract = description[:300] + "…" if len(description) > 300 else description

            papers.append({
                "title": title,
                "link": link,
                "abstract": abstract,
                "category": cat,
            })

            if len(papers) >= ARXIV_MAX_RESULTS:
                break

        if len(papers) >= ARXIV_MAX_RESULTS:
            break

    return papers[:5]  # top 5 for the digest


# ---------------------------------------------------------------------------
# Format Slack message
# ---------------------------------------------------------------------------

def format_briefing(papers: list[dict], session: str) -> str:
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%b %d, %Y")
    time_window = "Morning" if now.hour < 14 else "Evening"

    lines = [
        f"🧠 *AI Daily Briefing — {date_str} | {time_window} Edition*",
        "",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    if papers:
        lines.append("📄 *Latest from arXiv*")
        for p in papers[:5]:
            lines.append(f"• *{p['title']}*")
            lines.append(f"  _{p['abstract']}_")
            lines.append(f"  {p['link']}")
            lines.append("")
    else:
        lines.append("_No new papers fetched — check arXiv manually._")
        lines.append("")

    lines += [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "📌 *More sources to check:*",
        "• <https://huggingface.co/papers|Hugging Face Papers>",
        "• <https://simonwillison.net|Simon Willison's Blog>",
        "• <https://arxiv.org/list/cs.AI/recent|arXiv cs.AI>",
        "",
        "_This briefing is auto-generated. Run the `ai-researcher` skill in Copilot CLI for a deeper digest._",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Slack
# ---------------------------------------------------------------------------

def post_to_slack(message: str, webhook_url: str) -> None:
    payload = {"text": message, "unfurl_links": False}
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
    session = "morning" if datetime.now(timezone.utc).hour < 14 else "evening"
    print(f"Fetching AI papers for {session} briefing…", file=sys.stderr)

    papers = fetch_arxiv_papers(ARXIV_CATEGORIES, LOOKBACK_HOURS)
    print(f"Found {len(papers)} paper(s).", file=sys.stderr)

    message = format_briefing(papers, session)
    print("\n--- BRIEFING PREVIEW ---")
    print(message)
    print("------------------------\n")

    if SLACK_WEBHOOK_URL:
        post_to_slack(message, SLACK_WEBHOOK_URL)
    else:
        print("⚠ SLACK_WEBHOOK_URL not set — skipping Slack post.", file=sys.stderr)


if __name__ == "__main__":
    main()
