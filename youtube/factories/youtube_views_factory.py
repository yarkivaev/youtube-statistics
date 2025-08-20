"""YouTube API factory for ViewsBreakdown."""

from typing import TYPE_CHECKING, Optional
from models.factories.base import Factory
from models import ViewsBreakdown
from models.daily_metrics import ContentType

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeViewsFactory(Factory):
    """Factory that fetches views breakdown from YouTube API."""
    
    def __init__(self, api_client: 'YouTubeAPIClient'):
        """Initialize with API client.
        
        Args:
            api_client: YouTube API client for fetching data
        """
        self.api_client = api_client
    
    def create(self, 
               start_date: Optional[str] = None,
               end_date: Optional[str] = None,
               **kwargs) -> ViewsBreakdown:
        """Create ViewsBreakdown, fetching from API if data not provided.
        
        If total_views is not in kwargs and dates are provided, fetches
        views breakdown from YouTube API. Otherwise creates ViewsBreakdown directly.
        
        Args:
            start_date: Start date for API query (ISO format)
            end_date: End date for API query (ISO format)
            **kwargs: Arguments for creating ViewsBreakdown
            
        Returns:
            ViewsBreakdown instance
        """
        # If data already provided, create directly
        if 'total_views' in kwargs:
            return ViewsBreakdown(**kwargs)
        
        # Need dates to fetch from API
        if not start_date or not end_date:
            return ViewsBreakdown(
                total_views=kwargs.get('total_views', 0),
                video_views=kwargs.get('video_views', 0),
                shorts_views=kwargs.get('shorts_views', 0),
                live_stream_views=kwargs.get('live_stream_views', 0)
            )
        
        # Fetch from YouTube Analytics API
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
            data = self.api_client.execute_request(request)
            
            # Calculate views breakdown
            video_views = 0
            shorts_views = 0
            live_stream_views = 0
            
            for row in data.get('rows', []):
                if len(row) > 2:
                    content_type = ContentType.from_api_value(row[1])
                    views = row[2]
                    
                    if content_type == ContentType.VIDEO:
                        video_views += views
                    elif content_type == ContentType.SHORTS:
                        shorts_views += views
                    elif content_type == ContentType.LIVE_STREAM:
                        live_stream_views += views
            
            kwargs['total_views'] = video_views + shorts_views + live_stream_views
            kwargs['video_views'] = video_views
            kwargs['shorts_views'] = shorts_views
            kwargs['live_stream_views'] = live_stream_views
            
        except Exception as e:
            print(f"Error fetching content type breakdown: {e}")
            # Set defaults on error
            kwargs['total_views'] = 0
            kwargs['video_views'] = 0
            kwargs['shorts_views'] = 0
            kwargs['live_stream_views'] = 0
        
        # Create ViewsBreakdown with fetched data
        return ViewsBreakdown(**kwargs)