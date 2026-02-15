# How to run the app: streamlit run app.py

import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000") # Default to localhost for local testing, but can be overridden by setting the API_URL environment variable (in the docker-compose)

st.title("Financial News Sentiment Dashboard V0.1")

st.sidebar.header("Options")

if st.sidebar.button("Update News Data"):
    with st.spinner("Updating news data..."):
        response = requests.post(f"{API_URL}/update_news")
    if response.status_code == 200:
        st.success("News data updated successfully!")
    else:
        st.error("Failed to update news data.")

# company_name = st.text_input("Enter the company name you want to analyze:", "Apple Inc")
company_name = st.selectbox("Select a company:", ["Apple", "Nvidia", "Meta", "Tesla", "Netflix"])
if st.button(f"Get News Sentiments for {company_name}"):
    with st.spinner("Fetching news data..."):
        response = requests.get(f"{API_URL}/news/{company_name}")
        # response = requests.get(f"http://localhost:8000/news/{company_name}") # For local testing without Docker, use localhost instead of api
    if response.status_code == 200:
        st.success("Data fetched successfully!")

        data = response.json()
        global_score = data.get("global_score", 50.0)
        history = data.get("score_history", {})
        news = data.get("news", [])
        
        yesterday_str = (pd.Timestamp.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
        yesterday_score = history.get(yesterday_str, global_score) # By default, if no data for yesterday, no evolution
        
        evolution = round(((global_score - yesterday_score) / yesterday_score) * 100, 2) if yesterday_score != 0 else 0

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label=f"Ticker: {company_name}", value=company_name)
        with col2:
            st.metric(label="Score of the Day", value=f"{global_score}/100", delta=f"{evolution}%")
        with col3:
            st.metric(label="Articles Analyzed", value=len(news))

        st.write("### Global Score Trend (Last 7 Days)")
        if history:
            df_history = pd.DataFrame(list(history.items()), columns=['Date', 'Score'])
            df_history['Date'] = pd.to_datetime(df_history['Date'])
            df_history = df_history.sort_values('Date')
            
            st.line_chart(df_history.set_index('Date')['Score'])
        else:
            st.info("Not enough history yet.")

        df_news = pd.DataFrame(news)
        if not df_news.empty:
            with st.expander("See detailed articles", expanded=False):
                for index, row in df_news.iterrows():
                    st.subheader(row['title'])
                    st.write(f"**Source:** {row['source']}")
                    st.write(f"**Sentiment:** {row['sentiment_label']}")
                    st.write(f"**Published on:** {row['publishing_date']}")
                    st.markdown("---")

    else:
        st.error("Failed to fetch data from the API.")