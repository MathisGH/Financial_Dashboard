# How to run the api: uvicorn api:app --reload

from fastapi import FastAPI
from src.db import get_connection
import logging
from pydantic import BaseModel
from typing import List

app = FastAPI()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NewsArticle(BaseModel): # Model for a news article that will be returned by the API
    title: str
    source: str
    sentiment_label: str
    sentiment_score: float
    publishing_date: str

class NewsResponse(BaseModel): # Model for the response that will be returned by the API (list of news articles)
    company: str
    news: List[NewsArticle]

logging.info("API server is starting up...")

@app.get("/")
async def root():
    return {"message": "test okok"}


@app.get("/news/{company_name}", response_model=NewsResponse)
async def get_news(company_name: str):
    logger.info(f"Received request for news sentiment analysis of company: {company_name}")
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT title, source, sentiment_label, sentiment_score, publishing_date FROM news WHERE company = ?"

    cursor.execute(query, (company_name,))
    results = cursor.fetchall()

    conn.close()
    
    news_list = []
    for row in results:
        news_item = {
            "title": row[0],
            "source": row[1],
            "sentiment_label": row[2],
            "sentiment_score": row[3],
            "publishing_date": row[4]
        }
        news_list.append(news_item)
    return {"company": company_name, "news": news_list}
