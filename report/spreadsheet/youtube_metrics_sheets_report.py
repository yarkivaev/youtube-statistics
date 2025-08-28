"""Google Sheets Report wrapper for YouTubeMetrics model."""

from domain import YouTubeMetrics
from typing import Optional, List
from ..google_sheets_report import GoogleSheetsReport


class YoutubeMetricsSheetsReport(GoogleSheetsReport):
    """Google Sheets exporter for YouTubeMetrics model.
    
    Creates a multi-sheet spreadsheet with organized analytics data.
    """
    
    def __init__(
        self,
        report: YouTubeMetrics,
        spreadsheet_id: Optional[str] = None,
        sheet_name: Optional[str] = None,
        create_new: bool = False,
        share_emails: Optional[List[str]] = None
    ):
        """Initialize with YouTubeMetrics instance.
        
        Args:
            report: YouTubeMetrics instance to export
            spreadsheet_id: ID of existing spreadsheet or None to create new
            sheet_name: Name for the sheet (defaults to 'Analytics')
            create_new: Whether to create a new spreadsheet
            share_emails: List of emails to share the spreadsheet with
        """
        # Call parent with empty data - we'll handle export differently
        super().__init__(
            data={},
            spreadsheet_id=spreadsheet_id,
            create_new=create_new,
            share_emails=share_emails
        )
        self.report = report
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name or 'Analytics'
        
        # Initialize all export components
        self._initialize_export_components()
    
    def _initialize_export_components(self):
        """Initialize all export components in the constructor."""
        # Import necessary components
        from domain import MonthlyMetricsFactory
        from .factories import (
            SpreadsheetFragmentFactory,
            HeaderFragmentFactory,
            ChannelFragmentFactory,
            MonthlyMetricsFragmentFactory,
            SectionHeaderFragmentFactory,
            SubscriberTotalFragmentFactory,
            GeographicFragmentFactory
        )
        
        # Create monthly aggregation factory using the report's daily metrics and video counts
        self.monthly_factory = MonthlyMetricsFactory(
            self.report.daily_metrics,
            video_counts_by_month=self.report.video_counts_by_month,
            geographic_views_by_month=self.report.geographic_views_by_month,
            geographic_subscribers_by_month=self.report.geographic_subscribers_by_month
        )
        
        # Create base spreadsheet fragment factory
        spreadsheet_factory = SpreadsheetFragmentFactory()
        
        # Compose fragment factories with spreadsheet factory
        self.header_fragment_factory = HeaderFragmentFactory(spreadsheet_factory)
        self.channel_fragment_factory = ChannelFragmentFactory(spreadsheet_factory)
        self.metrics_fragment_factory = MonthlyMetricsFragmentFactory(spreadsheet_factory)
        self.section_fragment_factory = SectionHeaderFragmentFactory(spreadsheet_factory)
        self.subscriber_fragment_factory = SubscriberTotalFragmentFactory(spreadsheet_factory)
        self.geographic_fragment_factory = GeographicFragmentFactory(spreadsheet_factory)
    
    def export(self) -> str:
        """Export YouTubeMetrics to Google Sheets in monthly columns format.
        
        Returns:
            URL of the created/updated spreadsheet
        """
        from .monthly_columns_formatter import MonthlyColumnsFormatter
        
        spreadsheet_id = self.spreadsheet_id
        if not spreadsheet_id:
            spreadsheet_id = "1YBazG-UVCnSYwYjSKmXwaySVFDaQuifsL14aWTq7S9U"  # Default
        
        # Get monthly data from the pre-created factory
        monthly_data = self.monthly_factory.create()
        
        # Create and execute formatter with pre-initialized factories
        formatter = MonthlyColumnsFormatter(
            report=self.report,
            monthly_data=monthly_data,
            header_factory=self.header_fragment_factory,
            channel_factory=self.channel_fragment_factory,
            metrics_factory=self.metrics_fragment_factory,
            section_factory=self.section_fragment_factory,
            subscriber_factory=self.subscriber_fragment_factory,
            geographic_factory=self.geographic_fragment_factory,
            spreadsheet_id=spreadsheet_id,
            sheet_name=self.sheet_name,
            create_new=False
        )
        
        # Export and return URL
        return formatter.export()
    
    # Delegate attribute access to the wrapped report
    def __getattr__(self, name):
        """Delegate attribute access to the wrapped report."""
        return getattr(self.report, name)