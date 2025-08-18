"""Google Sheets Exported for YouTube format matching the template."""

from models import AnalyticsReport
from typing import Optional, List, Dict, Any
from collections import defaultdict
from datetime import datetime
import calendar
from ...google_sheets_exported import GoogleSheetsExported


class YouTubeFormatSheetsExported(GoogleSheetsExported):
    """Google Sheets exporter that matches the YouTube sheet format from the template.
    
    Creates a spreadsheet with the same structure as the reference sheet:
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
        report: AnalyticsReport,
        spreadsheet_id: Optional[str] = None,
        create_new: bool = True,
        share_emails: Optional[List[str]] = None
    ):
        """Initialize with AnalyticsReport instance."""
        super().__init__(
            data={},
            spreadsheet_id=spreadsheet_id,
            create_new=create_new,
            share_emails=share_emails
        )
        self.report = report
    
    def _aggregate_by_month(self) -> Dict[str, Dict[str, Any]]:
        """Aggregate daily metrics by month.
        
        Returns:
            Dictionary with month keys (YYYY-MM) and aggregated metrics
        """
        monthly_data = defaultdict(lambda: {
            'views': 0,
            'watch_time_minutes': 0,
            'subscribers_gained': 0,
            'subscribers_lost': 0,
            'video_count': 0,  # This would need to be tracked separately
            'advertiser_count': 0,  # This would need manual input
            'integrations': '',  # This would need manual input
            'days_with_data': 0
        })
        
        if self.report.daily_metrics:
            for daily in self.report.daily_metrics:
                # Get month key
                daily_dict = daily.export()
                date_str = daily_dict.get('date', '')
                if date_str:
                    date_obj = datetime.fromisoformat(date_str)
                    month_key = f"{date_obj.year}-{date_obj.month:02d}"
                    
                    # Aggregate metrics
                    monthly_data[month_key]['views'] += daily_dict.get('views', 0)
                    monthly_data[month_key]['watch_time_minutes'] += daily_dict.get('watch_time_minutes', 0)
                    monthly_data[month_key]['subscribers_gained'] += daily_dict.get('subscribers_gained', 0)
                    monthly_data[month_key]['subscribers_lost'] += daily_dict.get('subscribers_lost', 0)
                    
                    # Count days with activity
                    if daily_dict.get('views', 0) > 0:
                        monthly_data[month_key]['days_with_data'] += 1
        
        return dict(monthly_data)
    
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
    
    def _create_youtube_sheet_data(self) -> List[List[Any]]:
        """Create sheet data in YouTube format.
        
        Returns:
            2D list of cell values matching the YouTube sheet structure
        """
        monthly_data = self._aggregate_by_month()
        
        # Get sorted list of months
        months = sorted(monthly_data.keys())
        
        # Initialize rows
        rows = []
        
        # Row 1: MM header
        row1 = ['MM'] + ['', '', ''] * len(months)
        rows.append(row1)
        
        # Row 2: Month headers (each month takes 3 columns)
        row2 = ['']
        for month_key in months:
            year, month = map(int, month_key.split('-'))
            month_header = self._format_month_header(year, month)
            row2.extend([month_header, '', ''])
        rows.append(row2)
        
        # Row 3: Количество роликов (Video count)
        row3 = ['Количество роликов']
        for month_key in months:
            # Get video count from channel data if available
            video_count = self.report.channel.video_count if hasattr(self.report, 'channel') else 0
            # For now, we'll show total video count, but ideally this should be per-month uploads
            row3.extend([str(video_count), '', ''])
        rows.append(row3)
        
        # Row 4: Количество рекламодателей (Advertiser count)
        row4 = ['Количество рекламодателей']
        for month_key in months:
            # This needs manual input or separate tracking
            row4.extend(['[Требуется ручной ввод]', '', ''])
        rows.append(row4)
        
        # Row 5: Интеграции Ghost Writer или Школьных продуктов
        row5 = ['Интеграции Ghost Writer или Школьных продуктов']
        for month_key in months:
            # This needs manual input
            row5.extend(['[Требуется ручной ввод]', '', ''])
        rows.append(row5)
        
        # Add empty row
        rows.append([''] * (1 + 3 * len(months)))
        
        # Metrics section
        rows.append(['Метрики'] + ['', '', ''] * len(months))
        
        # Row: Views
        row_views = ['Просмотры']
        for month_key in months:
            views = monthly_data[month_key]['views']
            row_views.extend([str(views), '', ''])
        rows.append(row_views)
        
        # Row: Watch time (hours)
        row_watch = ['Время просмотра (часы)']
        for month_key in months:
            hours = round(monthly_data[month_key]['watch_time_minutes'] / 60, 1)
            row_watch.extend([str(hours), '', ''])
        rows.append(row_watch)
        
        # Row: New subscribers
        row_subs = ['Новые подписчики']
        for month_key in months:
            subs_gained = monthly_data[month_key]['subscribers_gained']
            row_subs.extend([str(subs_gained), '', ''])
        rows.append(row_subs)
        
        # Row: Lost subscribers
        row_lost = ['Потерянные подписчики']
        for month_key in months:
            subs_lost = monthly_data[month_key]['subscribers_lost']
            row_lost.extend([str(subs_lost), '', ''])
        rows.append(row_lost)
        
        # Row: Net change
        row_net = ['Чистый прирост']
        for month_key in months:
            net = monthly_data[month_key]['subscribers_gained'] - monthly_data[month_key]['subscribers_lost']
            row_net.extend([f"{net:+d}" if net != 0 else "0", '', ''])
        rows.append(row_net)
        
        # Add total subscriber count if available
        if hasattr(self.report.channel, 'subscriber_count'):
            row_total = ['Всего подписчиков']
            for month_key in months:
                # This would need cumulative calculation
                total = self.report.channel.subscriber_count
                row_total.extend([str(total), '', ''])
            rows.append(row_total)
        
        return rows
    
    def export(self) -> str:
        """Export AnalyticsReport to Google Sheets in YouTube format.
        
        Returns:
            URL of the created/updated spreadsheet
        """
        try:
            # Authenticate
            self.client = self._authenticate()
            
            # Get or create spreadsheet
            self.spreadsheet = self._get_or_create_spreadsheet()
            
            # Create YouTube sheet
            self.sheet_name = 'YouTube Analytics'
            self.worksheet = self._get_or_create_worksheet()
            
            # Prepare and write data
            sheet_data = self._create_youtube_sheet_data()
            
            if sheet_data:
                # Update all cells at once
                self.worksheet.update('A1', sheet_data)
                
                # Apply formatting
                self._apply_youtube_formatting(len(sheet_data[0]))
            
            # Create additional sheets with other data
            self._create_supplementary_sheets()
            
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
    
    def _apply_youtube_formatting(self, num_cols: int):
        """Apply formatting similar to the YouTube template.
        
        Args:
            num_cols: Number of columns in the sheet
        """
        from gspread_formatting import CellFormat, Color, TextFormat, format_cell_range, set_frozen
        
        # Format header rows
        header_format = CellFormat(
            backgroundColor=Color(0.9, 0.9, 0.9),
            textFormat=TextFormat(bold=True),
            horizontalAlignment='CENTER'
        )
        
        # Apply to first 2 rows (headers)
        format_cell_range(
            self.worksheet,
            f'A1:{chr(65 + min(num_cols - 1, 25))}2',
            header_format
        )
        
        # Format metric labels
        label_format = CellFormat(
            textFormat=TextFormat(bold=True),
            horizontalAlignment='LEFT'
        )
        
        format_cell_range(
            self.worksheet,
            'A3:A20',
            label_format
        )
        
        # Auto-resize columns
        self.worksheet.columns_auto_resize(0, min(num_cols - 1, 25))
        
        # Freeze first column and first 2 rows
        set_frozen(self.worksheet, rows=2, cols=1)
    
    def _create_supplementary_sheets(self):
        """Create additional sheets with detailed data."""
        # Daily metrics sheet
        if self.report.daily_metrics:
            self.sheet_name = 'Ежедневные метрики'
            self.worksheet = self._get_or_create_worksheet()
            
            daily_data = []
            for daily in self.report.daily_metrics:
                daily_dict = daily.export()
                daily_data.append({
                    'Дата': daily_dict.get('date', ''),
                    'Просмотры': daily_dict.get('views', 0),
                    'Время просмотра (часы)': round(daily_dict.get('watch_time_minutes', 0) / 60, 2),
                    'Средняя продолжительность (мин)': round(daily_dict.get('average_view_duration_seconds', 0) / 60, 2),
                    'Новые подписчики': daily_dict.get('subscribers_gained', 0),
                    'Отписки': daily_dict.get('subscribers_lost', 0),
                    'Чистый прирост': daily_dict.get('subscribers_gained', 0) - daily_dict.get('subscribers_lost', 0)
                })
            
            if daily_data:
                self._write_list_data(daily_data)
        
        # Geographic data sheet
        if self.report.geographic_views:
            self.sheet_name = 'География'
            self.worksheet = self._get_or_create_worksheet()
            
            geo_data = []
            for geo in self.report.geographic_views:
                geo_dict = geo.export()
                geo_data.append({
                    'Страна': geo_dict.get('country_name', ''),
                    'Код страны': geo_dict.get('country_code', ''),
                    'Просмотры': geo_dict.get('views', 0),
                    'Процент': f"{geo_dict.get('percentage', 0):.2f}%"
                })
            
            if geo_data:
                self._write_list_data(geo_data)