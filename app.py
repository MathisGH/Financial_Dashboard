# How to run the app: streamlit run app.py

import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000") # Default to localhost for local testing, but can be overridden by setting the API_URL environment variable (in the docker-compose)

### Function to display a company card
def display_company_card(company_name):
    """Gather data from API and display it in a card format with score, evolution, and news"""
    try:
        response = requests.get(f"{API_URL}/news/{company_name}")
        if response.status_code == 200:
            data = response.json()
            global_score = data.get("global_score", 50.0)
            history = data.get("score_history", {})
            news = data.get("news", [])

            yesterday_str = (pd.Timestamp.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            yesterday_score = history.get(yesterday_str, global_score)
            evolution = round(((global_score - yesterday_score) / yesterday_score) * 100, 2) if yesterday_score != 0 else 0

            with st.container(border=True):
                st.subheader(f"{company_name}")
                
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("Score", f"{global_score}/100", delta=f"{evolution}%")
                m_col2.metric("Articles", len(news))

                if history:
                    df_hist = pd.DataFrame(list(history.items()), columns=['Date', 'Score'])
                    df_hist['Date'] = pd.to_datetime(df_hist['Date'])
                    st.line_chart(df_hist.set_index('Date')['Score'], height=200)
                else:
                    st.info("No history yet.")
        else:
            st.error(f"Error {company_name}: API Unreachable")
    except Exception as e:
        st.error(f"Connection error for {company_name}")

st.set_page_config(layout="wide") # Use the entire width of the page
st.title("Financial News Sentiment Dashboard V1")

### Sidebar
st.sidebar.header("Options")
if st.sidebar.button("Update News Data"):
    with st.spinner("Scraping new articles..."):
        requests.post(f"{API_URL}/update_news")
        st.sidebar.success("Database updated!")

companies = st.sidebar.multiselect(
    "Select Companies",
    options=["Apple", "Nvidia", "Meta", "Tesla", "Netflix"],
    default=["Apple"]
)

# Display selected companies
if st.button("Analyze Selected Companies"):
    for i in range(0, len(companies), 2):
        cols = st.columns(2)
        with cols[0]:
            display_company_card(companies[i])
        if i + 1 < len(companies):
            with cols[1]:
                display_company_card(companies[i+1])