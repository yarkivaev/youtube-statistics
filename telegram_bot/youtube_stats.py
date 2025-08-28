"""YouTube statistics fetcher for Telegram bot."""

import sys
import os
from datetime import datetime, timedelta
from typing import Optional

# Add parent directory to path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from youtube.youtube_api import YouTubeAPIClient
from youtube.youtube_metrics_factory import YouTubeMetricsFactory
from domain import DateRange
from telegram_bot.auth import get_credentials, get_youtube_services


def get_own_channel(youtube_data_service) -> tuple[Optional[str], str]:
    """Get authenticated user's channel ID and name.
    
    Returns:
        Tuple of (channel_id, channel_name)
    """
    try:
        request = youtube_data_service.channels().list(
            part='snippet',
            mine=True
        )
        response = request.execute()
        if response['items']:
            channel = response['items'][0]
            return channel['id'], channel['snippet']['title']
    except Exception as e:
        print(f"Error getting own channel: {e}")
    
    return None, "Unknown"


# Keep old function name for compatibility but simplified
def resolve_channel(youtube_data_service, channel_query: str) -> tuple[Optional[str], str]:
    """Resolve channel - always returns user's own channel.
    
    Args:
        channel_query: Ignored, kept for compatibility
        
    Returns:
        Tuple of (channel_id, channel_name)
    """
    return get_own_channel(youtube_data_service)


def get_video_count_for_period(youtube_data, channel_id: str, start_date, end_date) -> int:
    """Get the number of videos uploaded in a specific period.
    
    Args:
        youtube_data: YouTube Data API service
        channel_id: YouTube channel ID
        start_date: Start date of the period
        end_date: End date of the period
        
    Returns:
        Number of videos uploaded in the period
    """
    try:
        # Convert dates to RFC 3339 format for YouTube API
        start_datetime = datetime.combine(start_date, datetime.min.time()).isoformat() + 'Z'
        end_datetime = datetime.combine(end_date, datetime.max.time()).isoformat() + 'Z'
        
        video_count = 0
        next_page_token = None
        
        while True:
            # Search for videos uploaded by the channel in the specified period
            request = youtube_data.search().list(
                part='id',
                channelId=channel_id,
                type='video',
                publishedAfter=start_datetime,
                publishedBefore=end_datetime,
                maxResults=50,
                pageToken=next_page_token
            )
            
            response = request.execute()
            video_count += len(response.get('items', []))
            
            # Check if there are more pages
            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
                
        return video_count
        
    except Exception as e:
        print(f"Error fetching video count: {e}")
        return 0


def get_channel_statistics(user_id: int, channel_query: Optional[str] = None, month_query: Optional[str] = None) -> str:
    """Get YouTube channel statistics formatted for Telegram.
    
    Args:
        user_id: Telegram user ID
        channel_query: Not used anymore, kept for compatibility
        month_query: Optional month in YYYY-MM format
        
    Returns:
        Formatted statistics string
    """
    try:
        # Get YouTube services
        youtube_analytics, youtube_data = get_youtube_services(user_id)
        if not youtube_analytics or not youtube_data:
            return "❌ Authentication required. Please use /auth command first."
        
        # Always get user's own channel
        channel_id, channel_name = resolve_channel(youtube_data, None)
        if not channel_id:
            return "❌ Could not find your channel. Please check your authentication."
        
        # Create API client wrapper
        api_client = YouTubeAPIClient()
        api_client._youtube_analytics = youtube_analytics
        api_client._youtube_data = youtube_data
        
        # Set date range based on month_query
        if month_query:
            try:
                # Parse YYYY-MM format
                year, month = month_query.split('-')
                year = int(year)
                month = int(month)
                
                # Validate month
                if month < 1 or month > 12:
                    return f"❌ Invalid month: {month_query}. Use format YYYY-MM (e.g., 2024-01)"
                
                # Get first and last day of the month
                import calendar
                start_date = datetime(year, month, 1).date()
                last_day = calendar.monthrange(year, month)[1]
                end_date = datetime(year, month, last_day).date()
                
                # If the month is in the future, return error
                if start_date > datetime.now().date():
                    return f"❌ Cannot get statistics for future month: {month_query}"
                
                # If end date is in the future, use today
                if end_date > datetime.now().date():
                    end_date = datetime.now().date()
                    
            except Exception as e:
                return f"❌ Invalid month format: {month_query}. Use YYYY-MM (e.g., 2024-01)"
        else:
            # Default: last 30 days
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        
        period = DateRange(start_date=start_date, end_date=end_date)
        
        # Get video count for the period
        videos_uploaded = get_video_count_for_period(youtube_data, channel_id, start_date, end_date)
        
        # Get metrics using factory (always include revenue for own channel)
        factory = YouTubeMetricsFactory(
            api_client=api_client,
            period=period,
            skip_revenue=False  # Always show revenue for own channel
        )
        
        # Fetch metrics
        metrics = factory.create()
        
        # Format response
        response = f"📊 *{channel_name} Statistics*\n"
        
        # Show period based on what was requested
        if month_query:
            import calendar
            month_name = calendar.month_name[int(month_query.split('-')[1])]
            year = month_query.split('-')[0]
            response += f"_📅 {month_name} {year}_\n"
            response += f"_({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})_\n\n"
        else:
            response += f"_Last 30 days ({start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')})_\n\n"
        
        # Channel stats
        if metrics.channel:
            response += f"👥 *Subscribers:* {metrics.channel.subscriber_count:,}\n"
            response += f"🎬 *Total Videos:* {metrics.channel.video_count:,}\n"
            response += f"👁 *Total Views:* {metrics.channel.total_view_count:,}\n\n"
        
        # Videos uploaded in the period
        if videos_uploaded > 0:
            if month_query:
                response += f"🆕 *Videos uploaded in {calendar.month_name[int(month_query.split('-')[1])]}:* {videos_uploaded}\n\n"
            else:
                response += f"🆕 *Videos uploaded (30d):* {videos_uploaded}\n\n"
        elif month_query:
            response += f"🆕 *Videos uploaded in {calendar.month_name[int(month_query.split('-')[1])]}:* 0\n\n"
        
        # Period stats
        if metrics.subscription_metrics:
            net_change = metrics.subscription_metrics.net_change
            response += f"📈 *New Subscribers:* {metrics.subscription_metrics.subscribers_gained:,}\n"
            response += f"📉 *Lost Subscribers:* {metrics.subscription_metrics.subscribers_lost:,}\n"
            response += f"➡️ *Net Change:* {'+' if net_change >= 0 else ''}{net_change:,}\n\n"
        
        # Views breakdown
        if metrics.views_breakdown:
            period_label = f"{calendar.month_name[int(month_query.split('-')[1])]}" if month_query else "30d"
            response += f"👀 *Total Views ({period_label}):* {metrics.views_breakdown.total_views:,}\n"
            if metrics.views_breakdown.video_views > 0:
                response += f"  • Videos: {metrics.views_breakdown.video_views:,} ({metrics.views_breakdown.video_percentage:.1f}%)\n"
            if metrics.views_breakdown.shorts_views > 0:
                response += f"  • Shorts: {metrics.views_breakdown.shorts_views:,} ({metrics.views_breakdown.shorts_percentage:.1f}%)\n"
            response += "\n"
        
        # Watch time
        if metrics.daily_metrics:
            total_watch_minutes = sum(d.watch_time_minutes for d in metrics.daily_metrics)
            total_watch_hours = total_watch_minutes / 60
            response += f"⏱ *Watch Time:* {total_watch_hours:,.0f} hours\n"
            
            # Average views per day
            active_days = sum(1 for d in metrics.daily_metrics if d.has_activity)
            if active_days > 0:
                avg_daily_views = sum(d.views for d in metrics.daily_metrics) / active_days
                response += f"📅 *Avg Daily Views:* {avg_daily_views:,.0f}\n"
        
        # Revenue
        if metrics.revenue_metrics and metrics.revenue_metrics.has_revenue:
            response += f"\n💰 *Revenue:* ${metrics.revenue_metrics.total_revenue:.2f}\n"
            response += f"  • Ad Revenue: ${metrics.revenue_metrics.ad_revenue:.2f}\n"
            if metrics.revenue_metrics.red_partner_revenue > 0:
                response += f"  • YouTube Premium: ${metrics.revenue_metrics.red_partner_revenue:.2f}\n"
        
        # Top countries
        if metrics.geographic_views and len(metrics.geographic_views) > 0:
            response += "\n🌍 *Top Countries (Views):*\n"
            # Show top 5 countries
            top_countries = metrics.geographic_views[:5]
            total_top_views = 0
            for i, geo in enumerate(top_countries, 1):
                response += f"  {i}. {geo.country_name}: {geo.views:,}\n"
                total_top_views += geo.views
            
            # If there are more countries, show "Others" with the sum
            if len(metrics.geographic_views) > 5:
                other_views = sum(g.views for g in metrics.geographic_views[5:])
                if other_views > 0:
                    response += f"  • Others ({len(metrics.geographic_views) - 5} countries): {other_views:,}\n"
            
            # Calculate total geographic views
            total_geo_views = sum(g.views for g in metrics.geographic_views)
            
            # Check if there's unaccounted traffic
            if metrics.views_breakdown and metrics.views_breakdown.total_views > total_geo_views:
                unaccounted = metrics.views_breakdown.total_views - total_geo_views
                response += f"  • Unspecified regions: {unaccounted:,}\n"
                total_geo_views = metrics.views_breakdown.total_views
            
            response += f"  _Total: {total_geo_views:,} views_\n"
        
        return response
        
    except Exception as e:
        return f"❌ Error fetching statistics: {str(e)}\n\nPlease check if the channel exists and you have access to it."


def format_number(num: int) -> str:
    """Format large numbers in a readable way."""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)