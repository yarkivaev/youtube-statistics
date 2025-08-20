"""YouTube API factory for GeographicMetrics."""

from typing import TYPE_CHECKING, List
from models.factories.base import Factory
from models import GeographicMetrics

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeGeographicFactory(Factory):
    """Factory that fetches geographic metrics from YouTube API.
    
    Returns a list of GeographicMetrics instances.
    """
    
    def __init__(self, api_client: 'YouTubeAPIClient'):
        """Initialize with API client.
        
        Args:
            api_client: YouTube API client for fetching data
        """
        self.api_client = api_client
    
    def create(self,
               fetch_type: str,
               start_date: str,
               end_date: str,
               **kwargs) -> List[GeographicMetrics]:
        """Fetch geographic metrics from YouTube API.
        
        Args:
            fetch_type: "views" or "subscribers"
            start_date: Start date for API query (ISO format)
            end_date: End date for API query (ISO format)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            List of GeographicMetrics instances
        """
        youtube_analytics = self.api_client.get_analytics_service()
        geo_metrics = []
        
        try:
            if fetch_type == "views":
                request = youtube_analytics.reports().query(
                    ids='channel==MINE',
                    startDate=start_date,
                    endDate=end_date,
                    metrics='views,estimatedMinutesWatched',
                    dimensions='country',
                    sort='-views',
                    maxResults=9
                )
                response = self.api_client.execute_request(request)
                
                if response and response.get('rows'):
                    for row in response['rows']:
                        geo = GeographicMetrics(
                            country_code=row[0],
                            views=row[1],
                            watch_time_minutes=row[2],
                            subscribers_gained=0  # Default value for views fetch
                        )
                        geo_metrics.append(geo)
                        
            elif fetch_type == "subscribers":
                request = youtube_analytics.reports().query(
                    ids='channel==MINE',
                    startDate=start_date,
                    endDate=end_date,
                    metrics='subscribersGained',
                    dimensions='country',
                    sort='-subscribersGained',
                    maxResults=5
                )
                response = self.api_client.execute_request(request)
                
                if response and response.get('rows'):
                    for row in response['rows']:
                        geo = GeographicMetrics(
                            country_code=row[0],
                            views=0,  # Default value for subscribers fetch
                            watch_time_minutes=0,  # Default value for subscribers fetch
                            subscribers_gained=row[1]
                        )
                        geo_metrics.append(geo)
                        
        except Exception as e:
            print(f"Error fetching geographic {fetch_type}: {e}")
        
        return geo_metrics