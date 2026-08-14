"""Configuration management for the persistence layer."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from .exceptions import DatabaseConnectionError


@dataclass
class Settings:
    """Configuration settings for database connections.

    Attributes:
        database_url: PostgreSQL connection string
        pool_size: Connection pool size
        max_overflow: Maximum overflow connections beyond pool_size
        pool_timeout: Timeout in seconds for getting a connection from pool
        pool_recycle: Recycle connections after this many seconds
    """

    database_url: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600

    @classmethod
    def from_env(cls) -> Settings:
        """Load settings from environment variables.

        Loads environment variables from .env file if present.
        Expects DB_DATABASE_URL to be set.

        Returns:
            Settings instance configured from environment.

        Raises:
            DatabaseConnectionError: if required environment variables are missing.
        """
        load_dotenv()

        database_url = os.getenv("DB_DATABASE_URL")
        if not database_url:
            raise DatabaseConnectionError(
                "DB_DATABASE_URL environment variable is required"
            )

        return cls(
            database_url=database_url,
            pool_size=int(os.getenv("DB_POOL_SIZE", str(cls.pool_size))),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", str(cls.max_overflow))),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", str(cls.pool_timeout))),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", str(cls.pool_recycle))),
        )
