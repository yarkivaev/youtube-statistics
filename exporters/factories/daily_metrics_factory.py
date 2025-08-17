"""Factory for creating DailyMetrics with optional export decorator."""

from typing import Optional, Type
from datetime import date
from models import DailyMetrics
from models.metrics import ContentType
from ..base import Exported


class DailyMetricsFactory:
    """Factory for creating DailyMetrics with optional export decorator."""
    
    def __init__(self, exported_class: Optional[Type[Exported]] = None):
        """Initialize with optional decorator class."""
        self.exported_class = exported_class
    
    def create(self, date: date, views: int, watch_time_minutes: int,
               average_view_duration_seconds: int,
               subscribers_gained: int, subscribers_lost: int,
               content_type: Optional[ContentType] = None):
        """Create DailyMetrics instance with configured decorator.
        
        Returns:
            DailyMetrics or DailyMetricsExported instance
        """
        daily = DailyMetrics(
            date=date,
            views=views,
            watch_time_minutes=watch_time_minutes,
            average_view_duration_seconds=average_view_duration_seconds,
            subscribers_gained=subscribers_gained,
            subscribers_lost=subscribers_lost,
            content_type=content_type
        )
        
        if self.exported_class:
            return self.exported_class(daily)
        return daily