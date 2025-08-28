"""Google Sheets Exported wrapper for SubscriptionMetrics model."""

from domain import SubscriptionMetrics
from ..base import Report


class SubscriptionMetricsSheetsReport(Report):
    """Google Sheets exporter for SubscriptionMetrics model."""
    
    def __init__(self, subscription: SubscriptionMetrics):
        """Initialize with SubscriptionMetrics instance."""
        super().__init__(subscription)
    
    def export(self) -> dict:
        """Export SubscriptionMetrics to dictionary for Google Sheets.
        
        Returns:
            Dictionary with subscription metrics formatted for sheets
        """
        # Handle period - check if it has export method
        if hasattr(self.period, 'export'):
            period_data = self.period.export()
            period_str = f"{period_data.get('start_date', '')} to {period_data.get('end_date', '')}"
        else:
            period_str = f"{self.period.start_date} to {self.period.end_date}"
        
        result = {
            'Period': period_str,
            'Subscribers Gained': self.subscribers_gained,
            'Subscribers Lost': self.subscribers_lost,
            'Net Change': self.net_change,
            'Growth Rate': f"{self.growth_rate:.2f}%"
        }
        
        # Add trend indicator
        if self.net_change > 0:
            result['Trend'] = '📈 Growing'
        elif self.net_change < 0:
            result['Trend'] = '📉 Declining'
        else:
            result['Trend'] = '➡️ Stable'
        
        return result