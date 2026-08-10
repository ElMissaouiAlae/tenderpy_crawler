"""Tests for discovery.paginator module."""

import pytest

from core.exceptions import PaginationError
from discovery.paginator import Paginator, PageParams
from discovery.parser import SearchResultPage


def test_page_params_creation():
    params = PageParams(current_page=1, page_size=20, total_pages=5)
    assert params.current_page == 1
    assert params.page_size == 20
    assert params.total_pages == 5


def test_page_params_without_total_pages():
    params = PageParams(current_page=1, page_size=20)
    assert params.current_page == 1
    assert params.page_size == 20
    assert params.total_pages is None


def test_paginator_initialization():
    paginator = Paginator()
    assert paginator.current_page == 1
    assert paginator.page_size is None
    assert paginator.total_pages is None


def test_paginator_has_next_page_when_total_unknown():
    paginator = Paginator()
    assert paginator.has_next_page() is True


def test_paginator_has_next_page_when_more_pages_exist():
    paginator = Paginator()
    paginator._current_page = 1
    paginator._total_pages = 5
    assert paginator.has_next_page() is True


def test_paginator_has_next_page_when_on_last_page():
    paginator = Paginator()
    paginator._current_page = 5
    paginator._total_pages = 5
    assert paginator.has_next_page() is False


def test_paginator_set_total_pages():
    paginator = Paginator()
    paginator.set_total_pages(10)
    assert paginator.total_pages == 10


def test_paginator_page_size_setter_valid():
    paginator = Paginator()
    paginator.page_size = 25
    assert paginator.page_size == 25


def test_paginator_page_size_setter_invalid():
    paginator = Paginator()
    with pytest.raises(ValueError, match="Page size must be greater than 0"):
        paginator.page_size = 0


def test_paginator_page_size_setter_negative():
    paginator = Paginator()
    with pytest.raises(ValueError, match="Page size must be greater than 0"):
        paginator.page_size = -5


def test_paginator_sync_from_page():
    paginator = Paginator()
    page = SearchResultPage(
        current_page=2,
        page_size=15,
        total_pages=10,
        total_results=150
    )
    
    paginator.sync_from_page(page)
    
    assert paginator.current_page == 2
    assert paginator.page_size == 15
    assert paginator.total_pages == 10


def test_paginator_sync_from_page_with_none_values():
    paginator = Paginator()
    page = SearchResultPage()
    
    paginator.sync_from_page(page)
    
    assert paginator.current_page == 1  # default unchanged
    assert paginator.page_size is None
    assert paginator.total_pages is None


def test_paginator_next_page_payload():
    paginator = Paginator()
    paginator._current_page = 1
    paginator._page_size = 20
    paginator._total_pages = 5
    
    payload = paginator.next_page_payload()
    
    assert payload["ctl0$CONTENU_PAGE$resultSearch$numPageTop"] == "2"
    assert payload["ctl0$CONTENU_PAGE$resultSearch$listePageSizeTop"] == "20"
    assert payload["ctl0$CONTENU_PAGE$resultSearch$numPageBottom"] == "2"
    assert payload["ctl0$CONTENU_PAGE$resultSearch$listePageSizeBottom"] == "20"


def test_paginator_next_page_payload_increments_page():
    paginator = Paginator()
    paginator._current_page = 1
    paginator._page_size = 20
    paginator._total_pages = 5
    
    paginator.next_page_payload()
    assert paginator.current_page == 2


def test_paginator_next_page_payload_raises_when_no_next_page():
    paginator = Paginator()
    paginator._current_page = 5
    paginator._total_pages = 5
    
    with pytest.raises(PaginationError, match="No more pages available"):
        paginator.next_page_payload()


def test_paginator_reset():
    paginator = Paginator()
    paginator._current_page = 5
    paginator._page_size = 20
    paginator._total_pages = 10
    
    paginator.reset()
    
    assert paginator.current_page == 1
    assert paginator.page_size is None
    assert paginator.total_pages is None


@pytest.mark.parametrize("bad_size", [0, -5])
def test_paginator_reset_rejects_invalid_page_size(bad_size):
    paginator = Paginator()
    paginator._current_page = 5
    paginator._page_size = 20
    paginator._total_pages = 10

    with pytest.raises(ValueError, match="Page size must be greater than 0"):
        paginator.reset(page_size=bad_size)

    assert paginator.current_page == 1
    assert paginator.page_size == 20
    assert paginator.total_pages == 10


def test_paginator_reset_with_page_size():
    paginator = Paginator()
    paginator._current_page = 5
    paginator._page_size = 20
    paginator._total_pages = 10
    
    paginator.reset(page_size=15)
    
    assert paginator.current_page == 1
    assert paginator.page_size == 15
    assert paginator.total_pages is None
