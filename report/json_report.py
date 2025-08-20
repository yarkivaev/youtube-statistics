"""JSON Report implementation."""

import json
from typing import Dict, Any
from .base import Report


class JsonReport(Report):
    """Export dictionary to JSON format using decorator pattern."""
    
    def __init__(self, data: Dict[str, Any], indent: int = 2, ensure_ascii: bool = False):
        """Initialize JSON exporter with a dictionary.
        
        Args:
            data: Dictionary to export as JSON
            indent: JSON indentation level
            ensure_ascii: Whether to escape non-ASCII characters
        """
        super().__init__(data)
        self.data = data
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def export(self) -> str:
        """Export dictionary to JSON string.
        
        Returns:
            JSON formatted string
        """
        # Add metadata to the exported data
        export_data = dict(self.data)
        if '_metadata' not in export_data:
            export_data['_metadata'] = {}
        
        export_data['_metadata']['exporter'] = 'JsonReport'
        
        return json.dumps(
            export_data,
            indent=self.indent,
            ensure_ascii=self.ensure_ascii,
            default=str  # Handle datetime and other non-serializable types
        )