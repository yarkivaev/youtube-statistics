"""YouTube API factory for RevenueMetrics."""

from typing import TYPE_CHECKING, Optional
from datetime import date, datetime
from decimal import Decimal
from domain import Factory, RevenueMetrics, DateRange, DailyMetrics

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeRevenueFactory(Factory):
    """Factory that fetches revenue metrics from YouTube API."""
    
    def __init__(self, api_client: 'YouTubeAPIClient'):
        """Initialize with API client.
        
        Args:
            api_client: YouTube API client for fetching data
        """
        self.api_client = api_client
    
    def create(self,
               start_date: Optional[str] = None,
               end_date: Optional[str] = None,
               fetch_from_api: bool = False,
               **kwargs) -> RevenueMetrics:
        """Create RevenueMetrics, fetching from API if requested.
        
        Args:
            start_date: Start date for the period (ISO format string)
            end_date: End date for the period (ISO format string)
            fetch_from_api: Whether to fetch from API
            **kwargs: Arguments for creating RevenueMetrics
            
        Returns:
            RevenueMetrics instance
        """
        # If not fetching from API or data already provided, create directly
        if not fetch_from_api or 'total_revenue' in kwargs:
            period = kwargs.get('period')
            if not period and start_date and end_date:
                # Convert string dates to date objects
                from datetime import datetime as dt
                start_dt = dt.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
                end_dt = dt.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
                period = DateRange(start_date=start_dt, end_date=end_dt)
            return RevenueMetrics(
                total_revenue=kwargs.get('total_revenue', Decimal('0')),
                ad_revenue=kwargs.get('ad_revenue', Decimal('0')),
                red_partner_revenue=kwargs.get('red_partner_revenue', Decimal('0')),
                period=period,
                daily_revenue=kwargs.get('daily_revenue', []),
                is_monetized=kwargs.get('is_monetized', False)
            )
        
        # Need dates to fetch from API
        if not start_date or not end_date:
            period = kwargs.get('period')
            if not period and start_date and end_date:
                # Convert string dates to date objects
                from datetime import datetime as dt
                start_dt = dt.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
                end_dt = dt.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
                period = DateRange(start_date=start_dt, end_date=end_dt)
            return RevenueMetrics(
                total_revenue=kwargs.get('total_revenue', Decimal('0')),
                ad_revenue=kwargs.get('ad_revenue', Decimal('0')),
                red_partner_revenue=kwargs.get('red_partner_revenue', Decimal('0')),
                period=period,
                daily_revenue=kwargs.get('daily_revenue', []),
                is_monetized=kwargs.get('is_monetized', False)
            )
        
        # Fetch from YouTube Analytics API
        youtube_analytics = self.api_client.get_analytics_service()
        
        try:
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,  # Already a string from the composite factory
                endDate=end_date,  # Already a string from the composite factory
                metrics='estimatedRevenue,estimatedAdRevenue,estimatedRedPartnerRevenue',
                dimensions='day',
                sort='day'
            )
            response = self.api_client.execute_request(request)
            
            if response and response.get('rows'):
                daily_revenue = []
                total_revenue = Decimal('0')
                total_ad_revenue = Decimal('0')
                total_red_revenue = Decimal('0')
                
                for row in response['rows']:
                    date_obj = datetime.strptime(row[0], '%Y-%m-%d').date()
                    estimated = Decimal(str(row[1])) if row[1] else Decimal('0')
                    ad_rev = Decimal(str(row[2])) if len(row) > 2 and row[2] else Decimal('0')
                    red_rev = Decimal(str(row[3])) if len(row) > 3 and row[3] else Decimal('0')
                    
                    daily_revenue.append(DailyMetrics(
                        date=date_obj,
                        views=0,  # Revenue data doesn't include views
                        watch_time_minutes=0,
                        average_view_duration_seconds=0,
                        subscribers_gained=0,
                        subscribers_lost=0,
                        estimated_revenue=estimated,
                        ad_revenue=ad_rev,
                        red_partner_revenue=red_rev
                    ))
                    
                    total_revenue += estimated
                    total_ad_revenue += ad_rev
                    total_red_revenue += red_rev
                
                kwargs['total_revenue'] = total_revenue
                kwargs['ad_revenue'] = total_ad_revenue
                kwargs['red_partner_revenue'] = total_red_revenue
                kwargs['daily_revenue'] = daily_revenue
                kwargs['is_monetized'] = total_revenue > 0
            else:
                # No revenue data
                kwargs['total_revenue'] = Decimal('0')
                kwargs['ad_revenue'] = Decimal('0')
                kwargs['red_partner_revenue'] = Decimal('0')
                kwargs['daily_revenue'] = []
                kwargs['is_monetized'] = False
                
        except Exception as e:
            print(f"Error fetching revenue data: {e}")
            if "Insufficient permission" in str(e):
                print("Note: Revenue metrics require proper AdSense integration and permissions")
            # Re-raise the exception to fail the entire process
            raise
        
        # Create RevenueMetrics with fetched data
        # Convert string dates to date objects for DateRange
        from datetime import datetime as dt
        start_dt = dt.strptime(start_date, '%Y-%m-%d').date() if isinstance(start_date, str) else start_date
        end_dt = dt.strptime(end_date, '%Y-%m-%d').date() if isinstance(end_date, str) else end_date
        period = DateRange(start_date=start_dt, end_date=end_dt)
        return RevenueMetrics(
            total_revenue=kwargs.get('total_revenue', Decimal('0')),
            ad_revenue=kwargs.get('ad_revenue'),
            red_partner_revenue=kwargs.get('red_partner_revenue'),
            period=period,
            daily_revenue=kwargs.get('daily_revenue', []),
            is_monetized=kwargs.get('is_monetized', False)
        )