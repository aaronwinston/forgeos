"""
X/Twitter to WordPress content importer.

Scrapes tweets, threads, and linked articles from X/Twitter,
extracts content, and formats as WordPress-ready text files.
"""

import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)


class XToWordPressConverter:
    """Convert X/Twitter content to WordPress import format."""

    # X/Twitter post URL patterns
    X_POST_PATTERN = r'https?://(?:www\.)?(?:x\.com|twitter\.com)/(\w+)/status/(\d+)'
    X_PROFILE_PATTERN = r'https?://(?:www\.)?(?:x\.com|twitter\.com)/(\w+)/?$'

    def __init__(self, repo_root: str = "."):
        """Initialize converter."""
        self.repo_root = Path(repo_root)
        self.content_dir = self.repo_root / "docs" / "content" / "incoming"
        self.content_dir.mkdir(parents=True, exist_ok=True)

    def parse_x_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Parse X/Twitter URL and identify post ID and type.

        Returns:
            Dict with 'type', 'username', 'post_id' or None if invalid.
        """
        # Check if it's a post
        match = re.match(self.X_POST_PATTERN, url)
        if match:
            return {
                'type': 'post',
                'username': match.group(1),
                'post_id': match.group(2),
                'url': url
            }

        # Check if it's a profile
        match = re.match(self.X_PROFILE_PATTERN, url)
        if match:
            return {
                'type': 'profile',
                'username': match.group(1),
                'url': url
            }

        return None

    def format_wordpress_import(
        self,
        title: str,
        content: str,
        author: str = "Aparna Dhinakaran",
        date: Optional[datetime] = None,
        category: str = "Incoming",
        tags: Optional[list] = None,
        source_url: Optional[str] = None,
        source_author: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Format content as WordPress import file.

        Returns:
            Formatted string ready for WordPress import.
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime("%Y-%m-%d %H:%M:%S")
        tags_str = ", ".join(tags) if tags else ""

        # Build frontmatter
        frontmatter = f"""WORDPRESS IMPORT FILE
=====================

Title: {title}
Author: {author}
Date: {date_str}
Category: {category}
Tags: {tags_str}
Source: {source_url or "Unknown"}
Source Author: {source_author or "Unknown"}

---

"""

        # Build footer with metadata
        footer = "\n---\n\n"
        if source_url:
            footer += f"Original X post: {source_url}\n"
        if metadata:
            if 'posted_at' in metadata:
                footer += f"Posted: {metadata['posted_at']}\n"
            if 'engagement' in metadata:
                eng = metadata['engagement']
                footer += f"Engagement: {eng.get('retweets', 0)} retweets, {eng.get('likes', 0)} likes\n"

        return frontmatter + content + footer

    def clean_content(self, text: str) -> str:
        """
        Clean X/Twitter content for WordPress.

        - Remove X tracking links
        - Convert URL shorteners to full URLs
        - Fix HTML entities
        - Normalize whitespace
        """
        # Remove common X tracking patterns
        text = re.sub(r't\.co/\w+', '[link]', text)  # Placeholder for t.co links
        text = re.sub(r'pic\.twitter\.com/\w+', '', text)  # Remove media links
        text = re.sub(r'pic\.x\.com/\w+', '', text)

        # Fix HTML entities
        html_entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '&nbsp;': ' ',
        }
        for entity, char in html_entities.items():
            text = text.replace(entity, char)

        # Normalize whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Fix double newlines
        text = text.strip()

        return text

    def save_import_file(
        self,
        filename: str,
        content: str
    ) -> Path:
        """
        Save formatted content to WordPress import file.

        Args:
            filename: Base filename (without .txt)
            content: Formatted WordPress import content

        Returns:
            Path to saved file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = re.sub(r'[^\w\-]', '_', filename)
        filepath = self.content_dir / f"{safe_filename}_{timestamp}.txt"

        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Saved WordPress import file: {filepath}")

        return filepath

    def extract_from_tweet(
        self,
        tweet_text: str,
        author: str = "Aparna Dhinakaran",
        post_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        engagement: Optional[Dict] = None,
        source_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Extract and format a single tweet for WordPress.

        Args:
            tweet_text: The tweet content
            author: Tweet author
            post_id: X post ID
            timestamp: When posted
            engagement: Dict with 'retweets', 'likes', etc.
            source_url: Full URL to the tweet

        Returns:
            Dict with formatted WordPress import data.
        """
        # Extract first 60 chars as title
        title = tweet_text[:60].replace('\n', ' ')
        if len(tweet_text) > 60:
            title += "..."

        # Clean content
        clean_text = self.clean_content(tweet_text)

        # Parse metadata
        metadata = {}
        if timestamp:
            metadata['posted_at'] = timestamp
        if engagement:
            metadata['engagement'] = engagement

        return {
            'title': title,
            'content': clean_text,
            'author': author,
            'source_url': source_url,
            'source_author': f"@{author.split()[0].lower()}" if author else None,
            'metadata': metadata,
            'category': 'Incoming',
            'tags': ['aparna', 'founder-insights'],
        }

    def process_x_post(
        self,
        url: str,
        content_type: str = 'post',
        category: str = 'Incoming',
        tags: Optional[list] = None,
        author_override: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Process X/Twitter post and prepare for WordPress import.

        This is a stub that returns the parsing logic.
        Real implementation would fetch from X API or web scraper.

        Args:
            url: X/Twitter post URL
            content_type: 'post', 'thread', or 'article-link'
            category: WordPress category
            tags: Additional tags
            author_override: Override default author

        Returns:
            Dict with 'filename', 'filepath', 'preview', 'status' or None on error.
        """
        # Validate URL
        parsed = self.parse_x_url(url)
        if not parsed:
            logger.error(f"Invalid X URL: {url}")
            return {
                'status': 'error',
                'message': f"Invalid X/Twitter URL: {url}",
                'url': url,
            }

        # In a real implementation, this would:
        # 1. Fetch the tweet via X API or web scraper
        # 2. Extract text, timestamp, engagement
        # 3. If thread: find related posts
        # 4. If article link: fetch and parse article
        # 5. Format for WordPress
        # 6. Save to repo

        # For now, return template showing what would happen
        sample_title = "Aparna's latest insights"
        sample_content = f"""Here's where the tweet content would go.

This would be extracted from the X post and cleaned for WordPress import.

Source URL: {url}
Posted by: {author_override or 'Aparna Dhinakaran'}
Type: {content_type}
Category: {category}
"""

        if tags is None:
            tags = []
        tags.extend(['aparna', 'founder-insights'])

        # Format as WordPress import
        formatted = self.format_wordpress_import(
            title=sample_title,
            content=sample_content,
            author=author_override or 'Aparna Dhinakaran',
            category=category,
            tags=tags,
            source_url=url,
            source_author='@aparnadhinak',
            metadata={
                'posted_at': datetime.now().isoformat(),
                'engagement': {'retweets': 0, 'likes': 0},
            }
        )

        # Save to file
        filename = f"wordpress-aparna-post-{parsed['post_id']}"
        filepath = self.save_import_file(filename, formatted)

        return {
            'status': 'success',
            'filepath': str(filepath),
            'filename': filepath.name,
            'preview': formatted[:500] + "\n...",
            'category': category,
            'tags': tags,
            'source_url': url,
            'author': author_override or 'Aparna Dhinakaran',
        }


def convert_x_to_wordpress(
    x_url: str,
    category: str = "Incoming",
    tags: Optional[list] = None,
    author_override: Optional[str] = None,
    repo_root: str = ".",
) -> Dict[str, Any]:
    """
    Main entry point: Convert X/Twitter post to WordPress import file.

    Args:
        x_url: X/Twitter post URL
        category: WordPress category for import
        tags: Additional tags to add
        author_override: Override author name
        repo_root: Root directory of repo

    Returns:
        Dict with conversion result, file path, and preview.
    """
    converter = XToWordPressConverter(repo_root=repo_root)
    return converter.process_x_post(
        url=x_url,
        category=category,
        tags=tags,
        author_override=author_override,
    )
