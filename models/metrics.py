"""Metrics-related domain entities."""

from dataclasses import dataclass
from .date_range import DateRange


@dataclass
class SubscriptionMetrics:
    """Subscription-related metrics for a period."""
    
    subscribers_gained: int
    subscribers_lost: int
    period: DateRange
    
    @property
    def net_change(self) -> int:
        """Calculate net change in subscribers."""
        return self.subscribers_gained - self.subscribers_lost
    
    @property
    def change_percentage(self) -> float:
        """Calculate percentage change."""
        if self.subscribers_gained == 0:
            return 0.0
        return round((self.net_change / self.subscribers_gained) * 100, 2)
    
    @property
    def has_growth(self) -> bool:
        """Check if there's positive growth."""
        return self.net_change > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost,
            'net_change': self.net_change,
            'change_percentage': self.change_percentage,
            'period': self.period.to_dict()
        }


@dataclass
class ViewsBreakdown:
    """Breakdown of views by content type."""
    
    total_views: int
    video_views: int
    shorts_views: int
    live_stream_views: int = 0
    
    @property
    def video_percentage(self) -> float:
        """Calculate percentage of video views."""
        if self.total_views == 0:
            return 0.0
        return round((self.video_views / self.total_views) * 100, 2)
    
    @property
    def shorts_percentage(self) -> float:
        """Calculate percentage of shorts views."""
        if self.total_views == 0:
            return 0.0
        return round((self.shorts_views / self.total_views) * 100, 2)
    
    @property
    def live_percentage(self) -> float:
        """Calculate percentage of live stream views."""
        if self.total_views == 0:
            return 0.0
        return round((self.live_stream_views / self.total_views) * 100, 2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'total_views': self.total_views,
            'video_views': self.video_views,
            'shorts_views': self.shorts_views,
            'live_stream_views': self.live_stream_views,
            'video_percentage': self.video_percentage,
            'shorts_percentage': self.shorts_percentage,
            'live_percentage': self.live_percentage
        }


