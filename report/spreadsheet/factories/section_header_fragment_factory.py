"""Section header fragment factory for creating section header fragments."""

from models.factories.base import Factory, FactoryDecorator
from ..spreadsheet_fragment import SpreadsheetFragment
from ..formatted_spreadsheet_fragment import FormattedSpreadsheetFragment, CellFormat, RangeFormat


class SectionHeaderFragmentFactory(FactoryDecorator):
    """Factory decorator for creating section header fragments.
    
    Decorates a base factory to add section header fragment creation capabilities.
    """
    
    def __init__(self, factory: Factory):
        """Initialize with a factory to decorate.
        
        Args:
            factory: The base factory to wrap (typically SpreadsheetFragmentFactory)
        """
        super().__init__(factory)
    
    def create(self, **kwargs) -> SpreadsheetFragment:
        """Create section header fragment with formatting.
        
        Args:
            **kwargs: Must include:
                - title: Section title
                - num_months: Number of months (for column span)
            
        Returns:
            Formatted SpreadsheetFragment with section header
        """
        title = kwargs.get('title', '')
        num_months = kwargs.get('num_months', 0)
        
        # Use the wrapped factory to create base fragment
        fragment = self.factory.create()
        row = [title] + ['', '', ''] * num_months
        fragment = fragment.with_row(row)
        
        # Apply section header formatting
        formats = []
        
        # Bold and background color for section headers
        if fragment.rows:
            num_cols = max(len(row) for row in fragment.rows) if fragment.rows else 0
            formats.append(RangeFormat(0, 0, 0, num_cols - 1, CellFormat(
                bold=True,
                font_size=11,
                background_color="#F5F5F5"
            )))
        
        return FormattedSpreadsheetFragment(fragment, formats)