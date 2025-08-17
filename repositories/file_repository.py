"""File-based implementation of AnalyticsRepository."""

import json
import os
from typing import Optional, Union, List
from datetime import datetime
from pathlib import Path

from models import AnalyticsReport, DateRange
from .base import AnalyticsRepository


class FileRepository(AnalyticsRepository):
    """File-based repository for analytics reports."""
    
    def __init__(self, base_path: str = "data/reports"):
        """Initialize repository with base path.
        
        Args:
            base_path: Directory to store report files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def load(self, period: Optional[Union[DateRange, str]] = None) -> Optional[Union[AnalyticsReport, List[AnalyticsReport]]]:
        """Load analytics report(s) from files.
        
        Args:
            period: Can be:
                - None or "latest": Load the latest report
                - DateRange: Load report for specific date range
                - "all": Load all available reports
            
        Returns:
            - Single AnalyticsReport if period is DateRange, None, or "latest"
            - List of AnalyticsReport if period is "all"
            - None if no matching report found
        """
        # Handle "all" case - return all reports
        if period == "all":
            return self._load_all_reports()
        
        # Handle "latest" or None case - return most recent report
        if period is None or period == "latest":
            return self._load_latest_report()
        
        # Handle DateRange case - return specific report
        if isinstance(period, DateRange):
            return self._load_report_by_period(period)
        
        # Invalid period type
        raise ValueError(f"Invalid period type: {type(period)}")
    
    def _load_all_reports(self) -> List[AnalyticsReport]:
        """Load all available reports from files."""
        reports = []
        for file_path in self.base_path.glob("report_*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Here you would deserialize the JSON to AnalyticsReport
                    # For now, we'll just return empty list as placeholder
                    pass
            except Exception:
                continue
        return reports
    
    def _load_latest_report(self) -> Optional[AnalyticsReport]:
        """Load the most recently created report."""
        files = list(self.base_path.glob("report_*.json"))
        if not files:
            return None
        
        # Get most recent file by modification time
        latest_file = max(files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
                # Here you would deserialize the JSON to AnalyticsReport
                # For now, returning None as placeholder
                return None
        except Exception:
            return None
    
    def _load_report_by_period(self, period: DateRange) -> Optional[AnalyticsReport]:
        """Load report for specific date range."""
        # Generate filename based on period
        filename = f"report_{period.start_date}_{period.end_date}.json"
        file_path = self.base_path / filename
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Here you would deserialize the JSON to AnalyticsReport
                # For now, returning None as placeholder
                return None
        except Exception:
            return None