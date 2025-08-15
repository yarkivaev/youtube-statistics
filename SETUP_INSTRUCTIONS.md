# YouTube Analytics Setup Instructions

## Prerequisites

1. **Enable YouTube Data API v3** in Google Cloud Console:
   - Visit: https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=579930114598
   - Click "Enable API"
   - Wait a few minutes for changes to propagate

2. **Ensure YouTube Analytics API v2** is enabled (should already be enabled)

3. **For Revenue Data (AdSense)**:
   - Your channel must be monetized
   - You need to be part of the YouTube Partner Program
   - AdSense account must be linked to your YouTube channel
   - Note: Revenue data may not be available for all accounts

## Running the Script

```bash
# Activate virtual environment
source venv/bin/activate

# Run the script
python main.py
```

## Output Files

- `youtube_analytics.json` - Raw data in JSON format
- `youtube_report.txt` - Formatted report in Russian

## Metrics Available

✅ **Working Metrics:**
- Количество новых подписок (Subscribers gained)
- Количество отписок (Subscribers lost) 
- Динамика подписок (Net subscriber change)
- Динамика подписок, % (Percentage change)
- География просмотров (Views by country - top 9)
- География подписчиков (Subscribers by country - top 5)
- Daily metrics data

⚠️ **Partially Working:**
- Количество просмотров videos vs shorts (requires videos with views)
- Соотношение % videos vs % shorts

❌ **Requires Additional Setup:**
- Количество роликов (requires YouTube Data API v3 enabled)
- AdSense revenue (requires monetization and proper permissions)

❌ **Not Available via API:**
- Количество рекламодателей (manual tracking required)
- Интеграции Ghost Writer или Школьных продуктов (manual tracking required)

## Troubleshooting

1. **"YouTube Data API v3 has not been used" error**:
   - Enable the API at the link provided in the error message
   - Wait 2-5 minutes and try again

2. **"Insufficient permission to access this report" for revenue**:
   - This is normal if your channel isn't monetized
   - Revenue data requires YouTube Partner Program membership

3. **Zero views in videos/shorts breakdown**:
   - The breakdown only shows data when there are actual views
   - Check if the date range has video activity

## Data Notes

- The script fetches data from 2024-01-01 to the current date
- Geographic data shows top countries only
- All monetary values are in USD
- Subscriber loss showing as 0 may indicate no unsubscribes during the period