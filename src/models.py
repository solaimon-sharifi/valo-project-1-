"""
Domain models for the web search demo application.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class SearchOptions:
    """Configuration options for web search requests."""
    
    model: str = "gpt-4o-mini"
    allowed_domains: Optional[List[str]] = None
    user_location: Optional[Dict[str, Any]] = None
    reasoning_effort: str = "low"


@dataclass
class Citation:
    """Represents a citation from a web search result."""
    
    url: str
    title: str
    start_index: int
    end_index: int
    
    @property
    def length(self) -> int:
        """Calculate the length of the cited text."""
        return self.end_index - self.start_index
    
    def __str__(self) -> str:
        """String representation of the citation."""
        return f"[{self.title}]({self.url})"


@dataclass
class Source:
    """Represents a source consulted during web search."""
    
    url: str
    type: str  # 'web', 'oai-sports', 'oai-weather', 'oai-finance', etc.
    
    @property
    def is_special(self) -> bool:
        """Check if this is a special OpenAI source."""
        return self.type.startswith("oai-")
    
    def __str__(self) -> str:
        """String representation of the source."""
        return f"{self.url} ({self.type})"


@dataclass
class SearchResult:
    """Represents the complete result of a web search operation."""
    
    query: str
    text: str
    citations: List[Citation]
    sources: List[Source]
    search_id: str
    timestamp: datetime
    
    @property
    def has_citations(self) -> bool:
        """Check if the result has any citations."""
        return len(self.citations) > 0
    
    def __str__(self) -> str:
        """String representation of the search result."""
        return f"SearchResult(query='{self.query}', citations={len(self.citations)})"


@dataclass
class SearchError(Exception):
    """Custom exception for search-related errors."""
    
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """String representation of the error."""
        error_str = f"[{self.code}] {self.message}"
        if self.details:
            error_str += f" | Details: {self.details}"
        return error_str
