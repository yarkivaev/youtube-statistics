"""Pure factory for creating RevenueMetrics instances."""

from datetime import date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from models import RevenueMetrics, DateRange
from models.revenue import DailyRevenue
from .base import Factory

if TYPE_CHECKING:
    from .date_range_factory import DateRangeFactory


class RevenueMetricsFactory(Factory):
    """Factory for creating RevenueMetrics instances from provided data."""
    
    def __init__(self, date_range_factory: Optional['DateRangeFactory'] = None):
        """Initialize with optional DateRange factory.
        
        Args:
            date_range_factory: Factory for creating DateRange instances
        """
        self.date_range_factory = date_range_factory
    
    def create(self,
               total_revenue: Decimal = Decimal('0'),
               ad_revenue: Optional[Decimal] = None,
               red_partner_revenue: Optional[Decimal] = None,
               start_date: Optional[date] = None,
               end_date: Optional[date] = None,
               daily_revenue: Optional[List[DailyRevenue]] = None,
               is_monetized: bool = False,
               **kwargs) -> RevenueMetrics:
        """Create RevenueMetrics instance from provided data.
        
        Args:
            total_revenue: Total revenue amount
            ad_revenue: Revenue from ads
            red_partner_revenue: Revenue from YouTube Red/Premium
            start_date: Start date of the period
            end_date: End date of the period
            daily_revenue: List of daily revenue entries
            is_monetized: Whether channel is monetized
            **kwargs: Additional arguments (ignored)
            
        Returns:
            RevenueMetrics instance
        """
        # Create period using factory if available, else create directly
        period = None
        if start_date and end_date:
            if self.date_range_factory:
                period = self.date_range_factory.create(
                    start_date=start_date,
                    end_date=end_date
                )
            else:
                period = DateRange(start_date=start_date, end_date=end_date)
        
        return RevenueMetrics(
            total_revenue=total_revenue,
            ad_revenue=ad_revenue,
            red_partner_revenue=red_partner_revenue,
            period=period,
            daily_revenue=daily_revenue or [],
            is_monetized=is_monetized
        )