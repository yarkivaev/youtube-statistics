"""Google Sheets Exported wrapper for Channel model."""

from domain import Channel
from ..base import Report


class ChannelSheetsReport(Report):
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