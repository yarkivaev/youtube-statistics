"""Main script for YouTube Analytics - fetches data and updates Google Sheets."""

import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

# Import modular components
from youtube.youtube_api import YouTubeAPIClient
from youtube.youtube_metrics_factory import YouTubeMetricsFactory


def parse_arguments() -> Tuple[str, Optional[List[int]], Optional[Tuple[str, str]], bool, Optional[List[str]], bool]:
    """Parse command line arguments.
    
    Returns:
        Tuple of (spreadsheet_id, channel_indices, date_filter, dry_run, channel_names, skip_revenue)
    """
    # Default values
    spreadsheet_id = "1YBazG-UVCnSYwYjSKmXwaySVFDaQuifsL14aWTq7S9U"  # Default spreadsheet
    channel_indices = None
    date_filter = None
    dry_run = False
    channel_names = None
    skip_revenue = False
    
    # Parse flags
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    skip_revenue = '--skip-revenue' in sys.argv
    
    # Parse date range
    start_date = None
    end_date = None
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg in ['--range', '-r'] and i < len(sys.argv) - 1:
            # Handle range like "2024-01-01:2024-12-31"
            date_range = sys.argv[i + 1].split(':')
            if len(date_range) == 2:
                start_date = date_range[0]
                end_date = date_range[1]
        elif arg in ['--start', '--from'] and i < len(sys.argv) - 1:
            start_date = sys.argv[i + 1]
        elif arg in ['--end', '--to'] and i < len(sys.argv) - 1:
            end_date = sys.argv[i + 1]
        elif arg in ['--channel', '--channels'] and i < len(sys.argv) - 1:
            # Parse channel names (comma-separated)
            channel_names = sys.argv[i + 1].split(',')
            channel_names = [name.strip() for name in channel_names]
    
    if start_date or end_date:
        date_filter = (start_date, end_date)
    
    # Get non-flag arguments
    args = []
    skip_next = False
    for i, arg in enumerate(sys.argv[1:]):
        if skip_next:
            skip_next = False
            continue
        if arg.startswith('-'):
            # Check if this flag has a value
            if arg in ['--range', '-r', '--start', '--from', '--end', '--to', '--channel', '--channels']:
                skip_next = True
            continue
        if ':' not in arg:  # Skip date ranges
            args.append(arg)
    
    # First non-flag arg is spreadsheet ID
    if args:
        spreadsheet_id = args[0]
    
    # Parse channel indices if provided (e.g., "0,1,2" or "1")
    if len(args) > 1:
        try:
            if ',' in args[1]:
                channel_indices = [int(x) for x in args[1].split(',')]
            else:
                channel_indices = [int(args[1])]
        except ValueError:
            print(f"Invalid channel indices: {args[1]}")
            print("Use format: 0,1,2 or just 1 for single channel")
            sys.exit(1)
    
    return spreadsheet_id, channel_indices, date_filter, dry_run, channel_names, skip_revenue


def resolve_channel_identifier(youtube_data_service, channel_identifier: str) -> Optional[str]:
    """Resolve a channel name, handle, or ID to a channel ID.
    
    Args:
        youtube_data_service: YouTube Data API v3 service
        channel_identifier: Channel name, @handle, or channel ID
    
    Returns:
        Channel ID string or None if not found
    """
    if not channel_identifier:
        return None
    
    try:
        # If it starts with @, search by handle
        if channel_identifier.startswith('@'):
            response = youtube_data_service.channels().list(
                part="id,snippet",
                forHandle=channel_identifier[1:]  # Remove @ prefix
            ).execute()
            
            if response.get('items'):
                channel_id = response['items'][0]['id']
                channel_name = response['items'][0]['snippet']['title']
                print(f"  Found channel by handle: {channel_name} ({channel_id})")
                return channel_id
        
        # If it looks like a channel ID (starts with UC), use it directly
        elif channel_identifier.startswith('UC') and len(channel_identifier) == 24:
            # Verify it exists
            response = youtube_data_service.channels().list(
                part="id,snippet",
                id=channel_identifier
            ).execute()
            
            if response.get('items'):
                channel_name = response['items'][0]['snippet']['title']
                print(f"  Using channel ID: {channel_name} ({channel_identifier})")
                return channel_identifier
        
        # Otherwise, search by channel name
        else:
            # Search for channels matching the name
            search_response = youtube_data_service.search().list(
                part="id,snippet",
                q=channel_identifier,
                type="channel",
                maxResults=5
            ).execute()
            
            if search_response.get('items'):
                # Find exact match or closest match
                for item in search_response['items']:
                    if item['snippet']['channelTitle'].lower() == channel_identifier.lower():
                        channel_id = item['snippet']['channelId']
                        channel_name = item['snippet']['channelTitle']
                        print(f"  Found channel by name: {channel_name} ({channel_id})")
                        return channel_id
                
                # If no exact match, use first result
                channel_id = search_response['items'][0]['snippet']['channelId']
                channel_name = search_response['items'][0]['snippet']['channelTitle']
                print(f"  Found channel (closest match): {channel_name} ({channel_id})")
                return channel_id
    
    except Exception as e:
        print(f"  Error resolving channel: {e}")
    
    return None


def update_channel_in_spreadsheet(
    api_client: YouTubeAPIClient,
    spreadsheet_id: str,
    channel_id: Optional[str],
    date_filter: Optional[Tuple[str, str]],
    dry_run: bool,
    skip_revenue: bool = False
) -> None:
    """Update a single channel's data in the spreadsheet.
    
    Args:
        api_client: YouTube API client
        spreadsheet_id: Google Sheets ID
        channel_id: Optional channel ID (None uses authenticated channel)
        date_filter: Optional date range filter
        dry_run: If True, show what would be done without making changes
        skip_revenue: If True, skip fetching revenue data
    """
    # Determine date range
    if date_filter:
        start_str, end_str = date_filter
        if start_str and end_str:
            from models import DateRange
            from datetime import date as dt_date
            period = DateRange(
                start_date=dt_date.fromisoformat(start_str),
                end_date=dt_date.fromisoformat(end_str)
            )
        else:
            period = None
    else:
        period = None
    
    # Create composite factory with all configuration
    youtube_factory = YouTubeMetricsFactory(
        api_client=api_client,
        period=period,
        skip_revenue=skip_revenue,
        exportable=not dry_run,
        spreadsheet_id=spreadsheet_id if not dry_run else None,
        sheet_name='YouTube'  # Hardcoded sheet name
    )
    
    # Create report (YouTubeMetrics or YoutubeMetricsSheetsReport)
    print("Fetching analytics data...")
    report = youtube_factory.create()
    
    if dry_run:
        print("\n" + "="*60)
        print("DRY RUN MODE - No changes will be made")
        print("="*60)
        print(f"\nWould update spreadsheet: {spreadsheet_id}")
        print(f"Channel ID: {channel_id or 'Authenticated channel'}")
        print(f"Period: {report.period.start_date} to {report.period.end_date}")
        print(f"Total views: {sum(dm.views for dm in report.daily_metrics) if report.daily_metrics else 0}")
        print(f"Subscribers gained: {report.subscription_metrics.subscribers_gained if report.subscription_metrics else 0}")
        print(f"Subscribers lost: {report.subscription_metrics.subscribers_lost if report.subscription_metrics else 0}")
    else:
        # Export using the report's export method
        print(f"\nExporting to Google Sheets...")
        url = report.export()
        print(f"\nSuccessfully updated spreadsheet")
        print(f"View at: {url}")


def main():
    """Main function to handle command line execution.
    
    Usage:
        python main.py <spreadsheet_id> <channel_index> [options]
        python main.py <spreadsheet_id> <channel_index> --channel <channel_name/handle/id> [options]
        
    Examples:
        # Update with default (authenticated) channel data
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0
        
        # Update with specific channel by name
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0 --channel "MrBeast"
        
        # Update with specific channel by handle
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0 --channel "@MrBeast"
        
        # Update with date range
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0 --range 2024-01-01:2024-12-31
        
        # Skip revenue data (for non-Partner accounts)
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0 --skip-revenue
        
        # Dry run to see what would be updated
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0 --dry-run
    """
    print("YouTube Analytics")
    print("="*60)
    
    # Parse arguments
    spreadsheet_id, channel_indices, date_filter, dry_run, channel_names, skip_revenue = parse_arguments()
    
    if date_filter:
        print(f"Date filter: {date_filter[0] or 'any'} to {date_filter[1] or 'any'}")
    if skip_revenue:
        print("Skipping revenue data (--skip-revenue flag set)")
    
    # Initialize API client
    api_client = YouTubeAPIClient()
    
    # Get YouTube Data service for channel resolution
    _, youtube_data = api_client.get_services()
    
    # Resolve channel names to IDs if provided
    channel_ids = []
    if channel_names:
        print(f"\nResolving channel identifiers...")
        for name in channel_names:
            channel_id = resolve_channel_identifier(youtube_data, name)
            if channel_id:
                channel_ids.append(channel_id)
            else:
                print(f"  Warning: Could not resolve channel '{name}'")
                channel_ids.append(None)
    
    # If no specific channel indices, update first channel
    if channel_indices is None:
        channel_indices = [0]
    
    # Update each channel
    for i, idx in enumerate(channel_indices):
        print(f"\n{'='*60}")
        print(f"Processing Channel {idx}")
        print(f"{'='*60}")
        
        # Get channel ID for this index if available
        channel_id = channel_ids[i] if i < len(channel_ids) else None
        
        try:
            update_channel_in_spreadsheet(
                api_client=api_client,
                spreadsheet_id=spreadsheet_id,
                channel_id=channel_id,
                date_filter=date_filter,
                dry_run=dry_run,
                skip_revenue=skip_revenue
            )
        except Exception as e:
            print(f"Error updating channel {idx}: {e}")
            if not dry_run:
                print("Continuing with next channel...")
    
    print(f"\n{'='*60}")
    print("Completed")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()