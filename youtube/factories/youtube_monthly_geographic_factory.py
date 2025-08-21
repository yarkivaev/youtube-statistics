"""YouTube API factory for fetching geographic metrics by month."""

from typing import TYPE_CHECKING, Dict, List
from datetime import datetime, date, timedelta
from models import GeographicMetrics
from models.factories.base import Factory

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeMonthlyGeographicFactory(Factory):
    """Factory that fetches geographic metrics for each month from YouTube API."""
    
    def __init__(self, api_client: 'YouTubeAPIClient'):
        """Initialize with API client.
        
        Args:
            api_client: YouTube API client for fetching data
        """
        self.api_client = api_client
    
    def _fetch_month_geographic(self, 
                               year: int, 
                               month: int, 
                               fetch_type: str,
                               max_results: int) -> List[GeographicMetrics]:
        """Fetch geographic data for a specific month.
        
        Args:
            year: Year to fetch
            month: Month to fetch (1-12)
            fetch_type: "views" or "subscribers"
            max_results: Maximum number of countries to return
            
        Returns:
            List of GeographicMetrics for the month
        """
        # Calculate month start and end dates
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        youtube_analytics = self.api_client.get_analytics_service()
        geo_metrics = []
        
        try:
            if fetch_type == "views":
                request = youtube_analytics.reports().query(
                    ids='channel==MINE',
                    startDate=start_date.isoformat(),
                    endDate=end_date.isoformat(),
                    metrics='views,estimatedMinutesWatched',
                    dimensions='country',
                    sort='-views',
                    maxResults=max_results
                )
                response = self.api_client.execute_request(request)
                
                if response and response.get('rows'):
                    for row in response['rows']:
                        geo = GeographicMetrics(
                            country_code=row[0],
                            views=row[1],
                            watch_time_minutes=row[2] if len(row) > 2 else 0,
                            subscribers_gained=0
                        )
                        geo_metrics.append(geo)
                        
            elif fetch_type == "subscribers":
                request = youtube_analytics.reports().query(
                    ids='channel==MINE',
                    startDate=start_date.isoformat(),
                    endDate=end_date.isoformat(),
                    metrics='subscribersGained',
                    dimensions='country',
                    sort='-subscribersGained',
                    maxResults=max_results
                )
                response = self.api_client.execute_request(request)
                
                if response and response.get('rows'):
                    for row in response['rows']:
                        geo = GeographicMetrics(
                            country_code=row[0],
                            views=0,
                            watch_time_minutes=0,
                            subscribers_gained=row[1]
                        )
                        geo_metrics.append(geo)
                        
        except Exception as e:
            print(f"Error fetching geographic {fetch_type} for {year}-{month:02d}: {e}")
        
        return geo_metrics
    
    def create(self,
               start_date: str,
               end_date: str,
               fetch_type: str,
               max_results: int = 9,
               **kwargs) -> Dict[str, List[GeographicMetrics]]:
        """Fetch geographic metrics for each month in the period.
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            fetch_type: "views" or "subscribers"
            max_results: Maximum countries per month (default 9 for views, should be 5 for subscribers)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            Dictionary with month keys (YYYY-MM) and lists of GeographicMetrics
        """
        monthly_geographic = {}
        
        # Parse dates
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        # Iterate through each month in the period
        current = start
        while current <= end:
            month_key = f"{current.year}-{current.month:02d}"
            
            # Fetch geographic data for this month
            geo_data = self._fetch_month_geographic(
                current.year,
                current.month,
                fetch_type,
                max_results
            )
            
            if geo_data:
                monthly_geographic[month_key] = geo_data
            
            # Move to next month
            if current.month == 12:
                current = date(current.year + 1, 1, 1)
            else:
                current = date(current.year, current.month + 1, 1)
        
        print(f"Fetched {fetch_type} geographic data for {len(monthly_geographic)} months")
        return monthly_geographic