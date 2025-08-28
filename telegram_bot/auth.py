"""Google OAuth authentication handler for Telegram bot."""

import os
import pickle
import json
from urllib.parse import urlencode
import google_auth_oauthlib.flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from telegram_bot.config import CLIENT_SECRETS_FILE, SCOPES, TOKEN_DIR


def get_token_file(user_id: int) -> str:
    """Get token file path for a user."""
    return os.path.join(TOKEN_DIR, f'token_{user_id}.pickle')


def get_auth_state_file(user_id: int) -> str:
    """Get auth state file path for a user."""
    return os.path.join(TOKEN_DIR, f'auth_state_{user_id}.json')


def has_credentials(user_id: int) -> bool:
    """Check if user has stored credentials."""
    return os.path.exists(get_token_file(user_id))


def get_auth_url(user_id: int) -> str:
    """Generate Google OAuth URL for user authentication.
    
    Note: Since we can't use the standard flow.run_local_server() in a bot context,
    we'll construct the URL manually for the out-of-band flow.
    """
    # Load client secrets to get client ID
    with open(CLIENT_SECRETS_FILE, 'r') as f:
        client_config = json.load(f)
    
    if 'installed' in client_config:
        client_id = client_config['installed']['client_id']
    elif 'web' in client_config:
        client_id = client_config['web']['client_id']
    else:
        raise ValueError("Invalid client_secrets.json format")
    
    # Construct OAuth URL manually with all required parameters
    auth_params = {
        'client_id': client_id,
        'redirect_uri': 'urn:ietf:wg:oauth:2.0:oob',
        'response_type': 'code',  # This was missing!
        'scope': ' '.join(SCOPES),
        'access_type': 'offline',
        'prompt': 'consent',
        'include_granted_scopes': 'true'
    }
    
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"
    
    # Debug: Print the URL to console
    print(f"Generated OAuth URL: {auth_url}")
    
    # Store client config for later use
    state_file = get_auth_state_file(user_id)
    with open(state_file, 'w') as f:
        json.dump({
            'client_config': client_config,
            'scopes': SCOPES
        }, f)
    
    return auth_url


def save_credentials(user_id: int, auth_code: str) -> bool:
    """Save user credentials after authentication."""
    try:
        # Use the standard flow for exchanging the code
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES
        )
        
        # Set redirect URI to match the auth URL
        flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
        
        # Exchange auth code for credentials
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Save credentials
        token_file = get_token_file(user_id)
        with open(token_file, 'wb') as f:
            pickle.dump(credentials, f)
        
        # Clean up state file
        state_file = get_auth_state_file(user_id)
        if os.path.exists(state_file):
            os.remove(state_file)
        
        return True
        
    except Exception as e:
        print(f"Error saving credentials: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_credentials(user_id: int):
    """Get valid credentials for a user."""
    token_file = get_token_file(user_id)
    
    if not os.path.exists(token_file):
        return None
    
    try:
        with open(token_file, 'rb') as f:
            credentials = pickle.load(f)
        
        # Refresh if expired
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # Save refreshed credentials
            with open(token_file, 'wb') as f:
                pickle.dump(credentials, f)
        
        return credentials
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return None


def get_youtube_services(user_id: int):
    """Get YouTube API services for a user."""
    credentials = get_credentials(user_id)
    if not credentials:
        return None, None
    
    try:
        youtube_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)
        youtube_data = build('youtube', 'v3', credentials=credentials)
        return youtube_analytics, youtube_data
    except Exception as e:
        print(f"Error building YouTube services: {e}")
        return None, None


def delete_credentials(user_id: int) -> bool:
    """Delete user credentials (for re-authentication)."""
    token_file = get_token_file(user_id)
    state_file = get_auth_state_file(user_id)
    
    deleted = False
    if os.path.exists(token_file):
        os.remove(token_file)
        deleted = True
    
    if os.path.exists(state_file):
        os.remove(state_file)
    
    return deleted