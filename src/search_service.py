"""
Search service for orchestrating web search operations.

This module provides the business logic layer for web search.
"""

from typing import Any, Dict, List, Optional

# Local application imports
from src.client import WebSearchClient
from src.models import SearchError, SearchOptions, SearchResult
from src.parser import ResponseParser


# A tiny demo client used when no API key is available. This returns a
# minimal response structure compatible with ResponseParser so the app can
# run in "demo" mode without calling the real OpenAI API.
class _DummyWebSearchClient:  # pragma: no cover
    def __init__(self):
        self.api_key = None

    def search(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> Dict[str, Any]:
        # Return a minimal, deterministic response that the parser can handle
        return {
            "id": "demo-1",
            "model": "demo",
            "created": 0,
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": f"Demo answer for: {query}",
                            "annotations": [
                                {
                                    "type": "url_citation",
                                    "url": "https://example.com",
                                    "title": "Example Domain",
                                    "start_index": 0,
                                    "end_index": 10,
                                }
                            ],
                        }
                    ],
                },
                {
                    "type": "web_search_call",
                    "id": "demo-search-1",
                    "action": {
                        "sources": [{"url": "https://example.com", "type": "web"}]
                    },
                },
            ],
        }


class SearchService:
    """Service for coordinating web search operations.

    This is the production service which expects a valid API key. It will
    raise a ValueError if initialized without one (preserves previous test
    expectations).
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the search service.

        Args:
            api_key: OpenAI API key

        Raises:
            ValueError: If no API key is provided
        """
        if not api_key:
            raise ValueError("API key is required")

        self.client = WebSearchClient(api_key=api_key)
        self.parser = ResponseParser()

    def search(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> SearchResult:
        """
        Perform a web search.

        Args:
            query: The search query
            options: Optional search configuration

        Returns:
            SearchResult with parsed data

        Raises:
            ValueError: If query is invalid
            SearchError: If search fails
        """
        # Validate query
        if not self.validate_query(query):
            raise ValueError(
                "Invalid query: must be non-empty and under 5000 characters"
            )

        # Use default options if none provided
        if options is None:
            options = SearchOptions()

        try:
            # Perform search via client
            raw_response = self.client.search(query, options)

            # Parse response
            result = self.parser.parse(raw_response, query)

            return result

        except SearchError:
            # Re-raise search errors
            raise
        except Exception as e:
            # Wrap other exceptions
            raise SearchError(
                code="SEARCH_FAILED",
                message=f"Search operation failed: {str(e)}",
                details={"original_error": str(e)},
            )

    def validate_query(self, query: str) -> bool:
        """
        Validate a search query.

        Args:
            query: The query to validate

        Returns:
            True if valid, False otherwise
        """
        if not query:
            return False

        # Check if query is just whitespace
        if not query.strip():
            return False

        # Check length
        if len(query) > 5000:
            return False

        return True

    def apply_domain_filters(self, domains: List[str]) -> SearchOptions:
        """
        Create SearchOptions with domain filtering.

        Args:
            domains: List of allowed domains

        Returns:
            SearchOptions with domain filters applied

        Raises:
            ValueError: If domains are invalid
        """
        # Validate domains
        if len(domains) > 20:
            raise ValueError("Too many domains (max 20 allowed)")

        for domain in domains:
            # Check for invalid domain format
            if domain.startswith("http://") or domain.startswith(
                "https://"
            ):  # pragma: no cover
                # Edge case: user includes protocol (should be validated earlier)
                raise ValueError(
                    f"Invalid domain '{domain}': remove http:// or https:// prefix"
                )

            # Basic validation
            if not domain or " " in domain:  # pragma: no cover
                # Edge case: spaces in domain (should be caught earlier)
                raise ValueError(f"Invalid domain format: '{domain}'")

        return SearchOptions(allowed_domains=domains)


class DemoSearchService:  # pragma: no cover
    """A lightweight demo search service used when a real API key is not
    available. It mimics the public API of SearchService but uses a local
    dummy client so the app can be run for demos without secrets.
    """

    def __init__(self):
        self.client = _DummyWebSearchClient()
        self.parser = ResponseParser()

    def search(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> SearchResult:
        # Reuse the same logic as the production service but with a local client
        if not self.validate_query(query):
            raise ValueError(
                "Invalid query: must be non-empty and under 5000 characters"
            )

        if options is None:
            options = SearchOptions()

        try:
            raw_response = self.client.search(query, options)
            result = self.parser.parse(raw_response, query)
            return result
        except SearchError:
            raise
        except Exception as e:
            raise SearchError(
                code="SEARCH_FAILED",
                message=f"Search operation failed: {str(e)}",
                details={"original_error": str(e)},
            )

    def validate_query(self, query: str) -> bool:
        if not query:
            return False
        if not query.strip():
            return False
        if len(query) > 5000:
            return False
        return True

    def apply_domain_filters(self, domains: List[str]) -> SearchOptions:
        if len(domains) > 20:
            raise ValueError("Too many domains (max 20 allowed)")
        for domain in domains:
            if domain.startswith("http://") or domain.startswith("https://"):
                raise ValueError(
                    f"Invalid domain '{domain}': remove http:// or https:// prefix"
                )
            if not domain or " " in domain:
                raise ValueError(f"Invalid domain format: '{domain}'")
        return SearchOptions(allowed_domains=domains)


def create_search_service(
    api_key: Optional[str] = None, allow_demo: bool = False
):  # pragma: no cover
    """Factory that returns a SearchService or DemoSearchService depending on
    whether an API key is provided and demo mode is allowed.
    """
    if api_key:
        return SearchService(api_key=api_key)
    if allow_demo:
        return DemoSearchService()
    # Preserve original behavior
    return SearchService(api_key=api_key)
