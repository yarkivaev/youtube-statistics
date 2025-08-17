"""Factory for creating ViewsBreakdown with optional export decorator."""

from typing import Optional, Type
from models import ViewsBreakdown
from ..base import Exported


class ViewsBreakdownFactory:
    """Factory for creating ViewsBreakdown with optional export decorator."""
    
    def __init__(self, exported_class: Optional[Type[Exported]] = None):
        """Initialize with optional decorator class."""
        self.exported_class = exported_class
    
    def create(self, total_views: int, video_views: int,
               shorts_views: int, live_stream_views: int = 0):
        """Create ViewsBreakdown instance with configured decorator.
        
        Returns:
            ViewsBreakdown or ViewsBreakdownExported instance
        """
        breakdown = ViewsBreakdown(
            total_views=total_views,
            video_views=video_views,
            shorts_views=shorts_views,
            live_stream_views=live_stream_views
        )
        
        if self.exported_class:
            return self.exported_class(breakdown)
        return breakdown