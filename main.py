"""Main script for YouTube Analytics - fetches data and updates Google Sheets."""

import gspread
import gspread.utils
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os
import json
from datetime import datetime, timedelta
from collections import defaultdict
import sys

# Russian month names mapping
MONTH_NAMES_RU = {
    1: 'янв', 2: 'февр', 3: 'мар', 4: 'апр', 5: 'мая', 6: 'июн',
    7: 'июл', 8: 'авг', 9: 'сент', 10: 'окт', 11: 'нояб', 12: 'дек'
}

class ChannelSection:
    """Represents a channel's section in the spreadsheet."""
    
    def __init__(self, name, start_row, end_row):
        self.name = name
        self.start_row = start_row
        self.end_row = end_row
        self.metric_rows = {}
        self.month_columns = {}
    
    def __repr__(self):
        return f"ChannelSection({self.name}, rows {self.start_row}-{self.end_row})"

def authenticate():
    """Authenticate with Google APIs and return both clients."""
    token_path = 'token.pickle'
    creds = None
    
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/yt-analytics.readonly',
        'https://www.googleapis.com/auth/youtube.readonly'
    ]
    
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except:
            creds = None
    
    if not creds or not creds.valid:
        if os.path.exists('client_secrets.json'):
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)
    
    # Return Google Sheets client, YouTube Analytics service, and YouTube Data service
    sheets_client = gspread.authorize(creds)
    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=creds)
    youtube_data = build('youtube', 'v3', credentials=creds)
    
    return sheets_client, youtube_analytics, youtube_data

def parse_month_header(header):
    """Parse month header like 'дек. 2024' to (2024, 12)."""
    if not header:
        return None
    
    # Clean up the header
    header = header.strip()
    
    # Handle both formats: "мая 2025" and "мая. 2025"
    parts = header.replace('.', '').split()
    if len(parts) < 2:
        return None
        
    month_str = parts[0]
    year_str = parts[1]
    
    # Find month number
    month_num = None
    for num, name in MONTH_NAMES_RU.items():
        if name in month_str or month_str in name:
            month_num = num
            break
    
    if month_num and year_str.isdigit():
        return (int(year_str), month_num)
    return None

def find_channel_sections(worksheet):
    """Find all channel sections in the worksheet.
    
    Each channel section contains the same structure with 'Количество роликов' as a key marker.
    """
    values = worksheet.get_all_values()
    channels = []
    
    # Find all rows with 'Количество роликов' - this marks the start of each channel's data
    video_count_rows = []
    for row_idx, row in enumerate(values):
        if row and row[0] and 'Количество роликов' in str(row[0]):
            video_count_rows.append(row_idx + 1)  # 1-based row number
    
    print(f"  Found {len(video_count_rows)} channel sections at rows: {video_count_rows}")
    
    # Create channel sections based on these markers
    for i, start_row in enumerate(video_count_rows):
        # Each section starts 2 rows before "Количество роликов" (for headers)
        section_start = max(1, start_row - 2)
        
        # Section ends just before the next channel's section starts
        if i < len(video_count_rows) - 1:
            section_end = video_count_rows[i + 1] - 3
        else:
            section_end = len(values)
        
        channel_name = f"Channel_{i+1}"
        channel = ChannelSection(channel_name, section_start, section_end)
        channels.append(channel)
        print(f"  {channel_name}: rows {section_start}-{section_end}")
    
    # If no sections found, treat the whole sheet as one channel
    if not channels:
        print("  No channel markers found, treating as single channel")
        channels.append(ChannelSection("Channel_1", 1, len(values)))
    
    return channels

def add_missing_month_columns(worksheet, channel_section, existing_columns, date_filter, header_row):
    """Add missing month columns to the spreadsheet.
    
    Returns:
        True if columns were added, False otherwise
    """
    if not date_filter:
        return False
    
    start_str, end_str = date_filter
    if not end_str:
        return False
    
    # Parse end date to find which months we need
    end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
    
    # Find the last existing column
    if not existing_columns:
        return False
    
    last_month = max(existing_columns.keys())
    last_col = existing_columns[last_month]
    
    # Generate list of months we need
    needed_months = []
    current = datetime(last_month[0], last_month[1], 1)
    
    while True:
        # Move to next month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)
        
        # Check if we've gone past the end date
        if current.date() > end_date:
            break
        
        month_key = (current.year, current.month)
        if month_key not in existing_columns:
            needed_months.append(month_key)
    
    if not needed_months:
        return False
    
    print(f"  Adding {len(needed_months)} new month columns: {', '.join([f'{MONTH_NAMES_RU[m]} {y}' for y, m in needed_months])}")
    
    # Prepare all column insertions and headers in batch
    requests = []
    headers_to_update = []
    
    for year, month in needed_months:
        # Move to next position (3 columns after last)
        last_col += 3
        
        # Format month header
        month_name = MONTH_NAMES_RU[month]
        if month == 5:  # May uses genitive case
            header = f"{month_name} {year}"
        else:
            header = f"{month_name}. {year}"
        
        # Add insert dimension request
        requests.append({
            "insertDimension": {
                "range": {
                    "sheetId": worksheet.id,
                    "dimension": "COLUMNS",
                    "startIndex": last_col - 1,  # 0-based index
                    "endIndex": last_col + 2  # 0-based exclusive (insert 3 columns)
                },
                "inheritFromBefore": True
            }
        })
        
        # Store header update info
        headers_to_update.append((header_row, last_col, header))
        print(f"    Will add {header} at column {last_col}")
    
    # Execute all column insertions in one batch
    if requests:
        print(f"  Inserting {len(requests) * 3} columns...")
        worksheet.spreadsheet.batch_update({"requests": requests})
        
        # Update all headers in one batch
        batch_data = []
        for row, col, header in headers_to_update:
            cell = gspread.utils.rowcol_to_a1(row, col)
            batch_data.append({
                'range': cell,
                'values': [[header]]
            })
        
        worksheet.batch_update(batch_data)
        print(f"  Headers updated")
    
    return True


def find_month_columns_for_section(worksheet, channel_section, create_missing=False, date_filter=None):
    """Find month columns for a specific channel section.
    
    Args:
        worksheet: The worksheet object
        channel_section: The channel section to find columns for
        create_missing: If True, create columns for months in date_filter that don't exist
        date_filter: Tuple of (start_date, end_date) to determine which months to create
    """
    values = worksheet.get_all_values()
    
    # Look for month headers within the channel's row range
    for row_idx in range(channel_section.start_row - 1, 
                         min(channel_section.start_row + 5, channel_section.end_row)):
        if row_idx >= len(values):
            break
            
        row = values[row_idx]
        month_cols = {}
        
        for col_idx, header in enumerate(row):
            if header and ('202' in header or any(m in header for m in MONTH_NAMES_RU.values())):
                parsed = parse_month_header(header)
                if parsed:
                    month_cols[parsed] = col_idx + 1  # 1-based column
                else:
                    # Debug: show headers that couldn't be parsed
                    if header.strip():
                        print(f"    Warning: Could not parse month header: '{header}'")
        
        if month_cols:
            channel_section.month_columns = month_cols
            
            # Create missing columns if requested
            if create_missing and date_filter:
                created = add_missing_month_columns(worksheet, channel_section, month_cols, date_filter, row_idx + 1)
                if created:
                    # Re-read the columns after adding new ones
                    return find_month_columns_for_section(worksheet, channel_section, False, None)
            
            return month_cols
    
    return {}

def find_metric_rows_for_section(worksheet, channel_section):
    """Find metric rows within a specific channel section."""
    values = worksheet.get_all_values()
    metric_rows = {}
    
    # Mapping of row labels to internal keys
    label_mapping = {
        'Количество новых подписок': 'subscribers_gained',
        'Количество подписок': 'subscribers_gained',  # Alternative label
        'Количество отписок': 'subscribers_lost',
        'Динамика подписок': 'net_change',
        'Динамика подписок, %': 'growth_rate',
        'Количество просмотров, total': 'total_views',
        'Количество просмотров, videos': 'video_views',
        'Количество просмотров, shorts': 'shorts_views',
        'Соотношение, % videos vs. % shorts': 'views_ratio',
        'Количество роликов': 'video_count',
        'Количество рекламодателей': 'advertiser_count',
        'Интеграции': 'integrations',
        'AdSense': 'adsense',
        'География, топ-1': 'geo_views_1',
        'География, топ-2': 'geo_views_2',
        'География, топ-3': 'geo_views_3',
        'География, топ-4': 'geo_views_4',
        'География, топ-5': 'geo_views_5',
        'География, топ-6': 'geo_views_6',
        'География, топ-7': 'geo_views_7',
        'География, топ-8': 'geo_views_8',
        'География, топ-9': 'geo_views_9',
        'топ-1': 'geo_subs_1',
        'топ-2': 'geo_subs_2',
        'топ-3': 'geo_subs_3',
        'топ-4': 'geo_subs_4',
        'топ-5': 'geo_subs_5',
        'Изначальное кол-во подписчиков': 'initial_subscribers',
        'Количество подписчиков': 'total_subscribers'
    }
    
    # Search within the channel's row range
    for row_idx in range(channel_section.start_row - 1, channel_section.end_row):
        if row_idx >= len(values):
            break
            
        row = values[row_idx]
        if row:
            first_cell = str(row[0]).strip()
            for label, key in label_mapping.items():
                if label in first_cell:
                    metric_rows[key] = row_idx + 1  # 1-based row
                    break
    
    channel_section.metric_rows = metric_rows
    return metric_rows

def resolve_channel_identifier(youtube_data, channel_identifier):
    """Resolve a channel name, handle, or ID to a channel ID.
    
    Args:
        youtube_data: YouTube Data API v3 service
        channel_identifier: Channel name, @handle, or channel ID
    
    Returns:
        Channel ID string or None if not found
    """
    if not channel_identifier or not youtube_data:
        return None
    
    try:
        # If it starts with @, search by handle
        if channel_identifier.startswith('@'):
            response = youtube_data.channels().list(
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
            response = youtube_data.channels().list(
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
            search_response = youtube_data.search().list(
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

def fetch_monthly_video_counts(youtube_data, date_filter, channel_id=None):
    """Fetch video upload counts for each month in the date range.
    
    Args:
        youtube_data: YouTube Data API v3 service
        date_filter: Tuple of (start_date, end_date) strings
        channel_id: Optional channel ID to fetch videos for (if None, uses authenticated channel)
    
    Returns:
        Dictionary with (year, month) tuples as keys and video counts as values
    """
    if not date_filter or not youtube_data:
        return {}
    
    start_str, end_str = date_filter
    if not start_str or not end_str:
        return {}
    
    monthly_video_counts = defaultdict(int)
    
    try:
        # Get channel ID if not provided
        if not channel_id:
            channels_response = youtube_data.channels().list(
                part="id",
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                return {}
            
            channel_id = channels_response['items'][0]['id']
        
        # Parse dates
        start_dt = datetime.strptime(start_str, '%Y-%m-%d')
        end_dt = datetime.strptime(end_str, '%Y-%m-%d')
        
        # Convert to RFC3339 format for API
        start_rfc = start_dt.isoformat() + 'Z'
        end_rfc = end_dt.isoformat() + 'Z'
        
        next_page_token = None
        
        while True:
            # Search for videos uploaded by the channel within date range
            search_response = youtube_data.search().list(
                part="id,snippet",
                channelId=channel_id,
                type="video",
                publishedAfter=start_rfc,
                publishedBefore=end_rfc,
                maxResults=50,
                pageToken=next_page_token,
                order="date"
            ).execute()
            
            # Count videos by month
            for item in search_response.get('items', []):
                publish_time = item['snippet']['publishedAt']
                # Parse the publish time
                publish_dt = datetime.strptime(publish_time[:19], '%Y-%m-%dT%H:%M:%S')
                month_key = (publish_dt.year, publish_dt.month)
                monthly_video_counts[month_key] += 1
            
            # Check for more pages
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token:
                break
    
    except Exception as e:
        print(f"    Error fetching video counts: {e}")
    
    return dict(monthly_video_counts)


def fetch_monthly_geographic_data(youtube_analytics, date_filter, monthly_data, channel_id=None):
    """Fetch geographic data for each month in the date range.
    
    Args:
        youtube_analytics: YouTube Analytics API service
        date_filter: Tuple of (start_date, end_date) strings
        monthly_data: Dictionary with monthly totals to calculate "Other" views
        channel_id: Optional channel ID to fetch data for (if None, uses authenticated channel)
    
    Returns:
        Dictionary with (year, month) tuples as keys and geographic data as values
    """
    if not date_filter:
        return {}
    
    start_str, end_str = date_filter
    if not start_str or not end_str:
        return {}
    
    monthly_geo = {}
    
    # Parse dates
    start = datetime.strptime(start_str, '%Y-%m-%d')
    end = datetime.strptime(end_str, '%Y-%m-%d')
    
    # Process each month
    current = datetime(start.year, start.month, 1)
    
    while current <= end:
        # Calculate month end
        if current.month == 12:
            next_month = datetime(current.year + 1, 1, 1)
        else:
            next_month = datetime(current.year, current.month + 1, 1)
        
        month_end = next_month - timedelta(days=1)
        
        # Ensure we don't go past the end date
        if month_end.date() > end.date():
            month_end = end
        
        month_start_str = current.strftime('%Y-%m-%d')
        month_end_str = month_end.strftime('%Y-%m-%d')
        
        month_key = (current.year, current.month)
        
        try:
            # Fetch geographic data for this month
            ids_param = f'channel=={channel_id}' if channel_id else 'channel==MINE'
            response = youtube_analytics.reports().query(
                ids=ids_param,
                startDate=month_start_str,
                endDate=month_end_str,
                metrics='views,estimatedMinutesWatched',
                dimensions='country',
                sort='-views',
                maxResults=10
            ).execute()
            
            # Process response
            countries = []
            geo_total = 0
            
            if 'rows' in response:
                for row in response['rows']:
                    countries.append({
                        'country_code': row[0],
                        'views': row[1],
                        'watch_time_minutes': row[2]
                    })
                    geo_total += row[1]
            
            # Calculate "Other" views or add all as "Unknown" if no geographic data
            if month_key in monthly_data:
                total_views = monthly_data[month_key].get('views', 0)
                
                if geo_total > 0:
                    # We have some geographic data, add "Other" for the difference
                    other_views = total_views - geo_total
                    if other_views > 0:
                        countries.append({
                            'country_code': 'Other',
                            'views': other_views,
                            'watch_time_minutes': 0
                        })
                elif total_views > 0:
                    # No geographic data but we have views, mark all as "Unknown"
                    countries.append({
                        'country_code': 'Unknown',
                        'views': total_views,
                        'watch_time_minutes': 0
                    })
            
            monthly_geo[month_key] = countries
            
        except Exception as e:
            # If error, just skip this month
            monthly_geo[month_key] = []
        
        # Move to next month
        current = next_month
    
    return monthly_geo


def fetch_monthly_views_breakdown(youtube_analytics, date_filter, channel_id=None):
    """Fetch views breakdown between videos and shorts for each month.
    
    Args:
        youtube_analytics: YouTube Analytics API service
        date_filter: Tuple of (start_date, end_date) strings
        channel_id: Optional channel ID to fetch data for (if None, uses authenticated channel)
    
    Returns:
        Dictionary with (year, month) tuples as keys and views breakdown as values
    """
    if not date_filter or not youtube_analytics:
        return {}
    
    start_str, end_str = date_filter
    if not start_str or not end_str:
        return {}
    
    monthly_breakdown = {}
    
    # Parse dates
    start = datetime.strptime(start_str, '%Y-%m-%d')
    end = datetime.strptime(end_str, '%Y-%m-%d')
    
    # Process each month
    current = datetime(start.year, start.month, 1)
    
    while current <= end:
        # Calculate month end
        if current.month == 12:
            next_month = datetime(current.year + 1, 1, 1)
        else:
            next_month = datetime(current.year, current.month + 1, 1)
        
        month_end = next_month - timedelta(days=1)
        
        # Ensure we don't go past the end date
        if month_end.date() > end.date():
            month_end = end
        
        month_start_str = current.strftime('%Y-%m-%d')
        month_end_str = month_end.strftime('%Y-%m-%d')
        
        month_key = (current.year, current.month)
        
        try:
            # Fetch views breakdown for this month
            ids_param = f'channel=={channel_id}' if channel_id else 'channel==MINE'
            response = youtube_analytics.reports().query(
                ids=ids_param,
                startDate=month_start_str,
                endDate=month_end_str,
                metrics='views',
                dimensions='creatorContentType'
            ).execute()
            
            video_views = 0
            shorts_views = 0
            total_views = 0
            
            if 'rows' in response:
                for row in response['rows']:
                    content_type = row[0]
                    views = row[1]
                    total_views += views
                    
                    if content_type == 'SHORTS':
                        shorts_views = views
                    elif content_type == 'LONG_FORM_VIDEOS':
                        video_views = views
            
            # Calculate percentages
            video_pct = (video_views / total_views * 100) if total_views > 0 else 0
            shorts_pct = (shorts_views / total_views * 100) if total_views > 0 else 0
            
            monthly_breakdown[month_key] = {
                'total_views': total_views,
                'video_views': video_views,
                'shorts_views': shorts_views,
                'video_percentage': video_pct,
                'shorts_percentage': shorts_pct
            }
            
        except Exception as e:
            # If error, set empty data for this month
            monthly_breakdown[month_key] = {
                'total_views': 0,
                'video_views': 0,
                'shorts_views': 0,
                'video_percentage': 0,
                'shorts_percentage': 0
            }
        
        # Move to next month
        current = next_month
    
    return monthly_breakdown

def aggregate_monthly_data(channel_index=0, date_filter=None, youtube_analytics=None, channel_id=None):
    """Load and aggregate YouTube Analytics data by month for a specific channel.
    
    Args:
        channel_index: Which channel's data to load (0, 1, or 2)
        date_filter: Optional tuple of (start_date, end_date) to filter data
        youtube_analytics: YouTube Analytics API service
        channel_id: Optional channel ID to fetch data for (if None, uses authenticated channel)
    """
    monthly = defaultdict(lambda: {
        'views': 0,
        'watch_time_minutes': 0,
        'subscribers_gained': 0,
        'subscribers_lost': 0,
        'days_with_data': 0
    })
    
    # Parse date filter if provided
    start_filter = None
    end_filter = None
    if date_filter:
        start_str, end_str = date_filter
        if start_str:
            start_filter = datetime.fromisoformat(start_str).date()
        if end_str:
            end_filter = datetime.fromisoformat(end_str).date()
    
    # If we have YouTube Analytics API, fetch real data
    if youtube_analytics and date_filter:
        start_str, end_str = date_filter
        
        # Parse dates
        start = datetime.strptime(start_str, '%Y-%m-%d')
        end = datetime.strptime(end_str, '%Y-%m-%d')
        
        # Process each month
        current = datetime(start.year, start.month, 1)
        
        while current <= end:
            # Calculate month end
            if current.month == 12:
                next_month = datetime(current.year + 1, 1, 1)
            else:
                next_month = datetime(current.year, current.month + 1, 1)
            
            month_end = next_month - timedelta(days=1)
            
            # Ensure we don't go past the end date
            if month_end.date() > end.date():
                month_end = end
            
            month_start_str = current.strftime('%Y-%m-%d')
            month_end_str = month_end.strftime('%Y-%m-%d')
            
            month_key = (current.year, current.month)
            
            try:
                # Fetch metrics for this month
                ids_param = f'channel=={channel_id}' if channel_id else 'channel==MINE'
                response = youtube_analytics.reports().query(
                    ids=ids_param,
                    startDate=month_start_str,
                    endDate=month_end_str,
                    metrics='views,estimatedMinutesWatched,subscribersGained,subscribersLost'
                ).execute()
                
                if 'rows' in response and response['rows']:
                    row = response['rows'][0]
                    monthly[month_key]['views'] = row[0]
                    monthly[month_key]['watch_time_minutes'] = row[1]
                    monthly[month_key]['subscribers_gained'] = row[2]
                    monthly[month_key]['subscribers_lost'] = row[3]
                    monthly[month_key]['days_with_data'] = 1  # At least some data exists
                    
                    # Debug output to see what data we're getting
                    if row[2] > 0 or row[3] > 0:
                        print(f"      {current.strftime('%Y-%m')}: +{row[2]} / -{row[3]} subscribers")
                
            except Exception as e:
                print(f"    Warning: Could not fetch data for {current.strftime('%Y-%m')}: {e}")
            
            # Move to next month
            current = next_month
    
    # Try to load from JSON file as fallback (for testing or offline mode)
    elif os.path.exists('youtube_analytics.json'):
        try:
            with open('youtube_analytics.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Aggregate daily metrics by month
            if 'daily_metrics' in data:
                for day in data['daily_metrics']:
                    date = datetime.fromisoformat(day['date'])
                    month_key = (date.year, date.month)
                    
                    monthly[month_key]['views'] += day.get('views', 0)
                    monthly[month_key]['watch_time_minutes'] += day.get('watch_time_minutes', 0)
                    monthly[month_key]['subscribers_gained'] += day.get('subscribers_gained', 0)
                    monthly[month_key]['subscribers_lost'] += day.get('subscribers_lost', 0)
                    
                    if day.get('views', 0) > 0:
                        monthly[month_key]['days_with_data'] += 1
        except Exception as e:
            print(f"    Could not load data from JSON: {e}")
    
    # Add empty data for months in the filter range that don't have data
    if date_filter and start_filter and end_filter:
        current = datetime(start_filter.year, start_filter.month, 1)
        end = datetime(end_filter.year, end_filter.month, 1)
        
        while current <= end:
            month_key = (current.year, current.month)
            if month_key not in monthly:
                # Add empty data for this month
                monthly[month_key] = {
                    'views': 0,
                    'watch_time_minutes': 0,
                    'subscribers_gained': 0,
                    'subscribers_lost': 0,
                    'days_with_data': 0
                }
            
            # Move to next month
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
    
    # Fetch monthly views breakdown if we have the API
    monthly_views_breakdown = {}
    if youtube_analytics and date_filter:
        monthly_views_breakdown = fetch_monthly_views_breakdown(youtube_analytics, date_filter, channel_id)
    
    # Add overall metrics
    overall = {
        'channel': {},
        'views_breakdown': {},  # Will be set per month
        'monthly_views_breakdown': monthly_views_breakdown,
        'geographic_views': [],
        'geographic_subscribers': [],
        'revenue_metrics': {}
    }
    
    return dict(monthly), overall

def format_number(value):
    """Format number for spreadsheet (use space as thousands separator)."""
    if isinstance(value, (int, float)):
        if value >= 1000:
            return f"{value:,.0f}".replace(',', ' ')
        return str(int(value))
    return str(value)

def update_channel_section(worksheet, channel_section, channel_index, date_filter=None, dry_run=False, youtube_analytics=None, youtube_data=None, channel_id=None):
    """Update a specific channel section in the spreadsheet.
    
    Args:
        worksheet: Google Sheets worksheet object
        channel_section: ChannelSection object with row/column mappings
        channel_index: Index of the channel (0, 1, 2)
        date_filter: Optional tuple of (start_date, end_date) to filter updates
        dry_run: If True, only show what would be updated
        youtube_analytics: YouTube Analytics API service
        youtube_data: YouTube Data API v3 service
        channel_id: Optional channel ID to fetch data for
    """
    print(f"\n{'='*60}")
    print(f"Processing {channel_section.name} (rows {channel_section.start_row}-{channel_section.end_row})")
    print(f"{'='*60}")
    
    # Get month columns and metric rows for this section
    # Disable column creation temporarily to avoid duplicates
    find_month_columns_for_section(worksheet, channel_section, create_missing=False, date_filter=date_filter)
    find_metric_rows_for_section(worksheet, channel_section)
    
    print(f"Found {len(channel_section.month_columns)} month columns")
    print(f"Found {len(channel_section.metric_rows)} metric rows")
    
    # Debug: Show which metrics were found
    if channel_section.metric_rows:
        found_metrics = list(channel_section.metric_rows.keys())
        print(f"  Metrics found: {', '.join(found_metrics[:10])}")
        if len(found_metrics) > 10:
            print(f"    ... and {len(found_metrics) - 10} more")
    
    if not channel_section.month_columns:
        print("No month columns found in this section, skipping...")
        return []
    
    # Load data for this channel with date filter
    monthly_data, overall_data = aggregate_monthly_data(channel_index, date_filter, youtube_analytics, channel_id)
    print(f"Have data for {len(monthly_data)} months")
    
    # Apply additional date filter for month selection
    if date_filter:
        start_str, end_str = date_filter
        if start_str:
            start_date = datetime.fromisoformat(start_str).date()
            print(f"Filtering from: {start_date}")
        else:
            start_date = None
        if end_str:
            end_date = datetime.fromisoformat(end_str).date()
            print(f"Filtering to: {end_date}")
        else:
            end_date = None
    
    # Prepare updates
    updates = []
    
    for month_key, col in channel_section.month_columns.items():
        if month_key not in monthly_data:
            continue
        
        # Apply date filter to skip months outside range
        year, month = month_key
        month_date = datetime(year, month, 1).date()
        
        if date_filter:
            # Skip months outside the specified range
            if start_date and month_date < start_date:
                continue
            if end_date:
                # Check if month is after end date (use first day of next month)
                from calendar import monthrange
                last_day = monthrange(year, month)[1]
                month_end = datetime(year, month, last_day).date()
                if month_end > end_date:
                    # Check if month starts after end date
                    if month_date > end_date:
                        continue
        
        data = monthly_data[month_key]
        month_name = MONTH_NAMES_RU.get(month, str(month))
        
        print(f"\n  {month_name}. {year} (column {col}):")
        
        # Update metrics
        metrics_updated = []
        
        if 'subscribers_gained' in channel_section.metric_rows:
            value = format_number(data['subscribers_gained'])
            row = channel_section.metric_rows['subscribers_gained']
            updates.append((row, col, value))
            metrics_updated.append(f"New subs: {value}")
        
        if 'subscribers_lost' in channel_section.metric_rows:
            value = format_number(data['subscribers_lost'])
            row = channel_section.metric_rows['subscribers_lost']
            updates.append((row, col, value))
            metrics_updated.append(f"Lost subs: {value}")
        
        if 'net_change' in channel_section.metric_rows:
            net = data['subscribers_gained'] - data['subscribers_lost']
            value = f"{net:+d}" if net != 0 else "0"
            row = channel_section.metric_rows['net_change']
            updates.append((row, col, value))
            metrics_updated.append(f"Net: {value}")
        
        if 'growth_rate' in channel_section.metric_rows:
            # Calculate growth rate percentage
            # Need to get previous month's subscriber count to calculate growth
            net = data['subscribers_gained'] - data['subscribers_lost']
            # For now, just show the net change as we don't have cumulative subscriber data
            # In production, you'd track cumulative subscribers to calculate proper percentage
            value = f"{net:+d}" if net != 0 else "0"
            row = channel_section.metric_rows['growth_rate']
            updates.append((row, col, value))
            metrics_updated.append(f"Growth%: {value}")
        
        if 'total_views' in channel_section.metric_rows:
            value = format_number(data['views'])
            row = channel_section.metric_rows['total_views']
            updates.append((row, col, value))
            metrics_updated.append(f"Views: {value}")
        
        # Update views breakdown if available from monthly data
        if 'monthly_views_breakdown' in overall_data and month_key in overall_data['monthly_views_breakdown']:
            vb = overall_data['monthly_views_breakdown'][month_key]
            
            if 'video_views' in channel_section.metric_rows:
                value = format_number(vb.get('video_views', 0))
                row = channel_section.metric_rows['video_views']
                updates.append((row, col, value))
                metrics_updated.append(f"Video views: {value}")
            
            if 'shorts_views' in channel_section.metric_rows:
                value = format_number(vb.get('shorts_views', 0))
                row = channel_section.metric_rows['shorts_views']
                updates.append((row, col, value))
                metrics_updated.append(f"Shorts views: {value}")
            
            if 'views_ratio' in channel_section.metric_rows:
                video_pct = int(vb.get('video_percentage', 0))
                shorts_pct = int(vb.get('shorts_percentage', 0))
                value = f"{video_pct} / {shorts_pct}"
                row = channel_section.metric_rows['views_ratio']
                updates.append((row, col, value))
                metrics_updated.append(f"V/S: {value}")
        
        if metrics_updated:
            print(f"    {', '.join(metrics_updated)}")
    
    # Add monthly video counts if YouTube Data API is available
    if youtube_data and 'video_count' in channel_section.metric_rows:
        print(f"    Fetching monthly video counts...")
        monthly_video_counts = fetch_monthly_video_counts(youtube_data, date_filter, channel_id)
        
        row = channel_section.metric_rows['video_count']
        videos_updated = 0
        
        for month_key, col in channel_section.month_columns.items():
            if month_key in monthly_data:
                # Apply date filter
                year, month = month_key
                month_date = datetime(year, month, 1).date()
                
                if date_filter:
                    if start_date and month_date < start_date:
                        continue
                    if end_date and month_date > end_date:
                        continue
                
                # Get video count for this month (default to 0)
                video_count = monthly_video_counts.get(month_key, 0)
                updates.append((row, col, str(video_count)))
                videos_updated += 1
        
        print(f"    Updated video counts for {videos_updated} months")
    
    # Add geographic data if YouTube Analytics service is available
    if youtube_analytics:
        print(f"    Fetching monthly geographic data...")
        monthly_geo = fetch_monthly_geographic_data(youtube_analytics, date_filter, monthly_data, channel_id)
        
        # Update geographic rows with monthly data
        for i in range(1, 10):
            geo_key = f'geo_views_{i}'
            if geo_key in channel_section.metric_rows:
                row = channel_section.metric_rows[geo_key]
                
                # Update each month column
                for month_key, col in channel_section.month_columns.items():
                    if month_key in monthly_data:
                        # Apply date filter
                        year, month = month_key
                        month_date = datetime(year, month, 1).date()
                        
                        if date_filter:
                            if start_date and month_date < start_date:
                                continue
                            if end_date and month_date > end_date:
                                continue
                        
                        # Get geographic data for this month
                        if month_key in monthly_geo:
                            countries = monthly_geo[month_key]
                            if i <= len(countries):
                                # We have data for this country rank
                                country = countries[i - 1]
                                total_month_views = sum(c['views'] for c in countries)
                                percentage = (country['views'] / total_month_views * 100) if total_month_views > 0 else 0
                                
                                updates.append((row, col, country['country_code']))
                                updates.append((row, col + 1, format_number(country['views'])))
                                updates.append((row, col + 2, f"{percentage:.1f}"))
                            else:
                                # No country at this rank for this month
                                updates.append((row, col, ''))
                                updates.append((row, col + 1, ''))
                                updates.append((row, col + 2, ''))
                        else:
                            # No data for this month
                            updates.append((row, col, ''))
                            updates.append((row, col + 1, ''))
                            updates.append((row, col + 2, ''))
        
        print(f"    Updated geographic data for {len(monthly_geo)} months")
    else:
        print(f"    Skipping geographic data (YouTube Analytics not available)")
    
    # Add AdSense/Revenue data if available
    if 'adsense' in channel_section.metric_rows:
        row = channel_section.metric_rows['adsense']
        # Get revenue or show $0.00 if not available
        revenue = overall_data.get('revenue_metrics', {})
        total_revenue = revenue.get('total_revenue', 0)
        # Format as currency
        value = f"${total_revenue:,.2f}".replace(',', ' ')
        
        print(f"  Updating AdSense (row {row}): {value}")
        
        # Add to all month columns (since we don't have monthly breakdown)
        for month_key, col in channel_section.month_columns.items():
            if month_key in monthly_data:
                # Apply date filter
                year, month = month_key
                month_date = datetime(year, month, 1).date()
                
                if date_filter:
                    if start_date and month_date < start_date:
                        continue
                    if end_date and month_date > end_date:
                        continue
                
                updates.append((row, col, value))
    
    # Add total subscribers (even if 0)
    if 'total_subscribers' in channel_section.metric_rows:
        total_subs = overall_data.get('channel', {}).get('subscriber_count', 0)
        row = channel_section.metric_rows['total_subscribers']
        value = format_number(total_subs)
        
        # Add to all month columns
        for month_key, col in channel_section.month_columns.items():
            if month_key in monthly_data:
                # Apply date filter
                year, month = month_key
                month_date = datetime(year, month, 1).date()
                
                if date_filter:
                    if start_date and month_date < start_date:
                        continue
                    if end_date and month_date > end_date:
                        continue
                
                updates.append((row, col, value))
    
    return updates

def update_multi_channel_spreadsheet(spreadsheet_id, channel_indices=None, date_filter=None, dry_run=False, channel_names=None):
    """Update multiple YouTube channels in the same spreadsheet.
    
    Args:
        spreadsheet_id: Google Spreadsheet ID
        channel_indices: List of channel indices to update (0, 1, 2) or None for all
        date_filter: Optional tuple of (start_date, end_date) to filter updates
        dry_run: If True, show what would be updated without making changes
        channel_names: Optional list of channel names/handles/IDs to use for each channel section
    """
    print(f"Updating spreadsheet: {spreadsheet_id}")
    if dry_run:
        print("DRY RUN MODE - No changes will be made")
    
    # Authenticate and get all clients
    client, youtube_analytics, youtube_data = authenticate()
    spreadsheet = client.open_by_key(spreadsheet_id)
    
    # Find YouTube sheet
    youtube_sheet = None
    for sheet in spreadsheet.worksheets():
        if 'YouTube' in sheet.title:
            youtube_sheet = sheet
            break
    
    if not youtube_sheet:
        print("ERROR: YouTube sheet not found")
        return
    
    print(f"Found sheet: {youtube_sheet.title}")
    
    # Find channel sections
    channel_sections = find_channel_sections(youtube_sheet)
    print(f"Found {len(channel_sections)} channel sections")
    
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
    
    # Update each channel
    all_updates = []
    
    if channel_indices is None:
        channel_indices = range(len(channel_sections))
    
    for i, idx in enumerate(channel_indices):
        if idx < len(channel_sections):
            # Get channel ID for this section if available
            channel_id = channel_ids[i] if i < len(channel_ids) else None
            
            updates = update_channel_section(
                youtube_sheet, 
                channel_sections[idx], 
                idx,
                date_filter,
                dry_run,
                youtube_analytics,
                youtube_data,
                channel_id
            )
            all_updates.extend(updates)
    
    # Apply all updates
    if all_updates:
        if dry_run:
            print(f"\n{'='*60}")
            print(f"SUMMARY: Would update {len(all_updates)} cells total")
            print(f"{'='*60}")
        else:
            print(f"\n{'='*60}")
            print(f"Applying {len(all_updates)} updates...")
            
            # Batch update for efficiency
            batch_data = []
            for row, col, value in all_updates:
                cell = gspread.utils.rowcol_to_a1(row, col)
                batch_data.append({
                    'range': cell,
                    'values': [[value]]
                })
            
            youtube_sheet.batch_update(batch_data)
            print(f"Successfully updated {len(all_updates)} cells")
            print(f"{'='*60}")
    else:
        print("\nNo updates to make")
    
    print(f"\nView spreadsheet: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")

def main():
    """Main function to handle command line arguments.
    
    Usage:
        python main.py <spreadsheet_id> <channel_index> [options]
        python main.py <spreadsheet_id> <channel_index> --channel <channel_name/handle/id> [options]
        
    Examples:
        # Update channel 0 with default (authenticated) channel data
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0
        
        # Update channel 0 with specific channel by name
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0 --channel "MrBeast"
        
        # Update channel 0 with specific channel by handle
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0 --channel "@MrBeast"
        
        # Update multiple channels with different channel names
        python main.py 1YrSnJyJq0xZ87QW9LzP0ODY8gfTjp_ZKqQRS2YW-A3I 0,1,2 --channels "MrBeast,PewDiePie,@mkbhd"
    """
    # Parse arguments
    dry_run = '--dry-run' in sys.argv or '-d' in sys.argv
    
    # Parse date range
    date_filter = None
    start_date = None
    end_date = None
    channel_names = None
    
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
        print(f"Date filter: {start_date or 'any'} to {end_date or 'any'}")
    
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
    else:
        # Default to the provided spreadsheet
        spreadsheet_id = "1YBazG-UVCnSYwYjSKmXwaySVFDaQuifsL14aWTq7S9U"
    
    # Parse channel indices if provided (e.g., "0,1,2" or "1")
    channel_indices = None
    if len(args) > 1:
        try:
            if ',' in args[1]:
                channel_indices = [int(x) for x in args[1].split(',')]
            else:
                channel_indices = [int(args[1])]
        except ValueError:
            print(f"Invalid channel indices: {args[1]}")
            print("Use format: 0,1,2 or just 1 for single channel")
            return
    
    # Run update
    update_multi_channel_spreadsheet(spreadsheet_id, channel_indices, date_filter, dry_run, channel_names)

if __name__ == "__main__":
    main()