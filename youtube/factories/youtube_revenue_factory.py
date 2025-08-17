"""YouTube API decorator for RevenueMetrics factory."""

from typing import TYPE_CHECKING, Any, Optional
from datetime import date, datetime
from decimal import Decimal
from models.factories.base import FactoryDecorator, Factory
from models.revenue import DailyRevenue

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeRevenueFactory(FactoryDecorator):
    """Decorator that adds YouTube API fetching to RevenueMetrics factory."""
    
    def __init__(self, factory: Factory, api_client: 'YouTubeAPIClient'):
        """Initialize with wrapped factory and API client.
        
        Args:
            factory: The RevenueMetrics factory to wrap
            api_client: YouTube API client for fetching data
        """
        super().__init__(factory)
        self.api_client = api_client
    
    def create(self,
               start_date: Optional[date] = None,
               end_date: Optional[date] = None,
               fetch_from_api: bool = False,
               **kwargs) -> Any:
        """Create RevenueMetrics, fetching from API if requested.
        
        Args:
            start_date: Start date for the period
            end_date: End date for the period
            fetch_from_api: Whether to fetch from API
            **kwargs: Arguments for creating RevenueMetrics
            
        Returns:
            RevenueMetrics instance
        """
        # If not fetching from API or data already provided, just delegate
        if not fetch_from_api or 'total_revenue' in kwargs:
            return self.factory.create(
                start_date=start_date,
                end_date=end_date,
                **kwargs
            )
        
        # Need dates to fetch from API
        if not start_date or not end_date:
            return self.factory.create(
                start_date=start_date,
                end_date=end_date,
                **kwargs
            )
        
        # Fetch from YouTube Analytics API
        youtube_analytics = self.api_client.get_analytics_service()
        
        try:
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date.isoformat() if isinstance(start_date, date) else start_date,
                endDate=end_date.isoformat() if isinstance(end_date, date) else end_date,
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
                
                kwargs['total_revenue'] = total_revenue
                kwargs['ad_revenue'] = total_ad_revenue if total_ad_revenue > 0 else None
                kwargs['red_partner_revenue'] = total_red_revenue if total_red_revenue > 0 else None
                kwargs['daily_revenue'] = daily_revenue
                kwargs['is_monetized'] = total_revenue > 0
            else:
                # No revenue data
                kwargs['total_revenue'] = Decimal('0')
                kwargs['ad_revenue'] = None
                kwargs['red_partner_revenue'] = None
                kwargs['daily_revenue'] = []
                kwargs['is_monetized'] = False
                
        except Exception as e:
            print(f"Error fetching revenue data: {e}")
            if "Insufficient permission" in str(e):
                print("Note: Revenue metrics require proper AdSense integration and permissions")
            # Create unavailable revenue metrics
            kwargs['total_revenue'] = Decimal('0')
            kwargs['ad_revenue'] = None
            kwargs['red_partner_revenue'] = None
            kwargs['daily_revenue'] = []
            kwargs['is_monetized'] = False
        
        # Delegate to wrapped factory with fetched data
        return self.factory.create(
            start_date=start_date,
            end_date=end_date,
            **kwargs
        )