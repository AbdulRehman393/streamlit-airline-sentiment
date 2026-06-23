import streamlit as st
import pandas as pd
import numpy as np



st.title("Sentiment Analysis of Tweet about US Airlines")
st.sidebar.title("Sentiment Analysis of Tweet about US Airlines ")

st.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")
st.sidebar.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")

DATA_URL = r"C:\Users\PMLS\OneDrive - Higher Education Commission\Desktop\New Desktop Material\Courses , Learning Content and Material\Create Interactive Dashboards with Streamlit and Python/Tweets.csv"

# @st.cache_data stores the output of this function in Streamlit's cache.
# It prevents loading and processing the CSV file again every time the app reruns,
# making the Streamlit app faster and more efficient.
@st.cache_data(persist = True)
def load_data():
    data = pd.read_csv(DATA_URL)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

data = load_data()
