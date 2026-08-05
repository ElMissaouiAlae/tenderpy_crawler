"""
Integration test script for testing the crawler against the real website.
This script tests different search parameters and logs returned tender objects.
"""

import json
import logging
from datetime import date, datetime, timedelta
from pathlib import Path

from core.http import HttpClient
from core.session import SearchSession
from discovery.orchestrator import DiscoveryOrchestrator
from discovery.parser import SearchCriteria

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integration_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration - UPDATE THIS WITH THE REAL WEBSITE BASE URL
BASE_URL = "https://www.marchespublics.gov.ma"  # Example URL - update with actual URL


def tender_to_dict(tender):
    """Convert Tender object to dictionary for JSON serialization."""
    return {
        'tender_id': tender.tender_id,
        'organization_acronym': tender.organization_acronym,
        'procurement_type': tender.procurement_type,
        'category': tender.category,
        'publication_date': tender.publication_date,
        'reference_number': tender.reference_number,
        'tender_object': tender.tender_object,
        'public_buyer': tender.public_buyer,
        'location': tender.location,
        'tender_end_date': tender.tender_end_date,
    }


def log_tenders(tenders, test_name):
    """Log tender details to both console and file."""
    logger.info(f"=== {test_name} - Found {len(tenders)} tenders ===")
    
    # Create output directory if it doesn't exist
    output_dir = Path('test_results')
    output_dir.mkdir(exist_ok=True)
    
    # Save to JSON file
    output_file = output_dir / f'{test_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([tender_to_dict(t) for t in tenders], f, indent=2, ensure_ascii=False)
    
    logger.info(f"Results saved to {output_file}")
    
    # Log summary
    for i, tender in enumerate(tenders[:5], 1):  # Log first 5 tenders
        logger.info(f"Tender {i}:")
        logger.info(f"  ID: {tender.tender_id}")
        logger.info(f"  Organization: {tender.organization_acronym}")
        logger.info(f"  Object: {tender.tender_object}")
        logger.info(f"  Buyer: {tender.public_buyer}")
        logger.info(f"  Publication Date: {tender.publication_date}")
    
    if len(tenders) > 5:
        logger.info(f"... and {len(tenders) - 5} more tenders")


def log_http_error(error, context=""):
    """Log detailed HTTP error information including response details."""
    logger.error(f"HTTP Error in {context}")
    logger.error(f"Error type: {type(error).__name__}")
    logger.error(f"Error message: {str(error)}")
    
    # Try to extract response details if available
    if hasattr(error, 'args') and error.args:
        for arg in error.args:
            if isinstance(arg, str):
                logger.error(f"Error details: {arg}")
    
    # Try to access response object if it's a requests-related error
    if hasattr(error, '__cause__') and error.__cause__:
        cause = error.__cause__
        logger.error(f"Cause: {type(cause).__name__} - {str(cause)}")
        
        # If it's a requests.Response, log headers and body
        if hasattr(cause, 'response') and cause.response is not None:
            response = cause.response
            logger.error(f"HTTP Status Code: {response.status_code}")
            logger.error(f"Response Headers:")
            for key, value in response.headers.items():
                logger.error(f"  {key}: {value}")
            
            # Log response body (truncated if too long)
            body = response.text
            if body:
                logger.error(f"Response Body (first 1000 chars):")
                logger.error(body[:1000])
                if len(body) > 1000:
                    logger.error(f"... (body truncated, total length: {len(body)} chars)")
    
    # Log the full traceback
    logger.error("Full traceback:", exc_info=True)


def test_keyword_search():
    """Test search with keyword parameter."""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Keyword Search")
    logger.info("="*60)
    
    try:
        with HttpClient(base_url=BASE_URL, timeout=30) as http_client:
            session = SearchSession(http_client)
            
            # Initialize session with the search page
            init_url = f"{BASE_URL}/index.php?page=entreprise.EntrepriseAdvancedSearch"
            logger.info(f"Initializing session with: {init_url}")
            session.initialize(init_url)
            logger.info(f"Session initialized successfully. PRADO state: {session.state.prado_page_state[:50] if session.state.prado_page_state else 'None'}...")
            
            orchestrator = DiscoveryOrchestrator(session)
            
            # Search with keyword
            criteria = SearchCriteria(keyword="construction")
            logger.info(f"Searching with criteria: keyword='construction'")
            
            tenders = orchestrator.discover(criteria)
            log_tenders(tenders, "keyword_search")
            
            return tenders
    except Exception as e:
        log_http_error(e, "keyword_search")
        return []


def test_date_range_search():
    """Test search with date range parameters."""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Date Range Search")
    logger.info("="*60)
    
    try:
        with HttpClient(base_url=BASE_URL, timeout=30) as http_client:
            session = SearchSession(http_client)
            
            # Initialize session
            init_url = f"{BASE_URL}/index.php?page=entreprise.EntrepriseAdvancedSearch"
            logger.info(f"Initializing session with: {init_url}")
            session.initialize(init_url)
            logger.info(f"Session initialized successfully. PRADO state: {session.state.prado_page_state[:50] if session.state.prado_page_state else 'None'}...")
            
            orchestrator = DiscoveryOrchestrator(session)
            
            # Search with date range (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            criteria = SearchCriteria(
                publication_date_from=start_date,
                publication_date_to=end_date
            )
            logger.info(f"Searching with date range: {start_date} to {end_date}")
            
            tenders = orchestrator.discover(criteria)
            log_tenders(tenders, "date_range_search")
            
            return tenders
    except Exception as e:
        log_http_error(e, "date_range_search")
        return []


def test_buyer_search():
    """Test search with buyer parameter."""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Buyer Search")
    logger.info("="*60)
    
    try:
        with HttpClient(base_url=BASE_URL, timeout=30) as http_client:
            session = SearchSession(http_client)
            
            # Initialize session
            init_url = f"{BASE_URL}/index.php?page=entreprise.EntrepriseAdvancedSearch"
            logger.info(f"Initializing session with: {init_url}")
            session.initialize(init_url)
            logger.info(f"Session initialized successfully. PRADO state: {session.state.prado_page_state[:50] if session.state.prado_page_state else 'None'}...")
            
            orchestrator = DiscoveryOrchestrator(session)
            
            # Search with buyer
            criteria = SearchCriteria(buyer="Commune")
            logger.info(f"Searching with criteria: buyer='Commune'")
            
            tenders = orchestrator.discover(criteria)
            log_tenders(tenders, "buyer_search")
            
            return tenders
    except Exception as e:
        log_http_error(e, "buyer_search")
        return []


def test_combined_search():
    """Test search with multiple parameters combined."""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Combined Search")
    logger.info("="*60)
    
    try:
        with HttpClient(base_url=BASE_URL, timeout=30) as http_client:
            session = SearchSession(http_client)
            
            # Initialize session
            init_url = f"{BASE_URL}/index.php?page=entreprise.EntrepriseAdvancedSearch"
            logger.info(f"Initializing session with: {init_url}")
            session.initialize(init_url)
            logger.info(f"Session initialized successfully. PRADO state: {session.state.prado_page_state[:50] if session.state.prado_page_state else 'None'}...")
            
            orchestrator = DiscoveryOrchestrator(session)
            
            # Search with multiple parameters
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
            
            criteria = SearchCriteria(
                keyword="travaux",
                publication_date_from=start_date,
                publication_date_to=end_date
            )
            logger.info(f"Searching with combined criteria: keyword='travaux', date range: {start_date} to {end_date}")
            
            tenders = orchestrator.discover(criteria)
            log_tenders(tenders, "combined_search")
            
            return tenders
    except Exception as e:
        log_http_error(e, "combined_search")
        return []


def test_pagination():
    """Test pagination functionality."""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: Pagination")
    logger.info("="*60)
    
    try:
        with HttpClient(base_url=BASE_URL, timeout=30) as http_client:
            session = SearchSession(http_client)
            
            # Initialize session
            init_url = f"{BASE_URL}/index.php?page=entreprise.EntrepriseAdvancedSearch"
            logger.info(f"Initializing session with: {init_url}")
            session.initialize(init_url)
            logger.info(f"Session initialized successfully. PRADO state: {session.state.prado_page_state[:50] if session.state.prado_page_state else 'None'}...")
            
            orchestrator = DiscoveryOrchestrator(session)
            
            # Search with a broad criteria to get multiple pages
            criteria = SearchCriteria(keyword="services")
            logger.info(f"Testing pagination with keyword='services'")
            
            # Use discover_paginated to get pages separately
            pages = orchestrator.discover_paginated(criteria)
            
            logger.info(f"Found {len(pages)} pages")
            
            total_tenders = 0
            for i, page_tenders in enumerate(pages, 1):
                logger.info(f"Page {i}: {len(page_tenders)} tenders")
                total_tenders += len(page_tenders)
            
            logger.info(f"Total tenders across all pages: {total_tenders}")
            
            # Save pagination results
            output_dir = Path('test_results')
            output_dir.mkdir(exist_ok=True)
            
            pagination_file = output_dir / f'pagination_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(pagination_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_pages': len(pages),
                    'total_tenders': total_tenders,
                    'tenders_per_page': [len(page) for page in pages],
                    'all_tenders': [tender_to_dict(t) for page in pages for t in page]
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Pagination results saved to {pagination_file}")
            
            return pages
    except Exception as e:
        log_http_error(e, "pagination")
        return []


def analyze_results():
    """Analyze test results and identify potential issues."""
    logger.info("\n" + "="*60)
    logger.info("ANALYSIS OF RESULTS")
    logger.info("="*60)
    
    output_dir = Path('test_results')
    if not output_dir.exists():
        logger.warning("No test results found to analyze")
        return
    
    json_files = list(output_dir.glob('*.json'))
    logger.info(f"Found {len(json_files)} test result files")
    
    # Check for common issues
    issues = []
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if data is a list of tenders or pagination result
            if isinstance(data, list):
                # List of tenders
                if len(data) == 0:
                    issues.append(f"{json_file.name}: No tenders found")
                
                # Check for missing critical fields
                for tender in data:
                    if not tender.get('tender_id'):
                        issues.append(f"{json_file.name}: Tender missing ID")
                    if not tender.get('tender_object'):
                        issues.append(f"{json_file.name}: Tender missing object")
            
            elif isinstance(data, dict):
                # Pagination result
                if data.get('total_tenders', 0) == 0:
                    issues.append(f"{json_file.name}: No tenders found in pagination")
        
        except Exception as e:
            issues.append(f"{json_file.name}: Error reading file - {e}")
    
    if issues:
        logger.warning("Potential issues identified:")
        for issue in issues:
            logger.warning(f"  - {issue}")
    else:
        logger.info("No obvious issues identified in test results")


def main():
    """Run all integration tests."""
    logger.info("Starting integration tests for crawler")
    logger.info(f"Base URL: {BASE_URL}")
    logger.info("Make sure to update BASE_URL with the correct website URL")
    
    # Run tests
    test_keyword_search()
    test_date_range_search()
    test_buyer_search()
    test_combined_search()
    test_pagination()
    
    # Analyze results
    analyze_results()
    
    logger.info("\n" + "="*60)
    logger.info("Integration tests completed")
    logger.info("Check integration_test.log for detailed logs")
    logger.info("Check test_results/ directory for JSON output files")
    logger.info("="*60)


if __name__ == "__main__":
    main()
