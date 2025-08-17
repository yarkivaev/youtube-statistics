"""Pure factory for creating SubscriptionMetrics instances."""

from datetime import date
from typing import Optional, TYPE_CHECKING
from models import SubscriptionMetrics, DateRange
from .base import Factory

if TYPE_CHECKING:
    from .date_range_factory import DateRangeFactory


class SubscriptionMetricsFactory(Factory):
    """Factory for creating SubscriptionMetrics instances from provided data."""
    
    def __init__(self, date_range_factory: Optional['DateRangeFactory'] = None):
        """Initialize with optional DateRange factory.
        
        Args:
            date_range_factory: Factory for creating DateRange instances
        """
        self.date_range_factory = date_range_factory
    
    def create(self,
               subscribers_gained: int = 0,
               subscribers_lost: int = 0,
               start_date: Optional[date] = None,
               end_date: Optional[date] = None,
               **kwargs) -> SubscriptionMetrics:
        """Create SubscriptionMetrics instance from provided data.
        
        Args:
            subscribers_gained: Number of subscribers gained
            subscribers_lost: Number of subscribers lost
            start_date: Start date of the period
            end_date: End date of the period
            **kwargs: Additional arguments (ignored)
            
        Returns:
            SubscriptionMetrics instance
        """
        # Create period using factory if available, else create directly
        period = None
        if start_date and end_date:
            if self.date_range_factory:
                period = self.date_range_factory.create(
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                period = DateRange(start_date=start_date, end_date=end_date)
        
        return SubscriptionMetrics(
            subscribers_gained=subscribers_gained,
            subscribers_lost=subscribers_lost,
            period=period
        )