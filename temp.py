import os
from dotenv import load_dotenv
from newsapi import NewsApiClient
from datetime import datetime, timedelta, timezone

# Load .env
load_dotenv()
newsapi_key = os.getenv("NEWSAPI_KEY")
if not newsapi_key:
    raise ValueError("NEWSAPI_KEY not found in .env")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=newsapi_key)

# Calculate datetime 24 hours ago (timezone-aware)
yesterday = datetime.now(timezone.utc) - timedelta(days=7)
from_date = yesterday.strftime('%Y-%m-%dT%H:%M:%S')  # Remove 'Z'

# Fetch articles from last 24 hours
articles = newsapi.get_everything(
    q="Telugu cinema",                 # keyword search
    from_param=from_date,      # articles published after this time
    language="en",
    
    page_size=10
)

# Print results
if articles['totalResults'] == 0:
    print("No articles found in the last 24 hours.")
else:
    for i, article in enumerate(articles['articles'], 1):
        print(f"{i}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   URL: {article['url']}\n")
