"""Geographic metrics domain entity."""

from dataclasses import dataclass
from typing import Optional, Dict


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
    views: Optional[int] = None
    watch_time_minutes: Optional[int] = None
    subscribers_gained: Optional[int] = None
    
    @property
    def country_name(self) -> str:
        """Get localized country name."""
        return COUNTRY_NAMES.get(self.country_code, self.country_code)
    
    @property
    def has_views_data(self) -> bool:
        """Check if this entry has views data."""
        return self.views is not None and self.views > 0
    
    @property
    def has_subscriber_data(self) -> bool:
        """Check if this entry has subscriber data."""
        return self.subscribers_gained is not None and self.subscribers_gained > 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        result = {
            'country_code': self.country_code,
            'country_name': self.country_name
        }
        
        if self.views is not None:
            result['views'] = self.views
        if self.watch_time_minutes is not None:
            result['watch_time_minutes'] = self.watch_time_minutes
        if self.subscribers_gained is not None:
            result['subscribers_gained'] = self.subscribers_gained
            
        return result
    
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