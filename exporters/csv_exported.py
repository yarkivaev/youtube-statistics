"""CSV Exported implementation."""

import csv
import io
from typing import Dict, Any, List, Union
from .base import Exported


class CSVExported(Exported):
    """Export data to CSV format using decorator pattern."""
    
    def __init__(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]):
        """Initialize CSV exporter.
        
        Args:
            data: Data to export (dict or list of dicts)
        """
        super().__init__(data)
        self.data = data
    
    def export(self) -> str:
        """Export data to CSV string.
        
        Returns:
            CSV formatted string
        """
        output = io.StringIO()
        
        if isinstance(self.data, list) and self.data:
            # List of dictionaries - export as table
            fieldnames = list(self.data[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in self.data:
                # Convert complex types to strings
                cleaned_row = {}
                for key, value in row.items():
                    if isinstance(value, (dict, list)):
                        cleaned_row[key] = str(value)
                    elif value is None:
                        cleaned_row[key] = ''
                    else:
                        cleaned_row[key] = value
                writer.writerow(cleaned_row)
        
        elif isinstance(self.data, dict):
            # Dictionary - export as key-value pairs
            writer = csv.writer(output)
            writer.writerow(['Key', 'Value'])
            
            for key, value in self.data.items():
                if isinstance(value, (dict, list)):
                    writer.writerow([key, str(value)])
                else:
                    writer.writerow([key, value])
        
        return output.getvalue()
    
    def export_to_file(self, filename: str):
        """Export data directly to a CSV file.
        
        Args:
            filename: Path to the CSV file to create
        """
        csv_content = self.export()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            f.write(csv_content)