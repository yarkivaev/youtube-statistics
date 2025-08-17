"""Factory for creating SubscriptionMetrics with optional export decorator."""

from typing import Optional, Type
from datetime import date
from models import SubscriptionMetrics
from ..base import Exported
from .date_range_factory import DateRangeFactory


class SubscriptionMetricsFactory:
    """Factory for creating SubscriptionMetrics with optional export decorator."""
    
    def __init__(self, date_range_factory: DateRangeFactory,
                 exported_class: Optional[Type[Exported]] = None):
        """Initialize with dependencies.
        
        Args:
            date_range_factory: Factory for creating DateRange instances
            exported_class: Decorator class to apply
        """
        self.date_range_factory = date_range_factory
        self.exported_class = exported_class
    
    def create(self, subscribers_gained: int, subscribers_lost: int,
               start_date: date, end_date: date):
        """Create SubscriptionMetrics instance with configured decorator.
        
        Returns:
            SubscriptionMetrics or SubscriptionMetricsExported instance
        """
        period = self.date_range_factory.create(start_date, end_date)
        
        metrics = SubscriptionMetrics(
            subscribers_gained=subscribers_gained,
            subscribers_lost=subscribers_lost,
            period=period
        )
        
        if self.exported_class:
            return self.exported_class(metrics)
        return metrics