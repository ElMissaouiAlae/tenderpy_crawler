"""Custom exceptions for the persistence layer."""


class PersistenceError(Exception):
    """Base exception for persistence-related failures."""


class DatabaseConnectionError(PersistenceError):
    """Raised when database connection fails."""


class RepositoryError(PersistenceError):
    """Raised when repository operations fail."""


class DuplicateTenderError(PersistenceError):
    """Raised when attempting to insert a duplicate tender record."""


class RecordNotFoundError(PersistenceError):
    """Raised when a requested record is not found."""


class TransactionError(PersistenceError):
    """Raised when a database transaction fails."""
