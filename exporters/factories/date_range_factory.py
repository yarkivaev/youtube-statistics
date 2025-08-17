"""Factory for creating DateRange instances with optional export decorator."""

from typing import Optional, Type
from datetime import date
from models import DateRange
from ..base import Exported


class DateRangeFactory:
    """Factory for creating DateRange instances with optional export decorator."""
    
    def __init__(self, exported_class: Optional[Type[Exported]] = None):
        """Initialize with optional decorator class."""
        self.exported_class = exported_class
    
    def create(self, start_date: date, end_date: date):
        """Create DateRange instance with configured decorator.
        
        Returns:
            DateRange or DateRangeExported instance
        """
        date_range = DateRange(start_date=start_date, end_date=end_date)
        
        if self.exported_class:
            return self.exported_class(date_range)
        return date_range