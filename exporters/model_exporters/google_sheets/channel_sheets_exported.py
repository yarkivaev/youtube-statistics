"""Google Sheets Exported wrapper for Channel model."""

from models import Channel
from ...base import Exported


class ChannelSheetsExported(Exported):
    """Google Sheets exporter for Channel model."""
    
    def __init__(self, channel: Channel):
        """Initialize with Channel instance."""
        super().__init__(channel)
    
    def export(self) -> dict:
        """Export Channel to dictionary for Google Sheets.
        
        Returns:
            Dictionary with channel data formatted for sheets
        """
        return {
            'Channel ID': self.channel_id,
            'Channel Name': self.name,
            'Video Count': self.video_count,
            'Subscriber Count': self.subscriber_count
        }