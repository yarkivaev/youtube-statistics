"""SpreadsheetFragment - An immutable type-safe representation of spreadsheet data."""

from typing import List, Any, Optional, Union, Tuple
from dataclasses import dataclass


@dataclass(frozen=True)
class SpreadsheetFragment:
    """Immutable representation of spreadsheet data with rows and columns.
    
    This class provides a minimal, type-safe, immutable way to work with spreadsheet data.
    All operations return new instances rather than modifying the existing one.
    """
    
    rows: Tuple[Tuple[Any, ...], ...]
    
    def __init__(self, rows: Optional[Union[List[List[Any]], Tuple[Tuple[Any, ...], ...]]] = None):
        """Initialize with optional rows data.
        
        Args:
            rows: Initial rows data, defaults to empty tuple
        """
        if rows is None:
            rows_tuple = tuple()
        elif isinstance(rows, tuple):
            # Ensure inner elements are also tuples
            rows_tuple = tuple(
                tuple(row) if not isinstance(row, tuple) else row 
                for row in rows
            )
        else:
            # Convert list to tuple of tuples
            rows_tuple = tuple(tuple(row) for row in rows)
        
        # Use object.__setattr__ since the class is frozen
        object.__setattr__(self, 'rows', rows_tuple)
    
    # ============= Core Methods (4) =============
    
    def with_row(self, row: Union[List[Any], Tuple[Any, ...]]) -> 'SpreadsheetFragment':
        """Create a new fragment with an additional row.
        
        Args:
            row: Row data to add
            
        Returns:
            New SpreadsheetFragment with the added row
        """
        if not isinstance(row, (list, tuple)):
            raise ValueError(f"Row must be a list or tuple, got {type(row)}")
        new_rows = self.rows + (tuple(row),)
        return SpreadsheetFragment(new_rows)
    
    def with_rows(self, rows: Union[List[List[Any]], List[Tuple[Any, ...]]]) -> 'SpreadsheetFragment':
        """Create a new fragment with additional rows.
        
        Args:
            rows: List of rows to add
            
        Returns:
            New SpreadsheetFragment with the added rows
        """
        new_rows = self.rows + tuple(tuple(row) for row in rows)
        return SpreadsheetFragment(new_rows)
    
    def to_list(self) -> List[List[Any]]:
        """Convert to raw list format for API calls.
        
        Returns:
            List of lists representing the spreadsheet data
        """
        return [list(row) for row in self.rows]
    
    @classmethod
    def from_dict_list(cls, data: List[dict], columns: Optional[List[str]] = None) -> 'SpreadsheetFragment':
        """Create fragment from a list of dictionaries.
        
        Args:
            data: List of dictionaries
            columns: Column names to use (defaults to all keys)
            
        Returns:
            SpreadsheetFragment instance
        """
        if not data:
            return cls()
        
        # Determine columns
        if columns is None:
            columns = list(data[0].keys())
        
        # Build all rows at once
        rows = [columns]  # Header row
        
        # Add data rows
        for item in data:
            row = [item.get(col, '') for col in columns]
            rows.append(row)
        
        return cls(rows)
    
    def update(self, worksheet, spreadsheet=None) -> None:
        """Update worksheet with fragment data and apply any formatting.
        
        Args:
            worksheet: Google Sheets worksheet object
            spreadsheet: Google Sheets spreadsheet object (optional, for formatting)
        """
        # Base implementation just updates the data
        sheet_data = self.to_list()
        if sheet_data:
            worksheet.update('A1', sheet_data)