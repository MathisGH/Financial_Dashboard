import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "news.db"

# Step 1: connection to the database
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

# Step 2: create table
def create_news_table():
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


### -------------------------------------------------------------------------------------------------------------- ###

if __name__ == "__main__":
    create_news_table()