from dotenv import load_dotenv
import requests
import os
from src.db import get_connection, create_news_table, get_last_article_date
import sqlite3
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Variables

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

API_URL = "https://newsapi.org/v2/everything"

companies = ["Apple", "Nvidia", "Amazon", "Google", "Meta", "Tesla", "Netflix"]

# Step 1: fetch news data from NewsAPI
def fetch_news(company, params):
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json().get("articles", [])
    else:
        print(f"Error fetching news for {company}: {response.status_code}")
        return []

# Step 2: store news data into the database
def save_to_db(articles, company):
    conn = get_connection()
    cursor = conn.cursor()

    data_to_insert = []
    sql_query = """
            INSERT OR IGNORE INTO news (source, company, title, description, publishing_date, url, sentiment_label, sentiment_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

    for article in articles:
        data_to_insert.append((
            article['source']['name'],
            company,
            article['title'],
            article['description'],
            article['publishedAt'],
            article['url'],
            None,
            None
        ))
    cursor.executemany(sql_query, data_to_insert) # Adding multiple records at once
    conn.commit()
    conn.close()

def automated_loop():
    for company in companies:
        last_date = get_last_article_date(company)
        from_date = last_date if last_date else "2026-02-02" # just a default date to fetch all news if the database is empty
        params = {
            "q": company,
            "apiKey": NEWSAPI_KEY,
            "language": "en",
            "sortBy": "publishedAt", # options: popularity, publishedAt and relevancy (mix of both)
            "pageSize": 50,
            "from": from_date # just a default date to fetch all news if the database is empty
        }
        articles = fetch_news(company, params)
        print(f"Fetched {len(articles)} articles for {company}")
        save_to_db(articles, company)

### -------------------------------------------------------------------------------------------------------------- ###

if __name__ == "__main__":
    logger.info("Starting news ingestion process...")
    while True:
        try:
            automated_loop()
            logger.info("News ingestion cycle completed successfully.")
        except Exception as e:
            logger.error(f"Error during news ingestion: {e}")
        time.sleep(3600) # Wait for 1 hour before the next cycle