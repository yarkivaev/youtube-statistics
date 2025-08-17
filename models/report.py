"""Analytics report aggregate entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from .channel import Channel
from .metrics import SubscriptionMetrics, ViewsBreakdown, DailyMetrics, DateRange
from .geography import GeographicMetrics
from .revenue import RevenueMetrics


@dataclass
class AnalyticsReport:
    """Aggregate root entity containing all analytics data."""
    
    channel: Channel
    period: DateRange
    generated_at: datetime
    subscription_metrics: Optional[SubscriptionMetrics] = None
    views_breakdown: Optional[ViewsBreakdown] = None
    revenue_metrics: Optional[RevenueMetrics] = None
    geographic_views: List[GeographicMetrics] = field(default_factory=list)
    geographic_subscribers: List[GeographicMetrics] = field(default_factory=list)
    daily_metrics: List[DailyMetrics] = field(default_factory=list)
    
    @property
    def has_complete_data(self) -> bool:
        """Check if report has all essential data."""
        return (
            self.subscription_metrics is not None and
            self.views_breakdown is not None and
            len(self.daily_metrics) > 0
        )
    
    @property
    def has_revenue_data(self) -> bool:
        """Check if report has revenue data."""
        return (
            self.revenue_metrics is not None and 
            self.revenue_metrics.has_revenue
        )
    
    @property
    def has_geographic_data(self) -> bool:
        """Check if report has geographic data."""
        return len(self.geographic_views) > 0 or len(self.geographic_subscribers) > 0
    
    def get_top_countries_by_views(self, limit: int = 5) -> List[GeographicMetrics]:
        """Get top countries by views."""
        sorted_countries = sorted(
            self.geographic_views,
            key=lambda g: g.views or 0,
            reverse=True
        )
        return sorted_countries[:limit]
    
    def get_top_countries_by_subscribers(self, limit: int = 5) -> List[GeographicMetrics]:
        """Get top countries by new subscribers."""
        sorted_countries = sorted(
            self.geographic_subscribers,
            key=lambda g: g.subscribers_gained or 0,
            reverse=True
        )
        return sorted_countries[:limit]
    
    def get_active_days(self) -> List[DailyMetrics]:
        """Get days with activity."""
        return [day for day in self.daily_metrics if day.has_activity]
    
    def get_total_watch_time_hours(self) -> float:
        """Calculate total watch time in hours."""
        total_minutes = sum(day.watch_time_minutes for day in self.daily_metrics)
        return total_minutes / 60
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            'channel': self.channel.to_dict(),
            'period': self.period.to_dict(),
            'generated_at': self.generated_at.isoformat()
        }
        
        if self.subscription_metrics:
            result['subscription_metrics'] = self.subscription_metrics.to_dict()
        
        if self.views_breakdown:
            result['views_breakdown'] = self.views_breakdown.to_dict()
        
        if self.revenue_metrics:
            result['revenue_metrics'] = self.revenue_metrics.to_dict()
        
        if self.geographic_views:
            result['geographic_views'] = [g.to_dict() for g in self.geographic_views]
        
        if self.geographic_subscribers:
            result['geographic_subscribers'] = [g.to_dict() for g in self.geographic_subscribers]
        
        if self.daily_metrics:
            result['daily_metrics'] = [d.to_dict() for d in self.daily_metrics]
            result['total_watch_time_hours'] = self.get_total_watch_time_hours()
            result['active_days_count'] = len(self.get_active_days())
        
        return result
    
    @classmethod
    def create_empty(cls, channel: Channel, period: DateRange) -> 'AnalyticsReport':
        """Create an empty report."""
        return cls(
            channel=channel,
            period=period,
            generated_at=datetime.now()
        )