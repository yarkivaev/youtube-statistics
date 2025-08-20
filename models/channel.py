"""Channel domain entity."""

from dataclasses import dataclass


@dataclass
class Channel:
    """Represents a YouTube channel with its core statistics."""
    
    video_count: int
    subscriber_count: int
    total_view_count: int
    advertiser_count: int = 0
    integrations: str = ''
    
    def calculate_avg_views_per_video(self) -> float:
        """Calculate average views per video."""
        if self.video_count == 0:
            return 0.0
        return self.total_view_count / self.video_count
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'video_count': self.video_count,
            'subscriber_count': self.subscriber_count,
            'total_view_count': self.total_view_count,
            'advertiser_count': self.advertiser_count,
            'integrations': self.integrations
        }
    
    @classmethod
    def from_api_response(cls, stats: dict) -> 'Channel':
        """Create Channel instance from YouTube API response."""
        return cls(
            video_count=int(stats.get('videoCount', 0)),
            subscriber_count=int(stats.get('subscriberCount', 0)),
            total_view_count=int(stats.get('viewCount', 0))
        )