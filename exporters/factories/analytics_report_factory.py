"""Factory for creating AnalyticsReport with all dependencies."""

from typing import Optional, Type, List, Dict, Any
from datetime import datetime
from models import AnalyticsReport
from ..base import Exported
from .channel_factory import ChannelFactory
from .date_range_factory import DateRangeFactory
from .subscription_metrics_factory import SubscriptionMetricsFactory
from .views_breakdown_factory import ViewsBreakdownFactory
from .geographic_metrics_factory import GeographicMetricsFactory
from .daily_metrics_factory import DailyMetricsFactory
from .revenue_metrics_factory import RevenueMetricsFactory


class AnalyticsReportFactory:
    """Factory for creating AnalyticsReport with all dependencies."""
    
    def __init__(self,
                 channel_factory: ChannelFactory,
                 date_range_factory: DateRangeFactory,
                 subscription_factory: Optional[SubscriptionMetricsFactory] = None,
                 views_breakdown_factory: Optional[ViewsBreakdownFactory] = None,
                 geographic_factory: Optional[GeographicMetricsFactory] = None,
                 daily_metrics_factory: Optional[DailyMetricsFactory] = None,
                 revenue_factory: Optional[RevenueMetricsFactory] = None,
                 exported_class: Optional[Type[Exported]] = None):
        """Initialize with all factory dependencies.
        
        Args:
            channel_factory: Factory for creating Channel instances
            date_range_factory: Factory for creating DateRange instances
            subscription_factory: Factory for creating SubscriptionMetrics
            views_breakdown_factory: Factory for creating ViewsBreakdown
            geographic_factory: Factory for creating GeographicMetrics
            daily_metrics_factory: Factory for creating DailyMetrics
            revenue_factory: Factory for creating RevenueMetrics
            exported_class: Decorator class to apply to the report
        """
        self.channel_factory = channel_factory
        self.date_range_factory = date_range_factory
        self.subscription_factory = subscription_factory
        self.views_breakdown_factory = views_breakdown_factory
        self.geographic_factory = geographic_factory
        self.daily_metrics_factory = daily_metrics_factory
        self.revenue_factory = revenue_factory
        self.exported_class = exported_class
    
    def create(self, channel_data: Dict[str, Any],
               period_data: Dict[str, Any],
               generated_at: datetime,
               subscription_data: Optional[Dict[str, Any]] = None,
               views_breakdown_data: Optional[Dict[str, Any]] = None,
               geographic_views_data: Optional[List[Dict[str, Any]]] = None,
               geographic_subscribers_data: Optional[List[Dict[str, Any]]] = None,
               daily_metrics_data: Optional[List[Dict[str, Any]]] = None,
               revenue_data: Optional[Dict[str, Any]] = None):
        """Create AnalyticsReport using injected factories.
        
        Returns:
            AnalyticsReport or AnalyticsReportExported instance
        """
        # Create required components
        channel = self.channel_factory.create(**channel_data)
        period = self.date_range_factory.create(**period_data)
        
        # Create optional components
        subscription_metrics = None
        if subscription_data and self.subscription_factory:
            subscription_metrics = self.subscription_factory.create(**subscription_data)
        
        views_breakdown = None
        if views_breakdown_data and self.views_breakdown_factory:
            views_breakdown = self.views_breakdown_factory.create(**views_breakdown_data)
        
        geographic_views = []
        if geographic_views_data and self.geographic_factory:
            for geo_data in geographic_views_data:
                geographic_views.append(
                    self.geographic_factory.create(**geo_data)
                )
        
        geographic_subscribers = []
        if geographic_subscribers_data and self.geographic_factory:
            for geo_data in geographic_subscribers_data:
                geographic_subscribers.append(
                    self.geographic_factory.create(**geo_data)
                )
        
        daily_metrics = []
        if daily_metrics_data and self.daily_metrics_factory:
            for daily_data in daily_metrics_data:
                daily_metrics.append(
                    self.daily_metrics_factory.create(**daily_data)
                )
        
        revenue_metrics = None
        if revenue_data and self.revenue_factory:
            revenue_metrics = self.revenue_factory.create(**revenue_data)
        
        # Build the report
        report = AnalyticsReport(
            channel=channel,
            period=period,
            generated_at=generated_at,
            subscription_metrics=subscription_metrics,
            views_breakdown=views_breakdown,
            revenue_metrics=revenue_metrics,
            geographic_views=geographic_views,
            geographic_subscribers=geographic_subscribers,
            daily_metrics=daily_metrics
        )
        
        if self.exported_class:
            return self.exported_class(report)
        return report