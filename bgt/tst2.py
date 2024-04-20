import re 
import tweepy 
from tweepy import OAuthHandler 
from textblob import TextBlob 
from textblob.sentiments import NaiveBayesAnalyzer

from flask import Flask, render_template , redirect, url_for, request
import string
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from snowballstemmer import stemmer

ar_stemmer = stemmer("arabic")

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

def get_tweet_sentiment(tweet): 
    cleaned_tweet = cleaningText(tweet)
    tokens = tokenizingText(cleaned_tweet)
    filtered_tokens = filteringText(tokens)
    stemmed_tokens = stemmingText(filtered_tokens)
    processed_tweet = toSentence(stemmed_tokens)
    return processed_tweet

# Update the get_tweets function to process Arabic text
def get_tweets(api, query, count=5): 
    count = int(count)
    tweets = [] 
    try: 
        fetched_tweets = tweepy.Cursor(api.search_tweets, q=query, lang='ar', tweet_mode='extended').items(count)
        
        for tweet in fetched_tweets: 
            parsed_tweet = {} 

            if 'retweeted_status' in dir(tweet):
                parsed_tweet['text'] = tweet.retweeted_status.full_text
            else:
                parsed_tweet['text'] = tweet.full_text

            parsed_tweet['sentiment'] = get_tweet_sentiment(parsed_tweet['text']) 

            if tweet.retweet_count > 0: 
                if parsed_tweet not in tweets: 
                    tweets.append(parsed_tweet) 
            else: 
                tweets.append(parsed_tweet) 
        return tweets 
    except tweepy.TweepyException as e: 
        print("Error : " + str(e)) 

app = Flask(__name__)
app.static_folder = 'static'

@app.route('/')
def home():
    return render_template("tst.html")

# Update the route to process Arabic text
@app.route("/predict1", methods=['POST','GET'])
def pred1():
    if request.method=='POST':
        text = request.form['txt']
        processed_text = get_tweet_sentiment(text)
        return render_template('result1.html', msg=text, result=processed_text)

if __name__ == '__main__':
    app.debug=True
    app.run(host='localhost')
