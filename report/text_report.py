"""Text Report implementation."""

from typing import Dict, Any, List
from .base import Report


class TextReport(Report):
    """Export dictionary to formatted text using decorator pattern."""
    
    def __init__(self, data: Dict[str, Any], language: str = 'ru'):
        """Initialize text exporter with a dictionary.
        
        Args:
            data: Dictionary to export as text
            language: Language for the report ('ru' or 'en')
        """
        super().__init__(data)
        self.data = data
        self.language = language
    
    def export(self) -> str:
        """Export dictionary to formatted text string.
        
        Returns:
            Formatted text report
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("YouTube Analytics Report")
        
        # Period if available
        if 'period' in self.data:
            period = self.data['period']
            lines.append(f"Period: {period.get('start_date', 'N/A')} to {period.get('end_date', 'N/A')}")
        
        # Generated time
        if 'generated_at' in self.data:
            lines.append(f"Generated: {self.data['generated_at']}")
        
        lines.append("=" * 60)
        lines.append("")
        
        # Channel metrics
        if 'channel' in self.data:
            self._add_channel_section(lines, self.data['channel'])
        
        # Subscription dynamics
        if 'subscription_metrics' in self.data:
            self._add_subscription_section(lines, self.data['subscription_metrics'])
        
        # Views breakdown
        if 'views_breakdown' in self.data:
            self._add_views_section(lines, self.data['views_breakdown'])
        
        # Revenue
        self._add_revenue_section(lines, self.data.get('revenue_metrics'))
        
        # Geographic views
        if 'geographic_views' in self.data:
            self._add_geographic_views_section(lines, self.data['geographic_views'])
        
        # Geographic subscribers
        if 'geographic_subscribers' in self.data:
            self._add_geographic_subscribers_section(lines, self.data['geographic_subscribers'])
        
        # Summary statistics
        if 'daily_metrics' in self.data:
            self._add_summary_section(lines, self.data)
        
        return "\n".join(lines)
    
    def _add_channel_section(self, lines: List[str], channel: Dict[str, Any]) -> None:
        """Add channel metrics section."""
        lines.append("CHANNEL METRICS:")
        lines.append(f"Количество роликов: {channel.get('video_count', 0)}")
        
        advertiser_count = channel.get('advertiser_count')
        if advertiser_count is not None:
            lines.append(f"Количество рекламодателей: {advertiser_count}")
        else:
            lines.append("Количество рекламодателей: [Требуется ручной ввод]")
        
        integrations = channel.get('integrations')
        if integrations:
            lines.append(f"Интеграции: {integrations}")
        else:
            lines.append("Интеграции Ghost Writer или Школьных продуктов: [Требуется ручной ввод]")
        lines.append("")
    
    def _add_subscription_section(self, lines: List[str], metrics: Dict[str, Any]) -> None:
        """Add subscription dynamics section."""
        lines.append("SUBSCRIPTION DYNAMICS:")
        lines.append(f"Количество новых подписок: {metrics.get('subscribers_gained', 0)}")
        lines.append(f"Количество отписок: {metrics.get('subscribers_lost', 0)}")
        
        net_change = metrics.get('net_change', 0)
        sign = '+' if net_change >= 0 else ''
        lines.append(f"Динамика подписок: {sign}{net_change}")
        
        change_percentage = metrics.get('change_percentage', 0)
        sign = '+' if change_percentage >= 0 else ''
        lines.append(f"Динамика подписок, %: {sign}{change_percentage}%")
        lines.append("")
    
    def _add_views_section(self, lines: List[str], breakdown: Dict[str, Any]) -> None:
        """Add views breakdown section."""
        lines.append("VIEWS BREAKDOWN:")
        lines.append(f"Количество просмотров, total: {breakdown.get('total_views', 0)}")
        lines.append(f"Количество просмотров, videos: {breakdown.get('video_views', 0)}")
        lines.append(f"Количество просмотров, shorts: {breakdown.get('shorts_views', 0)}")
        
        video_pct = breakdown.get('video_percentage', 0)
        shorts_pct = breakdown.get('shorts_percentage', 0)
        lines.append(f"Соотношение: {video_pct}% videos vs. {shorts_pct}% shorts")
        lines.append("")
    
    def _add_revenue_section(self, lines: List[str], revenue: Dict[str, Any] = None) -> None:
        """Add revenue section."""
        lines.append("REVENUE:")
        if revenue and revenue.get('has_revenue'):
            total_revenue = revenue.get('total_revenue', 0)
            lines.append(f"AdSense: ${total_revenue:.2f}")
        else:
            lines.append("AdSense: [Данные недоступны - требуется интеграция AdSense]")
        lines.append("")
    
    def _add_geographic_views_section(self, lines: List[str], geo_list: List[Dict[str, Any]]) -> None:
        """Add geographic views section."""
        if not geo_list:
            return
        
        lines.append("ГЕОГРАФИЯ ПРОСМОТРОВ (TOP 9):")
        for i, geo in enumerate(geo_list[:9], 1):
            country = self._format_country(geo.get('country_code', geo.get('country_name', 'Unknown')))
            views = geo.get('views', 0)
            lines.append(f"География, топ-{i}: {country} - {views} просмотров")
        lines.append("")
    
    def _add_geographic_subscribers_section(self, lines: List[str], geo_list: List[Dict[str, Any]]) -> None:
        """Add geographic subscribers section."""
        if not geo_list:
            return
        
        lines.append("ГЕОГРАФИЯ ПОДПИСЧИКОВ (TOP 5):")
        for i, geo in enumerate(geo_list[:5], 1):
            country = self._format_country(geo.get('country_code', geo.get('country_name', 'Unknown')))
            subscribers = geo.get('subscribers_gained', 0)
            lines.append(f"топ-{i}: {country} - {subscribers} подписчиков")
        lines.append("")
    
    def _add_summary_section(self, lines: List[str], data: Dict[str, Any]) -> None:
        """Add summary statistics section."""
        lines.append("SUMMARY STATISTICS:")
        
        total_watch_hours = data.get('total_watch_time_hours', 0)
        lines.append(f"Total watch time: {total_watch_hours:.2f} hours")
        
        active_days = data.get('active_days_count', 0)
        lines.append(f"Active days: {active_days}")
        
        # Calculate average views per video if possible
        if 'channel' in data:
            channel = data['channel']
            video_count = channel.get('video_count', 0)
            total_views = channel.get('total_view_count', 0)
            if video_count > 0:
                avg_views = total_views / video_count
                lines.append(f"Average views per video: {avg_views:.2f}")
    
    def _format_country(self, code: str) -> str:
        """Format country code to readable name."""
        if self.language == 'ru':
            country_map = {
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
                'SE': 'Швеция'
            }
            return country_map.get(code, code)
        return code