"""Pure factory for creating ViewsBreakdown instances."""

from models import ViewsBreakdown
from .base import Factory


class ViewsBreakdownFactory(Factory):
    """Factory for creating ViewsBreakdown instances from provided data."""
    
    def create(self,
               total_views: int = 0,
               video_views: int = 0,
               shorts_views: int = 0,
               live_stream_views: int = 0,
               **kwargs) -> ViewsBreakdown:
        """Create ViewsBreakdown instance from provided data.
        
        Args:
            total_views: Total number of views
            video_views: Views from regular videos
            shorts_views: Views from shorts
            live_stream_views: Views from live streams
            **kwargs: Additional arguments (ignored)
            
        Returns:
            ViewsBreakdown instance
        """
        return ViewsBreakdown(
            total_views=total_views,
            video_views=video_views,
            shorts_views=shorts_views,
            live_stream_views=live_stream_views
        )