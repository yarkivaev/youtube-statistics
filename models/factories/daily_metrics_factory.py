"""Pure factory for creating DailyMetrics instances."""

from datetime import date
from typing import List
from models import DailyMetrics
from .base import Factory


class DailyMetricsFactory(Factory):
    """Factory for creating DailyMetrics instances from provided data."""
    
    def create(self,
               date_val: date,
               views: int = 0,
               watch_time_minutes: int = 0,
               average_view_duration_seconds: int = 0,
               subscribers_gained: int = 0,
               subscribers_lost: int = 0,
               **kwargs) -> DailyMetrics:
        """Create DailyMetrics instance from provided data.
        
        Args:
            date_val: Date for the metrics
            views: Number of views
            watch_time_minutes: Watch time in minutes
            average_view_duration_seconds: Average view duration
            subscribers_gained: Subscribers gained
            subscribers_lost: Subscribers lost
            **kwargs: Additional arguments (ignored)
            
        Returns:
            DailyMetrics instance
        """
        return DailyMetrics(
            date=date_val,
            views=views,
            watch_time_minutes=watch_time_minutes,
            average_view_duration_seconds=average_view_duration_seconds,
            subscribers_gained=subscribers_gained,
            subscribers_lost=subscribers_lost
        )