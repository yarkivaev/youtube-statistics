"""YouTube subscription-related metrics value object."""

from dataclasses import dataclass
from domain.common.entities.date_range import DateRange


@dataclass
class YouTubeSubscriptionMetrics:
    """YouTube subscription-related metrics for a period."""
    
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