"""Date range domain entity."""

from dataclasses import dataclass
from datetime import date


@dataclass
class DateRange:
    """Represents a date range."""
    start_date: date
    end_date: date
    
    def __str__(self) -> str:
        return f"{self.start_date.isoformat()} to {self.end_date.isoformat()}"
    
    def to_dict(self) -> dict:
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }