"""Google Sheets Exported wrapper for ViewsBreakdown model."""

from models import ViewsBreakdown
from ..base import Report


class ViewsBreakdownSheetsReport(Report):
    """Google Sheets exporter for ViewsBreakdown model."""
    
    def __init__(self, views: ViewsBreakdown):
        """Initialize with ViewsBreakdown instance."""
        super().__init__(views)
    
    def export(self) -> dict:
        """Export ViewsBreakdown to dictionary for Google Sheets.
        
        Returns:
            Dictionary with views breakdown formatted for sheets
        """
        return {
            'Total Views': self.total_views,
            'Video Views': self.video_views,
            'Shorts Views': self.shorts_views,
            'Live Views': self.live_views,
            'Video Percentage': f"{self.video_percentage:.1f}%",
            'Shorts Percentage': f"{self.shorts_percentage:.1f}%",
            'Live Percentage': f"{self.live_percentage:.1f}%",
            'Most Popular Format': self._get_most_popular_format()
        }
    
    def _get_most_popular_format(self) -> str:
        """Determine the most popular content format.
        
        Returns:
            String indicating the most popular format
        """
        formats = [
            ('Videos', self.video_views),
            ('Shorts', self.shorts_views),
            ('Live', self.live_views)
        ]
        
        # Sort by views and get the top one
        formats.sort(key=lambda x: x[1], reverse=True)
        
        if formats[0][1] > 0:
            return f"{formats[0][0]} ({formats[0][1]:,} views)"
        else:
            return "No views yet"