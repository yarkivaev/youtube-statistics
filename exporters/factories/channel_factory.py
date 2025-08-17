"""Factory for creating Channel instances with optional export decorator."""

from typing import Optional, Type
from models import Channel
from ..base import Exported


class ChannelFactory:
    """Factory for creating Channel instances with optional export decorator."""
    
    def __init__(self, exported_class: Optional[Type[Exported]] = None):
        """Initialize with optional decorator class.
        
        Args:
            exported_class: Decorator class to apply, or None for no decoration
        """
        self.exported_class = exported_class
    
    def create(self, video_count: int, subscriber_count: int,
               total_view_count: int, advertiser_count: Optional[int] = None,
               integrations: Optional[str] = None):
        """Create Channel instance with configured decorator.
        
        Returns:
            Channel or ChannelExported instance
        """
        channel = Channel(
            video_count=video_count,
            subscriber_count=subscriber_count,
            total_view_count=total_view_count,
            advertiser_count=advertiser_count,
            integrations=integrations
        )
        
        if self.exported_class:
            return self.exported_class(channel)
        return channel