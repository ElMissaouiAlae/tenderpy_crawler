"""Analyze the JSON result files produced by the other test_* scripts."""

import json
from pathlib import Path

from .config import logger


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
