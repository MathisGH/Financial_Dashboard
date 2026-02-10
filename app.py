# How to run the app: streamlit run app.py

import streamlit as st
import pandas as pd
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000") # Default to localhost for local testing, but can be overridden by setting the API_URL environment variable

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
company_name = st.selectbox("Select a company:", ["Apple", "Nvidia", "Microsoft", "Amazon", "Google", "Meta", "Tesla", "Netflix"])
if st.button("Get News Sentiments"):
    with st.spinner("Fetching news data..."):
        response = requests.get(f"{API_URL}/news/{company_name}")
        # response = requests.get(f"http://localhost:8000/news/{company_name}") # For local testing without Docker, use localhost instead of api
        print(response)
        df = pd.DataFrame(response.json().get("news", []))
    if response.status_code == 200:
        st.success("Data fetched successfully!")

        col1, col2 , col3 = st.columns(3)
        with col1:
            st.write(f"### {company_name}")
        with col2:
            score_of_the_day = "not yet implemented"
            st.write(f"### Score of the day: {score_of_the_day}")
        with col3:
            evolution_since_yesterday = "not yet implemented"
            st.write(f"### Evolution since yesterday: {evolution_since_yesterday} % change")

        st.line_chart(df['sentiment_score']) # There will be the evolution graph of sentiment scores over time (7 days, 1 month, etc.)

        if not df.empty:
            with st.expander("See detailed articles", expanded=False):
                for index, row in df.iterrows():
                    st.subheader(row['title'])
                    st.write(f"**Source:** {row['source']}")
                    st.write(f"**Sentiment:** {row['sentiment_label']}")
                    st.write(f"**Published on:** {row['publishing_date']}")
                    st.markdown("---")

    else:
        st.error("Failed to fetch data from the API.")