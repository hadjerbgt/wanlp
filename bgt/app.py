import re 
import pandas
from flask import Flask, render_template, request
import tweepy 
from textblob import TextBlob 
from textblob.sentiments import NaiveBayesAnalyzer
import string
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from snowballstemmer import stemmer
from camel_tools.sentiment import SentimentAnalyzer

ar_stemmer = stemmer("arabic")
sa = SentimentAnalyzer("CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment")

def remove_chars(text, del_chars):
    translator = str.maketrans('', '', del_chars)
    return text.translate(translator)

def remove_repeating_char(text):
    return re.sub(r'(.)\1{2,}', r'\1', text)

def cleaningText(text):
    text = re.sub(r'[0-9]+', '', text)  
    arabic_punctuations = '''`÷×؛<>_()*&^%][ـ،/:"؟.,'{}~¦+|!”…“–ـ'''
    english_punctuations = string.punctuation
    punctuations_list = arabic_punctuations + english_punctuations
    text = remove_chars(text, punctuations_list)
    text = remove_repeating_char(text)
    text = text.replace('\n', ' ')  
    text = text.strip(' ')  
    return text

def tokenizingText(text): 
    tokens_list = word_tokenize(text) 
    return tokens_list

def filteringText(tokens_list):  
    listStopwords = set(stopwords.words('arabic'))
    filtered = []
    for txt in tokens_list:
        if txt not in listStopwords:
            filtered.append(txt)
    tokens_list = filtered 
    return tokens_list

def stemmingText(tokens_list): 
    tokens_list = [ar_stemmer.stemWord(word) for word in tokens_list]
    return tokens_list

def toSentence(words_list):  
    sentence = ' '.join(word for word in words_list)
    return sentence

def get_tweet_sentiment(sentence): 
    cleaned_sentence = cleaningText(sentence)
    tokens = tokenizingText(cleaned_sentence)
    processed_tokens = []
    for token in tokens:
        processed_token, sentiment = get_word_sentiment(token)  # Get sentiment for each word
        processed_tokens.append(processed_token)
    processed_sentence = toSentence(processed_tokens)
    return processed_sentence, sentiment

def get_word_sentiment(word):
    # Process each word here
    sentiment = sa.predict([word])[0]  # Assuming sa.predict can process individual words
    return word, sentiment


# Update the get_tweets function to process Arabic text
def get_tweets(file, query, count=5): 
    count = int(count)
    tweets = [] 
    try: 
        for index, row in file.iterrows():
            if query in row['tweet']:  # Assuming 'tweet' is the name of the column containing the tweets
                tweet = row['tweet']
                sentiment = get_tweet_sentiment(tweet)[1]  # Get sentiment for the tweet
                tweets.append({"text": tweet, "sentiment": sentiment})  # Append tweet and its sentiment
                if len(tweets) == count:
                    break
        return tweets 
    except Exception as e: 
        print("Error : " + str(e))
        return []  # Return an empty list if an error occurs or no tweets are found

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/predict1", methods=['POST','GET'])
def pred1():
    if request.method=='POST':
        text = request.form['txt']
        processed_text, sentiment = get_tweet_sentiment(text)
        return render_template('result1.html', msg=text, result=processed_text, sentiment=sentiment)


from collections import Counter

@app.route("/predict", methods=['POST','GET'])
def pred():
    if request.method=='POST':
        query = request.form['query']
        count = request.form['num']
        file = pandas.read_csv('tweets.csv')
        fetched_tweets = get_tweets(file, query, count) 
        sentiments = [tweet["sentiment"] for tweet in fetched_tweets]  # Extract sentiments
        sentiment_counts = Counter(sentiments)  # Count the occurrences of each sentiment
        return render_template('result.html', result=fetched_tweets, sentiments=sentiments, sentiment_counts=sentiment_counts)




if __name__ == '__main__':
    app.debug=True
    app.run(host='localhost')
