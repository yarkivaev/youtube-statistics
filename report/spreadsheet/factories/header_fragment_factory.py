"""Header fragment factory for creating spreadsheet header fragments."""

from typing import List, Dict
from domain import Factory, FactoryDecorator
from ..spreadsheet_fragment import SpreadsheetFragment
from ..formatted_spreadsheet_fragment import FormattedSpreadsheetFragment, CellFormat, RangeFormat


class HeaderFragmentFactory(FactoryDecorator):
    """Factory decorator for creating header row fragments.
    
    Decorates a base factory to add header fragment creation capabilities.
    """
    
    def __init__(self, factory: Factory):
        """Initialize with a factory to decorate.
        
        Args:
            factory: The base factory to wrap (typically SpreadsheetFragmentFactory)
        """
        super().__init__(factory)
    
    def create(self, **kwargs) -> SpreadsheetFragment:
        """Create header fragment with formatting.
        
        Args:
            **kwargs: Must include:
                - months: List of month keys (YYYY-MM format)
                - month_names_ru: Russian month names mapping
            
        Returns:
            Formatted SpreadsheetFragment with header rows
        """
        months = kwargs.get('months', [])
        month_names_ru = kwargs.get('month_names_ru', {})
        
        # Use the wrapped factory to create base fragment
        fragment = self.factory.create()
        
        # Row 1: MM header
        row1 = ['MM'] + ['', '', ''] * len(months)
        fragment = fragment.with_row(row1)
        
        # Row 2: Month headers
        row2 = ['']
        for month_key in months:
            year, month = map(int, month_key.split('-'))
            month_name = month_names_ru.get(month, str(month))
            month_header = f"{month_name}. {year}"
            row2.extend([month_header, '', ''])
        fragment = fragment.with_row(row2)
        
        # Apply header formatting
        formats = []
        
        # Bold first two rows (MM and month headers)
        if len(fragment.rows) >= 2:
            num_cols = max(len(row) for row in fragment.rows) if fragment.rows else 0
            formats.append(RangeFormat(0, 0, 0, num_cols - 1, CellFormat(bold=True, font_size=11)))
            formats.append(RangeFormat(1, 0, 1, num_cols - 1, CellFormat(
                bold=True, 
                font_size=10,
                horizontal_align="center",
                background_color="#E8F0FE"
            )))
        
        # Bold first column (metric names)
        num_rows = len(fragment.rows)
        formats.append(RangeFormat(0, 0, num_rows - 1, 0, CellFormat(bold=True)))
        
        return FormattedSpreadsheetFragment(fragment, formats)