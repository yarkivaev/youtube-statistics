"""Base repository abstraction."""

from abc import ABC, abstractmethod
from typing import Optional, Union, List
from datetime import date
from models import AnalyticsReport, DateRange


class AnalyticsRepository(ABC):
    """Abstract base class for analytics data persistence."""
    
    @abstractmethod
    def load(self, period: Optional[Union[DateRange, str]] = None) -> Optional[Union[AnalyticsReport, List[AnalyticsReport]]]:
        """Load analytics report(s).
        
        Args:
            period: Can be:
                - None: Load the latest report
                - DateRange: Load report for specific date range
                - "all": Load all available reports
                - "latest": Load the latest report (same as None)
            
        Returns:
            - Single AnalyticsReport if period is DateRange, None, or "latest"
            - List of AnalyticsReport if period is "all"
            - None if no matching report found
        """
        pass