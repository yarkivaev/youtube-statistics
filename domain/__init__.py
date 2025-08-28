"""Domain layer for social media analytics.

This package contains domain entities and value objects for various social platforms.
Currently supports YouTube with architecture ready for other platforms.
"""

# Import from common
from domain.common import (
    DateRange,
    GeographicMetrics,
    Factory,
    FactoryDecorator
)

# Import from YouTube domain
from domain.youtube import (
    YouTubeChannel,
    YouTubeDailyMetrics,
    YouTubeMonthlyMetrics,
    YouTubeRevenueMetrics,
    YouTubeMetrics,
    YouTubeContentType,
    YouTubeSubscriptionMetrics,
    YouTubeViewsBreakdown,
    YouTubeMonthlyMetricsFactory,
    COUNTRY_NAMES
)

# Temporary backward compatibility aliases
# These will be removed in future versions
Channel = YouTubeChannel
DailyMetrics = YouTubeDailyMetrics
MonthlyMetrics = YouTubeMonthlyMetrics
RevenueMetrics = YouTubeRevenueMetrics
YouTubeMetrics = YouTubeMetrics
ContentType = YouTubeContentType
SubscriptionMetrics = YouTubeSubscriptionMetrics
ViewsBreakdown = YouTubeViewsBreakdown
MonthlyMetricsFactory = YouTubeMonthlyMetricsFactory

__all__ = [
    # Common entities
    'DateRange',
    'GeographicMetrics',
    'Factory',
    'FactoryDecorator',
    # YouTube entities (new names)
    'YouTubeChannel',
    'YouTubeDailyMetrics',
    'YouTubeMonthlyMetrics',
    'YouTubeRevenueMetrics',
    'YouTubeMetrics',
    'YouTubeContentType',
    'YouTubeSubscriptionMetrics',
    'YouTubeViewsBreakdown',
    'YouTubeMonthlyMetricsFactory',
    # Backward compatibility (old names)
    'Channel',
    'DailyMetrics',
    'MonthlyMetrics',
    'RevenueMetrics',
    'ContentType',
    'SubscriptionMetrics',
    'ViewsBreakdown',
    'MonthlyMetricsFactory',
    # Constants
    'COUNTRY_NAMES'
]