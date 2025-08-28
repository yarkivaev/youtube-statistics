"""YouTube views breakdown value object."""

from dataclasses import dataclass


@dataclass
class YouTubeViewsBreakdown:
    """Breakdown of YouTube views by content type."""
    
    total_views: int
    video_views: int
    shorts_views: int
    live_stream_views: int = 0
    
    @property
    def video_percentage(self) -> float:
        """Calculate percentage of video views."""
        if self.total_views == 0:
            return 0.0
        return round((self.video_views / self.total_views) * 100, 2)
    
    @property
    def shorts_percentage(self) -> float:
        """Calculate percentage of YouTube Shorts views."""
        if self.total_views == 0:
            return 0.0
        return round((self.shorts_views / self.total_views) * 100, 2)
    
    @property
    def live_percentage(self) -> float:
        """Calculate percentage of live stream views."""
        if self.total_views == 0:
            return 0.0
        return round((self.live_stream_views / self.total_views) * 100, 2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'total_views': self.total_views,
            'video_views': self.video_views,
            'shorts_views': self.shorts_views,
            'live_stream_views': self.live_stream_views,
            'video_percentage': self.video_percentage,
            'shorts_percentage': self.shorts_percentage,
            'live_percentage': self.live_percentage
        }