"""Exported wrapper for DateRange model."""

from domain import DateRange
from ..base import Report


class DateRangeReport(Report):
    """Exported wrapper for DateRange model."""
    
    def __init__(self, date_range: DateRange):
        """Initialize with DateRange instance."""
        super().__init__(date_range)
    
    def export(self) -> dict:
        """Export DateRange to dictionary."""
        # Convert dates to strings
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }