"""Geographic metrics domain entity."""

from dataclasses import dataclass
from typing import Dict


# Country code to name mapping (class level constant)
COUNTRY_NAMES = {
        'US': 'США',
        'RU': 'Россия',
        'GB': 'Великобритания',
        'DE': 'Германия',
        'FR': 'Франция',
        'JP': 'Япония',
        'CN': 'Китай',
        'IN': 'Индия',
        'BR': 'Бразилия',
        'CA': 'Канада',
        'AU': 'Австралия',
        'IT': 'Италия',
        'ES': 'Испания',
        'MX': 'Мексика',
        'KR': 'Южная Корея',
        'UA': 'Украина',
        'PL': 'Польша',
        'NL': 'Нидерланды',
        'TR': 'Турция',
        'SE': 'Швеция',
        'AR': 'Аргентина',
        'ID': 'Индонезия',
        'TH': 'Таиланд',
        'VN': 'Вьетнам',
        'PH': 'Филиппины',
        'EG': 'Египет',
        'SA': 'Саудовская Аравия',
        'AE': 'ОАЭ',
        'IL': 'Израиль',
        'ZA': 'Южная Африка'
}


@dataclass
class GeographicMetrics:
    """Geographic distribution of metrics."""
    
    country_code: str
    views: int = 0
    watch_time_minutes: int = 0
    subscribers_gained: int = 0
    
    @property
    def country_name(self) -> str:
        """Get localized country name."""
        return COUNTRY_NAMES.get(self.country_code, self.country_code)
    
    def export(self) -> dict:
        """Export GeographicMetrics to dictionary."""
        result = {
            'country_code': self.country_code,
            'country_name': self.country_name
        }
        
        result['views'] = self.views
        result['watch_time_minutes'] = self.watch_time_minutes
        result['subscribers_gained'] = self.subscribers_gained
        # Calculate percentage if we can
        result['percentage'] = 0.0  # Would need total to calculate
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return self.export()
    
    @classmethod
    def from_views_data(cls, country_code: str, views: int, 
                       watch_time: int) -> 'GeographicMetrics':
        """Create instance from views data."""
        return cls(
            country_code=country_code,
            views=views,
            watch_time_minutes=watch_time
        )
    
    @classmethod
    def from_subscriber_data(cls, country_code: str, 
                           subscribers: int) -> 'GeographicMetrics':
        """Create instance from subscriber data."""
        return cls(
            country_code=country_code,
            subscribers_gained=subscribers
        )