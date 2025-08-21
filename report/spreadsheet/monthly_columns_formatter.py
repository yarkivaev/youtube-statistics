"""Monthly columns formatter for analytics reports."""

from models import YouTubeMetrics
from typing import Optional, List, Dict, Any
from models.factories.base import Factory
from ..google_sheets_report import GoogleSheetsReport
from .merged_spreadsheet_fragment import VerticalMergedSpreadsheetFragment
from .spreadsheet_fragment import SpreadsheetFragment


class MonthlyColumnsFormatter(GoogleSheetsReport):
    """Formatter that creates spreadsheet with monthly columns structure.
    
    Creates a spreadsheet with:
    - Months as column groups (3 columns per month)
    - Metrics as rows
    """
    
    # Russian month names
    MONTH_NAMES_RU = {
        1: 'янв',
        2: 'февр',
        3: 'мар',
        4: 'апр',
        5: 'мая',
        6: 'июн',
        7: 'июл',
        8: 'авг',
        9: 'сент',
        10: 'окт',
        11: 'нояб',
        12: 'дек'
    }
    
    def __init__(
        self,
        report: YouTubeMetrics,
        monthly_data: Dict[str, Dict[str, Any]],
        header_factory: Factory,
        channel_factory: Factory,
        metrics_factory: Factory,
        section_factory: Factory,
        subscriber_factory: Factory,
        geographic_factory: Factory = None,
        spreadsheet_id: Optional[str] = None,
        sheet_name: Optional[str] = None,
        create_new: bool = True,
        share_emails: Optional[List[str]] = None
    ):
        """Initialize with YouTubeMetrics instance and fragment factories.
        
        Args:
            report: YouTubeMetrics instance
            monthly_data: Pre-aggregated monthly metrics from MonthlyModelFactory
            header_factory: Factory for creating header fragments
            channel_factory: Factory for creating channel fragments
            metrics_factory: Factory for creating metrics fragments
            section_factory: Factory for creating section header fragments
            subscriber_factory: Factory for creating subscriber total fragments
            geographic_factory: Optional factory for creating geographic fragments
            spreadsheet_id: Optional existing spreadsheet ID
            sheet_name: Optional name for the sheet (defaults to 'Analytics')
            create_new: Whether to create a new spreadsheet
            share_emails: Optional list of emails to share with
        """
        super().__init__(
            data={},
            spreadsheet_id=spreadsheet_id,
            create_new=create_new,
            share_emails=share_emails
        )
        self.report = report
        self.monthly_data = monthly_data
        self.header_factory = header_factory
        self.channel_factory = channel_factory
        self.metrics_factory = metrics_factory
        self.section_factory = section_factory
        self.subscriber_factory = subscriber_factory
        self.geographic_factory = geographic_factory
        self.sheet_name = sheet_name or 'Analytics'
    
    def _format_month_header(self, year: int, month: int) -> str:
        """Format month header in Russian.
        
        Args:
            year: Year number
            month: Month number (1-12)
            
        Returns:
            Formatted month string like "янв. 2025"
        """
        month_name = self.MONTH_NAMES_RU.get(month, str(month))
        return f"{month_name}. {year}"
    
    def _create_monthly_columns_data(self) -> SpreadsheetFragment:
        """Create sheet data in monthly columns format using fragment exporters.
        
        Returns:
            SpreadsheetFragment containing the YouTube sheet structure
        """
        months = sorted(self.monthly_data.keys())
        
        if not months:
            return SpreadsheetFragment()
        
        # Create individual fragments using passed factories
        header_fragment = self.header_factory.create(months=months, month_names_ru=self.MONTH_NAMES_RU)
        channel_fragment = self.channel_factory.create(
            channel=self.report.channel, 
            months=months,
            monthly_data=self.monthly_data
        )
        
        # Empty row between sections
        empty_row = SpreadsheetFragment().with_row([''] * (1 + 3 * len(months)))
        
        # Metrics section header
        metrics_header = self.section_factory.create(title='Метрики', num_months=len(months))
        
        # Monthly metrics
        metrics_fragment = self.metrics_factory.create(monthly_data=self.monthly_data, months=months)
        
        # Optional subscriber total
        subscriber_total = self.subscriber_factory.create(channel=self.report.channel, months=months)
        
        # Optional geographic data
        if self.geographic_factory:
            geographic_fragment = self.geographic_factory.create(monthly_data=self.monthly_data, months=months)
        else:
            geographic_fragment = None
        
        # Merge all fragments vertically
        result = header_fragment
        result = VerticalMergedSpreadsheetFragment(result, channel_fragment)
        result = VerticalMergedSpreadsheetFragment(result, empty_row)
        result = VerticalMergedSpreadsheetFragment(result, metrics_header)
        result = VerticalMergedSpreadsheetFragment(result, metrics_fragment)
        
        if subscriber_total.rows:
            result = VerticalMergedSpreadsheetFragment(result, subscriber_total)
        
        if geographic_fragment and geographic_fragment.rows:
            result = VerticalMergedSpreadsheetFragment(result, empty_row)
            result = VerticalMergedSpreadsheetFragment(result, geographic_fragment)
        
        return result
    
    def export(self) -> str:
        """Export YouTubeMetrics to Google Sheets in monthly columns format.
        
        Returns:
            URL of the created/updated spreadsheet
        """
        try:
            # Authenticate
            self.client = self._authenticate()
            
            # Get or create spreadsheet
            self.spreadsheet = self._get_or_create_spreadsheet()
            
            # Create sheet with configured name
            self.worksheet = self._get_or_create_worksheet()
            
            # Prepare and write data with formatting
            sheet_fragment = self._create_monthly_columns_data()
            
            # Use the fragment's update method to handle both data and formatting
            sheet_fragment.update(self.worksheet, self.spreadsheet)
            
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}"
            
        except Exception as e:
            if "Drive API" in str(e):
                raise Exception(
                    "Google Drive API is required to create new spreadsheets. "
                    "Please either:\n"
                    "1. Enable Google Drive API at https://console.developers.google.com/apis/api/drive.googleapis.com/\n"
                    "2. Provide an existing spreadsheet ID using --spreadsheet-id option\n"
                    "3. Create a new spreadsheet manually and share it with your service account"
                )
            elif "permission" in str(e).lower():
                raise Exception(
                    f"No permission to modify the spreadsheet. "
                    "Please ensure you have edit access to the spreadsheet or create your own copy."
                )
            else:
                raise
    
    
