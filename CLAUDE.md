# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube Statistics collector - A Python script that fetches YouTube channel analytics data using the YouTube Analytics API and stores it in a simple text file format.

## Setup and Environment

### Prerequisites
- Python 3.9.6 or higher
- Google Cloud Console project with YouTube Analytics API enabled
- OAuth 2.0 credentials (client_secrets.json)

### Initial Setup Commands
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies (if requirements.txt exists)
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Common Development Commands

```bash
# Run the analytics collector
python main.py

# Deactivate virtual environment when done
deactivate
```

## Architecture and Code Structure

### Core Components

**main.py** - Contains all application logic:
- `get_authenticated_service()`: Handles OAuth 2.0 authentication flow with token caching
- `get_youtube_analytics()`: Fetches daily analytics data and appends to output file

### Data Flow
1. **Authentication**: Uses OAuth 2.0 with token persistence via pickle
2. **API Request**: Fetches metrics (views, watchTime, averageViewDuration, subscribersGained, subscribersLost)
3. **Data Storage**: Appends results to youtube_analytics.txt in human-readable format

### File Structure
- `client_secrets.json` - Google API OAuth credentials (must be populated)
- `token.pickle` - Cached authentication token (auto-generated)
- `youtube_analytics.txt` - Analytics data output (append-only)
- `venv/` - Python virtual environment

## Key Implementation Details

### Authentication Pattern
The script uses Google's OAuth 2.0 flow with local token caching. On first run, it opens a browser for authentication. Subsequent runs use the cached token from `token.pickle`.

### Data Collection Strategy
- Fetches daily metrics from 2024-01-01 to current date
- Groups data by day with dimension filtering
- Appends new data to existing file rather than overwriting

### Error Handling Considerations
- The script currently lacks explicit error handling for API failures
- Token refresh is handled automatically by the Google auth library
- File operations use append mode to prevent data loss

## Development Guidelines

### When Modifying the Script
1. Preserve the append-only data storage pattern
2. Maintain backward compatibility with existing data format
3. Test authentication flow after any OAuth-related changes
4. Ensure virtual environment is activated before running

### Adding New Features
- Consider maintaining the simple, single-script architecture
- New metrics should follow the existing append format
- Any database migration should preserve historical data

### API Considerations
- YouTube Analytics API has quotas and rate limits
- The current date range (2024-01-01 to present) may need adjustment
- Channel ID is hardcoded and may need parameterization for multi-channel support