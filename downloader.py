"""Download the DCE (Dossier de Consultation des Entreprises) zip archive for a tender."""

from __future__ import annotations

from urllib.parse import urlencode

import requests

from core.http import HttpClient


class TenderDownloader:
    """Fetch the DCE zip archive for a single tender via a direct GET request.
    """

    DOWNLOAD_PAGE = "entreprise.EntrepriseDownloadCompleteDce"

    def __init__(self, http_client: HttpClient, tender_id: str, organization_acronym: str) -> None:
        """Initialize the downloader with an HttpClient and the target tender's identity."""
        self._http_client = http_client
        self._tender_id = tender_id
        self._organization_acronym = organization_acronym

    @property
    def download_url(self) -> str:
        """Build the direct DCE download URL for this tender.

        tender_id/organization_acronym are untrusted values scraped off search
        results, so they're run through urlencode rather than interpolated
        directly - a reserved character (e.g. "&") would otherwise split or
        truncate the query string.
        """
        query = urlencode({
            "page": self.DOWNLOAD_PAGE,
            "reference": self._tender_id,
            "orgAcronym": self._organization_acronym,
        })
        return f"?{query}"

    def download(self) -> requests.Response:
        """Fetch the DCE zip archive; `.content` holds the raw zip bytes."""
        return self._http_client.get(self.download_url)
