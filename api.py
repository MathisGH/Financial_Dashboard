from fastapi import FastAPI
from src.db import get_connection

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "test okok"}


@app.get("/news/{company_name}")
async def get_news(company_name: str):
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
