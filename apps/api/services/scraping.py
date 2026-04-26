import httpx
import json
import feedparser
from datetime import datetime
import asyncio

async def scrape_hackernews(keywords: list[str] = None, min_points: int = 50) -> list[dict]:
    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        if keywords:
            for kw in keywords[:3]:
                try:
                    r = await client.get(
                        "https://hn.algolia.com/api/v1/search",
                        params={"query": kw, "tags": "story", "hitsPerPage": 20}
                    )
                    for hit in r.json().get("hits", []):
                        results.append({
                            "source": "hackernews",
                            "source_url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                            "title": hit.get("title", ""),
                            "body": hit.get("story_text", ""),
                            "author": hit.get("author", ""),
                            "published_at": datetime.utcfromtimestamp(hit.get("created_at_i", 0)) if hit.get("created_at_i") else None,
                            "raw_json": json.dumps(hit),
                        })
                except Exception:
                    pass
        try:
            r = await client.get("https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage=30")
            for hit in r.json().get("hits", []):
                if hit.get("points", 0) >= min_points:
                    results.append({
                        "source": "hackernews",
                        "source_url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        "title": hit.get("title", ""),
                        "body": hit.get("story_text", ""),
                        "author": hit.get("author", ""),
                        "published_at": datetime.utcfromtimestamp(hit.get("created_at_i", 0)) if hit.get("created_at_i") else None,
                        "raw_json": json.dumps(hit),
                    })
        except Exception:
            pass
    return results

DEFAULT_SUBREDDITS = [
    "MachineLearning", "LocalLLaMA", "programming",
    "devops", "LangChain", "AI_Agents"
]

async def scrape_reddit(subreddits: list[str] = None) -> list[dict]:
    subreddits = subreddits or DEFAULT_SUBREDDITS
    results = []
    headers = {"User-Agent": "ForgeOS/1.0 (developer marketing intelligence tool)"}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        for sub in subreddits:
            try:
                r = await client.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=25")
                data = r.json()
                for post in data.get("data", {}).get("children", []):
                    p = post.get("data", {})
                    results.append({
                        "source": "reddit",
                        "source_url": f"https://reddit.com{p.get('permalink', '')}",
                        "title": p.get("title", ""),
                        "body": p.get("selftext", "")[:1000],
                        "author": p.get("author", ""),
                        "published_at": datetime.utcfromtimestamp(p.get("created_utc", 0)) if p.get("created_utc") else None,
                        "raw_json": json.dumps({"subreddit": sub, "score": p.get("score"), "num_comments": p.get("num_comments")}),
                    })
            except Exception:
                pass
    return results

GITHUB_TOPICS = ["ai", "llm", "agents", "observability", "llm-evaluation", "mlops"]

async def scrape_github_trending(topics: list[str] = None) -> list[dict]:
    topics = topics or GITHUB_TOPICS
    results = []
    async with httpx.AsyncClient(timeout=30) as client:
        for topic in topics[:4]:
            try:
                r = await client.get(
                    "https://api.github.com/search/repositories",
                    params={"q": f"topic:{topic}", "sort": "stars", "order": "desc", "per_page": 10},
                    headers={"Accept": "application/vnd.github.v3+json"}
                )
                for repo in r.json().get("items", []):
                    results.append({
                        "source": "github",
                        "source_url": repo.get("html_url", ""),
                        "title": f"{repo.get('full_name', '')} — {repo.get('description', '')}",
                        "body": repo.get("description", ""),
                        "author": repo.get("owner", {}).get("login", ""),
                        "published_at": None,
                        "raw_json": json.dumps({"stars": repo.get("stargazers_count"), "topic": topic}),
                    })
                await asyncio.sleep(1)
            except Exception:
                pass
    return results

ARXIV_FEEDS = [
    "https://rss.arxiv.org/rss/cs.AI",
    "https://rss.arxiv.org/rss/cs.LG",
    "https://rss.arxiv.org/rss/cs.CL",
]

async def scrape_arxiv(feeds: list[str] = None) -> list[dict]:
    feeds = feeds or ARXIV_FEEDS
    results = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:20]:
                results.append({
                    "source": "arxiv",
                    "source_url": entry.get("link", ""),
                    "title": entry.get("title", ""),
                    "body": entry.get("summary", "")[:1000],
                    "author": ", ".join([a.get("name", "") for a in entry.get("authors", [])[:3]]),
                    "published_at": datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") and entry.published_parsed else None,
                    "raw_json": None,
                })
        except Exception:
            pass
    return results

DEFAULT_RSS_FEEDS = [
    "https://www.anthropic.com/rss.xml",
    "https://openai.com/blog/rss.xml",
    "https://simonwillison.net/atom/everything/",
    "https://www.latent.space/feed",
    "https://sebastianraschka.com/rss.xml",
    "https://lilianweng.github.io/index.xml",
    "https://eugeneyan.com/rss/",
    "https://hamel.dev/feed.xml",
    "https://arize.com/blog/feed/",
]

async def scrape_rss(feeds: list[str] = None) -> list[dict]:
    feeds = feeds or DEFAULT_RSS_FEEDS
    results = []
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:
                results.append({
                    "source": "rss",
                    "source_url": entry.get("link", ""),
                    "title": entry.get("title", ""),
                    "body": (entry.get("summary") or entry.get("content", [{}])[0].get("value", ""))[:1000],
                    "author": entry.get("author", feed.feed.get("title", "")),
                    "published_at": datetime(*entry.published_parsed[:6]) if hasattr(entry, "published_parsed") and entry.published_parsed else None,
                    "raw_json": json.dumps({"feed": feed_url}),
                })
        except Exception:
            pass
    return results

async def scrape_twitter_stub() -> list[dict]:
    return []

async def scrape_web_search_stub(queries: list[str] = None) -> list[dict]:
    return []

async def run_all_scrapers(config: dict = None) -> list[dict]:
    config = config or {}
    all_results = []
    tasks = [
        scrape_hackernews(
            keywords=config.get("hn_keywords", ["LLM observability", "AI agents", "eval harness"]),
            min_points=config.get("hn_min_points", 50)
        ),
        scrape_reddit(subreddits=config.get("subreddits", DEFAULT_SUBREDDITS)),
        scrape_github_trending(topics=config.get("github_topics", GITHUB_TOPICS)),
        scrape_arxiv(feeds=config.get("arxiv_feeds", ARXIV_FEEDS)),
        scrape_rss(feeds=config.get("rss_feeds", DEFAULT_RSS_FEEDS)),
        scrape_twitter_stub(),
        scrape_web_search_stub(),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for r in results:
        if isinstance(r, list):
            all_results.extend(r)
    return all_results
