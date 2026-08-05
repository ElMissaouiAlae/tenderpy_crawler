"""Pagination logic for discovery searches."""

from __future__ import annotations

from dataclasses import dataclass
from discovery.parser import SearchResultPage


@dataclass
class PageParams:
    """Represents pagination parameters for a POST request."""

    current_page: int
    page_size: int
    total_pages: int | None = None


class Paginator:
    """Manage pagination state and generate next page payloads."""

    PAGE_NUMBER_TOP_PARAM = "ctl0$CONTENU_PAGE$resultSearch$numPageTop"
    PAGE_SIZE_TOP_PARAM = "ctl0$CONTENU_PAGE$resultSearch$listePageSizeTop"
    PAGE_NUMBER_BOTTOM_PARAM = "ctl0$CONTENU_PAGE$resultSearch$numPageBottom"
    PAGE_SIZE_BOTTOM_PARAM = "ctl0$CONTENU_PAGE$resultSearch$listePageSizeBottom"

    def __init__(self) -> None:
        """Initialize paginator to a pre-search state.

        All fields are placeholders until the first `sync_from_page()` call,
        which is the sole source of truth for pagination state — see
        `Client.search()`.
        """
        self._current_page = 1
        self._page_size: int | None = None   # unknown until first response
        self._total_pages: int | None = None

    def has_next_page(self) -> bool:
        """Check if another page exists."""
        if self._total_pages is None:
            # If total pages unknown, assume more pages exist
            return True
        return self._current_page < self._total_pages

    def set_total_pages(self, total_pages: int | None) -> None:
        """Update total pages from search results."""
        self._total_pages = total_pages

    @property
    def current_page(self) -> int:
        """Get the current page number."""
        return self._current_page

    @property
    def page_size(self) -> int:
        """Get the page size."""
        return self._page_size

    @page_size.setter
    def page_size(self, size: int) -> None:
        """Set the page size."""
        if size <= 0:
            raise ValueError("Page size must be greater than 0")
        self._page_size = size

    @property
    def total_pages(self) -> int | None:
        """Get the total number of pages."""
        return self._total_pages
    
    def sync_from_page(self, page: SearchResultPage) -> None:
        """Reconcile paginator state with the server's authoritative response.

        This is the ONLY path by which current_page/page_size are updated
        post-request. Called after every request, first page or not.
        """
        if page.current_page is not None:
            self._current_page = page.current_page
        if page.page_size is not None:
            self.page_size = page.page_size  # goes through the validating setter
        self.set_total_pages(page.total_pages)

    def next_page_payload(self) -> dict[str, str]:
        """Generate POST payload parameters for the next page."""
        
        if not self.has_next_page():
            raise StopIteration("No more pages available")

        self._current_page += 1

        return {
            self.PAGE_NUMBER_TOP_PARAM: str(self._current_page),
            self.PAGE_SIZE_TOP_PARAM: str(self._page_size),
            self.PAGE_NUMBER_BOTTOM_PARAM: str(self._current_page),
            self.PAGE_SIZE_BOTTOM_PARAM: str(self._page_size),
        }

    def reset(self, page_size: int | None = None) -> None:
        """Reset pagination to the first page."""
        self._current_page = 1
        if page_size is not None:
            self._page_size = page_size
        else:
            self._page_size = None
        
        self._total_pages = None
