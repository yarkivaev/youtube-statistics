"""Generic factory wrapper for JSON export functionality."""

from models.factories.base import Factory
from typing import Any, Type, Optional


class JsonReportFactory(Factory):
    """Generic factory wrapper that adds JSON export capability.
    
    This factory wraps any base factory and applies a JSON report wrapper
    to its output, enabling structured JSON export functionality.
    """
    
    def __init__(self, 
                 base_factory: Factory,
                 wrapper_class: Optional[Type] = None):
        """Initialize JSON report factory.
        
        Args:
            base_factory: Any factory that produces data/models
            wrapper_class: Optional report wrapper class to use (e.g., YoutubeMetricsJsonReport)
                          If not provided, uses generic wrapper
        """
        self.base_factory = base_factory
        self.wrapper_class = wrapper_class
    
    def create(self, **kwargs) -> Any:
        """Create data and wrap it with JSON export capability.
        
        Args:
            **kwargs: Arguments passed to the base factory
            
        Returns:
            An instance of wrapper_class containing the data from base_factory,
            or a generic wrapper if no wrapper_class specified
        """
        # Get the data from wrapped factory
        data = self.base_factory.create(**kwargs)
        
        # If specific wrapper class provided, use it
        if self.wrapper_class:
            return self.wrapper_class(report=data)
        
        # Otherwise use generic wrapper
        return JsonReportWrapper(data)


class JsonReportWrapper:
    """Generic wrapper that adds JSON export capability to any data object."""
    
    def __init__(self, data: Any):
        """Initialize wrapper with data.
        
        Args:
            data: Data object that has a to_dict() method
        """
        self.data = data
    
    def export(self, filename: str = "youtube_analytics.json") -> str:
        """Export data to JSON file.
        
        Args:
            filename: Name of the file to export to
            
        Returns:
            Path to the exported file
        """
        from .json_report import JsonReport
        
        # Convert data to dictionary
        data_dict = self.data.to_dict()
        
        # Create JSON exporter and export
        json_exporter = JsonReport(data_dict)
        json_content = json_exporter.export()
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_content)
        
        return filename
    
    def to_dict(self) -> dict:
        """Convert wrapped data to dictionary.
        
        Returns:
            Dictionary representation of the data
        """
        return self.data.to_dict()
    
    def __getattr__(self, name):
        """Delegate attribute access to wrapped data.
        
        This allows the wrapper to be used as if it were the original data object.
        """
        return getattr(self.data, name)