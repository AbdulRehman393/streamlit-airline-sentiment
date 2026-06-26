import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


st.title("Sentiment Analysis of Tweet about US Airlines")
st.sidebar.title("Sentiment Analysis of Tweet about US Airlines ")

st.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")
st.sidebar.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")

DATA_URL = r"C:\Users\PMLS\OneDrive - Higher Education Commission\Desktop\New Desktop Material\Courses , Learning Content and Material\Create Interactive Dashboards with Streamlit and Python\project\data\Tweets.csv"

# @st.cache_data stores the output of this function in Streamlit's cache.
# It prevents loading and processing the CSV file again every time the app reruns,
# making the Streamlit app faster and more efficient.

# @st.cache_data(persist=True) keeps the cached data even after the app restarts.
# Use it when your app is complete and the data changes infrequently.

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    data['tweet_created'] = pd.to_datetime(data['tweet_created'])
    return data

data = load_data()

# We use st.write() to display information on a Streamlit web app.
# st.write(data)

st.sidebar.subheader("Show random tweet")
random_tweet = st.sidebar.radio('Sentiment', ('positive', 'neutral', 'negative'))
st.sidebar.markdown(
    data.query('airline_sentiment ==  @random_tweet')[["text"]]
        .sample(n=1).iat[0 ,0])    

st.sidebar.markdown("### Number of tweets by sentiments")
select = st.sidebar.selectbox("Visulization type" , ['Histogram', 'Pie chart'], key = '1')

# Select the 'airline_sentiment' column and count how many times each
# unique sentiment (positive, neutral, negative) appears.
sentiment_count = data['airline_sentiment'].value_counts()

# Convert the Series into a DataFrame by creating two columns:
# 'Sentiment' for the sentiment names and 'Tweets' for their counts.
sentiment_count = pd.DataFrame({'Sentiment':sentiment_count.index, 'Tweets': sentiment_count.values})

if not st.sidebar.checkbox("Hide", True):
    st.markdown("### Number of tweets by sentiment")
    if select == 'Histogram':
        fig = px.bar(sentiment_count, x = 'Sentiment', y ='Tweets', color = 'Tweets', height = 500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(sentiment_count, values = 'Tweets', names = 'Sentiment')
        st.plotly_chart(fig)

st.sidebar.subheader("When and where are users tweeting from?")
#st.sidebar.slider("Hour of the day", 0, 23)  # this adds slider   st.sidebar.slider("text", min_value, max_value)
st.sidebar.number_input("Hour of the day", min_value = 1, max_value = 24)

