"""Main entry point for YouTube Analytics application."""

import datetime
from youtube import YouTubeAPIClient, YouTubeRepository
from models import DateRange
from exporters import JsonExported, TextExported

# Pure model factories
from models.factories import (
    ChannelFactory as BaseChannelFactory,
    DateRangeFactory as BaseDateRangeFactory,
    SubscriptionMetricsFactory as BaseSubscriptionFactory,
    ViewsBreakdownFactory as BaseViewsFactory,
    DailyMetricsFactory as BaseDailyMetricsFactory,
    GeographicMetricsFactory as BaseGeographicFactory,
    RevenueMetricsFactory as BaseRevenueFactory
)

# YouTube API decorators
from youtube.factories import (
    YouTubeChannelFactory,
    YouTubeViewsFactory,
    YouTubeDailyMetricsFactory,
    YouTubeGeographicFactory,
    YouTubeRevenueFactory
)

# Export decorators
from exporters.factories.decorators.exported_factory_decorator import ExportedFactoryDecorator
from exporters.factories.decorators.exported_list_factory_decorator import ExportedListFactoryDecorator

# Exported classes
from exporters.model_exporters import (
    ChannelExported, DateRangeExported, SubscriptionMetricsExported,
    ViewsBreakdownExported, GeographicMetricsExported, RevenueMetricsExported,
    DailyMetricsExported, AnalyticsReportExported
)


def main():
    """Main function to orchestrate analytics data collection."""
    print("Starting YouTube Analytics data collection...")
    
    # Set date range
    start_date = '2024-01-01'
    end_date = datetime.date.today().isoformat()
    
    # Initialize API client first
    api_client = YouTubeAPIClient()
    
    # Compose factories using decorator pattern
    # Channel: Exported(YouTube(Base))
    channel_factory = ExportedFactoryDecorator(
        factory=YouTubeChannelFactory(
            factory=BaseChannelFactory(),
            api_client=api_client
        ),
        exported_class=ChannelExported
    )
    
    # DateRange: Exported(Base) - no YouTube API needed
    date_range_factory = ExportedFactoryDecorator(
        factory=BaseDateRangeFactory(),
        exported_class=DateRangeExported
    )
    
    # SubscriptionMetrics: Exported(Base) - calculated from daily metrics
    # Uses the date_range_factory for creating period
    subscription_factory = ExportedFactoryDecorator(
        factory=BaseSubscriptionFactory(
            date_range_factory=date_range_factory
        ),
        exported_class=SubscriptionMetricsExported
    )
    
    # ViewsBreakdown: Exported(YouTube(Base))
    views_breakdown_factory = ExportedFactoryDecorator(
        factory=YouTubeViewsFactory(
            factory=BaseViewsFactory(),
            api_client=api_client
        ),
        exported_class=ViewsBreakdownExported
    )
    
    # DailyMetrics: ExportedList(YouTube(Base)) - returns list
    daily_metrics_factory = ExportedListFactoryDecorator(
        factory=YouTubeDailyMetricsFactory(
            api_client=api_client,
            base_factory=BaseDailyMetricsFactory()
        ),
        exported_class=DailyMetricsExported
    )
    
    # GeographicMetrics: ExportedList(YouTube(Base)) - returns list
    geographic_factory = ExportedListFactoryDecorator(
        factory=YouTubeGeographicFactory(
            api_client=api_client,
            base_factory=BaseGeographicFactory()
        ),
        exported_class=GeographicMetricsExported
    )
    
    # RevenueMetrics: Exported(YouTube(Base))
    revenue_factory = ExportedFactoryDecorator(
        factory=YouTubeRevenueFactory(
            factory=BaseRevenueFactory(
                date_range_factory=date_range_factory
            ),
            api_client=api_client
        ),
        exported_class=RevenueMetricsExported
    )
    
    # Initialize repository with all individual factories
    analytics_repo = YouTubeRepository(
        api_client=api_client,
        channel_factory=channel_factory,
        date_range_factory=date_range_factory,
        subscription_factory=subscription_factory,
        views_breakdown_factory=views_breakdown_factory,
        geographic_factory=geographic_factory,
        daily_metrics_factory=daily_metrics_factory,
        revenue_factory=revenue_factory,
        exported_class=AnalyticsReportExported
    )
    
    # Load analytics report using repository pattern
    period = DateRange(
        start_date=datetime.datetime.strptime(start_date, '%Y-%m-%d').date(),
        end_date=datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    )
    report = analytics_repo.load(period)
    
    # Report already has export() method from factory
    # Export report to dictionary - just call it directly
    report_dict = report.export()
    
    # Export to JSON string
    json_string = JsonExported(report_dict).export()
    with open('youtube_analytics.json', 'w', encoding='utf-8') as f:
        f.write(json_string)
    print("Data saved to youtube_analytics.json")
    
    # Export to text string
    text_string = TextExported(report_dict, language='ru').export()
    with open('youtube_report.txt', 'w', encoding='utf-8') as f:
        f.write(text_string)
    print("Report saved to youtube_report.txt")
    
    # Print summary - accessing directly through transparent wrapper
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    # Access attributes directly - the wrapper is transparent
    print(f"Channel: {report.channel.video_count} videos")
    
    if report.subscription_metrics:
        print(f"New subscribers: {report.subscription_metrics.subscribers_gained}")
        print(f"Net change: {report.subscription_metrics.net_change:+d}")
    
    if report.views_breakdown:
        print(f"Total views: {report.views_breakdown.total_views}")
        print(f"Videos vs Shorts: {report.views_breakdown.video_percentage:.1f}% vs {report.views_breakdown.shorts_percentage:.1f}%")
    
    if report.has_revenue_data:
        print(f"Revenue: ${report.revenue_metrics.total_revenue:.2f}")
    else:
        print("Revenue: Not available (monetization required)")
    
    if report.geographic_views:
        top_country = report.geographic_views[0]
        print(f"Top country: {top_country.country_name} ({top_country.views} views)")
    
    print("=" * 60)


if __name__ == "__main__":
    main()