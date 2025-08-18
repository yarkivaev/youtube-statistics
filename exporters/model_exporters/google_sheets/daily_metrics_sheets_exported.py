"""Google Sheets Exported wrapper for DailyMetrics model."""

from models import DailyMetrics
from typing import List
from ...base import Exported


class DailyMetricsSheetsExported(Exported):
    """Google Sheets exporter for DailyMetrics model."""
    
    def __init__(self, daily: DailyMetrics):
        """Initialize with DailyMetrics instance."""
        super().__init__(daily)
    
    def export(self) -> dict:
        """Export DailyMetrics to dictionary for Google Sheets.
        
        Returns:
            Dictionary with daily metrics formatted for sheets
        """
        result = {
            'Date': self.date.isoformat(),
            'Views': self.views,
            'Watch Time (hours)': round(self.watch_time_minutes / 60, 2),
            'Avg View Duration (min)': round(self.average_view_duration_seconds / 60, 2),
            'Subscribers Gained': self.subscribers_gained,
            'Subscribers Lost': self.subscribers_lost,
            'Net Subscribers': self.net_subscribers,
            'Has Activity': 'Yes' if self.has_activity else 'No'
        }
        
        # Add content type if available
        if self.content_type:
            try:
                result['Content Type'] = self.content_type.value
            except:
                result['Content Type'] = str(self.content_type)
        
        return result
    
    @staticmethod
    def export_list(metrics_list: List[DailyMetrics]) -> List[dict]:
        """Export list of DailyMetrics for Google Sheets table.
        
        Args:
            metrics_list: List of DailyMetrics instances
            
        Returns:
            List of dictionaries formatted for sheets
        """
        return [DailyMetricsSheetsExported(metric).export() for metric in metrics_list]