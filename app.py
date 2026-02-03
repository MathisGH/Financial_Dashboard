# How to run the app: streamlit run app.py

import streamlit as st
import pandas as pd
import requests

st.title("Financial News Sentiment Dashboard V1.0")

company_name = st.text_input("Enter the company name you want to analyze:", "Apple Inc")
if st.button("Get News Sentiments"):
    with st.spinner("Fetching news data..."):
        response = requests.get(f"http://127.0.0.1:8000/news/{company_name}")
    if response.status_code == 200:
        st.json(response.json())
        st.success("Data fetched successfully!")
    else:
        st.error("Failed to fetch data from the API.")