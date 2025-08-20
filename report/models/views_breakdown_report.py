"""Exported wrapper for ViewsBreakdown model."""

from models import ViewsBreakdown
from ..base import Report


class ViewsBreakdownReport(Report):
    """Exported wrapper for ViewsBreakdown model."""
    
    def __init__(self, breakdown: ViewsBreakdown):
        """Initialize with ViewsBreakdown instance."""
        super().__init__(breakdown)
    
    def export(self) -> dict:
        """Export ViewsBreakdown to dictionary."""
        return {
            'total_views': self.total_views,
            'video_views': self.video_views,
            'shorts_views': self.shorts_views,
            'video_percentage': self.video_percentage,
            'shorts_percentage': self.shorts_percentage
        }