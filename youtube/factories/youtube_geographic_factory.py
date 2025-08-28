"""YouTube API factory for GeographicMetrics."""

from typing import TYPE_CHECKING, List
from domain import Factory, GeographicMetrics

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
                    sort='-views'
                    # Removed maxResults to get all countries
                )
                response = self.api_client.execute_request(request)
                
                # Debug the raw response
                print(f"Raw API response: {response}")
                
                if response and response.get('rows'):
                    print(f"Geographic views API returned {len(response['rows'])} countries")
                    print(f"First few rows: {response['rows'][:5] if len(response['rows']) > 5 else response['rows']}")
                    
                    # Process ALL countries returned by the API
                    for row in response['rows']:
                        geo = GeographicMetrics(
                            country_code=row[0],
                            views=row[1],
                            watch_time_minutes=row[2],
                            subscribers_gained=0  # Default value for views fetch
                        )
                        geo_metrics.append(geo)
                        print(f"Added country {row[0]} with {row[1]} views")
                    
                    print(f"Created {len(geo_metrics)} GeographicMetrics objects")
                    # Log total views for debugging
                    total_views = sum(g.views for g in geo_metrics)
                    print(f"Total views from all countries: {total_views}")
                else:
                    print("No geographic data returned by API")
                        
            elif fetch_type == "subscribers":
                request = youtube_analytics.reports().query(
                    ids='channel==MINE',
                    startDate=start_date,
                    endDate=end_date,
                    metrics='subscribersGained',
                    dimensions='country',
                    sort='-subscribersGained'
                    # Removed maxResults to get all countries
                )
                response = self.api_client.execute_request(request)
                
                if response and response.get('rows'):
                    print(f"Geographic subscribers API returned {len(response['rows'])} countries")
                    # Process ALL countries returned by the API
                    for row in response['rows']:
                        geo = GeographicMetrics(
                            country_code=row[0],
                            views=0,  # Default value for subscribers fetch
                            watch_time_minutes=0,  # Default value for subscribers fetch
                            subscribers_gained=row[1]
                        )
                        geo_metrics.append(geo)
                    print(f"Created {len(geo_metrics)} GeographicMetrics objects for subscribers")
                        
        except Exception as e:
            print(f"Error fetching geographic {fetch_type}: {e}")
        
        return geo_metrics