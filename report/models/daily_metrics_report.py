"""Exported wrapper for DailyMetrics model."""

from models import DailyMetrics
from ..base import Report


class DailyMetricsReport(Report):
    """Exported wrapper for DailyMetrics model."""
    
    def __init__(self, daily: DailyMetrics):
        """Initialize with DailyMetrics instance."""
        super().__init__(daily)
    
    def export(self) -> dict:
        """Export DailyMetrics to dictionary."""
        result = {
            'date': self.date.isoformat(),
            'views': self.views,
            'watch_time_minutes': self.watch_time_minutes,
            'average_view_duration_seconds': self.average_view_duration_seconds,
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost
        }
        
        # Add optional fields - just try to access value attribute
        if self.content_type:
            try:
                result['content_type'] = self.content_type.value
            except:
                result['content_type'] = str(self.content_type)
        
        return result