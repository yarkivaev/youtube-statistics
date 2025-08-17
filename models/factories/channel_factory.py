"""Pure factory for creating Channel instances."""

from typing import Optional
from models import Channel
from .base import Factory


class ChannelFactory(Factory):
    """Factory for creating Channel instances from provided data."""
    
    def create(self, 
               video_count: int = 0,
               subscriber_count: int = 0,
               total_view_count: int = 0,
               advertiser_count: Optional[int] = None,
               integrations: Optional[str] = None,
               **kwargs) -> Channel:
        """Create Channel instance from provided data.
        
        Args:
            video_count: Number of videos
            subscriber_count: Number of subscribers
            total_view_count: Total views
            advertiser_count: Number of advertisers (optional)
            integrations: Integration details (optional)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            Channel instance
        """
        return Channel(
            video_count=video_count,
            subscriber_count=subscriber_count,
            total_view_count=total_view_count,
            advertiser_count=advertiser_count,
            integrations=integrations
        )