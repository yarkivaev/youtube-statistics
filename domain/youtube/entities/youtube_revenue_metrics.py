"""YouTube revenue-related domain entity."""

from dataclasses import dataclass
from decimal import Decimal
from typing import List
from datetime import date
from domain.common.entities.date_range import DateRange
from .youtube_daily_metrics import YouTubeDailyMetrics


@dataclass
class YouTubeRevenueMetrics:
    """YouTube revenue metrics for a period."""
    
    total_revenue: Decimal
    ad_revenue: Decimal
    red_partner_revenue: Decimal  # YouTube Premium revenue
    period: DateRange
    daily_revenue: List[YouTubeDailyMetrics]
    is_monetized: bool = False
    
    @property
    def average_daily_revenue(self) -> Decimal:
        """Calculate average daily revenue."""
        if not self.daily_revenue:
            return Decimal('0')
        return self.total_revenue / len(self.daily_revenue)
    
    @property
    def has_revenue(self) -> bool:
        """Check if there's any revenue."""
        return self.total_revenue > 0
    
    def get_best_day(self) -> YouTubeDailyMetrics:
        """Get the day with highest revenue."""
        if not self.daily_revenue:
            # Return a default empty day
            from datetime import date as dt
            return YouTubeDailyMetrics(
                date=dt.today(),
                views=0,
                watch_time_minutes=0,
                average_view_duration_seconds=0,
                subscribers_gained=0,
                subscribers_lost=0,
                estimated_revenue=Decimal('0')
            )
        return max(self.daily_revenue, key=lambda d: d.estimated_revenue)
    
    def get_revenue_days_count(self) -> int:
        """Count days with revenue > 0."""
        return sum(1 for d in self.daily_revenue if d.estimated_revenue > 0)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            'total_revenue': float(self.total_revenue),
            'period': self.period.to_dict(),
            'is_monetized': self.is_monetized,
            'average_daily_revenue': float(self.average_daily_revenue),
            'revenue_days_count': self.get_revenue_days_count()
        }
        
        result['ad_revenue'] = float(self.ad_revenue)
        result['red_partner_revenue'] = float(self.red_partner_revenue)
        
        result['daily_revenue'] = [d.to_dict() for d in self.daily_revenue]
        
        best_day = self.get_best_day()
        if self.daily_revenue:  # Only include best_day if we have data
            result['best_day'] = best_day.to_dict()
            
        return result
    
    @classmethod
    def create_unavailable(cls, period: DateRange) -> 'YouTubeRevenueMetrics':
        """Create a YouTubeRevenueMetrics instance for when data is unavailable."""
        return cls(
            total_revenue=Decimal('0'),
            ad_revenue=Decimal('0'),
            red_partner_revenue=Decimal('0'),
            period=period,
            daily_revenue=[],
            is_monetized=False
        )