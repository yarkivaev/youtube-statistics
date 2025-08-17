"""Factory for creating GeographicMetrics with optional export decorator."""

from typing import Optional, Type
from models import GeographicMetrics
from ..base import Exported


class GeographicMetricsFactory:
    """Factory for creating GeographicMetrics with optional export decorator."""
    
    def __init__(self, exported_class: Optional[Type[Exported]] = None):
        """Initialize with optional decorator class."""
        self.exported_class = exported_class
    
    def create(self, country_code: str,
               views: Optional[int] = None,
               watch_time_minutes: Optional[int] = None,
               subscribers_gained: Optional[int] = None,
               **kwargs):
        """Create GeographicMetrics instance with configured decorator.
        
        Returns:
            GeographicMetrics or GeographicMetricsExported instance
        """
        # Ignore country_name if passed - it's a computed property
        geo = GeographicMetrics(
            country_code=country_code,
            views=views,
            watch_time_minutes=watch_time_minutes,
            subscribers_gained=subscribers_gained
        )
        
        if self.exported_class:
            return self.exported_class(geo)
        return geo