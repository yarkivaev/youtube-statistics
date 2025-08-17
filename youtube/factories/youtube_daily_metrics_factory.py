"""YouTube API decorator for DailyMetrics factory."""

from typing import TYPE_CHECKING, Any, Optional, List
from datetime import datetime
from models.factories.base import Factory
from models import DailyMetrics

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeDailyMetricsFactory(Factory):
    """Factory that fetches daily metrics from YouTube API.
    
    This is not a decorator because it returns a list of DailyMetrics
    rather than a single instance.
    """
    
    def __init__(self, api_client: 'YouTubeAPIClient', base_factory: Factory):
        """Initialize with API client and base factory.
        
        Args:
            api_client: YouTube API client for fetching data
            base_factory: Base DailyMetrics factory for creating instances
        """
        self.api_client = api_client
        self.base_factory = base_factory
    
    def create(self,
               start_date: Optional[str] = None,
               end_date: Optional[str] = None,
               **kwargs) -> List[DailyMetrics]:
        """Fetch daily metrics from YouTube API.
        
        Args:
            start_date: Start date for API query (ISO format)
            end_date: End date for API query (ISO format)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            List of DailyMetrics instances
        """
        # Need dates to fetch from API
        if not start_date or not end_date:
            return []
        
        youtube_analytics = self.api_client.get_analytics_service()
        daily_metrics = []
        
        try:
            # Fetch daily metrics
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
                dimensions='day',
                sort='day'
            )
            response = self.api_client.execute_request(request)
            
            if response and response.get('rows'):
                for row in response['rows']:
                    date_obj = datetime.strptime(row[0], '%Y-%m-%d').date()
                    
                    # Create DailyMetrics using base factory
                    daily_metric = self.base_factory.create(
                        date_val=date_obj,
                        views=row[1] if len(row) > 1 else 0,
                        watch_time_minutes=row[2] if len(row) > 2 else 0,
                        average_view_duration_seconds=row[3] if len(row) > 3 else 0,
                        subscribers_gained=row[4] if len(row) > 4 else 0,
                        subscribers_lost=row[5] if len(row) > 5 else 0
                    )
                    daily_metrics.append(daily_metric)
            
        except Exception as e:
            print(f"Error fetching daily metrics: {e}")
        
        return daily_metrics