"""Spreadsheet fragment factory."""

from domain import Factory
from ..spreadsheet_fragment import SpreadsheetFragment


class SpreadsheetFragmentFactory(Factory):
    """Factory for creating spreadsheet fragments.
    
    This serves as the base factory that fragment decorators can wrap.
    """
    
    def create(self, **kwargs) -> SpreadsheetFragment:
        """Create an empty spreadsheet fragment.
        
        Args:
            **kwargs: Optional initialization parameters
            
        Returns:
            Empty SpreadsheetFragment instance
        """
        return SpreadsheetFragment()