"""Report wrapper for YouTubeMetrics model."""

from domain import YouTubeMetrics
from ..base import Report


class YoutubeMetricsReport(Report):
    """Report wrapper for YouTubeMetrics model.
    
    This exporter assumes components already have export() method if created via factories.
    """
    
    def __init__(self, report: YouTubeMetrics):
        """Initialize with YouTubeMetrics instance."""
        super().__init__(report)
    
    def export(self) -> dict:
        """Export YouTubeMetrics to dictionary.
        
        Assumes components have export() method if created through factories.
        """
        # Just call export() directly - trust duck typing
        channel_data = self.channel.export()
        period_data = self.period.export()
        
        result = {
            'channel': channel_data,
            'period': period_data,
            'generated_at': self.generated_at.isoformat()
        }
        
        # Export required fields - just call export() directly
        result['subscription_metrics'] = self.subscription_metrics.export()
        result['views_breakdown'] = self.views_breakdown.export()
        result['revenue_metrics'] = self.revenue_metrics.export()
        
        if self.geographic_views:
            result['geographic_views'] = []
            for geo in self.geographic_views:
                result['geographic_views'].append(geo.export())
        
        if self.geographic_subscribers:
            result['geographic_subscribers'] = []
            for geo in self.geographic_subscribers:
                result['geographic_subscribers'].append(geo.export())
        
        if self.daily_metrics:
            result['daily_metrics'] = []
            for daily in self.daily_metrics:
                result['daily_metrics'].append(daily.export())
            
            # Add computed fields - access attributes directly
            total_minutes = 0
            active_days = 0
            for daily in self.daily_metrics:
                total_minutes += daily.watch_time_minutes
                if daily.has_activity:
                    active_days += 1
            
            result['total_watch_time_hours'] = total_minutes / 60
            result['active_days_count'] = active_days
        
        return result