"""Pure factory for creating DateRange instances."""

from datetime import date
from models import DateRange
from .base import Factory


class DateRangeFactory(Factory):
    """Factory for creating DateRange instances from provided data."""
    
    def create(self,
               start_date: date,
               end_date: date,
               **kwargs) -> DateRange:
        """Create DateRange instance from provided data.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            **kwargs: Additional arguments (ignored)
            
        Returns:
            DateRange instance
        """
        return DateRange(
            start_date=start_date,
            end_date=end_date
        )