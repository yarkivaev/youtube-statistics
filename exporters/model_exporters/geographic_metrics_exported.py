"""Exported wrapper for GeographicMetrics model."""

from models import GeographicMetrics
from ..base import Exported


class GeographicMetricsExported(Exported):
    """Exported wrapper for GeographicMetrics model."""
    
    def __init__(self, geo: GeographicMetrics):
        """Initialize with GeographicMetrics instance."""
        super().__init__(geo)
    
    def export(self) -> dict:
        """Export GeographicMetrics to dictionary."""
        result = {
            'country_code': self.country_code,
            'country_name': self.country_name
        }
        
        # Add optional fields if they exist
        if self.views is not None:
            result['views'] = self.views
        if self.watch_time_minutes is not None:
            result['watch_time_minutes'] = self.watch_time_minutes
        if self.subscribers_gained is not None:
            result['subscribers_gained'] = self.subscribers_gained
        
        return result