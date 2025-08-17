"""YouTube API decorator for Channel factory."""

from typing import TYPE_CHECKING, Any
from models.factories.base import FactoryDecorator, Factory

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeChannelFactory(FactoryDecorator):
    """Decorator that adds YouTube API fetching to Channel factory."""
    
    def __init__(self, factory: Factory, api_client: 'YouTubeAPIClient'):
        """Initialize with wrapped factory and API client.
        
        Args:
            factory: The Channel factory to wrap
            api_client: YouTube API client for fetching data
        """
        super().__init__(factory)
        self.api_client = api_client
    
    def create(self, **kwargs) -> Any:
        """Create Channel, fetching from API if data not provided.
        
        If video_count is not in kwargs, fetches channel statistics
        from YouTube API. Otherwise delegates to wrapped factory.
        
        Args:
            **kwargs: Arguments for creating Channel
            
        Returns:
            Channel instance
        """
        # If data already provided, just delegate
        if 'video_count' in kwargs:
            return self.factory.create(**kwargs)
        
        # Fetch from YouTube API
        youtube_data = self.api_client.get_data_service()
        
        try:
            request = youtube_data.channels().list(
                part="statistics,contentDetails",
                mine=True
            )
            response = self.api_client.execute_request(request)
            
            if response and response.get('items'):
                stats = response['items'][0]['statistics']
                kwargs['video_count'] = int(stats.get('videoCount', 0))
                kwargs['subscriber_count'] = int(stats.get('subscriberCount', 0))
                kwargs['total_view_count'] = int(stats.get('viewCount', 0))
            else:
                # No channel data found
                kwargs['video_count'] = 0
                kwargs['subscriber_count'] = 0
                kwargs['total_view_count'] = 0
        except Exception as e:
            print(f"Error fetching channel statistics: {e}")
            # Set defaults on error
            kwargs['video_count'] = 0
            kwargs['subscriber_count'] = 0
            kwargs['total_view_count'] = 0
        
        # Delegate to wrapped factory with fetched data
        return self.factory.create(**kwargs)