import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt


st.title("Sentiment Analysis of Tweet about US Airlines")
st.sidebar.title("Sentiment Analysis of Tweet about US Airlines ")

st.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")
st.sidebar.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")

DATA_URL = r"DATA_URL = "https://raw.githubusercontent.com/AbdulRehman393/streamlit-airline-sentiment/main/data/Tweets.csv"

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
# st.sidebar.number_input("Hour of the day", min_value = 1, max_value = 24)

hour = st.sidebar.slider("Hour of the day", 0, 23)  

# Extract the hour from the 'tweet_created' column and keep
# only the tweets posted at the selected hour
modified_data = data[data['tweet_created'].dt.hour == hour]

if not st.sidebar.checkbox("Close", True, key='hide_map'):
    st.sidebar.markdown("### Tweets locations based on the time of the day")
    # Display the number of tweets posted during the selected one-hour time interval.
    st.markdown("%i tweets between %i:00 and %i:00" % (len(modified_data), hour, (hour+1)%24))
    # Display the locations of the filtered tweets on an interactive map.   
    st.map(modified_data)
    if st.sidebar.checkbox("Show raw data", False):
        st.write(modified_data)

st.sidebar.subheader("Breakdown airline tweets by sentiment")
choice = st.sidebar.multiselect('Pick Airlines', ('US Airways', 'United', 'American', 
                                                  'Southwest', 'Delta', 'Virgin America'), key = 'airline_selection')

if len(choice) > 0:
    choice_data = data[data.airline.isin(choice)]
    # Create a histogram to visualize the number of tweets for each selected airline.
    # The bars are colored and grouped by sentiment (positive, neutral, negative),
    # with a separate subplot for each sentiment.
    fig_choice = px.histogram(choice_data, x = 'airline', y = 'airline_sentiment', histfunc = 'count',
                              color = 'airline_sentiment', facet_col = 'airline_sentiment', 
                              labels = {'airline_sentiment': 'tweets'}, height = 600, width = 800)
    st.plotly_chart(fig_choice)

st.sidebar.header("Word Cloud")
word_sentiment = st.sidebar.radio('Select a sentiment for the word cloud', ('positive', 'neutral', 'negative'))

if not st.sidebar.checkbox('Close', True, key = '3'):
    # Filter the dataset to include only tweets with the selected sentiment
    st.header('Word cloud for %s sentiment' % (word_sentiment))
    # Filter the dataset to include only tweets with the selected sentiment
    df = data[data['airline_sentiment']==word_sentiment]
    words = ' '.join(df['text'])
    # Remove URLs, Twitter usernames, and "RT" (Retweet) from the text
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
     # Create a WordCloud object and generate the word cloud from the cleaned text
    wordcloud = WordCloud(stopwords = STOPWORDS, background_color = 'white', height = 600, width = 800
                          ).generate(processed_words)
    
    # Create a Matplotlib figure and axes for displaying the word cloud
    fig, ax = plt.subplots(figsize = (10, 8))
    # Display the generated word cloud image
    ax.imshow(wordcloud, interpolation = "bilinear")
    # Hide the x-axis and y-axis for a cleaner appearance
    ax.axis("off")
    # Display the Matplotlib figure in the Streamlit application
    st.pyplot(fig)

    
