"""Exported wrapper for Channel model."""

from models import Channel
from ..base import Report


class ChannelReport(Report):
    """Exported wrapper for Channel model."""
    
    def __init__(self, channel: Channel):
        """Initialize with Channel instance."""
        super().__init__(channel)
    
    def export(self) -> dict:
        """Export Channel to dictionary."""
        return {
            'video_count': self.video_count,
            'subscriber_count': self.subscriber_count,
            'total_view_count': self.total_view_count,
            'advertiser_count': self.advertiser_count,
            'integrations': self.integrations
        }