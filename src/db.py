import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "news.db"

# Step 1: connection to the database
def get_connection():
    """
    Creates a connection to the SQLite database. If the database file does not exist, it will be created automatically.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True) # parents=True means that it will create all the intermediate directories if they don't exist, and exist_ok=True means that it won't raise an error if the directory already exists
    conn = sqlite3.connect(DB_PATH)
    return conn

# Step 2: create table
def create_news_table():
    """
    Creates the 'news' table in the database if it does not already exist. The table has the following columns:
    - id: an auto-incrementing primary key
    - source: the source of the news article
    - company: the company that the news article is about
    - title: the title of the news article
    - description: a brief description of the news article given by the news API
    - publishing_date: the date the news article was published
    - url: the URL of the news article (UNIQUE)
    - sentiment_label: the sentiment label assigned to the news article (assigned later by the model)
    - sentiment_score: the sentiment score assigned to the news article (same)
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   source TEXT,
                   company TEXT,
                   title TEXT,
                   description TEXT,
                   publishing_date TEXT,
                   url TEXT UNIQUE,
                   sentiment_label TEXT,
                   sentiment_score REAL)"""
    )
    conn.commit()
    conn.close()

def get_last_article_date(company_name):
    """
    Gets the publishing date of the most recent news article for a given company from the database.
    This is used to determine the 'from' date when fetching new articles from the News API, ensuring that we only fetch articles that are newer than the most recent one we already have in our database.    
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(publishing_date) FROM news WHERE company = ?", (company_name,))
    result = cursor.fetchone()[0]
    conn.close()
    return result 

def create_daily_scores_table():   
    """
    Creates the 'daily_scores' table in the database. The table has the following columns:
    - id: an auto-incrementing primary key
    - company: the company that the score is about
    - date: the date of the score
    - score: the sentiment score for that date
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_scores (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   company TEXT,
                   date TEXT,
                   score REAL)"""
    )
    conn.commit()
    conn.close()

### -------------------------------------------------------------------------------------------------------------- ###

if __name__ == "__main__":
    create_news_table()
    create_daily_scores_table()