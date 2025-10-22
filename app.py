import streamlit as st
import pandas as pd
import time
import os
import schedule # Used for scheduling the fetch job
from news_fetcher import fetch_from_newsapi, fetch_from_marketaux, fetch_from_rss
from sentiment_analysis import classify_sentiment
from logger_setup import log_article
from load_symbols import get_static_company_symbols # Assuming you named the static loader file this way
from datetime import datetime


# --- Configuration ---
RSS_FEEDS = ["https://rss.cnn.com/rss/edition_world.rss"]
SYMBOL_FILE = 'static_symbols.csv'

# Store news items in session state to maintain data across Streamlit reruns
if 'news_items_df' not in st.session_state:
    st.session_state.news_items_df = pd.DataFrame()
if 'last_fetch' not in st.session_state:
    st.session_state.last_fetch = "Never"

@st.cache_data(ttl=1800)
def fetch_and_process_all():
    """Fetches news, classifies sentiment, and logs/stores results."""
    
    # 1. Load Company Symbols
    # Get the top 20 company names for NewsAPI (for broad search)
    # and their symbols (for Marketaux)
    company_symbols = get_static_company_symbols() # Assume this returns a list of symbols
    
    # Extract just the top 10 for broad NewsAPI searches to save API quota
    company_keywords = company_symbols[:10] 
    
    # Marketaux often needs the ticker with exchange, assuming .NS for NSE
    marketaux_symbols = [s + ".NS" for s in company_symbols[:20]] # Use top 20 for finance news

    all_articles = []
    
    # 2. Fetch NewsAPI (General News, based on name/keyword)
    st.sidebar.info("Fetching from NewsAPI...")
    for keyword in company_keywords:
        articles = fetch_from_newsapi(keyword)
        for art in articles:
            art['company'] = keyword
            all_articles.append(art)
    
    # 3. Fetch Marketaux (Financial News, based on symbols)
    st.sidebar.info("Fetching from Marketaux...")
    marketaux_news = fetch_from_marketaux(marketaux_symbols)
    # Marketaux articles might not have the 'company' field readily, 
    # but we can infer it or process based on the response structure.
    for art in marketaux_news:
        art['company'] = ", ".join(marketaux_symbols) # Simple placeholder
        all_articles.append(art)
        
    # 4. Fetch RSS Feeds
    st.sidebar.info("Fetching from RSS...")
    for feed_url in RSS_FEEDS:
        all_articles += fetch_from_rss(feed_url)

    # 5. Classify Sentiment, Log, and Store
    final_news_list = []
    st.sidebar.info(f"Classifying {len(all_articles)} articles...")
    for art in all_articles:
        # Use title for sentiment analysis
        sentiment = classify_sentiment(art.get('title', ''))
        
        # Log the article
        log_article(art.get('company', 'RSS/Unknown'), art['title'], art['url'], art['timestamp'], sentiment)
        
        # Prepare for dashboard storage
        final_news_list.append({
            'company': art.get('company', 'Unknown'),
            'title': art['title'],
            'url': art['url'],
            'timestamp': art['timestamp'],
            'sentiment': sentiment
        })

    # Update Streamlit state
    if final_news_list:
        new_df = pd.DataFrame(final_news_list)
        # Append new news to existing DataFrame and drop duplicates
        combined_df = pd.concat([st.session_state.news_items_df, new_df]).drop_duplicates(subset=['title', 'url'], keep='first')
        st.session_state.news_items_df = combined_df.sort_values(by='timestamp', ascending=False)
        st.session_state.last_fetch = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.sidebar.success(f"Fetch complete! Total articles: {len(st.session_state.news_items_df)}")


# --- Scheduling Logic (Initial Fetch) ---
# Fetch once immediately on app startup
if st.session_state.last_fetch == "Never":
    fetch_and_process_all()


# --- Streamlit Dashboard Layout ---
st.title("NSE Companies News Dashboard")
st.markdown(f"**Last fetched:** {st.session_state.last_fetch}")
st.markdown(f"Total articles tracked: **{len(st.session_state.news_items_df)}**")

# Sidebar filters
st.sidebar.title("Filters & Controls")
company_filter = st.sidebar.text_input("Filter by Company", "").strip()
sentiment_filter = st.sidebar.selectbox("Sentiment", ["All", "positive", "neutral", "negative"])
if st.sidebar.button("Fetch Now"):
    fetch_and_process_all()

# --- Display Logic ---
df = st.session_state.news_items_df.copy()

# Apply filters
if company_filter:
    df = df[df['company'].str.contains(company_filter, case=False)]
if sentiment_filter != 'All':
    df = df[df['sentiment'] == sentiment_filter]

# Display headlines
if df.empty:
    st.write("No articles found for the selected filters.")
else:
    st.write("### Filtered News Headlines")
    st.dataframe(df[['company', 'title', 'sentiment', 'timestamp', 'url']], 
                 column_config={"url": st.column_config.LinkColumn("URL")})

# To implement actual scheduling (outside of Streamlit's reactive loop):
# You would typically run a separate Python script with the schedule/time.sleep loop
# that just calls fetch_and_process_all() and saves the results to a file/database,
# and then Streamlit loads the results from that persistent storage.