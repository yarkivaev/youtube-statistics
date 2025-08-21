"""JSON Report wrapper for YouTubeMetrics model."""

from models import YouTubeMetrics
from typing import Dict, Any, List
from datetime import datetime
from .json_report import JsonReport


class YoutubeMetricsJsonReport:
    """JSON exporter for YouTubeMetrics model.
    
    Creates a structured JSON output with organized analytics data
    similar to the spreadsheet report structure.
    """
    
    def __init__(self, report: YouTubeMetrics):
        """Initialize with YouTubeMetrics instance.
        
        Args:
            report: YouTubeMetrics instance to export
        """
        self.report = report
        
        # Initialize monthly data aggregation
        self._initialize_monthly_data()
    
    def _initialize_monthly_data(self):
        """Initialize monthly aggregation of metrics."""
        from models.factories import MonthlyMetricsFactory
        
        # Create monthly aggregation factory using the report's daily metrics
        self.monthly_factory = MonthlyMetricsFactory(self.report.daily_metrics)
        self.monthly_data = self.monthly_factory.create()
    
    def _format_channel_section(self) -> Dict[str, Any]:
        """Format channel information section."""
        return {
            "title": "Channel Information",
            "data": self.report.channel.to_dict()
        }
    
    def _format_period_section(self) -> Dict[str, Any]:
        """Format period information section."""
        return {
            "title": "Reporting Period", 
            "data": self.report.period.to_dict()
        }
    
    def _format_summary_section(self) -> Dict[str, Any]:
        """Format summary metrics section."""
        total_views = sum(dm.views for dm in self.report.daily_metrics) if self.report.daily_metrics else 0
        total_watch_hours = sum(dm.watch_time_minutes for dm in self.report.daily_metrics) / 60 if self.report.daily_metrics else 0
        
        return {
            "title": "Summary Metrics",
            "data": {
                "total_views": total_views,
                "total_watch_time_hours": round(total_watch_hours, 2),
                "subscribers_gained": self.report.subscription_metrics.subscribers_gained,
                "subscribers_lost": self.report.subscription_metrics.subscribers_lost,
                "net_subscribers": self.report.subscription_metrics.net_change,
                "total_revenue": float(self.report.revenue_metrics.total_revenue) if self.report.revenue_metrics else 0,
                "active_days": sum(1 for dm in self.report.daily_metrics if dm.has_activity)
            }
        }
    
    def _format_monthly_metrics_section(self) -> Dict[str, Any]:
        """Format monthly metrics section."""
        monthly_metrics = []
        
        for month_key in sorted(self.monthly_data.keys()):
            month_data = self.monthly_data[month_key]
            monthly_metrics.append({
                "month": month_key,
                "year": month_data.get('year'),
                "month_number": month_data.get('month'),
                "views": month_data.get('views', 0),
                "watch_time_hours": round(month_data.get('watch_time_minutes', 0) / 60, 2),
                "average_view_duration_minutes": round(month_data.get('average_view_duration_seconds', 0) / 60, 2),
                "subscribers_gained": month_data.get('subscribers_gained', 0),
                "subscribers_lost": month_data.get('subscribers_lost', 0),
                "net_subscribers": month_data.get('subscribers_gained', 0) - month_data.get('subscribers_lost', 0),
                "revenue": float(month_data.get('estimated_revenue', 0)),
                "active_days": month_data.get('active_days', 0)
            })
        
        return {
            "title": "Monthly Metrics",
            "data": monthly_metrics
        }
    
    def _format_daily_metrics_section(self) -> Dict[str, Any]:
        """Format daily metrics section."""
        daily_metrics = []
        
        for dm in self.report.daily_metrics:
            daily_metrics.append({
                "date": dm.date.isoformat(),
                "views": dm.views,
                "watch_time_minutes": dm.watch_time_minutes,
                "average_view_duration_seconds": dm.average_view_duration_seconds,
                "subscribers_gained": dm.subscribers_gained,
                "subscribers_lost": dm.subscribers_lost,
                "net_subscribers": dm.net_subscribers,
                "revenue": float(dm.estimated_revenue),
                "has_activity": dm.has_activity
            })
        
        return {
            "title": "Daily Metrics",
            "data": daily_metrics
        }
    
    def _format_views_breakdown_section(self) -> Dict[str, Any]:
        """Format views breakdown section."""
        return {
            "title": "Views Breakdown",
            "data": self.report.views_breakdown.to_dict() if self.report.views_breakdown else {}
        }
    
    def _format_revenue_section(self) -> Dict[str, Any]:
        """Format revenue metrics section."""
        if not self.report.revenue_metrics:
            return {
                "title": "Revenue Metrics",
                "data": {"message": "Revenue data not available"}
            }
        
        revenue_data = self.report.revenue_metrics.to_dict()
        
        # Add best performing day if available
        if self.report.revenue_metrics.daily_revenue:
            best_day = self.report.revenue_metrics.get_best_day()
            revenue_data['best_performing_day'] = {
                "date": best_day.date.isoformat(),
                "revenue": float(best_day.estimated_revenue)
            }
        
        return {
            "title": "Revenue Metrics",
            "data": revenue_data
        }
    
    def _format_geographic_section(self) -> Dict[str, Any]:
        """Format geographic metrics section."""
        geo_data = {
            "views_by_country": [],
            "subscribers_by_country": []
        }
        
        # Top countries by views
        if self.report.geographic_views:
            top_views = sorted(
                self.report.geographic_views, 
                key=lambda x: x.views, 
                reverse=True
            )[:10]
            total_views = sum(gv.views for gv in self.report.geographic_views)
            if total_views > 0:
                geo_data["views_by_country"] = [
                    {
                        "country": g.country_code,
                        "country_name": g.country_name,
                        "views": g.views,
                        "watch_time_minutes": g.watch_time_minutes,
                        "percentage": round((g.views / total_views) * 100, 2)
                    } for g in top_views
                ]
        
        # Top countries by subscribers
        if self.report.geographic_subscribers:
            top_subs = sorted(
                self.report.geographic_subscribers, 
                key=lambda x: x.subscribers_gained, 
                reverse=True
            )[:10]
            total_subs = sum(gs.subscribers_gained for gs in self.report.geographic_subscribers)
            if total_subs > 0:
                geo_data["subscribers_by_country"] = [
                    {
                        "country": g.country_code,
                        "country_name": g.country_name,
                        "subscribers": g.subscribers_gained,
                        "percentage": round((g.subscribers_gained / total_subs) * 100, 2)
                    } for g in top_subs
                ]
        
        return {
            "title": "Geographic Distribution",
            "data": geo_data
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert YouTubeMetrics to structured dictionary.
        
        Returns:
            Dictionary with organized sections similar to spreadsheet structure
        """
        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "YouTube Analytics Report",
                "format_version": "2.0"
            },
            "sections": {
                "channel": self._format_channel_section(),
                "period": self._format_period_section(),
                "summary": self._format_summary_section(),
                "monthly_metrics": self._format_monthly_metrics_section(),
                "daily_metrics": self._format_daily_metrics_section(),
                "views_breakdown": self._format_views_breakdown_section(),
                "revenue": self._format_revenue_section(),
                "geographic": self._format_geographic_section()
            }
        }
    
    def export(self, filename: str = "youtube_analytics.json") -> str:
        """Export to JSON file.
        
        Args:
            filename: Name of the file to export to
            
        Returns:
            Path to the exported file
        """
        # Convert to structured dictionary
        data_dict = self.to_dict()
        
        # Create JSON exporter and export
        json_exporter = JsonReport(data_dict)
        json_content = json_exporter.export()
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_content)
        
        return filename
    
    # Delegate attribute access to the wrapped report
    def __getattr__(self, name):
        """Delegate attribute access to the wrapped report."""
        return getattr(self.report, name)