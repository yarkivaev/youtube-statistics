"""Google Sheets Exported implementation."""

import gspread
from gspread_formatting import *
from google.oauth2.credentials import Credentials
from typing import Dict, Any, List, Optional, Union
import pickle
import os
from datetime import datetime
from .base import Exported


class GoogleSheetsExported(Exported):
    """Export data to Google Sheets using decorator pattern."""
    
    # Default colors for formatting
    HEADER_COLOR = {
        'red': 0.2,
        'green': 0.4,
        'blue': 0.6
    }
    
    def __init__(
        self, 
        data: Union[Dict[str, Any], List[Dict[str, Any]]], 
        spreadsheet_id: Optional[str] = None,
        sheet_name: Optional[str] = None,
        create_new: bool = False,
        share_emails: Optional[List[str]] = None
    ):
        """Initialize Google Sheets exporter.
        
        Args:
            data: Data to export (dict or list of dicts)
            spreadsheet_id: ID of existing spreadsheet or None to create new
            sheet_name: Name of the sheet/tab to write to
            create_new: Whether to create a new spreadsheet
            share_emails: List of emails to share the spreadsheet with
        """
        super().__init__(data)
        self.data = data
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name or 'Sheet1'
        self.create_new = create_new
        self.share_emails = share_emails or []
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
    
    def _authenticate(self) -> gspread.Client:
        """Authenticate with Google Sheets API using existing OAuth token.
        
        Returns:
            Authenticated gspread client
        """
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        
        # Use existing token.pickle from YouTube API authentication
        token_path = 'token.pickle'
        creds = None
        
        # The required scopes for both YouTube Analytics and Google Sheets
        SCOPES = [
            'https://www.googleapis.com/auth/yt-analytics.readonly',
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Check if we need to add Google Sheets scopes
        if creds and creds.valid:
            # Check if we have the required scopes
            if hasattr(creds, 'scopes') and creds.scopes:
                missing_scopes = set(SCOPES) - set(creds.scopes)
                if missing_scopes:
                    # Need to re-authenticate with additional scopes
                    creds = None
        elif creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = None
        
        # If credentials are missing or invalid, re-authenticate
        if not creds or not creds.valid:
            if os.path.exists('client_secrets.json'):
                flow = InstalledAppFlow.from_client_secrets_file(
                    'client_secrets.json', SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for next run
                with open(token_path, 'wb') as token:
                    pickle.dump(creds, token)
            else:
                raise FileNotFoundError(
                    "client_secrets.json not found. Please ensure OAuth credentials are configured."
                )
        
        # Create gspread client
        client = gspread.authorize(creds)
        return client
    
    def _get_or_create_spreadsheet(self) -> gspread.Spreadsheet:
        """Get existing spreadsheet or create new one.
        
        Returns:
            Spreadsheet object
        """
        if self.create_new or not self.spreadsheet_id:
            # Create new spreadsheet
            title = f"YouTube Analytics - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            spreadsheet = self.client.create(title)
            self.spreadsheet_id = spreadsheet.id
            
            # Share with specified emails
            for email in self.share_emails:
                spreadsheet.share(email, perm_type='user', role='reader')
            
            return spreadsheet
        else:
            # Open existing spreadsheet
            return self.client.open_by_key(self.spreadsheet_id)
    
    def _get_or_create_worksheet(self) -> gspread.Worksheet:
        """Get worksheet by name or create new one.
        
        Returns:
            Worksheet object
        """
        try:
            # Try to get existing worksheet
            worksheet = self.spreadsheet.worksheet(self.sheet_name)
            # Clear existing content
            worksheet.clear()
        except gspread.WorksheetNotFound:
            # Create new worksheet
            worksheet = self.spreadsheet.add_worksheet(
                title=self.sheet_name,
                rows=1000,
                cols=26
            )
        
        return worksheet
    
    def _format_headers(self, worksheet: gspread.Worksheet, num_cols: int):
        """Apply formatting to header row.
        
        Args:
            worksheet: Worksheet to format
            num_cols: Number of columns with headers
        """
        # Create header format
        header_format = CellFormat(
            backgroundColor=Color(**self.HEADER_COLOR),
            textFormat=TextFormat(
                bold=True,
                foregroundColor=Color(1, 1, 1),
                fontSize=11
            ),
            horizontalAlignment='CENTER',
            verticalAlignment='MIDDLE'
        )
        
        # Apply to header row
        format_cell_range(
            worksheet,
            f'A1:{chr(65 + num_cols - 1)}1',
            header_format
        )
        
        # Freeze header row
        set_frozen(worksheet, rows=1)
    
    def _write_dict_data(self, data: Dict[str, Any]):
        """Write dictionary data to sheet as key-value pairs.
        
        Args:
            data: Dictionary to write
        """
        rows = []
        
        # Convert dict to rows (key-value pairs)
        for key, value in data.items():
            # Handle nested dicts and lists
            if isinstance(value, dict):
                rows.append([key, ''])
                for sub_key, sub_value in value.items():
                    rows.append([f'  {sub_key}', str(sub_value)])
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # List of dicts - create sub-table
                    rows.append([key, f'{len(value)} items'])
                else:
                    # Simple list
                    rows.append([key, ', '.join(map(str, value))])
            else:
                rows.append([key, str(value)])
        
        # Write to sheet
        if rows:
            self.worksheet.update('A1', rows)
            self._format_headers(self.worksheet, 2)
    
    def _write_list_data(self, data: List[Dict[str, Any]]):
        """Write list of dictionaries as table.
        
        Args:
            data: List of dictionaries to write
        """
        if not data:
            return
        
        # Get headers from first item
        headers = list(data[0].keys())
        rows = [headers]
        
        # Add data rows
        for item in data:
            row = []
            for header in headers:
                value = item.get(header, '')
                # Convert complex types to string
                if isinstance(value, (dict, list)):
                    value = str(value)
                elif isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                elif value is None:
                    value = ''
                else:
                    value = str(value)
                row.append(value)
            rows.append(row)
        
        # Write to sheet
        self.worksheet.update('A1', rows)
        self._format_headers(self.worksheet, len(headers))
        
        # Auto-resize columns
        self.worksheet.columns_auto_resize(0, len(headers) - 1)
    
    def export(self) -> str:
        """Export data to Google Sheets.
        
        Returns:
            URL of the spreadsheet
        """
        # Authenticate
        self.client = self._authenticate()
        
        # Get or create spreadsheet
        self.spreadsheet = self._get_or_create_spreadsheet()
        
        # Get or create worksheet
        self.worksheet = self._get_or_create_worksheet()
        
        # Write data based on type
        if isinstance(self.data, list):
            self._write_list_data(self.data)
        else:
            self._write_dict_data(self.data)
        
        # Return spreadsheet URL
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"
    
    def export_multi_sheet(self, sheets_data: Dict[str, Union[Dict, List]]) -> str:
        """Export multiple sheets at once.
        
        Args:
            sheets_data: Dictionary mapping sheet names to data
            
        Returns:
            URL of the spreadsheet
        """
        # Authenticate
        self.client = self._authenticate()
        
        # Get or create spreadsheet
        self.spreadsheet = self._get_or_create_spreadsheet()
        
        # Process each sheet
        for sheet_name, sheet_data in sheets_data.items():
            self.sheet_name = sheet_name
            self.worksheet = self._get_or_create_worksheet()
            
            # Write data based on type
            if isinstance(sheet_data, list):
                self._write_list_data(sheet_data)
            else:
                self._write_dict_data(sheet_data)
        
        # Delete default Sheet1 if it exists and is empty
        try:
            default_sheet = self.spreadsheet.worksheet('Sheet1')
            if default_sheet.row_count == 1000 and default_sheet.col_count == 26:
                # Check if empty
                values = default_sheet.get_all_values()
                if not any(any(cell for cell in row) for row in values):
                    self.spreadsheet.del_worksheet(default_sheet)
        except:
            pass
        
        return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"