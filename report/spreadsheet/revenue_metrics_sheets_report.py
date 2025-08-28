"""Google Sheets Exported wrapper for RevenueMetrics model."""

from domain import RevenueMetrics
from ..base import Report


class RevenueMetricsSheetsReport(Report):
    """Google Sheets exporter for RevenueMetrics model."""
    
    def __init__(self, revenue: RevenueMetrics):
        """Initialize with RevenueMetrics instance."""
        super().__init__(revenue)
    
    def export(self) -> dict:
        """Export RevenueMetrics to dictionary for Google Sheets.
        
        Returns:
            Dictionary with revenue metrics formatted for sheets
        """
        # Handle period - check if it has export method
        if hasattr(self.period, 'export'):
            period_data = self.period.export()
            period_str = f"{period_data.get('start_date', '')} to {period_data.get('end_date', '')}"
        else:
            period_str = f"{self.period.start_date} to {self.period.end_date}"
        
        return {
            'Period': period_str,
            'Total Revenue': f"${self.total_revenue:.2f}",
            'Ad Revenue': f"${self.ad_revenue:.2f}",
            'YouTube Premium Revenue': f"${self.youtube_premium_revenue:.2f}",
            'Transaction Revenue': f"${self.transaction_revenue:.2f}",
            'Fan Funding Revenue': f"${self.fan_funding_revenue:.2f}",
            'Total Views': self.total_views,
            'CPM (Cost per Mille)': f"${self.cpm:.2f}",
            'RPM (Revenue per Mille)': f"${self.rpm:.2f}",
            'Currency': self.currency
        }