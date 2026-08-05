from datetime import date

import pytest

from core.models import Tender
from discovery.parser import SearchCriteria, SearchResultPage, SearchResultParser
from core.exceptions import HtmlParsingError


def test_search_criteria_defaults_to_none():
    criteria = SearchCriteria()

    assert criteria.keyword is None
    assert criteria.buyer is None
    assert criteria.organization is None
    assert criteria.publication_date_from is None
    assert criteria.publication_date_to is None


def test_search_criteria_accepts_date_filters():
    criteria = SearchCriteria(
        keyword="infrastructure",
        buyer="City Hall",
        organization="Public Works",
        publication_date_from=date(2026, 1, 15),
        publication_date_to=date(2026, 1, 30),
    )

    assert criteria.keyword == "infrastructure"
    assert criteria.buyer == "City Hall"
    assert criteria.organization == "Public Works"
    assert criteria.publication_date_from == date(2026, 1, 15)
    assert criteria.publication_date_to == date(2026, 1, 30)


def test_search_criteria_rejects_from_date_after_to_date():
    with pytest.raises(ValueError, match="publication_date_from must be <= publication_date_to"):
        SearchCriteria(
            publication_date_from=date(2026, 2, 1),
            publication_date_to=date(2026, 1, 31),
        )


def test_tender_creation_with_defaults():
    tender = Tender()
    assert tender.tender_id is None
    assert tender.organization_acronym is None
    assert tender.procurement_type is None
    assert tender.category is None


def test_tender_creation_with_values():
    tender = Tender(
        tender_id="12345",
        organization_acronym="ORG",
        procurement_type="Open",
        category="Works",
        publication_date="15/01/2026",
        reference_number="REF-001",
        tender_object="Construction work",
        public_buyer="City Council",
        location="Paris",
        tender_end_date="30/01/2026"
    )
    assert tender.tender_id == "12345"
    assert tender.organization_acronym == "ORG"
    assert tender.procurement_type == "Open"


def test_search_result_page_creation_with_defaults():
    page = SearchResultPage()
    assert page.tenders == []
    assert page.current_page is None
    assert page.total_pages is None
    assert page.page_size is None
    assert page.total_results is None


def test_search_result_page_creation_with_values():
    tenders = [Tender(tender_id="1"), Tender(tender_id="2")]
    page = SearchResultPage(
        tenders=tenders,
        current_page=1,
        total_pages=5,
        page_size=20,
        total_results=100
    )
    assert len(page.tenders) == 2
    assert page.current_page == 1
    assert page.total_pages == 5


def test_search_result_parser_raises_on_empty_html():
    parser = SearchResultParser()
    with pytest.raises(HtmlParsingError, match="Received empty HTML response"):
        parser.parse("")


def test_search_result_parser_handles_missing_table():
    html = "<html><body><p>No table here</p></body></html>"
    parser = SearchResultParser()
    page = parser.parse(html)
    assert page.tenders == []
    assert page.current_page is None


def test_search_result_parser_extracts_pagination():
    html = """
    <html>
        <body>
            <input id="ctl0_CONTENU_PAGE_resultSearch_numPageTop" value="2" />
            <span id="ctl0_CONTENU_PAGE_resultSearch_nombrePageTop">5</span>
            <select id="ctl0_CONTENU_PAGE_resultSearch_listePageSizeTop">
                <option value="20" selected>20</option>
            </select>
            <span id="ctl0_CONTENU_PAGE_resultSearch_nombreElement">100</span>
        </body>
    </html>
    """
    parser = SearchResultParser()
    page = parser.parse(html)
    assert page.current_page == 2
    assert page.total_pages == 5
    assert page.page_size == 20
    assert page.total_results == 100


def test_search_result_parser_handles_missing_pagination():
    html = "<html><body><p>No pagination</p></body></html>"
    parser = SearchResultParser()
    page = parser.parse(html)
    assert page.current_page is None
    assert page.total_pages is None
    assert page.page_size is None
    assert page.total_results is None
