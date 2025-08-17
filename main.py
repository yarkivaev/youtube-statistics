"""Main entry point for YouTube Analytics application."""

import datetime
from services import YouTubeAPIClient, YouTubeAnalyticsService
from exporters import JsonExported, TextExported
from exporters.factories import (
    ChannelFactory, DateRangeFactory, SubscriptionMetricsFactory,
    ViewsBreakdownFactory, GeographicMetricsFactory, DailyMetricsFactory,
    RevenueMetricsFactory, AnalyticsReportFactory
)
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
    
    # Configure factories with export decorators
    # Create base factories
    channel_factory = ChannelFactory(exported_class=ChannelExported)
    date_range_factory = DateRangeFactory(exported_class=DateRangeExported)
    
    # Create factories with dependencies
    subscription_factory = SubscriptionMetricsFactory(
        date_range_factory=date_range_factory,
        exported_class=SubscriptionMetricsExported
    )
    
    views_breakdown_factory = ViewsBreakdownFactory(
        exported_class=ViewsBreakdownExported
    )
    
    geographic_factory = GeographicMetricsFactory(
        exported_class=GeographicMetricsExported
    )
    
    daily_metrics_factory = DailyMetricsFactory(
        exported_class=DailyMetricsExported
    )
    
    revenue_factory = RevenueMetricsFactory(
        date_range_factory=date_range_factory,
        exported_class=RevenueMetricsExported
    )
    
    # Create main report factory with all dependencies
    report_factory = AnalyticsReportFactory(
        channel_factory=channel_factory,
        date_range_factory=date_range_factory,
        subscription_factory=subscription_factory,
        views_breakdown_factory=views_breakdown_factory,
        geographic_factory=geographic_factory,
        daily_metrics_factory=daily_metrics_factory,
        revenue_factory=revenue_factory,
        exported_class=AnalyticsReportExported
    )
    
    # Initialize API client and service with factory
    api_client = YouTubeAPIClient()
    analytics_service = YouTubeAnalyticsService(api_client, report_factory)
    
    # Fetch analytics report - will return pre-decorated report
    report = analytics_service.fetch_analytics_report(start_date, end_date)
    
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