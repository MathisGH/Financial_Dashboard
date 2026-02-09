# How to run the api: uvicorn api:app --reload

from fastapi import FastAPI
from src.db import get_connection
import logging
from pydantic import BaseModel
from typing import List
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

app = FastAPI()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

model_name = "ProsusAI/finbert" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
logger.info("Model and tokenizer loaded successfully")

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

    query = "SELECT id, title, description, source, sentiment_label, sentiment_score, publishing_date FROM news WHERE company = ?"

    cursor.execute(query, (company_name,))
    results = cursor.fetchall()
    
    news_list = []
    for row in results:
        # row[0]=id, row[1]=title, row[2]=description, row[3]=source, row[4]=label, row[5]=score, row[6]=date
        if row[4] is None or row[5] is None: # If sentiment_label or sentiment_score is None, we need to process it before returning
            logger.info(f"Processing sentiment for article: {row[1]}")

            title = row[1] if row[1] else ""
            description = row[2] if row[2] else ""
            content = f"{title}. {description}"

            inputs = tokenizer(content, return_tensors="pt", padding=True, max_length=512, truncation=True) # Truncate long texts, set max length because of model limits and padding is needed for batch processing (even if single input, puts "" tokens to make up length)
            labels = model.config.id2label
            with torch.no_grad():
                outputs = model(**inputs)
                logits = outputs.logits
                probabilities = F.softmax(logits, dim=-1)
                predicted_class = torch.argmax(probabilities, dim=-1).item()
                sentiment_label = labels[predicted_class]
                sentiment_score = probabilities[0][predicted_class].item()
                
            # Update the database with the new sentiment_label and sentiment_score
            update_query = "UPDATE news SET sentiment_label = ?, sentiment_score = ? WHERE id = ?"
            cursor.execute(update_query, (sentiment_label, sentiment_score, row[0]))
            conn.commit()
        else:
            sentiment_label = row[4]
            sentiment_score = row[5]
        news_item = {
            "title": row[1] if row[1] else "No title",
            "source": row[3] if row[3] else "Unknown source",
            "sentiment_label": sentiment_label if sentiment_label else "Unknown sentiment",
            "sentiment_score": sentiment_score if sentiment_score is not None else 0.0,
            "publishing_date": row[6] if row[6] else "Unknown date"
        }
        news_list.append(news_item)
    conn.close()
    return {"company": company_name, "news": news_list}
