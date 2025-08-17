"""Revenue-related domain entity."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List
from datetime import date
from .metrics import DateRange


@dataclass
class DailyRevenue:
    """Revenue for a single day."""
    
    date: date
    estimated_revenue: Decimal
    ad_revenue: Optional[Decimal] = None
    red_partner_revenue: Optional[Decimal] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            'date': self.date.isoformat(),
            'estimated_revenue': float(self.estimated_revenue)
        }
        if self.ad_revenue is not None:
            result['ad_revenue'] = float(self.ad_revenue)
        if self.red_partner_revenue is not None:
            result['red_partner_revenue'] = float(self.red_partner_revenue)
        return result


@dataclass
class RevenueMetrics:
    """Revenue metrics for a period."""
    
    total_revenue: Decimal
    ad_revenue: Optional[Decimal]
    red_partner_revenue: Optional[Decimal]
    period: DateRange
    daily_revenue: List[DailyRevenue]
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
    
    def get_best_day(self) -> Optional[DailyRevenue]:
        """Get the day with highest revenue."""
        if not self.daily_revenue:
            return None
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
        
        if self.ad_revenue is not None:
            result['ad_revenue'] = float(self.ad_revenue)
        if self.red_partner_revenue is not None:
            result['red_partner_revenue'] = float(self.red_partner_revenue)
        
        result['daily_revenue'] = [d.to_dict() for d in self.daily_revenue]
        
        best_day = self.get_best_day()
        if best_day:
            result['best_day'] = best_day.to_dict()
            
        return result
    
    @classmethod
    def create_unavailable(cls, period: DateRange) -> 'RevenueMetrics':
        """Create a RevenueMetrics instance for when data is unavailable."""
        return cls(
            total_revenue=Decimal('0'),
            ad_revenue=None,
            red_partner_revenue=None,
            period=period,
            daily_revenue=[],
            is_monetized=False
        )