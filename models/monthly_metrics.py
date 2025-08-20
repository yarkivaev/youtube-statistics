"""Monthly aggregated metrics model."""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class MonthlyMetrics:
    """Represents aggregated metrics for a single month."""
    
    month_key: str  # Month identifier in YYYY-MM format
    views: int = 0
    watch_time_minutes: int = 0
    subscribers_gained: int = 0
    subscribers_lost: int = 0
    video_count: int = 0  # Would need to be tracked separately
    advertiser_count: int = 0  # Would need manual input
    integrations: str = ''  # Would need manual input
    days_with_data: int = 0
    
    
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
        return {
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return self.export()