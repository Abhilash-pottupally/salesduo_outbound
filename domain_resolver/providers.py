from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .discovery import SearchResult, SearchProvider


class DomainDiscoveryProvider(Protocol):
    def search(self, query: str, limit: int = 5) -> list[SearchResult]: ...


@dataclass
class StaticProvider:
    """Offline provider used for tests and development without an API key."""
    results: dict[str, list[SearchResult]]

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        return self.results.get(query, [])[:limit]


__all__ = ["DomainDiscoveryProvider", "SearchProvider", "StaticProvider"]
