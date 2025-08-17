"""Factory for creating RevenueMetrics with optional export decorator."""

from typing import Optional, Type, List
from datetime import date
from decimal import Decimal
from models import RevenueMetrics
from models.revenue import DailyRevenue
from ..base import Exported
from .date_range_factory import DateRangeFactory


class RevenueMetricsFactory:
    """Factory for creating RevenueMetrics with optional export decorator."""
    
    def __init__(self, date_range_factory: DateRangeFactory,
                 exported_class: Optional[Type[Exported]] = None):
        """Initialize with dependencies.
        
        Args:
            date_range_factory: Factory for creating DateRange instances
            exported_class: Decorator class to apply
        """
        self.date_range_factory = date_range_factory
        self.exported_class = exported_class
    
    def create(self, total_revenue: Decimal,
               ad_revenue: Optional[Decimal],
               red_partner_revenue: Optional[Decimal],
               start_date: date, end_date: date,
               daily_revenue: List[DailyRevenue],
               is_monetized: bool = False):
        """Create RevenueMetrics instance with configured decorator.
        
        Returns:
            RevenueMetrics or RevenueMetricsExported instance
        """
        period = self.date_range_factory.create(start_date, end_date)
        
        revenue = RevenueMetrics(
            total_revenue=total_revenue,
            ad_revenue=ad_revenue,
            red_partner_revenue=red_partner_revenue,
            period=period,
            daily_revenue=daily_revenue,
            is_monetized=is_monetized
        )
        
        if self.exported_class:
            return self.exported_class(revenue)
        return revenue