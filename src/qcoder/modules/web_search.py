"""Web search integration for grounding AI responses using DuckDuckGo."""

from typing import Optional, Any
import httpx
from urllib.parse import quote_plus

from ..core.config import get_config
from ..core.ai_client import get_ai_client
from ..utils.output import Console


class WebSearch:
    """Handles web search for grounding AI responses with up-to-date information using DuckDuckGo."""

    def __init__(self) -> None:
        """Initialize web search handler."""
        self.config = get_config()
        self.ai_client = get_ai_client()
        self.console = Console()

    def search(self, query: str, num_results: int = 5) -> list[dict[str, Any]]:
        """Perform web search using DuckDuckGo.

        Args:
            query: Search query.
            num_results: Number of results to return.

        Returns:
            List of search result dictionaries with title, url, snippet.
        """
        return self._search_duckduckgo(query, num_results)

    def _search_duckduckgo(self, query: str, num_results: int) -> list[dict[str, Any]]:
        """Search using DuckDuckGo (no API key required).

        Args:
            query: Search query.
            num_results: Number of results.

        Returns:
            List of search results.
        """
        try:
            # Using DuckDuckGo HTML search (unofficial API)
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"

            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                )
                response.raise_for_status()

            # Simple HTML parsing (basic extraction)
            results = []
            content = response.text

            # Extract results (this is a simplified approach)
            # In production, consider using BeautifulSoup or lxml
            snippets = content.split('class="result__snippet">')
            for i, snippet in enumerate(snippets[1 : num_results + 1], 1):
                end = snippet.find("</a>")
                if end > 0:
                    text = snippet[:end]
                    # Clean HTML tags
                    text = text.replace("<b>", "").replace("</b>", "")
                    results.append(
                        {
                            "title": f"Result {i}",
                            "url": "N/A",
                            "snippet": text.strip()[:300],
                        }
                    )

            return results if results else self._fallback_search_results(query)

        except Exception as e:
            self.console.warning(f"DuckDuckGo search failed: {e}")
            return self._fallback_search_results(query)


    def _fallback_search_results(self, query: str) -> list[dict[str, Any]]:
        """Provide fallback message when search fails.

        Args:
            query: Original search query.

        Returns:
            List with fallback message.
        """
        return [
            {
                "title": "Search Unavailable",
                "url": "N/A",
                "snippet": f"Web search is currently unavailable. Query was: {query}",
            }
        ]

    def search_and_summarize(self, query: str, num_results: int = 5) -> str:
        """Search the web and get AI summary of results.

        Args:
            query: Search query.
            num_results: Number of results to search.

        Returns:
            AI-generated summary of search results.
        """
        # Perform search
        results = self.search(query, num_results)

        if not results:
            return "No search results found."

        # Format results for AI
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append(
                f"{i}. **{result['title']}**\n"
                f"   URL: {result['url']}\n"
                f"   {result['snippet']}\n"
            )

        search_content = "\n".join(formatted_results)

        # Get AI summary
        messages = [
            {
                "role": "system",
                "content": "You are an expert at synthesizing information from web search results. "
                "Provide accurate, well-organized summaries with source attribution.",
            },
            {
                "role": "user",
                "content": f"Summarize these search results for the query: '{query}'\n\n"
                f"Search Results:\n{search_content}\n\n"
                "Provide:\n"
                "1. Concise summary of key information\n"
                "2. Important facts and findings\n"
                "3. Any conflicting information (if present)\n"
                "4. Source references (by result number)",
            },
        ]

        response = self.ai_client.chat(messages)
        return self.ai_client.extract_text_response(response)

    def ground_response(self, question: str, context: Optional[str] = None) -> str:
        """Get AI response grounded in current web information.

        Args:
            question: User's question.
            context: Optional additional context.

        Returns:
            AI response grounded in web search results.
        """
        # Perform search with the question
        search_results = self.search(question, num_results=5)

        # Format search results
        formatted_results = []
        for result in search_results:
            formatted_results.append(
                f"- {result['title']}: {result['snippet']}\n  Source: {result['url']}"
            )

        search_context = "\n".join(formatted_results)

        # Build prompt with search results
        system_prompt = (
            "You are QCoder, an AI assistant. Answer questions accurately using "
            "the provided web search results as primary sources. "
            "Always cite sources when referencing information."
        )

        user_prompt = f"Question: {question}\n\n"

        if context:
            user_prompt += f"Additional Context:\n{context}\n\n"

        user_prompt += f"Web Search Results:\n{search_context}\n\n"
        user_prompt += (
            "Please answer the question using the search results. "
            "Cite sources by mentioning the result titles or URLs."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = self.ai_client.chat(messages, temperature=0.5)
        return self.ai_client.extract_text_response(response)

    def fact_check(self, statement: str) -> str:
        """Fact-check a statement using web search.

        Args:
            statement: Statement to fact-check.

        Returns:
            Fact-check result with sources.
        """
        # Search for information about the statement
        search_query = f"fact check {statement}"
        results = self.search(search_query, num_results=5)

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(f"- {result['title']}\n  {result['snippet']}\n  {result['url']}")

        search_content = "\n".join(formatted_results)

        # Get AI fact-check analysis
        messages = [
            {
                "role": "system",
                "content": "You are a fact-checking expert. Analyze statements objectively "
                "using available sources and provide clear verdicts.",
            },
            {
                "role": "user",
                "content": f"Fact-check this statement:\n\n'{statement}'\n\n"
                f"Sources:\n{search_content}\n\n"
                "Provide:\n"
                "1. Verdict: True / False / Partially True / Unverifiable\n"
                "2. Explanation with evidence\n"
                "3. Source citations\n"
                "4. Important context or nuances",
            },
        ]

        response = self.ai_client.chat(messages, temperature=0.3)
        return self.ai_client.extract_text_response(response)
