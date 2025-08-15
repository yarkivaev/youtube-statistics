import os
import datetime
import json
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

# Set up API config
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = [
    'https://www.googleapis.com/auth/yt-analytics.readonly',
    'https://www.googleapis.com/auth/youtube.readonly'
]

def get_authenticated_services():
    """Authenticate and return both YouTube Data and Analytics API services"""
    credentials = None
    token_file = "token.pickle"

    # Load credentials from file
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            credentials = pickle.load(token)

    # If no valid credentials, let user log in
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)

        # Save the credentials
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)

    youtube_analytics = build('youtubeAnalytics', 'v2', credentials=credentials)
    youtube_data = build('youtube', 'v3', credentials=credentials)
    
    return youtube_analytics, youtube_data

def get_channel_statistics(youtube_data):
    """Get channel statistics including video count"""
    try:
        request = youtube_data.channels().list(
            part="statistics,contentDetails",
            mine=True
        )
        response = request.execute()
        
        if response['items']:
            stats = response['items'][0]['statistics']
            return {
                'video_count': int(stats.get('videoCount', 0)),
                'subscriber_count': int(stats.get('subscriberCount', 0)),
                'view_count': int(stats.get('viewCount', 0))
            }
    except Exception as e:
        print(f"Error fetching channel statistics: {e}")
        return None

def get_daily_metrics(youtube_analytics, start_date, end_date):
    """Get core daily metrics with videos/shorts breakdown"""
    try:
        # Get total metrics
        total_request = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched,averageViewDuration,subscribersGained,subscribersLost',
            dimensions='day',
            sort='day'
        )
        total_response = total_request.execute()
        
        # Get videos vs shorts breakdown
        content_type_request = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched',
            dimensions='day,creatorContentType',
            sort='day'
        )
        content_type_response = content_type_request.execute()
        
        return {
            'total_metrics': total_response,
            'content_type_breakdown': content_type_response
        }
    except Exception as e:
        print(f"Error fetching daily metrics: {e}")
        return None

def get_revenue_data(youtube_analytics, start_date, end_date):
    """Get AdSense revenue data"""
    try:
        request = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='estimatedRevenue,estimatedAdRevenue,estimatedRedPartnerRevenue',
            dimensions='day',
            sort='day'
        )
        response = request.execute()
        return response
    except Exception as e:
        print(f"Error fetching revenue data: {e}")
        print("Note: Revenue metrics require proper AdSense integration and permissions")
        return None

def get_geography_views(youtube_analytics, start_date, end_date):
    """Get top 9 countries by views"""
    try:
        request = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='views,estimatedMinutesWatched',
            dimensions='country',
            sort='-views',
            maxResults=9
        )
        response = request.execute()
        return response
    except Exception as e:
        print(f"Error fetching geography views: {e}")
        return None

def get_geography_subscribers(youtube_analytics, start_date, end_date):
    """Get top 5 countries by new subscribers"""
    try:
        request = youtube_analytics.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics='subscribersGained',
            dimensions='country',
            sort='-subscribersGained',
            maxResults=5
        )
        response = request.execute()
        return response
    except Exception as e:
        print(f"Error fetching geography subscribers: {e}")
        return None

def calculate_subscription_dynamics(daily_metrics):
    """Calculate subscription dynamics and percentages"""
    if not daily_metrics or 'total_metrics' not in daily_metrics:
        return None
    
    rows = daily_metrics['total_metrics'].get('rows', [])
    if not rows:
        return None
    
    total_gained = sum(row[4] for row in rows)  # subscribersGained (index 4)
    total_lost = sum(row[5] for row in rows)    # subscribersLost (index 5)
    net_change = total_gained - total_lost
    
    # Calculate percentage (avoiding division by zero)
    if total_gained > 0:
        change_percentage = (net_change / total_gained) * 100
    else:
        change_percentage = 0
    
    return {
        'subscribers_gained': total_gained,
        'subscribers_lost': total_lost,
        'net_change': net_change,
        'change_percentage': round(change_percentage, 2)
    }

def calculate_content_type_breakdown(content_type_data):
    """Calculate videos vs shorts percentage breakdown"""
    if not content_type_data or 'rows' not in content_type_data:
        return None
    
    videos_views = 0
    shorts_views = 0
    
    for row in content_type_data.get('rows', []):
        # row[1] is creatorContentType, row[2] is views
        if len(row) > 2:
            content_type = row[1]
            views = row[2]
            
            # Handle different content type values
            if content_type in ['VIDEO_TYPE_UPLOADED', 'videoOnDemand', 'LONG_FORM']:
                videos_views += views
            elif content_type in ['VIDEO_TYPE_SHORTS', 'shorts', 'SHORTS', 'SHORT_FORM']:
                shorts_views += views
            elif content_type == 'LIVE_STREAM':
                # Count live streams as videos
                videos_views += views
    
    total_views = videos_views + shorts_views
    
    if total_views > 0:
        videos_percentage = (videos_views / total_views) * 100
        shorts_percentage = (shorts_views / total_views) * 100
    else:
        videos_percentage = 0
        shorts_percentage = 0
    
    return {
        'total_views': total_views,
        'videos_views': videos_views,
        'shorts_views': shorts_views,
        'videos_percentage': round(videos_percentage, 2),
        'shorts_percentage': round(shorts_percentage, 2)
    }

def format_country_code(code):
    """Convert country code to readable format"""
    # Basic country code mapping (expand as needed)
    country_map = {
        'US': 'США',
        'RU': 'Россия',
        'GB': 'Великобритания',
        'DE': 'Германия',
        'FR': 'Франция',
        'JP': 'Япония',
        'CN': 'Китай',
        'IN': 'Индия',
        'BR': 'Бразилия',
        'CA': 'Канада',
        'AU': 'Австралия',
        'IT': 'Италия',
        'ES': 'Испания',
        'MX': 'Мексика',
        'KR': 'Южная Корея',
        'UA': 'Украина',
        'PL': 'Польша',
        'NL': 'Нидерланды',
        'TR': 'Турция',
        'SE': 'Швеция'
    }
    return country_map.get(code, code)

def generate_report(all_data, start_date, end_date):
    """Generate formatted report"""
    report_lines = []
    report_lines.append(f"{'='*60}")
    report_lines.append(f"YouTube Analytics Report")
    report_lines.append(f"Period: {start_date} to {end_date}")
    report_lines.append(f"Generated: {datetime.datetime.now().isoformat()}")
    report_lines.append(f"{'='*60}\n")
    
    # Channel metrics
    if all_data.get('channel_stats'):
        stats = all_data['channel_stats']
        report_lines.append("CHANNEL METRICS:")
        report_lines.append(f"Количество роликов: {stats['video_count']}")
        report_lines.append(f"Количество рекламодателей: [Требуется ручной ввод]")
        report_lines.append(f"Интеграции Ghost Writer или Школьных продуктов: [Требуется ручной ввод]\n")
    
    # Subscription dynamics
    if all_data.get('subscription_dynamics'):
        dynamics = all_data['subscription_dynamics']
        report_lines.append("SUBSCRIPTION DYNAMICS:")
        report_lines.append(f"Количество новых подписок: {dynamics['subscribers_gained']}")
        report_lines.append(f"Количество отписок: {dynamics['subscribers_lost']}")
        report_lines.append(f"Динамика подписок: {'+' if dynamics['net_change'] >= 0 else ''}{dynamics['net_change']}")
        report_lines.append(f"Динамика подписок, %: {'+' if dynamics['change_percentage'] >= 0 else ''}{dynamics['change_percentage']}%\n")
    
    # Views breakdown
    if all_data.get('content_breakdown'):
        breakdown = all_data['content_breakdown']
        report_lines.append("VIEWS BREAKDOWN:")
        report_lines.append(f"Количество просмотров, total: {breakdown['total_views']}")
        report_lines.append(f"Количество просмотров, videos: {breakdown['videos_views']}")
        report_lines.append(f"Количество просмотров, shorts: {breakdown['shorts_views']}")
        report_lines.append(f"Соотношение: {breakdown['videos_percentage']}% videos vs. {breakdown['shorts_percentage']}% shorts\n")
    
    # Revenue
    if all_data.get('revenue_total'):
        report_lines.append("REVENUE:")
        report_lines.append(f"AdSense: ${all_data['revenue_total']:.2f}\n")
    else:
        report_lines.append("REVENUE:")
        report_lines.append("AdSense: [Данные недоступны - требуется интеграция AdSense]\n")
    
    # Geography - Views
    if all_data.get('geography_views'):
        report_lines.append("ГЕОГРАФИЯ ПРОСМОТРОВ (TOP 9):")
        for i, country_data in enumerate(all_data['geography_views'], 1):
            country = format_country_code(country_data['country'])
            views = country_data['views']
            report_lines.append(f"География, топ-{i}: {country} - {views} просмотров")
        report_lines.append("")
    
    # Geography - Subscribers
    if all_data.get('geography_subscribers'):
        report_lines.append("ГЕОГРАФИЯ ПОДПИСЧИКОВ (TOP 5):")
        for i, country_data in enumerate(all_data['geography_subscribers'], 1):
            country = format_country_code(country_data['country'])
            subscribers = country_data['subscribers']
            report_lines.append(f"топ-{i}: {country} - {subscribers} подписчиков")
        report_lines.append("")
    
    return "\n".join(report_lines)

def main():
    """Main function to orchestrate all data collection"""
    print("Starting YouTube Analytics data collection...")
    
    # Set date range
    start_date = '2024-01-01'
    end_date = datetime.date.today().isoformat()
    
    # Get authenticated services
    youtube_analytics, youtube_data = get_authenticated_services()
    
    # Collect all data
    all_data = {
        'start_date': start_date,
        'end_date': end_date,
        'generated_at': datetime.datetime.now().isoformat()
    }
    
    # Get channel statistics
    print("Fetching channel statistics...")
    channel_stats = get_channel_statistics(youtube_data)
    if channel_stats:
        all_data['channel_stats'] = channel_stats
    
    # Get daily metrics with content type breakdown
    print("Fetching daily metrics...")
    daily_metrics = get_daily_metrics(youtube_analytics, start_date, end_date)
    if daily_metrics:
        all_data['daily_metrics'] = {
            'total': daily_metrics['total_metrics'].get('rows', []),
            'by_content_type': daily_metrics['content_type_breakdown'].get('rows', [])
        }
        
        # Calculate dynamics
        subscription_dynamics = calculate_subscription_dynamics(daily_metrics)
        if subscription_dynamics:
            all_data['subscription_dynamics'] = subscription_dynamics
        
        # Calculate content breakdown
        content_breakdown = calculate_content_type_breakdown(daily_metrics['content_type_breakdown'])
        if content_breakdown:
            all_data['content_breakdown'] = content_breakdown
    
    # Get revenue data
    print("Fetching revenue data...")
    revenue_data = get_revenue_data(youtube_analytics, start_date, end_date)
    if revenue_data and revenue_data.get('rows'):
        total_revenue = sum(row[1] for row in revenue_data['rows'] if len(row) > 1 and row[1])
        all_data['revenue_total'] = total_revenue
        all_data['revenue_daily'] = revenue_data.get('rows', [])
    
    # Get geography data for views
    print("Fetching geography data for views...")
    geo_views = get_geography_views(youtube_analytics, start_date, end_date)
    if geo_views and geo_views.get('rows'):
        all_data['geography_views'] = [
            {'country': row[0], 'views': row[1], 'watch_time': row[2]} 
            for row in geo_views['rows']
        ]
    
    # Get geography data for subscribers
    print("Fetching geography data for subscribers...")
    geo_subscribers = get_geography_subscribers(youtube_analytics, start_date, end_date)
    if geo_subscribers and geo_subscribers.get('rows'):
        all_data['geography_subscribers'] = [
            {'country': row[0], 'subscribers': row[1]} 
            for row in geo_subscribers['rows']
        ]
    
    # Save JSON data
    with open('youtube_analytics.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print("Data saved to youtube_analytics.json")
    
    # Generate and save formatted report
    report = generate_report(all_data, start_date, end_date)
    with open('youtube_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("Report saved to youtube_report.txt")
    
    # Also print the report
    print("\n" + report)

if __name__ == "__main__":
    main()