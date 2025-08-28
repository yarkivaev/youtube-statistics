"""YouTube content type value object for YouTube content classification."""


class YouTubeContentType:
    """Types of content on YouTube."""
    VIDEO = "video"
    SHORTS = "shorts"
    LIVE_STREAM = "live_stream"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_api_value(cls, value: str) -> str:
        """Map YouTube API values to YouTubeContentType."""
        mapping = {
            'VIDEO_TYPE_UPLOADED': cls.VIDEO,
            'videoOnDemand': cls.VIDEO,
            'LONG_FORM': cls.VIDEO,
            'VIDEO_TYPE_SHORTS': cls.SHORTS,
            'shorts': cls.SHORTS,
            'SHORTS': cls.SHORTS,
            'SHORT_FORM': cls.SHORTS,
            'LIVE_STREAM': cls.LIVE_STREAM
        }
        return mapping.get(value, cls.UNKNOWN)