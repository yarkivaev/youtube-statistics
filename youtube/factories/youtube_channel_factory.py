"""YouTube API factory for Channel."""

from typing import TYPE_CHECKING
from domain import Channel, Factory

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeChannelFactory(Factory):
    """Factory that fetches channel data from YouTube API."""
    
    def __init__(self, api_client: 'YouTubeAPIClient'):
        """Initialize with API client.
        
        Args:
            api_client: YouTube API client for fetching data
        """
        self.api_client = api_client
    
    def create(self, **kwargs) -> Channel:
        """Create Channel, fetching from API if data not provided.
        
        If video_count is not in kwargs, fetches channel statistics
        from YouTube API. Otherwise creates Channel directly.
        
        Args:
            **kwargs: Arguments for creating Channel
            
        Returns:
            Channel instance
        """
        # If data already provided, just create directly
        if 'video_count' in kwargs:
            return Channel(**kwargs)
        
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
                # Set defaults for optional fields
                kwargs.setdefault('advertiser_count', 0)
                kwargs.setdefault('integrations', '')
            else:
                # No channel data found
                kwargs['video_count'] = 0
                kwargs['subscriber_count'] = 0
                kwargs['total_view_count'] = 0
                kwargs['advertiser_count'] = 0
                kwargs['integrations'] = ''
        except Exception as e:
            print(f"Error fetching channel statistics: {e}")
            # Set defaults on error
            kwargs['video_count'] = 0
            kwargs['subscriber_count'] = 0
            kwargs['total_view_count'] = 0
            kwargs['advertiser_count'] = 0
            kwargs['integrations'] = ''
        
        # Create Channel with fetched data
        return Channel(**kwargs)