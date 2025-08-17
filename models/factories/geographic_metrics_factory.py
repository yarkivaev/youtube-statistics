"""Pure factory for creating GeographicMetrics instances."""

from typing import Optional
from models import GeographicMetrics
from .base import Factory


class GeographicMetricsFactory(Factory):
    """Factory for creating GeographicMetrics instances from provided data."""
    
    def create(self,
               country_code: str,
               views: Optional[int] = None,
               watch_time_minutes: Optional[int] = None,
               subscribers_gained: Optional[int] = None,
               **kwargs) -> GeographicMetrics:
        """Create GeographicMetrics instance from provided data.
        
        Args:
            country_code: ISO country code
            views: Number of views
            watch_time_minutes: Watch time in minutes
            subscribers_gained: Subscribers gained
            **kwargs: Additional arguments (ignored)
            
        Returns:
            GeographicMetrics instance
        """
        return GeographicMetrics(
            country_code=country_code,
            views=views,
            watch_time_minutes=watch_time_minutes,
            subscribers_gained=subscribers_gained
        )