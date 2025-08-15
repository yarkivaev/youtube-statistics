import os
import datetime
import sys
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

# Set up API config
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/yt-analytics.readonly']

def get_authenticated_service():
    """Authenticate and return YouTube Analytics API service"""
    credentials = None
    token_file = "token.pickle"
    
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            credentials = pickle.load(token)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=0)
        
        with open(token_file, 'wb') as token:
            pickle.dump(credentials, token)
    
    return build('youtubeAnalytics', 'v2', credentials=credentials)

def query_subscriptions(start_date=None, end_date=None, group_by='day'):
    """
    Query subscription data for a specific period
    
    Args:
        start_date: Start date (YYYY-MM-DD format). Default: 30 days ago
        end_date: End date (YYYY-MM-DD format). Default: today
        group_by: 'day', 'month', or 'total'
    """
    youtube_analytics = get_authenticated_service()
    
    # Set default dates if not provided
    if not end_date:
        end_date = datetime.date.today().isoformat()
    if not start_date:
        start_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    
    print(f"\nQuerying subscriptions from {start_date} to {end_date}")
    print("=" * 60)
    
    try:
        # Build the query based on grouping
        if group_by == 'day':
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='subscribersGained,subscribersLost',
                dimensions='day',
                sort='day'
            )
        elif group_by == 'month':
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='subscribersGained,subscribersLost',
                dimensions='month',
                sort='month'
            )
        else:  # total
            request = youtube_analytics.reports().query(
                ids='channel==MINE',
                startDate=start_date,
                endDate=end_date,
                metrics='subscribersGained,subscribersLost'
            )
        
        response = request.execute()
        
        # Process and display results
        if group_by == 'total':
            # Single row with totals
            if response.get('rows'):
                row = response['rows'][0]
                gained = row[0]
                lost = row[1]
                net = gained - lost
                
                print(f"PERIOD TOTALS:")
                print(f"├─ New subscriptions: {gained:,}")
                print(f"├─ Unsubscriptions: {lost:,}")
                print(f"├─ Net change: {net:+,}")
                if gained > 0:
                    print(f"└─ Growth rate: {(net/gained)*100:.2f}%")
        else:
            # Multiple rows with daily/monthly data
            rows = response.get('rows', [])
            if rows:
                total_gained = 0
                total_lost = 0
                
                print(f"{'Date':<12} {'Gained':>10} {'Lost':>10} {'Net':>10}")
                print("-" * 45)
                
                for row in rows:
                    date = row[0]
                    gained = row[1]
                    lost = row[2]
                    net = gained - lost
                    total_gained += gained
                    total_lost += lost
                    
                    # Only show non-zero days/months
                    if gained > 0 or lost > 0:
                        print(f"{date:<12} {gained:>10,} {lost:>10,} {net:>+10,}")
                
                # Show totals
                print("-" * 45)
                print(f"{'TOTAL':<12} {total_gained:>10,} {total_lost:>10,} {total_gained-total_lost:>+10,}")
                print()
                print(f"Summary:")
                print(f"├─ Total new subscriptions: {total_gained:,}")
                print(f"├─ Total unsubscriptions: {total_lost:,}")
                print(f"├─ Net change: {total_gained-total_lost:+,}")
                if total_gained > 0:
                    print(f"└─ Growth rate: {((total_gained-total_lost)/total_gained)*100:.2f}%")
            else:
                print("No subscription data found for this period.")
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    """Main function with command line interface"""
    print("YouTube Subscription Analytics Tool")
    print("=" * 60)
    
    # Interactive mode
    if len(sys.argv) == 1:
        print("\nOptions:")
        print("1. Last 30 days (daily breakdown)")
        print("2. Last 90 days (daily breakdown)")
        print("3. Year to date (monthly breakdown)")
        print("4. All time (monthly breakdown)")
        print("5. Custom date range")
        print("6. Specific month")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        today = datetime.date.today()
        
        if choice == '1':
            start_date = (today - datetime.timedelta(days=30)).isoformat()
            end_date = today.isoformat()
            group_by = 'day'
        elif choice == '2':
            start_date = (today - datetime.timedelta(days=90)).isoformat()
            end_date = today.isoformat()
            group_by = 'day'
        elif choice == '3':
            start_date = f"{today.year}-01-01"
            end_date = today.isoformat()
            group_by = 'month'
        elif choice == '4':
            start_date = "2020-01-01"  # Or your channel start date
            end_date = today.isoformat()
            group_by = 'month'
        elif choice == '5':
            start_date = input("Enter start date (YYYY-MM-DD): ").strip()
            end_date = input("Enter end date (YYYY-MM-DD): ").strip()
            group_input = input("Group by (day/month/total): ").strip().lower()
            group_by = group_input if group_input in ['day', 'month', 'total'] else 'day'
        elif choice == '6':
            year = input("Enter year (YYYY): ").strip()
            month = input("Enter month (1-12): ").strip().zfill(2)
            start_date = f"{year}-{month}-01"
            # Calculate last day of month
            if month == '12':
                end_date = f"{year}-12-31"
            else:
                next_month = datetime.date(int(year), int(month) + 1, 1)
                last_day = next_month - datetime.timedelta(days=1)
                end_date = last_day.isoformat()
            group_by = 'day'
        else:
            print("Invalid option")
            return
        
        query_subscriptions(start_date, end_date, group_by)
    
    # Command line arguments mode
    else:
        if len(sys.argv) >= 3:
            start_date = sys.argv[1]
            end_date = sys.argv[2]
            group_by = sys.argv[3] if len(sys.argv) > 3 else 'day'
            query_subscriptions(start_date, end_date, group_by)
        else:
            print("Usage:")
            print("  Interactive mode: python query_subscriptions.py")
            print("  Command line: python query_subscriptions.py START_DATE END_DATE [GROUP_BY]")
            print("  Example: python query_subscriptions.py 2024-01-01 2024-12-31 month")

if __name__ == "__main__":
    main()