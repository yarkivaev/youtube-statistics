"""MergedSpreadsheetFragment - Decorators for merging SpreadsheetFragments."""

from typing import List, Any, Tuple, Optional
from abc import ABC, abstractmethod
from .spreadsheet_fragment import SpreadsheetFragment
from .formatted_spreadsheet_fragment import FormattedSpreadsheetFragment, RangeFormat


class MergedSpreadsheetFragment(SpreadsheetFragment, ABC):
    """Abstract base class for merging two SpreadsheetFragments.
    
    This decorator pattern allows combining two fragments using different strategies
    while maintaining the SpreadsheetFragment interface.
    """
    
    def __init__(self, left: SpreadsheetFragment, right: SpreadsheetFragment):
        """Initialize with two fragments to merge.
        
        Args:
            left: First fragment
            right: Second fragment
        """
        self.left = left
        self.right = right
        # Initialize parent with merged rows
        super().__init__(self._merge_fragments())
    
    @abstractmethod
    def _merge_fragments(self) -> List[List[Any]]:
        """Merge the two fragments according to the strategy.
        
        Returns:
            Merged rows data
        """
        pass
    
    # Override methods to maintain immutability
    def with_row(self, row: List[Any]) -> 'SpreadsheetFragment':
        """Add a row to the merged result."""
        return SpreadsheetFragment(self.rows).with_row(row)
    
    def with_rows(self, rows: List[List[Any]]) -> 'SpreadsheetFragment':
        """Add rows to the merged result."""
        return SpreadsheetFragment(self.rows).with_rows(rows)


def VerticalMergedSpreadsheetFragment(left: SpreadsheetFragment, right: SpreadsheetFragment, gap_rows: int = 0) -> SpreadsheetFragment:
    """Merge fragments vertically (one below the other).
    
    Returns a FormattedSpreadsheetFragment if either input is formatted,
    otherwise returns a regular SpreadsheetFragment.
    
    Args:
        left: Top fragment
        right: Bottom fragment  
        gap_rows: Number of empty rows between fragments
        
    Returns:
        Merged SpreadsheetFragment (may be formatted)
    """
    # Merge rows
    merged = left.to_list()
    
    # Add gap rows if specified
    if gap_rows > 0:
        # Determine column count for empty rows
        num_cols = max(
            max(len(row) for row in left.rows) if left.rows else 0,
            max(len(row) for row in right.rows) if right.rows else 0
        )
        for _ in range(gap_rows):
            merged.append([''] * num_cols)
    
    # Add right fragment rows
    merged.extend(right.to_list())
    
    # Check if we need formatting
    left_has_formats = isinstance(left, FormattedSpreadsheetFragment)
    right_has_formats = isinstance(right, FormattedSpreadsheetFragment)
    
    if left_has_formats or right_has_formats:
        # Merge formats with adjusted indices
        merged_formats = []
        
        # Add left fragment formats (no adjustment needed)
        if left_has_formats and hasattr(left, 'formats'):
            merged_formats.extend(left.formats)
        
        # Add right fragment formats (adjust row indices)
        if right_has_formats and hasattr(right, 'formats'):
            left_rows = len(left.rows)
            gap_adjustment = left_rows + gap_rows
            
            for fmt in right.formats:
                adjusted_format = RangeFormat(
                    start_row=fmt.start_row + gap_adjustment,
                    start_col=fmt.start_col,
                    end_row=fmt.end_row + gap_adjustment,
                    end_col=fmt.end_col,
                    format=fmt.format
                )
                merged_formats.append(adjusted_format)
        
        # Return a FormattedSpreadsheetFragment
        return FormattedSpreadsheetFragment(SpreadsheetFragment(merged), merged_formats)
    else:
        # Return regular SpreadsheetFragment
        return SpreadsheetFragment(merged)
    


class HorizontalMergedSpreadsheetFragment(MergedSpreadsheetFragment):
    """Merge fragments horizontally (side by side)."""
    
    def __init__(self, left: SpreadsheetFragment, right: SpreadsheetFragment, gap_cols: int = 1):
        """Initialize horizontal merge.
        
        Args:
            left: Left fragment
            right: Right fragment
            gap_cols: Number of empty columns between fragments
        """
        self.gap_cols = gap_cols
        super().__init__(left, right)
    
    def _merge_fragments(self) -> List[List[Any]]:
        """Place fragments side by side with optional gap."""
        left_rows = self.left.to_list()
        right_rows = self.right.to_list()
        
        # Determine dimensions
        max_rows = max(len(left_rows), len(right_rows))
        left_cols = max(len(row) for row in left_rows) if left_rows else 0
        right_cols = max(len(row) for row in right_rows) if right_rows else 0
        
        merged = []
        for i in range(max_rows):
            row = []
            
            # Add left fragment cells
            if i < len(left_rows):
                row.extend(left_rows[i])
                # Pad to consistent width
                row.extend([''] * (left_cols - len(left_rows[i])))
            else:
                row.extend([''] * left_cols)
            
            # Add gap columns
            row.extend([''] * self.gap_cols)
            
            # Add right fragment cells
            if i < len(right_rows):
                row.extend(right_rows[i])
            else:
                row.extend([''] * right_cols)
            
            merged.append(row)
        
        return merged


class ColumnMergedSpreadsheetFragment(MergedSpreadsheetFragment):
    """Merge fragments by interleaving columns for each row.
    
    Useful for monthly data where each fragment represents different metrics
    for the same time periods.
    """
    
    def __init__(self, left: SpreadsheetFragment, right: SpreadsheetFragment, 
                 left_cols: int = 1, right_cols: int = 1):
        """Initialize column interleaving merge.
        
        Args:
            left: First fragment
            right: Second fragment
            left_cols: Number of columns to take from left for each group
            right_cols: Number of columns to take from right for each group
        """
        self.left_cols = left_cols
        self.right_cols = right_cols
        super().__init__(left, right)
    
    def _merge_fragments(self) -> List[List[Any]]:
        """Interleave columns from both fragments."""
        left_rows = self.left.to_list()
        right_rows = self.right.to_list()
        
        # Must have same number of rows
        if len(left_rows) != len(right_rows):
            raise ValueError(f"Column merge requires same row count: {len(left_rows)} != {len(right_rows)}")
        
        merged = []
        for left_row, right_row in zip(left_rows, right_rows):
            merged_row = []
            
            # Interleave columns
            left_idx = 0
            right_idx = 0
            
            while left_idx < len(left_row) or right_idx < len(right_row):
                # Take from left
                for _ in range(self.left_cols):
                    if left_idx < len(left_row):
                        merged_row.append(left_row[left_idx])
                        left_idx += 1
                    else:
                        merged_row.append('')
                
                # Take from right
                for _ in range(self.right_cols):
                    if right_idx < len(right_row):
                        merged_row.append(right_row[right_idx])
                        right_idx += 1
                    else:
                        merged_row.append('')
            
            merged.append(merged_row)
        
        return merged