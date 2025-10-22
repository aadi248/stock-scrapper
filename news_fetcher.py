import requests
import feedparser
import os
from newsapi import NewsApiClient
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')
MARKETAUX_KEY = os.getenv('MARKETAUX_KEY')

if not NEWSAPI_KEY or not MARKETAUX_KEY:
    print("FATAL ERROR: API keys not loaded. Check your .env file.")

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

def fetch_from_newsapi(query):
    """Fetch recent news articles matching the query (e.g., company name)."""
    
    # 1. Calculate the time window for the API call (e.g., the last 1 hour)
    time_window = datetime.now() - timedelta(hours=1) 
    from_date = time_window.strftime('%Y-%m-%dT:%M:%S')  # Correctly format as ISO string
    
    # Initialize list to store results
    articles = []
    
    if not NEWSAPI_KEY: 
        print("Warning: NewsAPI key is missing.")
        return []

    try:
        resp = newsapi.get_everything(
            q=query, 
            language='en', 
            # 2. PASS THE 'from_date' PARAMETER HERE
            from_param=from_date,  
            # 3. Sort by publication time to ensure freshness
            sort_by='publishedAt', 
            page_size=20
        )
        for art in resp.get('articles', []):
            articles.append({
                'source': art['source']['name'],
                'title': art['title'],
                'url': art['url'],
                'timestamp': art['publishedAt']
            })
    except Exception as e:
        print(f"NewsAPI error for query '{query}': {e}")
        
    return articles

def fetch_from_marketaux(symbols):
    """Fetch latest finance news for given NSE symbols using Marketaux API."""
    params= {
        'api_token': MARKETAUX_KEY, 'symbols': ','.join(symbols), 'language': 'en', 'limit': 50, 'sort': 'published_at'
    }
    if not MARKETAUX_KEY: return []
    url = "https://api.marketaux.com/v1/news/all"
    params = {
        'api_token': MARKETAUX_KEY,
        'symbols': ','.join(symbols),
        'language': 'en'
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status() # Raise exception for bad status codes (4xx or 5xx)
        data = r.json()
        return [{
            'source': art.get('source'),
            'title': art.get('title'),
            'url': art.get('url'),
            'timestamp': art.get('published_at')
        } for art in data.get('data', [])]
    except Exception as e:
        print(f"Marketaux error: {e}")
        return []

def fetch_from_rss(feed_url):
    """Parse RSS feed and return recent entries."""
    articles = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:15]: # Limiting to 5 entries
            articles.append({
                'source': feed.feed.get('title', ''),
                'title': entry.get('title'),
                'url': entry.get('link'),
                'timestamp': entry.get('published')
            })
        return articles
    except Exception as e:
        print(f"RSS error for URL '{feed_url}': {e}")
        return []