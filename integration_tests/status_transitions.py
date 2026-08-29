"""Test TenderRepository.update_status against a real Postgres database."""

from datetime import UTC, datetime

from sqlalchemy import delete, select

from core.models import Tender
from persistence import Database, Settings, TenderRecord, TenderRepository, TenderStatus

from .config import logger


def test_status_transitions():
    """Test status transitions written via TenderRepository.update_status.

    Covers a normal forward transition, a failure transition that sets
    FAILED plus a non-null last_status, and a subsequent successful
    transition that clears last_status back to null.

    Raises on any failure (connection errors, write failures, unexpected
    persisted state) instead of swallowing them - callers must not treat
    a caught exception here as a passing run.
    """
    logger.info("\n" + "=" * 60)
    logger.info("TEST: Status Transitions (persists to Postgres)")
    logger.info("=" * 60)

    tender_id = f"STATUS-TEST-{datetime.now(UTC).strftime('%Y%m%d%H%M%S%f')}"
    organization_acronym = "STATUS-TEST-ORG"

    database = None
    try:
        database = Database(Settings.from_env())
        repository = TenderRepository(database)

        repository.save(
            Tender(tender_id=tender_id, organization_acronym=organization_acronym)
        )

        def read_back() -> tuple[str, str | None]:
            with database.session() as session:
                stmt = select(TenderRecord.status, TenderRecord.last_status).where(
                    TenderRecord.tender_id == tender_id,
                    TenderRecord.organization_acronym == organization_acronym,
                )
                row = session.execute(stmt).one()
                return row.status, row.last_status

        # Normal forward transition: DISCOVERED -> DOWNLOADING, last_status stays null.
        repository.update_status(tender_id, organization_acronym, TenderStatus.DOWNLOADING)
        status, last_status = read_back()
        logger.info(f"After forward transition: status={status}, last_status={last_status}")
        if status != TenderStatus.DOWNLOADING.value or last_status is not None:
            raise AssertionError(
                f"Forward transition failed: expected status=DOWNLOADING, last_status=None, "
                f"got status={status}, last_status={last_status}"
            )

        # Failure transition: DOWNLOADING -> FAILED, last_status records DOWNLOADING.
        repository.update_status(
            tender_id,
            organization_acronym,
            TenderStatus.FAILED,
            last_status=TenderStatus.DOWNLOADING,
        )
        status, last_status = read_back()
        logger.info(f"After failure transition: status={status}, last_status={last_status}")
        if status != TenderStatus.FAILED.value or last_status != TenderStatus.DOWNLOADING.value:
            raise AssertionError(
                f"Failure transition failed: expected status=FAILED, last_status=DOWNLOADING, "
                f"got status={status}, last_status={last_status}"
            )

        # Retry succeeds: FAILED -> DOWNLOADING again, last_status clears back to null.
        repository.update_status(tender_id, organization_acronym, TenderStatus.DOWNLOADING)
        status, last_status = read_back()
        logger.info(f"After retry transition: status={status}, last_status={last_status}")
        if status != TenderStatus.DOWNLOADING.value or last_status is not None:
            raise AssertionError(
                f"Retry transition failed: expected status=DOWNLOADING, last_status=None, "
                f"got status={status}, last_status={last_status}"
            )

        logger.info("Status transitions verified successfully")
    finally:
        if database is not None:
            with database.session() as session:
                session.execute(
                    delete(TenderRecord).where(
                        TenderRecord.tender_id == tender_id,
                        TenderRecord.organization_acronym == organization_acronym,
                    )
                )
            database.close()
