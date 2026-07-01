import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

TEXT_COLUMNS = ("text", "tweet", "tweet_text", "full_text", "content", "body", "Tweets")
SENTIMENT_COLUMNS = ("airline_sentiment", "sentiment", "analysis", "label")
AIRLINE_COLUMNS = ("airline", "carrier", "company", "brand")
CREATED_COLUMNS = ("tweet_created", "created_at", "created", "date", "timestamp")
MAX_UPLOAD_BYTES = 2 * 1024 * 1024
MAX_CSV_ROWS = 5000

st.title("Sentiment Analysis of Tweet about US Airlines")
st.sidebar.title("Sentiment Analysis of Tweet about US Airlines ")

st.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")
st.sidebar.markdown("This application is a Streamlit dashboard used to analyze the sentiments of Tweets 𝕩")

DATA_URL = "https://raw.githubusercontent.com/AbdulRehman393/streamlit-airline-sentiment/main/data/Tweets.csv"

# @st.cache_data stores the output of this function in Streamlit's cache.
# It prevents loading and processing the CSV file again every time the app reruns,
# making the Streamlit app faster and more efficient.

# @st.cache_data(persist=True) keeps the cached data even after the app restarts.
# Use it when your app is complete and the data changes infrequently.

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL)
    return normalize_tweet_data(data)

def first_existing_column(columns, candidates):
    normalized_columns = {str(column).strip().lower(): column for column in columns}
    for candidate in candidates:
        column = normalized_columns.get(candidate.lower())
        if column is not None:
            return column
    return None

def normalize_tweet_data(data):
    normalized = data.copy()
    text_column = first_existing_column(normalized.columns, TEXT_COLUMNS)
    if text_column is None:
        raise ValueError("CSV must include a text, tweet, tweet_text, full_text, content, body, or Tweets column.")
    normalized["text"] = normalized[text_column].fillna("").astype(str)

    sentiment_column = first_existing_column(normalized.columns, SENTIMENT_COLUMNS)
    if sentiment_column is None:
        normalized["airline_sentiment"] = "unknown"
    else:
        normalized["airline_sentiment"] = (
            normalized[sentiment_column].fillna("unknown").astype(str).str.strip().str.lower()
        )
        normalized.loc[normalized["airline_sentiment"] == "", "airline_sentiment"] = "unknown"

    airline_column = first_existing_column(normalized.columns, AIRLINE_COLUMNS)
    if airline_column is None:
        normalized["airline"] = "Unknown"
    else:
        normalized["airline"] = normalized[airline_column].fillna("Unknown").astype(str).str.strip()
        normalized.loc[normalized["airline"] == "", "airline"] = "Unknown"

    created_column = first_existing_column(normalized.columns, CREATED_COLUMNS)
    if created_column is None:
        normalized["tweet_created"] = pd.NaT
    else:
        normalized["tweet_created"] = pd.to_datetime(normalized[created_column], errors="coerce")

    return normalized

def load_uploaded_data(uploaded_file):
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError("CSV file is too large. Upload a file under 2 MB.")
    try:
        uploaded_data = pd.read_csv(uploaded_file, nrows=MAX_CSV_ROWS + 1)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
        raise ValueError("Could not read the CSV. Upload a valid UTF-8 CSV file.") from error
    if len(uploaded_data) > MAX_CSV_ROWS:
        raise ValueError("CSV row limit is 5000 rows. Upload a smaller file.")
    return normalize_tweet_data(uploaded_data)

uploaded_file = st.sidebar.file_uploader(
    "Analyze another tweet CSV",
    type=["csv"],
    help="Use text, tweet, tweet_text, full_text, content, body, or Tweets for tweet text.",
)
if uploaded_file is None:
    data = load_data()
else:
    try:
        data = load_uploaded_data(uploaded_file)
        st.sidebar.success("Custom CSV loaded")
    except ValueError as error:
        st.sidebar.error(str(error))
        st.stop()

# We use st.write() to display information on a Streamlit web app.
# st.write(data)

st.sidebar.subheader("Show random tweet")
sentiment_options = tuple(data["airline_sentiment"].dropna().drop_duplicates())
if len(sentiment_options) == 0:
    sentiment_options = ("unknown",)
random_tweet = st.sidebar.radio('Sentiment', sentiment_options)
random_tweet_data = data.loc[data["airline_sentiment"] == random_tweet, "text"].dropna()
if len(random_tweet_data) > 0:
    st.sidebar.markdown(random_tweet_data.sample(n=1).iat[0])
else:
    st.sidebar.info("No tweet text available for this sentiment.")

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

has_timestamps = data["tweet_created"].notna().any()
if has_timestamps:
    hour = st.sidebar.slider("Hour of the day", 0, 23)
    # Extract the hour from the 'tweet_created' column and keep
    # only the tweets posted at the selected hour
    modified_data = data[data['tweet_created'].dt.hour == hour]
else:
    hour = 0
    modified_data = data
    st.sidebar.info("Add tweet_created or created_at to enable time filters.")

if not st.sidebar.checkbox("Close", True, key='hide_map'):
    st.sidebar.markdown("### Tweets locations based on the time of the day")
    # Display the number of tweets posted during the selected one-hour time interval.
    if has_timestamps:
        st.markdown("%i tweets between %i:00 and %i:00" % (len(modified_data), hour, (hour+1)%24))
    # Display the locations of the filtered tweets on an interactive map.
    if {"lat", "lon"}.issubset(modified_data.columns):
        st.map(modified_data)
    else:
        st.info("No lat and lon columns found for the map view.")
    if st.sidebar.checkbox("Show raw data", False):
        st.write(modified_data)

st.sidebar.subheader("Breakdown airline tweets by sentiment")
airline_options = tuple(data["airline"].dropna().drop_duplicates())
choice = st.sidebar.multiselect('Pick Airlines', airline_options, key = 'airline_selection')

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
word_sentiment = st.sidebar.radio('Select a sentiment for the word cloud', sentiment_options)

if not st.sidebar.checkbox('Close', True, key = '3'):
    # Filter the dataset to include only tweets with the selected sentiment
    st.header('Word cloud for %s sentiment' % (word_sentiment))
    # Filter the dataset to include only tweets with the selected sentiment
    df = data[data['airline_sentiment']==word_sentiment]
    words = ' '.join(df['text'].dropna().astype(str))
    # Remove URLs, Twitter usernames, and "RT" (Retweet) from the text
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
     # Create a WordCloud object and generate the word cloud from the cleaned text
    if len(processed_words.strip()) > 0:
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
    else:
        st.info("No words available for this sentiment.")

    
