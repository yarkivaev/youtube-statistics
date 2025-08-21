"""Composite factory that unifies all YouTube Analytics factories."""

from datetime import date, datetime, timedelta
from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from models import DateRange, SubscriptionMetrics, RevenueMetrics, YouTubeMetrics
from models.factories.base import Factory

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeMetricsFactory(Factory):
    """Composite factory that encapsulates all individual factories for YouTube Analytics."""
    
    def __init__(
        self,
        api_client: 'YouTubeAPIClient',
        period: Optional[DateRange] = None,
        skip_revenue: bool = False
    ):
        """Initialize composite factory with API client and configuration.
        
        Args:
            api_client: YouTube API client instance
            period: Date range for analytics (None = last 30 days)
            skip_revenue: If True, skip fetching revenue data
        """
        self.api_client = api_client
        self.period = period
        self.skip_revenue = skip_revenue
        
        # Initialize all factories
        self._initialize_factories()
    
    def _initialize_factories(self):
        """Initialize all individual factories."""
        # Import YouTube factories
        from youtube.factories import (
            YouTubeChannelFactory,
            YouTubeDailyMetricsFactory,
            YouTubeGeographicFactory,
            YouTubeRevenueFactory,
            YouTubeViewsFactory,
            YouTubeVideoListFactory
        )
        
        # Initialize YouTube API factories
        self.channel_factory = YouTubeChannelFactory(self.api_client)
        self.daily_metrics_factory = YouTubeDailyMetricsFactory(self.api_client)
        self.views_breakdown_factory = YouTubeViewsFactory(self.api_client)
        self.geographic_factory = YouTubeGeographicFactory(self.api_client)
        self.video_list_factory = YouTubeVideoListFactory(self.api_client)
        
        # Only initialize revenue factory if not skipping revenue
        if not self.skip_revenue:
            self.revenue_factory = YouTubeRevenueFactory(self.api_client)
        else:
            self.revenue_factory = None
        
    
    def create(self, **kwargs) -> YouTubeMetrics:
        """Fetch all YouTube data and create YouTubeMetrics.
        
        Args:
            **kwargs: Optional parameters (currently unused)
            
        Returns:
            YouTubeMetrics instance with all fetched data
        """
        # Determine period
        if self.period is None:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        elif isinstance(self.period, DateRange):
            start_date = self.period.start_date
            end_date = self.period.end_date
        else:
            raise ValueError(f"Invalid period type: {type(self.period)}")
        
        # Create period object
        period_obj = DateRange(
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"Fetching analytics for period: {start_date} to {end_date}")
        
        # Fetch channel statistics
        print("Fetching channel statistics...")
        channel = self.channel_factory.create()
        
        # Fetch video counts by month
        print("Fetching video upload counts by month...")
        video_counts_by_month = self.video_list_factory.create(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Fetch daily metrics first (needed for subscription aggregation)
        print("Fetching daily metrics...")
        daily_metrics = self.daily_metrics_factory.create(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Calculate subscription metrics from daily metrics
        print("Calculating subscription metrics...")
        total_subscribers_gained = sum(dm.subscribers_gained for dm in daily_metrics) if daily_metrics else 0
        total_subscribers_lost = sum(dm.subscribers_lost for dm in daily_metrics) if daily_metrics else 0
        subscription_metrics = SubscriptionMetrics(
            subscribers_gained=total_subscribers_gained,
            subscribers_lost=total_subscribers_lost,
            period=period_obj
        )
        
        # Fetch views breakdown
        print("Fetching views breakdown...")
        views_breakdown = self.views_breakdown_factory.create(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Fetch revenue metrics (if not skipped)
        if not self.skip_revenue:
            print("Fetching revenue metrics...")
            revenue_metrics = self.revenue_factory.create(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
        else:
            print("Skipping revenue metrics (--skip-revenue flag set)")
            # Create empty revenue metrics
            revenue_metrics = RevenueMetrics(
                total_revenue=Decimal('0'),
                ad_revenue=Decimal('0'),
                red_partner_revenue=Decimal('0'),
                period=period_obj,
                daily_revenue=[]
            )
        
        # Fetch geographic views
        print("Fetching geographic views...")
        geographic_views = self.geographic_factory.create(
            fetch_type='views',
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Fetch geographic subscribers
        print("Fetching geographic subscribers...")
        geographic_subscribers = self.geographic_factory.create(
            fetch_type='subscribers',
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # Create YouTubeMetrics model
        report = YouTubeMetrics(
            channel=channel,
            period=period_obj,
            generated_at=datetime.now(),
            subscription_metrics=subscription_metrics,
            views_breakdown=views_breakdown,
            revenue_metrics=revenue_metrics,
            geographic_views=geographic_views,
            geographic_subscribers=geographic_subscribers,
            daily_metrics=daily_metrics,
            video_counts_by_month=video_counts_by_month
        )
        
        return report
