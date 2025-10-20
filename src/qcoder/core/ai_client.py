"""AI client for interacting with language models via OpenRouter."""

from typing import Any, AsyncIterator, Optional
import json
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from .config import get_config


class AIClient:
    """Client for interacting with AI models through OpenRouter API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
    ) -> None:
        """Initialize AI client.

        Args:
            api_key: OpenRouter API key. If None, uses config.
            model: Model identifier. If None, uses config default.
            base_url: OpenRouter API base URL.
        """
        config = get_config()
        self.api_key = api_key or config.api_key
        self.model = model or config.model
        self.base_url = base_url

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ChatCompletion | AsyncIterator[ChatCompletionChunk]:
        """Send a chat completion request.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response.
            **kwargs: Additional parameters for the API.

        Returns:
            ChatCompletion response or stream iterator.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                extra_headers={
                    "HTTP-Referer": "https://github.com/qcoder-cli",
                    "X-Title": "QCoder CLI",
                },
                **kwargs,
            )
            return response
        except Exception as e:
            raise RuntimeError(f"AI API request failed: {e}") from e

    async def achat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> ChatCompletion | AsyncIterator[ChatCompletionChunk]:
        """Async version of chat completion request.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            temperature: Sampling temperature (0.0 to 2.0).
            max_tokens: Maximum tokens to generate.
            stream: Whether to stream the response.
            **kwargs: Additional parameters for the API.

        Returns:
            ChatCompletion response or async stream iterator.
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream,
                extra_headers={
                    "HTTP-Referer": "https://github.com/qcoder-cli",
                    "X-Title": "QCoder CLI",
                },
                **kwargs,
            )
            return response
        except Exception as e:
            raise RuntimeError(f"AI API request failed: {e}") from e

    def get_models(self) -> list[dict[str, Any]]:
        """Get list of available models from OpenRouter.

        Returns:
            List of model information dictionaries.
        """
        try:
            models = self.client.models.list()
            return [
                {
                    "id": model.id,
                    "name": getattr(model, "name", model.id),
                    "context_length": getattr(model, "context_length", None),
                }
                for model in models.data
            ]
        except Exception as e:
            raise RuntimeError(f"Failed to fetch models: {e}") from e

    def extract_text_response(self, response: ChatCompletion) -> str:
        """Extract text content from a chat completion response.

        Args:
            response: ChatCompletion response object.

        Returns:
            Text content of the response.
        """
        if not response.choices:
            return ""

        message = response.choices[0].message
        return message.content or ""

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text.

        This is a rough estimation. For accurate counts, use tiktoken.

        Args:
            text: Text to count tokens for.

        Returns:
            Estimated token count.
        """
        # Rough estimation: 1 token ≈ 4 characters for English text
        return len(text) // 4

    def create_system_prompt(self, base_prompt: str, context: Optional[str] = None) -> str:
        """Create a system prompt with optional context.

        Args:
            base_prompt: Base system prompt.
            context: Additional context to include.

        Returns:
            Combined system prompt.
        """
        if not context:
            return base_prompt

        return f"{base_prompt}\n\n# Additional Context\n{context}"


# Global AI client instance
_ai_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """Get or create global AI client instance.

    Returns:
        Global AIClient instance.
    """
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClient()
    return _ai_client
