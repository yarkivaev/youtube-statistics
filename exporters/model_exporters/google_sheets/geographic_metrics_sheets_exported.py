"""Google Sheets Exported wrapper for GeographicMetrics model."""

from models import GeographicMetrics
from typing import List
from ...base import Exported


class GeographicMetricsSheetsExported(Exported):
    """Google Sheets exporter for GeographicMetrics model."""
    
    def __init__(self, geo: GeographicMetrics):
        """Initialize with GeographicMetrics instance."""
        super().__init__(geo)
    
    def export(self) -> dict:
        """Export GeographicMetrics to dictionary for Google Sheets.
        
        Returns:
            Dictionary with geographic metrics formatted for sheets
        """
        result = {
            'Country': self.country_name,
            'Country Code': self.country_code,
            'Metric Type': self.metric_type.value if hasattr(self.metric_type, 'value') else str(self.metric_type)
        }
        
        # Add value based on metric type
        if hasattr(self, 'views'):
            result['Views'] = self.views
        if hasattr(self, 'subscribers_gained'):
            result['Subscribers'] = self.subscribers_gained
        if hasattr(self, 'watch_time_minutes'):
            result['Watch Time (hours)'] = round(self.watch_time_minutes / 60, 2)
        
        # Add percentage if available
        if hasattr(self, 'percentage'):
            result['Percentage'] = f"{self.percentage:.2f}%"
        
        return result
    
    @staticmethod
    def export_list(metrics_list: List[GeographicMetrics]) -> List[dict]:
        """Export list of GeographicMetrics for Google Sheets table.
        
        Args:
            metrics_list: List of GeographicMetrics instances
            
        Returns:
            List of dictionaries formatted for sheets
        """
        return [GeographicMetricsSheetsExported(metric).export() for metric in metrics_list]