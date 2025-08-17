"""YouTube Analytics Repository implementation."""

from datetime import date, datetime, timedelta
from typing import Optional, Union, List, TYPE_CHECKING, Type
from models import AnalyticsReport, DateRange
from repositories.base import AnalyticsRepository

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient
    from exporters.base import Exported
    from models.factories.base import Factory


class YouTubeRepository(AnalyticsRepository):
    """Repository that orchestrates individual factories to create analytics reports."""
    
    def __init__(self, 
                 api_client: 'YouTubeAPIClient',
                 channel_factory: 'Factory',
                 date_range_factory: 'Factory',
                 subscription_factory: 'Factory',
                 views_breakdown_factory: 'Factory',
                 geographic_factory: 'Factory',
                 daily_metrics_factory: 'Factory',
                 revenue_factory: 'Factory',
                 exported_class: Optional[Type['Exported']] = None):
        """Initialize with API client and individual factories.
        
        Args:
            api_client: YouTube API client instance
            channel_factory: Factory for creating Channel instances
            date_range_factory: Factory for creating DateRange instances
            subscription_factory: Factory for SubscriptionMetrics
            views_breakdown_factory: Factory for ViewsBreakdown
            geographic_factory: Factory for GeographicMetrics
            daily_metrics_factory: Factory for DailyMetrics
            revenue_factory: Factory for RevenueMetrics
            exported_class: Optional Exported wrapper class for the report
        """
        self.api_client = api_client
        self.channel_factory = channel_factory
        self.date_range_factory = date_range_factory
        self.subscription_factory = subscription_factory
        self.views_breakdown_factory = views_breakdown_factory
        self.geographic_factory = geographic_factory
        self.daily_metrics_factory = daily_metrics_factory
        self.revenue_factory = revenue_factory
        self.exported_class = exported_class
    
    def load(self, period: Optional[Union[DateRange, str]] = None) -> Optional[Union[AnalyticsReport, List[AnalyticsReport]]]:
        """Load analytics report by orchestrating individual factories.
        
        Args:
            period: Can be:
                - None or "latest": Fetch last 30 days of data
                - DateRange: Fetch data for specific date range
                - "all": Not supported for API fetching
            
        Returns:
            - Single AnalyticsReport if period is DateRange, None, or "latest"
            - Raises NotImplementedError if period is "all"
        """
        # Handle "all" case - not supported for API fetching
        if period == "all":
            raise NotImplementedError("Fetching all historical data is not supported for YouTube API")
        
        # Handle "latest" or None case - fetch last 30 days
        if period is None or period == "latest":
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        # Handle DateRange case - fetch specific period
        elif isinstance(period, DateRange):
            start_date = period.start_date
            end_date = period.end_date
        else:
            # Invalid period type
            raise ValueError(f"Invalid period type: {type(period)}")
        
        # Orchestrate all factories to build the report
        print("Fetching channel statistics...")
        channel = self.channel_factory.create()
        
        # Create period
        period_obj = self.date_range_factory.create(
            start_date=start_date,
            end_date=end_date
        )
        
        # Fetch daily metrics
        print("Fetching daily metrics...")
        daily_metrics = self.daily_metrics_factory.create(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Calculate subscription metrics from daily data
        total_gained = sum(dm.subscribers_gained for dm in daily_metrics) if daily_metrics else 0
        total_lost = sum(dm.subscribers_lost for dm in daily_metrics) if daily_metrics else 0
        
        subscription_metrics = self.subscription_factory.create(
            subscribers_gained=total_gained,
            subscribers_lost=total_lost,
            start_date=start_date,
            end_date=end_date
        )
        
        # Fetch views breakdown
        views_breakdown = self.views_breakdown_factory.create(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Fetch revenue metrics
        print("Fetching revenue data...")
        revenue_metrics = self.revenue_factory.create(
            start_date=start_date,
            end_date=end_date,
            fetch_from_api=True
        )
        
        # Fetch geographic data
        print("Fetching geographic data...")
        geographic_views = self.geographic_factory.create(
            fetch_type="views",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        geographic_subscribers = self.geographic_factory.create(
            fetch_type="subscribers",
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Create the report with all fetched data
        report = AnalyticsReport(
            channel=channel,
            period=period_obj,
            generated_at=datetime.now(),
            subscription_metrics=subscription_metrics,
            views_breakdown=views_breakdown,
            revenue_metrics=revenue_metrics,
            geographic_views=geographic_views,
            geographic_subscribers=geographic_subscribers,
            daily_metrics=daily_metrics
        )
        
        # Apply decorator if configured
        if self.exported_class:
            return self.exported_class(report)
        return report