"""Google Sheets Exported wrapper for AnalyticsReport model."""

from models import AnalyticsReport
from typing import Optional, List
from ...google_sheets_exported import GoogleSheetsExported


class AnalyticsReportSheetsExported(GoogleSheetsExported):
    """Google Sheets exporter for AnalyticsReport model.
    
    Creates a multi-sheet spreadsheet with organized analytics data.
    """
    
    def __init__(
        self,
        report: AnalyticsReport,
        spreadsheet_id: Optional[str] = None,
        create_new: bool = True,
        share_emails: Optional[List[str]] = None
    ):
        """Initialize with AnalyticsReport instance.
        
        Args:
            report: AnalyticsReport instance to export
            spreadsheet_id: ID of existing spreadsheet or None to create new
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
    
    def export(self) -> str:
        """Export AnalyticsReport to Google Sheets with multiple tabs.
        
        Returns:
            URL of the created/updated spreadsheet
        """
        # Prepare data for each sheet
        sheets_data = {}
        
        # Overview sheet
        overview_data = {
            'Report Period': f"{self.report.period.start_date} to {self.report.period.end_date}",
            'Generated At': self.report.generated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add channel info if available
        if hasattr(self.report.channel, 'export'):
            channel_data = self.report.channel.export()
            overview_data['Video Count'] = channel_data.get('video_count', 0)
            overview_data['Subscriber Count'] = channel_data.get('subscriber_count', 0)
            overview_data['Total View Count'] = channel_data.get('total_view_count', 0)
        
        # Add summary metrics
        if self.report.subscription_metrics:
            sub_data = self.report.subscription_metrics.export()
            overview_data['New Subscribers'] = sub_data.get('subscribers_gained', 0)
            overview_data['Lost Subscribers'] = sub_data.get('subscribers_lost', 0)
            overview_data['Net Change'] = sub_data.get('net_change', 0)
        
        if self.report.views_breakdown:
            views_data = self.report.views_breakdown.export()
            overview_data['Total Views'] = views_data.get('total_views', 0)
            overview_data['Video Views %'] = f"{views_data.get('video_percentage', 0):.1f}%"
            overview_data['Shorts Views %'] = f"{views_data.get('shorts_percentage', 0):.1f}%"
        
        if hasattr(self.report, 'revenue_metrics') and self.report.revenue_metrics:
            rev_data = self.report.revenue_metrics.export()
            overview_data['Total Revenue'] = f"${rev_data.get('total_revenue', 0):.2f}"
            overview_data['CPM'] = f"${rev_data.get('cpm', 0):.2f}"
        
        sheets_data['Overview'] = overview_data
        
        # Daily Metrics sheet
        if self.report.daily_metrics:
            daily_data = []
            for daily in self.report.daily_metrics:
                daily_dict = daily.export()
                # Format for better readability in sheets
                daily_data.append({
                    'Date': daily_dict.get('date', ''),
                    'Views': daily_dict.get('views', 0),
                    'Watch Time (hours)': round(daily_dict.get('watch_time_minutes', 0) / 60, 2),
                    'Avg View Duration (min)': round(daily_dict.get('average_view_duration_seconds', 0) / 60, 2),
                    'Subscribers Gained': daily_dict.get('subscribers_gained', 0),
                    'Subscribers Lost': daily_dict.get('subscribers_lost', 0),
                    'Net Subscribers': daily_dict.get('subscribers_gained', 0) - daily_dict.get('subscribers_lost', 0)
                })
            sheets_data['Daily Metrics'] = daily_data
        
        # Geographic Views sheet
        if self.report.geographic_views:
            geo_views_data = []
            for geo in self.report.geographic_views:
                geo_dict = geo.export()
                geo_views_data.append({
                    'Country': geo_dict.get('country_name', ''),
                    'Country Code': geo_dict.get('country_code', ''),
                    'Views': geo_dict.get('views', 0),
                    'Percentage': f"{geo_dict.get('percentage', 0):.2f}%"
                })
            sheets_data['Geographic Views'] = geo_views_data
        
        # Geographic Subscribers sheet
        if self.report.geographic_subscribers:
            geo_subs_data = []
            for geo in self.report.geographic_subscribers:
                geo_dict = geo.export()
                geo_subs_data.append({
                    'Country': geo_dict.get('country_name', ''),
                    'Country Code': geo_dict.get('country_code', ''),
                    'Subscribers': geo_dict.get('subscribers_gained', 0),
                    'Percentage': f"{geo_dict.get('percentage', 0):.2f}%"
                })
            sheets_data['Geographic Subscribers'] = geo_subs_data
        
        # Revenue sheet (if available)
        if hasattr(self.report, 'revenue_metrics') and self.report.revenue_metrics:
            rev_data = self.report.revenue_metrics.export()
            revenue_sheet = {
                'Period': f"{rev_data.get('period', {}).get('start_date', '')} to {rev_data.get('period', {}).get('end_date', '')}",
                'Total Revenue': f"${rev_data.get('total_revenue', 0):.2f}",
                'Ad Revenue': f"${rev_data.get('ad_revenue', 0):.2f}",
                'Premium Revenue': f"${rev_data.get('youtube_premium_revenue', 0):.2f}",
                'Transaction Revenue': f"${rev_data.get('transaction_revenue', 0):.2f}",
                'Fan Funding Revenue': f"${rev_data.get('fan_funding_revenue', 0):.2f}",
                'Total Views': rev_data.get('total_views', 0),
                'CPM': f"${rev_data.get('cpm', 0):.2f}",
                'RPM': f"${rev_data.get('rpm', 0):.2f}"
            }
            sheets_data['Revenue'] = revenue_sheet
        
        # Export all sheets
        return self.export_multi_sheet(sheets_data)