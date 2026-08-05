"""Domain models for crawler session state."""

from __future__ import annotations

from dataclasses import dataclass

from .exceptions import PradoStateError


@dataclass
class Tender:
    """Represents a single tender discovered in search results."""

    tender_id: str | None = None
    organization_acronym: str | None = None
    procurement_type: str | None = None
    category: str | None = None
    publication_date: str | None = None
    reference_number: str | None = None
    tender_object: str | None = None
    public_buyer: str | None = None
    location: str | None = None
    tender_end_date: str | None = None


@dataclass
class SessionState:
    """Represents the current hidden PRADO state for a server session."""

    prado_page_state: str | None = None
    
    def to_payload(self) -> dict[str, str]:
        """Convert the current PRADO session state into POST parameters.

        Raises:
            PradoStateError: if PRADO_PAGESTATE hasn't been captured yet —
                every postback requires it, so a missing value here means
                this was called before any page was fetched.
        """
        if self.prado_page_state is None:
            raise PradoStateError(
                "PRADO_PAGESTATE is not set — fetch a page before building a payload"
            )

        return {
            "PRADO_PAGESTATE": self.prado_page_state,
            "PRADO_POSTBACK_PARAMETER": "undefined",
        }
