"""YouTube metrics aggregate entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from .channel import Channel
from .metrics import SubscriptionMetrics, ViewsBreakdown, DateRange
from .daily_metrics import DailyMetrics
from .geography import GeographicMetrics
from .revenue import RevenueMetrics


@dataclass
class YouTubeMetrics:
    """Aggregate root entity containing all YouTube metrics data."""
    
    channel: Channel
    period: DateRange
    generated_at: datetime
    subscription_metrics: SubscriptionMetrics
    views_breakdown: ViewsBreakdown
    revenue_metrics: RevenueMetrics
    geographic_views: List[GeographicMetrics] = field(default_factory=list)
    geographic_subscribers: List[GeographicMetrics] = field(default_factory=list)
    daily_metrics: List[DailyMetrics] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            'channel': self.channel.to_dict(),
            'period': self.period.to_dict(),
            'generated_at': self.generated_at.isoformat()
        }
        
        result['subscription_metrics'] = self.subscription_metrics.to_dict()
        result['views_breakdown'] = self.views_breakdown.to_dict()
        result['revenue_metrics'] = self.revenue_metrics.to_dict()
        
        if self.geographic_views:
            result['geographic_views'] = [g.to_dict() for g in self.geographic_views]
        
        if self.geographic_subscribers:
            result['geographic_subscribers'] = [g.to_dict() for g in self.geographic_subscribers]
        
        if self.daily_metrics:
            result['daily_metrics'] = [d.to_dict() for d in self.daily_metrics]
            # Calculate total watch time in hours
            total_minutes = sum(day.watch_time_minutes for day in self.daily_metrics)
            result['total_watch_time_hours'] = total_minutes / 60
            # Count active days
            result['active_days_count'] = sum(1 for day in self.daily_metrics if day.has_activity)
        
        return result
    
