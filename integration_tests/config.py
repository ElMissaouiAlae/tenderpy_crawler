"""Shared logging setup and configuration for the integration test scripts."""

import logging

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
