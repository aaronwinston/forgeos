"""LLM Provider abstraction layer for pluggable AI backends."""

from typing import AsyncGenerator, Protocol, Optional
from config import settings
import anthropic


class LLMProvider(Protocol):
    """Protocol for LLM providers with async streaming."""

    async def stream_message(
        self,
        system: str,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream a message from the LLM.
        
        Args:
            system: System prompt
            messages: Conversation history [{role, content}, ...]
            model: Model name (uses provider default if None)
            max_tokens: Maximum tokens to generate
            
        Yields:
            Text chunks as they arrive
        """
        ...

    async def create_message(
        self,
        system: str,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Create a non-streaming message (full response at once).
        
        Args:
            system: System prompt
            messages: Conversation history
            model: Model name (uses provider default if None)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Full response text
        """
        ...


class AnthropicProvider:
    """Anthropic Claude provider implementation."""

    def __init__(self, api_key: str, default_model: str = "claude-opus-4-7"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_model = default_model

    async def stream_message(
        self,
        system: str,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream message from Anthropic API."""
        model = model or self.default_model
        with self.client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

    async def create_message(
        self,
        system: str,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Create non-streaming message from Anthropic API."""
        model = model or self.default_model
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text


class OpenAIProvider:
    """OpenAI provider stub. Not yet implemented."""

    def __init__(self, api_key: str, default_model: str = "gpt-4"):
        self.api_key = api_key
        self.default_model = default_model

    async def stream_message(
        self,
        system: str,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """OpenAI streaming not yet implemented."""
        raise NotImplementedError(
            "OpenAI provider is not yet implemented. "
            "Use AnthropicProvider or contribute support."
        )
        yield  # Make this an async generator

    async def create_message(
        self,
        system: str,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """OpenAI non-streaming not yet implemented."""
        raise NotImplementedError(
            "OpenAI provider is not yet implemented. "
            "Use AnthropicProvider or contribute support."
        )


# Global provider cache
_providers: dict[str, AnthropicProvider | OpenAIProvider] = {}


def get_provider(name: str = "anthropic") -> AnthropicProvider | OpenAIProvider:
    """Get or create an LLM provider by name.
    
    Args:
        name: Provider name ("anthropic" or "openai")
        
    Returns:
        Provider instance
        
    Raises:
        ValueError: If provider name is not recognized
    """
    if name in _providers:
        return _providers[name]

    if name == "anthropic":
        provider = AnthropicProvider(
            api_key=settings.ANTHROPIC_API_KEY,
            default_model=settings.MODEL_GENERATION,
        )
    elif name == "openai":
        provider = OpenAIProvider(
            api_key=settings.OPENAI_API_KEY,
            default_model="gpt-4",
        )
    else:
        raise ValueError(f"Unknown LLM provider: {name}")

    _providers[name] = provider
    return provider
