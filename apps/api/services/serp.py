"""SERP (Search Engine Results Page) adapter interface."""

from abc import ABC, abstractmethod
from typing import Optional


class SERPProvider(ABC):
    """
    Abstract base for SERP data providers (SerpAPI, Exa, Brave, etc).
    
    This is a stub interface for future implementation. The free-tier
    cross-reference pass works with GSC + Trends data; SERP data is optional.
    """
    
    @abstractmethod
    async def search(self, query: str, num_results: int = 10) -> list[dict]:
        """
        Perform a web search and return top results.
        
        Args:
            query: Search query string
            num_results: Number of results to return
        
        Returns:
            List of dicts with: title, url, snippet, position
        """
        pass
    
    @abstractmethod
    async def get_rank(self, query: str, target_url: str) -> Optional[int]:
        """
        Get the rank of a target URL for a given query.
        
        Args:
            query: Search query
            target_url: URL to find rank for
        
        Returns:
            Position in SERP (1-indexed), or None if not found in top 100
        """
        pass


class SERPProviderStub(SERPProvider):
    """Stub implementation that raises NotImplementedError."""
    
    async def search(self, query: str, num_results: int = 10) -> list[dict]:
        """SERP search not yet implemented in free tier."""
        raise NotImplementedError(
            "Web search via SERP providers is a v2 feature. "
            "Cross-reference pass currently uses only Google Search Console + Google Trends data. "
            "To add broad web search: set SERP_PROVIDER=serpapi|exa|brave in .env and provide API key."
        )
    
    async def get_rank(self, query: str, target_url: str) -> Optional[int]:
        """SERP rank check not yet implemented in free tier."""
        raise NotImplementedError(
            "Web search via SERP providers is a v2 feature. "
            "Cross-reference pass currently uses only Google Search Console + Google Trends data."
        )
