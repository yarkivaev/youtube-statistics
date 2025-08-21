"""Factory for creating monthly aggregated metrics from daily metrics."""

from typing import Dict, Any, List
from ..monthly_metrics import MonthlyMetrics
from ..daily_metrics import DailyMetrics
from .base import Factory


class MonthlyMetricsFactory(Factory):
    """Factory for creating monthly aggregated metrics from daily metrics."""
    
    def __init__(self, daily_metrics: List[DailyMetrics], video_counts_by_month: Dict[str, int] = None):
        """Initialize the factory.
        
        Args:
            daily_metrics: List of DailyMetrics to aggregate
            video_counts_by_month: Optional dictionary with month keys (YYYY-MM) and video count values
        """
        self.daily_metrics = daily_metrics
        self.video_counts_by_month = video_counts_by_month or {}
    
    def create(self, **kwargs) -> Dict[str, Dict[str, Any]]:
        """Create monthly aggregated metrics.
        
        Returns:
            Dictionary with month keys (YYYY-MM) and aggregated metrics
        """
        monthly_data = {}
        
        for daily in self.daily_metrics:
            if not daily.date:
                continue
                
            month_key = f"{daily.date.year}-{daily.date.month:02d}"
            
            # Create monthly metrics if needed
            if month_key not in monthly_data:
                monthly_data[month_key] = MonthlyMetrics(month_key)
            
            # Aggregate daily metrics
            monthly = monthly_data[month_key]
            monthly.views += daily.views
            monthly.watch_time_minutes += daily.watch_time_minutes
            monthly.subscribers_gained += daily.subscribers_gained
            monthly.subscribers_lost += daily.subscribers_lost
            
            # Count days with activity
            if daily.views > 0:
                monthly.days_with_data += 1
        
        # Add video counts if available
        for month_key, monthly in monthly_data.items():
            if month_key in self.video_counts_by_month:
                monthly.video_count = self.video_counts_by_month[month_key]
        
        # Return exported data
        return {
            month_key: metrics.export() 
            for month_key, metrics in monthly_data.items()
        }