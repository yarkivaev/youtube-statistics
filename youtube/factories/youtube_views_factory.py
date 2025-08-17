"""YouTube API decorator for ViewsBreakdown factory."""

from typing import TYPE_CHECKING, Any, Optional
from models.factories.base import FactoryDecorator, Factory
from models.metrics import ContentType

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeViewsFactory(FactoryDecorator):
    """Decorator that adds YouTube API fetching to ViewsBreakdown factory."""
    
    def __init__(self, factory: Factory, api_client: 'YouTubeAPIClient'):
        """Initialize with wrapped factory and API client.
        
        Args:
            factory: The ViewsBreakdown factory to wrap
            api_client: YouTube API client for fetching data
        """
        super().__init__(factory)
        self.api_client = api_client
    
    def create(self, 
               start_date: Optional[str] = None,
               end_date: Optional[str] = None,
               **kwargs) -> Any:
        """Create ViewsBreakdown, fetching from API if data not provided.
        
        If total_views is not in kwargs and dates are provided, fetches
        views breakdown from YouTube API. Otherwise delegates to wrapped factory.
        
        Args:
            start_date: Start date for API query (ISO format)
            end_date: End date for API query (ISO format)
            **kwargs: Arguments for creating ViewsBreakdown
            
        Returns:
            ViewsBreakdown instance
        """
        # If data already provided, just delegate
        if 'total_views' in kwargs:
            return self.factory.create(**kwargs)
        
        # Need dates to fetch from API
        if not start_date or not end_date:
            return self.factory.create(**kwargs)
        
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
        
        # Delegate to wrapped factory with fetched data
        return self.factory.create(**kwargs)