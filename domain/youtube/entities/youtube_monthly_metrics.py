"""YouTube monthly aggregated metrics model."""

from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class YouTubeMonthlyMetrics:
    """Represents YouTube aggregated metrics for a single month."""
    
    month_key: str  # Month identifier in YYYY-MM format
    views: int = 0
    watch_time_minutes: int = 0
    subscribers_gained: int = 0
    subscribers_lost: int = 0
    video_count: int = 0  # Number of videos uploaded in the month
    advertiser_count: int = 0  # Would need manual input
    integrations: str = ''  # Would need manual input
    days_with_data: int = 0
    geographic_views_top: List = field(default_factory=list)  # Top countries by views
    geographic_subscribers_top: List = field(default_factory=list)  # Top countries by subscribers
    
    
    @property
    def net_subscribers(self) -> int:
        """Calculate net subscribers for the month."""
        return self.subscribers_gained - self.subscribers_lost
    
    @property
    def average_daily_views(self) -> float:
        """Calculate average daily views for the month."""
        if self.days_with_data == 0:
            return 0.0
        return round(self.views / self.days_with_data, 2)
    
    def export(self) -> Dict[str, Any]:
        """Export monthly metrics as dictionary.
        
        Returns:
            Dictionary with aggregated monthly metrics
        """
        result = {
            'month_key': self.month_key,
            'views': self.views,
            'watch_time_minutes': self.watch_time_minutes,
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost,
            'video_count': self.video_count,
            'advertiser_count': self.advertiser_count,
            'integrations': self.integrations,
            'days_with_data': self.days_with_data,
            'net_subscribers': self.net_subscribers,
            'average_daily_views': self.average_daily_views
        }
        
        # Add geographic data if available
        if self.geographic_views_top:
            result['geographic_views_top'] = [
                {'country': g.country_code, 'views': g.views} 
                for g in self.geographic_views_top
            ]
        
        if self.geographic_subscribers_top:
            result['geographic_subscribers_top'] = [
                {'country': g.country_code, 'subscribers': g.subscribers_gained}
                for g in self.geographic_subscribers_top
            ]
        
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.export()