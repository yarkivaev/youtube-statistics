"""Daily metrics domain entity."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal


class ContentType:
    """Types of content on YouTube."""
    VIDEO = "video"
    SHORTS = "shorts"
    LIVE_STREAM = "live_stream"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_api_value(cls, value: str) -> str:
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
class DailyMetrics:
    """Metrics for a single day including revenue data."""
    
    date: date
    views: int
    watch_time_minutes: int
    average_view_duration_seconds: int
    subscribers_gained: int
    subscribers_lost: int
    content_type: Optional[str] = None
    # Revenue fields
    estimated_revenue: Decimal = Decimal('0')
    ad_revenue: Decimal = Decimal('0')
    red_partner_revenue: Decimal = Decimal('0')
    
    @property
    def net_subscribers(self) -> int:
        """Calculate net subscribers for the day."""
        return self.subscribers_gained - self.subscribers_lost
    
    @property
    def has_activity(self) -> bool:
        """Check if there was any activity on this day."""
        return self.views > 0 or self.subscribers_gained > 0 or self.subscribers_lost > 0
    
    def export(self) -> dict:
        """Export DailyMetrics to dictionary."""
        result = {
            'date': self.date.isoformat(),
            'views': self.views,
            'watch_time_minutes': self.watch_time_minutes,
            'average_view_duration_seconds': self.average_view_duration_seconds,
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost,
            'estimated_revenue': float(self.estimated_revenue),
            'ad_revenue': float(self.ad_revenue),
            'red_partner_revenue': float(self.red_partner_revenue)
        }
        
        if self.content_type:
            result['content_type'] = self.content_type
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            'date': self.date.isoformat(),
            'views': self.views,
            'watch_time_minutes': self.watch_time_minutes,
            'average_view_duration_seconds': self.average_view_duration_seconds,
            'subscribers_gained': self.subscribers_gained,
            'subscribers_lost': self.subscribers_lost,
            'content_type': self.content_type,
            'estimated_revenue': float(self.estimated_revenue),
            'ad_revenue': float(self.ad_revenue),
            'red_partner_revenue': float(self.red_partner_revenue)
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