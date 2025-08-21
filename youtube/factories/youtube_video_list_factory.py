"""YouTube API factory for fetching video list and counting by month."""

from typing import TYPE_CHECKING, Dict, Optional
from datetime import datetime
from models.factories.base import Factory

if TYPE_CHECKING:
    from youtube.youtube_api import YouTubeAPIClient


class YouTubeVideoListFactory(Factory):
    """Factory that fetches video upload counts by month from YouTube API."""
    
    def __init__(self, api_client: 'YouTubeAPIClient'):
        """Initialize with API client.
        
        Args:
            api_client: YouTube API client for fetching data
        """
        self.api_client = api_client
    
    def create(self,
               start_date: Optional[str] = None,
               end_date: Optional[str] = None,
               **kwargs) -> Dict[str, int]:
        """Fetch video counts by month from YouTube API.
        
        Args:
            start_date: Start date for filtering (ISO format)
            end_date: End date for filtering (ISO format)
            **kwargs: Additional arguments (ignored)
            
        Returns:
            Dictionary with month keys (YYYY-MM) and video count values
        """
        video_counts_by_month = {}
        
        youtube_data = self.api_client.get_data_service()
        
        try:
            # First, get the channel's uploads playlist ID
            channel_request = youtube_data.channels().list(
                part="contentDetails",
                mine=True
            )
            channel_response = self.api_client.execute_request(channel_request)
            
            if not channel_response or not channel_response.get('items'):
                print("No channel found for video list")
                return video_counts_by_month
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Fetch all videos from the uploads playlist
            next_page_token = None
            all_videos = []
            
            while True:
                playlist_request = youtube_data.playlistItems().list(
                    part="contentDetails",
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                )
                playlist_response = self.api_client.execute_request(playlist_request)
                
                if not playlist_response:
                    break
                
                video_ids = [item['contentDetails']['videoId'] 
                           for item in playlist_response.get('items', [])]
                
                if video_ids:
                    # Get video details including publishedAt
                    videos_request = youtube_data.videos().list(
                        part="snippet",
                        id=','.join(video_ids)
                    )
                    videos_response = self.api_client.execute_request(videos_request)
                    
                    if videos_response and videos_response.get('items'):
                        all_videos.extend(videos_response['items'])
                
                # Check for next page
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            # Count videos by month
            for video in all_videos:
                published_at_str = video['snippet'].get('publishedAt')
                if not published_at_str:
                    continue
                
                # Parse the date
                published_at = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                
                # Filter by date range if provided
                if start_date:
                    start_dt = datetime.fromisoformat(start_date)
                    if published_at.date() < start_dt.date():
                        continue
                
                if end_date:
                    end_dt = datetime.fromisoformat(end_date)
                    if published_at.date() > end_dt.date():
                        continue
                
                # Create month key
                month_key = f"{published_at.year}-{published_at.month:02d}"
                
                # Increment count for this month
                video_counts_by_month[month_key] = video_counts_by_month.get(month_key, 0) + 1
            
            print(f"Found video counts for {len(video_counts_by_month)} months")
            
        except Exception as e:
            print(f"Error fetching video list: {e}")
        
        return video_counts_by_month