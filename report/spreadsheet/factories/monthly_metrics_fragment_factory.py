"""Monthly metrics fragment factory for creating metrics data fragments."""

from typing import List, Dict, Any
from domain import Factory, FactoryDecorator
from ..spreadsheet_fragment import SpreadsheetFragment
from ..formatted_spreadsheet_fragment import FormattedSpreadsheetFragment, CellFormat, RangeFormat


class MonthlyMetricsFragmentFactory(FactoryDecorator):
    """Factory decorator for creating monthly metrics fragments.
    
    Decorates a base factory to add monthly metrics fragment creation capabilities.
    """
    
    def __init__(self, factory: Factory):
        """Initialize with a factory to decorate.
        
        Args:
            factory: The base factory to wrap (typically SpreadsheetFragmentFactory)
        """
        super().__init__(factory)
    
    def create(self, **kwargs) -> SpreadsheetFragment:
        """Create monthly metrics fragment with formatting.
        
        Args:
            **kwargs: Must include:
                - monthly_data: Dictionary with month keys and metric values
                - months: Sorted list of month keys
                - channel: Optional Channel object with initial subscriber count
            
        Returns:
            Formatted SpreadsheetFragment with metrics data
        """
        monthly_data = kwargs.get('monthly_data', {})
        months = kwargs.get('months', [])
        channel = kwargs.get('channel')
        
        # Use the wrapped factory to create base fragment
        fragment = self.factory.create()
        
        # Views row
        row_views = ['Просмотры']
        for month_key in months:
            views = monthly_data.get(month_key, {}).get('views', 0)
            row_views.extend([str(views), '', ''])
        fragment = fragment.with_row(row_views)
        
        # Watch time row
        row_watch = ['Время просмотра (часы)']
        for month_key in months:
            minutes = monthly_data.get(month_key, {}).get('watch_time_minutes', 0)
            hours = round(minutes / 60, 1)
            row_watch.extend([str(hours), '', ''])
        fragment = fragment.with_row(row_watch)
        
        # Subscribers gained row
        row_gained = ['Новые подписчики']
        for month_key in months:
            gained = monthly_data.get(month_key, {}).get('subscribers_gained', 0)
            row_gained.extend([str(gained), '', ''])
        fragment = fragment.with_row(row_gained)
        
        # Subscribers lost row
        row_lost = ['Потерянные подписчики']
        for month_key in months:
            lost = monthly_data.get(month_key, {}).get('subscribers_lost', 0)
            row_lost.extend([str(lost), '', ''])
        fragment = fragment.with_row(row_lost)
        
        # Net change row
        row_net = ['Чистый прирост']
        for month_key in months:
            gained = monthly_data.get(month_key, {}).get('subscribers_gained', 0)
            lost = monthly_data.get(month_key, {}).get('subscribers_lost', 0)
            net = gained - lost
            row_net.extend([f"{net:+d}" if net != 0 else "0", '', ''])
        fragment = fragment.with_row(row_net)
        
        # Total subscribers row - calculate cumulative total
        row_total_subs = ['Количество подписчиков']
        # Start with initial subscriber count from channel if available
        cumulative_subs = channel.subscriber_count if channel else 0
        for month_key in months:
            gained = monthly_data.get(month_key, {}).get('subscribers_gained', 0)
            lost = monthly_data.get(month_key, {}).get('subscribers_lost', 0)
            cumulative_subs += (gained - lost)
            row_total_subs.extend([str(cumulative_subs), '', ''])
        fragment = fragment.with_row(row_total_subs)
        
        # Apply metrics formatting
        formats = []
        
        # Bold first column (metric names)
        num_rows = len(fragment.rows)
        formats.append(RangeFormat(0, 0, num_rows - 1, 0, CellFormat(bold=True)))
        
        # Number format for data columns
        num_cols = max(len(row) for row in fragment.rows) if fragment.rows else 0
        for col in range(1, num_cols):
            formats.append(RangeFormat(0, col, num_rows - 1, col, CellFormat(
                number_format="#,##0",
                horizontal_align="right"
            )))
        
        return FormattedSpreadsheetFragment(fragment, formats)