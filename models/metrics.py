"""Metrics-related domain entities."""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class ContentType(Enum):
    """Types of content on YouTube."""
    VIDEO = "video"
    SHORTS = "shorts"
    LIVE_STREAM = "live_stream"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_api_value(cls, value: str) -> 'ContentType':
        """Map API values to ContentType."""
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


@dataclass
class DateRange:
    """Represents a date range."""
    start_date: date
    end_date: date
    
    def __str__(self) -> str:
        return f"{self.start_date.isoformat()} to {self.end_date.isoformat()}"
    
    def to_dict(self) -> dict:
        return {
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }


@dataclass
class SubscriptionMetrics:
    """Subscription-related metrics for a period."""
    
    subscribers_gained: int
    subscribers_lost: int
    period: DateRange
    
    @property
    def net_change(self) -> int:
        """Calculate net change in subscribers."""
        return self.subscribers_gained - self.subscribers_lost
    
    @property
    def change_percentage(self) -> float:
        """Calculate percentage change."""
        if self.subscribers_gained == 0:
            return 0.0
        return round((self.net_change / self.subscribers_gained) * 100, 2)
    
    @property
    def has_growth(self) -> bool:
        """Check if there's positive growth."""
        return self.net_change > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost,
            'net_change': self.net_change,
            'change_percentage': self.change_percentage,
            'period': self.period.to_dict()
        }


@dataclass
class ViewsBreakdown:
    """Breakdown of views by content type."""
    
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
        """Calculate percentage of shorts views."""
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


@dataclass
class DailyMetrics:
    """Metrics for a single day."""
    
    date: date
    views: int
    watch_time_minutes: int
    average_view_duration_seconds: int
    subscribers_gained: int
    subscribers_lost: int
    content_type: Optional[ContentType] = None
    
    @property
    def net_subscribers(self) -> int:
        """Calculate net subscribers for the day."""
        return self.subscribers_gained - self.subscribers_lost
    
    @property
    def has_activity(self) -> bool:
        """Check if there was any activity on this day."""
        return self.views > 0 or self.subscribers_gained > 0 or self.subscribers_lost > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'date': self.date.isoformat(),
            'views': self.views,
            'watch_time_minutes': self.watch_time_minutes,
            'average_view_duration_seconds': self.average_view_duration_seconds,
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost,
            'content_type': self.content_type.value if self.content_type else None
        }
    
    @classmethod
    def from_api_row(cls, row: List, with_content_type: bool = False) -> 'DailyMetrics':
        """Create DailyMetrics from API response row."""
        base_metrics = cls(
            date=datetime.strptime(row[0], '%Y-%m-%d').date(),
            views=row[1],
            watch_time_minutes=row[2] if not with_content_type else row[2],
            average_view_duration_seconds=row[3] if not with_content_type else 0,
            subscribers_gained=row[4] if not with_content_type and len(row) > 4 else 0,
            subscribers_lost=row[5] if not with_content_type and len(row) > 5 else 0
        )
        
        if with_content_type and len(row) > 1:
            base_metrics.content_type = ContentType.from_api_value(row[1])
            base_metrics.views = row[2] if len(row) > 2 else 0
            base_metrics.watch_time_minutes = row[3] if len(row) > 3 else 0
        
        return base_metrics