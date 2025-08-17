"""Exported wrapper for RevenueMetrics model."""

from models import RevenueMetrics
from ..base import Exported


class RevenueMetricsExported(Exported):
    """Exported wrapper for RevenueMetrics model."""
    
    def __init__(self, revenue: RevenueMetrics):
        """Initialize with RevenueMetrics instance."""
        super().__init__(revenue)
    
    def export(self) -> dict:
        """Export RevenueMetrics to dictionary."""
        result = {
            'total_revenue': float(self.total_revenue),
            'has_revenue': self.has_revenue,
            'is_monetized': self.is_monetized
        }
        
        # Add optional fields
        if self.ad_revenue is not None:
            result['ad_revenue'] = float(self.ad_revenue)
        if self.red_partner_revenue is not None:
            result['red_partner_revenue'] = float(self.red_partner_revenue)
        
        # Just call export() on period - trust it has the method
        if self.period:
            result['period'] = self.period.export()
        
        return result