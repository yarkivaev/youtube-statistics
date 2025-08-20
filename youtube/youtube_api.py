"""YouTube API client wrapper."""

import os
import pickle
from typing import Tuple, Optional, Any
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


class YouTubeAPIClient:
    """Handles YouTube API authentication and service creation."""
    
    def __init__(self, client_secrets_file: str = "client_secrets.json",
                 token_file: str = "token.pickle"):
        """Initialize API client.
        
        Args:
            client_secrets_file: Path to OAuth client secrets file
            token_file: Path to store/load authentication token
        """
        self.client_secrets_file = client_secrets_file
        self.token_file = token_file
        self.scopes = [
            'https://www.googleapis.com/auth/yt-analytics.readonly',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
        self._youtube_analytics = None
        self._youtube_data = None
    
    def authenticate(self) -> Any:
        """Authenticate and return credentials."""
        credentials = None
        
        # Load credentials from file
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                credentials = pickle.load(token)
        
        # If no valid credentials, let user log in
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes)
                credentials = flow.run_local_server(port=0)
            
            # Save the credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(credentials, token)
        
        return credentials
    
    def get_services(self) -> Tuple[Any, Any]:
        """Get authenticated YouTube Analytics and Data API services.
        
        Returns:
            Tuple of (youtube_analytics_service, youtube_data_service)
        """
        if not self._youtube_analytics or not self._youtube_data:
            credentials = self.authenticate()
            self._youtube_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)
            self._youtube_data = build('youtube', 'v3', credentials=credentials)
        
        return self._youtube_analytics, self._youtube_data
    
    def get_analytics_service(self) -> Any:
        """Get YouTube Analytics API service."""
        analytics, _ = self.get_services()
        return analytics
    
    def get_data_service(self) -> Any:
        """Get YouTube Data API service."""
        _, data = self.get_services()
        return data
    
    def execute_request(self, request: Any) -> dict:
        """Execute API request with error handling.
        
        Args:
            request: API request object
            
        Returns:
            Response dict
            
        Raises:
            Exception: If API request fails
        """
        try:
            return request.execute()
        except Exception as e:
            print(f"API request failed: {e}")
            raise