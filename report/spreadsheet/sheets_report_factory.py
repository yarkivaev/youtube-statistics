"""Generic factory wrapper for Google Sheets export functionality."""

from domain import Factory
from typing import Any, Type


class SheetsReportFactory(Factory):
    """Generic factory wrapper that adds Google Sheets export capability.
    
    This factory wraps any base factory and applies a sheets report wrapper
    to its output, enabling Google Sheets export functionality.
    """
    
    def __init__(self, 
                 base_factory: Factory,
                 wrapper_class: Type,
                 spreadsheet_id: str,
                 sheet_name: str = 'Sheet1'):
        """Initialize sheets report factory.
        
        Args:
            base_factory: Any factory that produces data/models
            wrapper_class: The report wrapper class to use (e.g., YoutubeMetricsSheetsReport)
            spreadsheet_id: Google Sheets ID for export
            sheet_name: Name of the sheet to create/update
        """
        self.base_factory = base_factory
        self.wrapper_class = wrapper_class
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
    
    def create(self, **kwargs) -> Any:
        """Create data and wrap it with sheets export capability.
        
        Args:
            **kwargs: Arguments passed to the base factory
            
        Returns:
            An instance of wrapper_class containing the data from base_factory
        """
        # Get the data from wrapped factory
        data = self.base_factory.create(**kwargs)
        
        # Wrap with sheets export capability
        return self.wrapper_class(
            report=data,
            spreadsheet_id=self.spreadsheet_id,
            sheet_name=self.sheet_name
        )