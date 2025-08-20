"""FormattedSpreadsheetFragment - Decorator for applying formatting to SpreadsheetFragments."""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from .spreadsheet_fragment import SpreadsheetFragment


@dataclass
class CellFormat:
    """Formatting properties for spreadsheet cells."""
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    font_size: Optional[int] = None
    font_family: Optional[str] = None
    text_color: Optional[str] = None  # Hex color like "#000000"
    background_color: Optional[str] = None  # Hex color like "#FFFFFF"
    horizontal_align: Optional[str] = None  # "left", "center", "right"
    vertical_align: Optional[str] = None  # "top", "middle", "bottom"
    number_format: Optional[str] = None  # e.g., "#,##0", "0.00%"
    borders: Optional[Dict[str, bool]] = None  # {"top": True, "bottom": True, etc.}
    
    def to_google_sheets_format(self) -> Dict[str, Any]:
        """Convert to Google Sheets API format."""
        format_dict = {}
        
        text_format = {}
        if self.bold is not None:
            text_format['bold'] = self.bold
        if self.italic is not None:
            text_format['italic'] = self.italic
        if self.font_size is not None:
            text_format['fontSize'] = self.font_size
        if self.font_family is not None:
            text_format['fontFamily'] = self.font_family
        if self.text_color is not None:
            text_format['foregroundColor'] = self._hex_to_rgb(self.text_color)
        
        if text_format:
            format_dict['textFormat'] = text_format
        
        if self.background_color is not None:
            format_dict['backgroundColor'] = self._hex_to_rgb(self.background_color)
        
        if self.horizontal_align is not None:
            format_dict['horizontalAlignment'] = self.horizontal_align.upper()
        
        if self.vertical_align is not None:
            format_dict['verticalAlignment'] = self.vertical_align.upper()
        
        if self.number_format is not None:
            format_dict['numberFormat'] = {'type': 'NUMBER', 'pattern': self.number_format}
        
        if self.borders:
            borders = {}
            for side, enabled in self.borders.items():
                if enabled:
                    borders[side] = {'style': 'SOLID'}
            if borders:
                format_dict['borders'] = borders
        
        return format_dict
    
    @staticmethod
    def _hex_to_rgb(hex_color: str) -> Dict[str, float]:
        """Convert hex color to RGB dict for Google Sheets."""
        hex_color = hex_color.lstrip('#')
        return {
            'red': int(hex_color[0:2], 16) / 255,
            'green': int(hex_color[2:4], 16) / 255,
            'blue': int(hex_color[4:6], 16) / 255
        }


@dataclass
class RangeFormat:
    """Formatting for a specific range of cells."""
    start_row: int
    start_col: int
    end_row: int
    end_col: int
    format: CellFormat
    
    def to_google_sheets_request(self, sheet_id: int = 0) -> Dict[str, Any]:
        """Create a Google Sheets format request."""
        return {
            'repeatCell': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': self.start_row,
                    'endRowIndex': self.end_row + 1,
                    'startColumnIndex': self.start_col,
                    'endColumnIndex': self.end_col + 1
                },
                'cell': {
                    'userEnteredFormat': self.format.to_google_sheets_format()
                },
                'fields': 'userEnteredFormat'
            }
        }


class FormattedSpreadsheetFragment(SpreadsheetFragment):
    """Decorator that adds formatting information to a SpreadsheetFragment.
    
    This maintains the immutable nature of SpreadsheetFragment while
    tracking formatting that should be applied when exported.
    """
    
    def __init__(self, fragment: SpreadsheetFragment, formats: Optional[List[RangeFormat]] = None):
        """Initialize with a fragment and optional formatting.
        
        Args:
            fragment: The SpreadsheetFragment to decorate
            formats: List of RangeFormat objects to apply
        """
        super().__init__(fragment.rows)
        self.formats = formats or []
    
    
    # Override parent methods to maintain immutability
    def with_row(self, row: List[Any]) -> 'FormattedSpreadsheetFragment':
        """Add a row, preserving formats."""
        new_fragment = SpreadsheetFragment(self.rows).with_row(row)
        return FormattedSpreadsheetFragment(new_fragment, self.formats)
    
    def with_rows(self, rows: List[List[Any]]) -> 'FormattedSpreadsheetFragment':
        """Add rows, preserving formats."""
        new_fragment = SpreadsheetFragment(self.rows).with_rows(rows)
        return FormattedSpreadsheetFragment(new_fragment, self.formats)
    
    def update(self, worksheet, spreadsheet=None) -> None:
        """Update worksheet with fragment data and apply formatting.
        
        Args:
            worksheet: Google Sheets worksheet object
            spreadsheet: Google Sheets spreadsheet object (required for formatting)
        """
        # First update the data using parent method
        super().update(worksheet, spreadsheet)
        
        # Then apply formatting if spreadsheet is provided
        if spreadsheet and self.formats:
            format_requests = [fmt.to_google_sheets_request(worksheet.id) for fmt in self.formats]
            if format_requests:
                spreadsheet.batch_update({'requests': format_requests})


