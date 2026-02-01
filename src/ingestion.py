from dotenv import load_dotenv
import requests
import os
from db import get_connection, create_news_table
import sqlite3

# Variables

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

API_URL = "https://newsapi.org/v2/everything"

companies = ["Apple Inc"]

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


### -------------------------------------------------------------------------------------------------------------- ###

if __name__ == "__main__":
    create_news_table()
    for company in companies:
        params = {
            "q": company,
            "apiKey": NEWSAPI_KEY,
            "language": "en",
            "sortBy": "relevancy", # mix between popularity, publishedAt
            "pageSize": 20,
        }
        articles = fetch_news(company, params)
        print(f"Fetched {len(articles)} articles for {company}")
        save_to_db(articles, company)
    print("News ingestion completed.")