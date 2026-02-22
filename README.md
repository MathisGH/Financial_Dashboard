### Financial Sentiment Analysis Dashboard ###


Containerized pipeline hosted on **AWS** that fetches real-time financial news, performs sentiment analysis using **FinBERT**, and visualizes the results through a Streamlit web interface.



## Architecture

The project is built using Docker:

1.  **Ingestion Worker**: A background service that periodically polls the NewsAPI, filters for specific companies (Apple, Meta, Netflix, etc.), and stores raw data in a SQLite database.
2.  **FastAPI Backend**: Loads the FinBERT model and provides endpoints to process and serve sentiment data.
3.  **Streamlit Frontend**: A dashboard that queries the API to display sentiment trends and article details.

## Tech Stack

* **Language:** Python 3.12
* **NLP Model:** [ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert) (Hugging Face)
* **Backend:** FastAPI + Uvicorn
* **Frontend:** Streamlit
* **Database:** SQLite (Shared Volume)
* **DevOps:** Docker, Docker Compose, AWS EC2

## Local Setup

### 1. Prerequisites
* Docker & Docker Compose installed.
* A [NewsAPI](https://newsapi.org/) Key.

### 2. Configuration
Create a `.env` file in the root directory:
```env
NEWSAPI_KEY=your_api_key_here
```

### 3. Initialize Docker
```
docker compose up --build -d
```

### 4. Initialize the database
```
docker compose exec api python src/db.py
```

### 5. Access the Dashboard and the API documentation
- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs


## Notes

This project runs on a t3.micro instance (AWS EC2), I had to use virtual memory (SWAP) in order handle high memory demand and expanded the EBS volume from 8 to 20GB