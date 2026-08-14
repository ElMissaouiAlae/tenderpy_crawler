"""Tests for the downloader module."""

from unittest.mock import Mock

from downloader import TenderDownloader


def test_tender_downloader_initialization():
    http_client = Mock()
    downloader = TenderDownloader(http_client, "1032737", "j0w")

    assert downloader._http_client is http_client
    assert downloader._tender_id == "1032737"
    assert downloader._organization_acronym == "j0w"


def test_download_url_builds_expected_query_string():
    http_client = Mock()
    downloader = TenderDownloader(http_client, "1032737", "j0w")

    assert downloader.download_url == (
        "?page=entreprise.EntrepriseDownloadCompleteDce"
        "&reference=1032737&orgAcronym=j0w"
    )


def test_download_calls_http_client_get_with_download_url():
    http_client = Mock()
    mock_response = Mock(content=b"PK\x03\x04fake-zip-bytes")
    http_client.get = Mock(return_value=mock_response)

    downloader = TenderDownloader(http_client, "1032737", "j0w")
    response = downloader.download()

    http_client.get.assert_called_once_with(downloader.download_url)
    assert response is mock_response
    assert response.content == b"PK\x03\x04fake-zip-bytes"
