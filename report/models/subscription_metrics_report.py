"""Exported wrapper for SubscriptionMetrics model."""

from models import SubscriptionMetrics
from ..base import Report


class SubscriptionMetricsReport(Report):
    """Exported wrapper for SubscriptionMetrics model."""
    
    def __init__(self, metrics: SubscriptionMetrics):
        """Initialize with SubscriptionMetrics instance."""
        super().__init__(metrics)
    
    def export(self) -> dict:
        """Export SubscriptionMetrics to dictionary.
        
        Uses DateRangeExported for the period field if needed.
        """
        result = {
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost,
            'net_change': self.net_change,
            'change_percentage': self.change_percentage
        }
        
        # Just call export() on period - trust it has the method
        if self.period:
            result['period'] = self.period.export()
        
        return result