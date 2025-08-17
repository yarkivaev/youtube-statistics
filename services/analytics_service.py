"""Service for fetching and processing YouTube Analytics data."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from models import (
    Channel, SubscriptionMetrics, ViewsBreakdown, 
    DailyMetrics, GeographicMetrics, RevenueMetrics,
    AnalyticsReport, DateRange
)
from models.revenue import DailyRevenue
from models.metrics import ContentType
from .youtube_api import YouTubeAPIClient

if TYPE_CHECKING:
    from exporters.factories import AnalyticsReportFactory


class YouTubeAnalyticsService:
    """Service for fetching and processing YouTube Analytics data."""
    
    def __init__(self, api_client: YouTubeAPIClient, 
                 report_factory: Optional['AnalyticsReportFactory'] = None):
        """Initialize service with API client and optional factory.
        
        Args:
            api_client: YouTube API client instance
            report_factory: Optional factory for creating report with decorators
        """
        self.api_client = api_client
        self.report_factory = report_factory
    
    def fetch_analytics_report(self, start_date: str, end_date: str) -> AnalyticsReport:
        """Fetch complete analytics report for a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Complete AnalyticsReport with all available data
        """
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if self.report_factory:
            # Use factory to create report with decorators
            return self._fetch_with_factory(start_date, end_date, start_date_obj, end_date_obj)
        else:
            # Create report without factory (backward compatibility)
            return self._fetch_without_factory(start_date, end_date, start_date_obj, end_date_obj)
    
    def _fetch_with_factory(self, start_date: str, end_date: str,
                           start_date_obj: date, end_date_obj: date) -> AnalyticsReport:
        """Fetch report using factory for decorated models."""
        # Fetch all data
        print("Fetching channel statistics...")
        channel_stats = self._fetch_channel_stats_dict()
        
        print("Fetching daily metrics...")
        daily_metrics_data = self._fetch_daily_metrics(start_date, end_date)
        
        print("Fetching revenue data...")
        revenue_data = self._fetch_revenue_metrics_dict(start_date, end_date, start_date_obj, end_date_obj)
        
        print("Fetching geographic data...")
        geo_views_data = self._fetch_geographic_views_dict(start_date, end_date)
        geo_subs_data = self._fetch_geographic_subscribers_dict(start_date, end_date)
        
        # Prepare data for factory
        report_data = {
            'channel_data': channel_stats,
            'period_data': {
                'start_date': start_date_obj,
                'end_date': end_date_obj
            },
            'generated_at': datetime.now()
        }
        
        # Add optional data if available
        if daily_metrics_data:
            # Process subscription metrics
            rows = daily_metrics_data.get('rows', [])
            total_gained = sum(row[4] if len(row) > 4 else 0 for row in rows)
            total_lost = sum(row[5] if len(row) > 5 else 0 for row in rows)
            
            report_data['subscription_data'] = {
                'subscribers_gained': total_gained,
                'subscribers_lost': total_lost,
                'start_date': start_date_obj,
                'end_date': end_date_obj
            }
            
            # Process views breakdown
            content_breakdown_data = self._fetch_content_type_breakdown(start_date, end_date)
            if content_breakdown_data:
                breakdown = self._calculate_views_breakdown_dict(content_breakdown_data)
                report_data['views_breakdown_data'] = breakdown
            
            # Process daily metrics
            report_data['daily_metrics_data'] = [
                self._daily_metrics_to_dict(row) for row in rows
            ]
        
        if geo_views_data:
            report_data['geographic_views_data'] = geo_views_data
        
        if geo_subs_data:
            report_data['geographic_subscribers_data'] = geo_subs_data
        
        if revenue_data:
            report_data['revenue_data'] = revenue_data
        
        # Use factory to create report
        return self.report_factory.create(**report_data)
    
    def _fetch_without_factory(self, start_date: str, end_date: str,
                               start_date_obj: date, end_date_obj: date) -> AnalyticsReport:
        """Fetch report without factory (original implementation)."""
        period = DateRange(start_date=start_date_obj, end_date=end_date_obj)
        
        # Fetch channel statistics
        print("Fetching channel statistics...")
        channel = self._fetch_channel_stats()
        
        # Create report
        report = AnalyticsReport(
            channel=channel,
            period=period,
            generated_at=datetime.now()
        )
        
        # Fetch daily metrics
        print("Fetching daily metrics...")
        daily_metrics_data = self._fetch_daily_metrics(start_date, end_date)
        if daily_metrics_data:
            report.daily_metrics = self._process_daily_metrics(daily_metrics_data)
            report.subscription_metrics = self._calculate_subscription_metrics(
                daily_metrics_data, period
            )
            
            # Fetch content type breakdown
            content_breakdown_data = self._fetch_content_type_breakdown(start_date, end_date)
            if content_breakdown_data:
                report.views_breakdown = self._calculate_views_breakdown(content_breakdown_data)
        
        # Fetch revenue data
        print("Fetching revenue data...")
        report.revenue_metrics = self._fetch_revenue_metrics(start_date, end_date, period)
        
        # Fetch geographic data
        print("Fetching geographic data...")
        report.geographic_views = self._fetch_geographic_views(start_date, end_date)
        report.geographic_subscribers = self._fetch_geographic_subscribers(start_date, end_date)
        
        return report
    
    def _fetch_channel_stats(self) -> Channel:
        """Fetch channel statistics."""
        youtube_data = self.api_client.get_data_service()
        
        try:
            request = youtube_data.channels().list(
                part="statistics,contentDetails",
                mine=True
            )
            response = self.api_client.execute_request(request)
            
            if response and response.get('items'):
                stats = response['items'][0]['statistics']
                return Channel.from_api_response(stats)
        except Exception as e:
            print(f"Error fetching channel statistics: {e}")
        
        # Return default channel if error
        return Channel(
            video_count=0,
            subscriber_count=0,
            total_view_count=0
        )
    
    def _fetch_daily_metrics(self, start_date: str, end_date: str) -> Optional[dict]:
        """Fetch daily metrics data."""
        youtube_analytics = self.api_client.get_analytics_service()
        
        try:
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
                dimensions='day',
                sort='day'
            )
            return self.api_client.execute_request(request)
        except Exception as e:
            print(f"Error fetching daily metrics: {e}")
            return None
    
    def _fetch_content_type_breakdown(self, start_date: str, end_date: str) -> Optional[dict]:
        """Fetch content type breakdown data."""
        youtube_analytics = self.api_client.get_analytics_service()
        
        try:
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched',
                dimensions='day,creatorContentType',
                sort='day'
            )
            return self.api_client.execute_request(request)
        except Exception as e:
            print(f"Error fetching content type breakdown: {e}")
            return None
    
    def _fetch_revenue_metrics(self, start_date: str, end_date: str, 
                              period: DateRange) -> Optional[RevenueMetrics]:
        """Fetch revenue metrics."""
        youtube_analytics = self.api_client.get_analytics_service()
        
        try:
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='estimatedRevenue,estimatedAdRevenue,estimatedRedPartnerRevenue',
                dimensions='day',
                sort='day'
            )
            response = self.api_client.execute_request(request)
            
            if response and response.get('rows'):
                return self._process_revenue_data(response, period)
        except Exception as e:
            print(f"Error fetching revenue data: {e}")
            if "Insufficient permission" in str(e):
                print("Note: Revenue metrics require proper AdSense integration and permissions")
        
        return RevenueMetrics.create_unavailable(period)
    
    def _fetch_geographic_views(self, start_date: str, end_date: str) -> List[GeographicMetrics]:
        """Fetch geographic views data."""
        youtube_analytics = self.api_client.get_analytics_service()
        
        try:
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched',
                dimensions='country',
                sort='-views',
                maxResults=9
            )
            response = self.api_client.execute_request(request)
            
            if response and response.get('rows'):
                return [
                    GeographicMetrics.from_views_data(
                        country_code=row[0],
                        views=row[1],
                        watch_time=row[2]
                    )
                    for row in response['rows']
                ]
        except Exception as e:
            print(f"Error fetching geographic views: {e}")
        
        return []
    
    def _fetch_geographic_subscribers(self, start_date: str, end_date: str) -> List[GeographicMetrics]:
        """Fetch geographic subscribers data."""
        youtube_analytics = self.api_client.get_analytics_service()
        
        try:
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='subscribersGained',
                dimensions='country',
                sort='-subscribersGained',
                maxResults=5
            )
            response = self.api_client.execute_request(request)
            
            if response and response.get('rows'):
                return [
                    GeographicMetrics.from_subscriber_data(
                        country_code=row[0],
                        subscribers=row[1]
                    )
                    for row in response['rows']
                ]
        except Exception as e:
            print(f"Error fetching geographic subscribers: {e}")
        
        return []
    
    def _process_daily_metrics(self, data: dict) -> List[DailyMetrics]:
        """Process daily metrics from API response."""
        metrics = []
        for row in data.get('rows', []):
            metrics.append(DailyMetrics.from_api_row(row))
        return metrics
    
    def _calculate_subscription_metrics(self, data: dict, period: DateRange) -> SubscriptionMetrics:
        """Calculate subscription metrics from daily data."""
        rows = data.get('rows', [])
        total_gained = sum(row[4] if len(row) > 4 else 0 for row in rows)
        total_lost = sum(row[5] if len(row) > 5 else 0 for row in rows)
        
        return SubscriptionMetrics(
            subscribers_gained=total_gained,
            subscribers_lost=total_lost,
            period=period
        )
    
    def _calculate_views_breakdown(self, data: dict) -> ViewsBreakdown:
        """Calculate views breakdown by content type."""
        videos_views = 0
        shorts_views = 0
        live_views = 0
        
        for row in data.get('rows', []):
            if len(row) > 2:
                content_type = ContentType.from_api_value(row[1])
                views = row[2]
                
                if content_type == ContentType.VIDEO:
                    videos_views += views
                elif content_type == ContentType.SHORTS:
                    shorts_views += views
                elif content_type == ContentType.LIVE_STREAM:
                    live_views += views
        
        total_views = videos_views + shorts_views + live_views
        
        return ViewsBreakdown(
            total_views=total_views,
            video_views=videos_views,
            shorts_views=shorts_views,
            live_stream_views=live_views
        )
    
    def _process_revenue_data(self, data: dict, period: DateRange) -> RevenueMetrics:
        """Process revenue data from API response."""
        daily_revenue = []
        total_revenue = Decimal('0')
        total_ad_revenue = Decimal('0')
        total_red_revenue = Decimal('0')
        
        for row in data.get('rows', []):
            date_obj = datetime.strptime(row[0], '%Y-%m-%d').date()
            estimated = Decimal(str(row[1])) if row[1] else Decimal('0')
            ad_rev = Decimal(str(row[2])) if len(row) > 2 and row[2] else None
            red_rev = Decimal(str(row[3])) if len(row) > 3 and row[3] else None
            
            daily_revenue.append(DailyRevenue(
                date=date_obj,
                estimated_revenue=estimated,
                ad_revenue=ad_rev,
                red_partner_revenue=red_rev
            ))
            
            total_revenue += estimated
            if ad_rev:
                total_ad_revenue += ad_rev
            if red_rev:
                total_red_revenue += red_rev
        
        return RevenueMetrics(
            total_revenue=total_revenue,
            ad_revenue=total_ad_revenue if total_ad_revenue > 0 else None,
            red_partner_revenue=total_red_revenue if total_red_revenue > 0 else None,
            period=period,
            daily_revenue=daily_revenue,
            is_monetized=total_revenue > 0
        )
    
    # Helper methods for factory-based creation
    
    def _fetch_channel_stats_dict(self) -> dict:
        """Fetch channel statistics as dictionary."""
        channel = self._fetch_channel_stats()
        return {
            'video_count': channel.video_count,
            'subscriber_count': channel.subscriber_count,
            'total_view_count': channel.total_view_count,
            'advertiser_count': channel.advertiser_count,
            'integrations': channel.integrations
        }
    
    def _fetch_geographic_views_dict(self, start_date: str, end_date: str) -> List[dict]:
        """Fetch geographic views as list of dictionaries."""
        geo_list = self._fetch_geographic_views(start_date, end_date)
        return [
            {
                'country_code': geo.country_code,
                'country_name': geo.country_name,
                'views': geo.views,
                'watch_time_minutes': geo.watch_time_minutes
            }
            for geo in geo_list
        ]
    
    def _fetch_geographic_subscribers_dict(self, start_date: str, end_date: str) -> List[dict]:
        """Fetch geographic subscribers as list of dictionaries."""
        geo_list = self._fetch_geographic_subscribers(start_date, end_date)
        return [
            {
                'country_code': geo.country_code,
                'country_name': geo.country_name,
                'subscribers_gained': geo.subscribers_gained
            }
            for geo in geo_list
        ]
    
    def _fetch_revenue_metrics_dict(self, start_date: str, end_date: str,
                                    start_date_obj: date, end_date_obj: date) -> Optional[dict]:
        """Fetch revenue metrics as dictionary."""
        period = DateRange(start_date=start_date_obj, end_date=end_date_obj)
        revenue = self._fetch_revenue_metrics(start_date, end_date, period)
        
        if not revenue or not revenue.has_revenue:
            return None
        
        return {
            'total_revenue': revenue.total_revenue,
            'ad_revenue': revenue.ad_revenue,
            'red_partner_revenue': revenue.red_partner_revenue,
            'start_date': start_date_obj,
            'end_date': end_date_obj,
            'daily_revenue': revenue.daily_revenue,
            'is_monetized': revenue.is_monetized
        }
    
    def _calculate_views_breakdown_dict(self, data: dict) -> dict:
        """Calculate views breakdown as dictionary."""
        breakdown = self._calculate_views_breakdown(data)
        return {
            'total_views': breakdown.total_views,
            'video_views': breakdown.video_views,
            'shorts_views': breakdown.shorts_views,
            'live_stream_views': breakdown.live_stream_views
        }
    
    def _daily_metrics_to_dict(self, row: List) -> dict:
        """Convert API row to daily metrics dictionary."""
        daily = DailyMetrics.from_api_row(row)
        return {
            'date': daily.date,
            'views': daily.views,
            'watch_time_minutes': daily.watch_time_minutes,
            'average_view_duration_seconds': daily.average_view_duration_seconds,
            'subscribers_gained': daily.subscribers_gained,
            'subscribers_lost': daily.subscribers_lost,
            'content_type': daily.content_type
        }