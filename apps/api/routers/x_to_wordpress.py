"""
X/Twitter to WordPress content import API.

Exposes the x-to-wordpress-scraper skill via REST API.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from services.x_to_wordpress import convert_x_to_wordpress
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/content", tags=["content"])


class ConvertXToWordPressRequest(BaseModel):
    """Request to convert X/Twitter post to WordPress import."""

    x_url: str
    """X/Twitter post URL (e.g., https://x.com/aparnadhinak/status/...)"""

    content_type: str = "post"
    """Type of content: 'post', 'thread', 'article-link'"""

    category: str = "Incoming"
    """Target WordPress category"""

    tags: Optional[List[str]] = None
    """Additional tags to apply (will add 'aparna', 'founder-insights')"""

    author_override: Optional[str] = None
    """Override default author (default: Aparna Dhinakaran)"""


class ConvertXToWordPressResponse(BaseModel):
    """Response from conversion."""

    status: str
    """'success' or 'error'"""

    filepath: Optional[str] = None
    """Path to saved WordPress import file"""

    filename: Optional[str] = None
    """Filename of saved file"""

    preview: Optional[str] = None
    """Preview of formatted content (first 500 chars)"""

    category: Optional[str] = None
    """WordPress category"""

    tags: Optional[List[str]] = None
    """Applied tags"""

    source_url: Optional[str] = None
    """Source X URL"""

    author: Optional[str] = None
    """Author name"""

    message: Optional[str] = None
    """Error message if status='error'"""

    url: Optional[str] = None
    """Original URL (returned on error)"""


@router.post("/x-to-wordpress")
async def convert_x_to_wordpress_endpoint(
    request: ConvertXToWordPressRequest,
) -> ConvertXToWordPressResponse:
    """
    Convert X/Twitter post to WordPress import file.

    Takes an X/Twitter URL, scrapes the content, and formats it as a
    WordPress-ready text file that can be imported directly into WordPress.

    The file is saved to `docs/content/incoming/` with a timestamp, so it
    persists in the repo for audit trail and backup.

    ## Usage

    ```bash
    curl -X POST http://localhost:8000/api/content/x-to-wordpress \\
      -H "Content-Type: application/json" \\
      -d '{
        "x_url": "https://x.com/aparnadhinak/status/2048492731929149929",
        "category": "Founder Insights",
        "tags": ["ai", "product-strategy"]
      }'
    ```

    ## Response

    ```json
    {
      "status": "success",
      "filepath": "/path/to/docs/content/incoming/wordpress-aparna-post-2048492731929149929_20260427_114216.txt",
      "filename": "wordpress-aparna-post-2048492731929149929_20260427_114216.txt",
      "preview": "Title: Aparna's latest insights...",
      "category": "Founder Insights",
      "tags": ["aparna", "founder-insights", "ai", "product-strategy"],
      "source_url": "https://x.com/aparnadhinak/status/2048492731929149929",
      "author": "Aparna Dhinakaran"
    }
    ```

    ## File Format

    The generated `.txt` file contains:

    ```
    WORDPRESS IMPORT FILE
    =====================

    Title: [Extracted or provided]
    Author: Aparna Dhinakaran
    Date: 2026-04-27 11:42:16
    Category: Founder Insights
    Tags: aparna, founder-insights, ai, product-strategy
    Source: https://x.com/aparnadhinak/status/...

    ---

    [Clean content body - ready for WordPress import]

    ---

    Original X post: https://x.com/aparnadhinak/status/...
    Posted: 2026-04-27T11:42:16Z
    Engagement: 245 retweets, 1250 likes
    ```

    ## Workflow

    1. Call this endpoint with X URL
    2. Content is scraped and formatted
    3. File is saved to `docs/content/incoming/`
    4. File persists in repo (audit trail)
    5. Return file path for import
    6. User opens file, reviews in WordPress editor
    7. Copy/paste into WordPress (or use import tool)
    8. Commit `.txt` file to repo for history

    ## Integration with WordPress

    The saved `.txt` file can be:

    1. **Copy/pasted directly** into WordPress post editor
    2. **Imported via CSV** if you have WordPress import tools
    3. **Processed by scripts** that read from `docs/content/incoming/`
    4. **Versioned in git** for audit trail

    """
    try:
        result = convert_x_to_wordpress(
            x_url=request.x_url,
            category=request.category,
            tags=request.tags,
            author_override=request.author_override,
            repo_root=".",  # Relative to API root
        )

        # Log successful conversion
        if result.get('status') == 'success':
            logger.info(
                f"Converted X post to WordPress: {result.get('filename')} "
                f"({request.x_url})"
            )

        return ConvertXToWordPressResponse(**result)

    except Exception as e:
        logger.error(f"Error converting X post: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to convert X post: {str(e)}",
        )


@router.get("/x-to-wordpress/validate")
async def validate_x_url(
    url: str = Query(..., description="X/Twitter URL to validate"),
) -> dict:
    """
    Validate X/Twitter URL format.

    Checks if the URL is a valid X/Twitter post URL without making any requests.

    ## Usage

    ```bash
    curl "http://localhost:8000/api/content/x-to-wordpress/validate?url=https://x.com/aparnadhinak/status/2048492731929149929"
    ```

    ## Response

    ```json
    {
      "valid": true,
      "type": "post",
      "username": "aparnadhinak",
      "post_id": "2048492731929149929",
      "url": "https://x.com/aparnadhinak/status/2048492731929149929"
    }
    ```
    """
    from services.x_to_wordpress import XToWordPressConverter

    converter = XToWordPressConverter()
    parsed = converter.parse_x_url(url)

    if parsed is None:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid X/Twitter URL: {url}",
        )

    return {**parsed, "valid": True}


@router.get("/x-to-wordpress/templates")
async def list_wordpress_templates() -> dict:
    """
    List available WordPress import templates.

    Shows example file structures for different content types.
    """
    return {
        "templates": {
            "post": {
                "description": "Single X post",
                "extension": ".txt",
                "fields": ["title", "content", "author", "category", "tags"],
            },
            "thread": {
                "description": "Multi-tweet thread (concatenated)",
                "extension": ".txt",
                "fields": ["title", "content", "author", "category", "tags", "thread_length"],
            },
            "article_link": {
                "description": "Article linked in X post",
                "extension": ".txt",
                "fields": ["title", "content", "author", "original_source", "category", "tags"],
            },
        },
        "output_directory": "docs/content/incoming/",
        "filename_format": "wordpress-[source]-[post_id]-[timestamp].txt",
        "encoding": "utf-8",
    }
