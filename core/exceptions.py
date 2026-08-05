"""Custom exceptions for the crawler package."""


class CrawlerException(Exception):
    """Base exception for crawler-related failures."""


class HttpRequestError(CrawlerException):
    """Raised when an HTTP request fails."""

    def __init__(self, message: str, set_cookies: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.set_cookies = set_cookies or {}


class SessionInitializationError(CrawlerException):
    """Raised when session initialization fails."""


class PradoStateError(CrawlerException):
    """Raised when PRADO state cannot be extracted or updated."""


class HtmlParsingError(CrawlerException):
    """Raised when HTML cannot be parsed for PRADO state."""


class SearchExecutionError(CrawlerException):
    """Raised when search execution fails."""


class PaginationError(CrawlerException):
    """Raised when pagination logic fails."""


class SearchParsingError(CrawlerException):
    """Raised when search results cannot be parsed."""


class MissingTenderFieldError(CrawlerException):
    """Raised when a required tender field is missing."""
