"""Repository abstractions for data persistence."""

from .base import AnalyticsRepository
from .file_repository import FileRepository

__all__ = ['AnalyticsRepository', 'FileRepository']