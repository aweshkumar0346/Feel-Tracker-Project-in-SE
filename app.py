from flask import Flask, request, render_template
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

import re
from nltk.corpus import stopwords
nltk.download('stopwords')

app = Flask(__name__)

@app.route('/') 
def my_form():
    return render_template('form.html')
@app.route('/', methods=['POST'])
def my_form_post():
    stop_words = stopwords.words('english')
    text1 = request.form['text1'].lower()
    
    if not text1.strip():
        return "Please enter a word or phrase to analyze!"
    
    text_final = ''.join(c for c in text1 if not c.isdigit())   
    processed_doc1 = ' '.join([word for word in text_final.split() if word not in stop_words])

    sa = SentimentIntensityAnalyzer()
    dd = sa.polarity_scores(text=processed_doc1)
    compound = round((1 + dd['compound']) / 2, 2)
    
    labels = ['Positive', 'Neutral', 'Negative']
    counts = [dd['pos'], dd['neu'], dd['neg']]

    plt.figure(figsize=(8, 6))
    plt.bar(labels, counts, color=['green', 'gray', 'red'])
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Sentiment Analysis Results')
    plot_filename = 'static/sentiment_plot.png'
    plt.savefig(plot_filename)  

    return render_template('form.html', final=compound, text1=text1, text2=dd['pos'], text5=dd['neg'], text4=compound, text3=dd['neu'], plot_image=plot_filename)

def scrape_reviews(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    reviews = []

    review_elements = soup.find_all('div', class_='review')

    for review_element in review_elements:
        review = review_element.text.strip()
        reviews.append(review)

    return reviews

def analyze_sentiment(reviews):
    sid = SentimentIntensityAnalyzer()
    sentiments = []

    for review in reviews:
        sentiment_score = sid.polarity_scores(review)
        sentiments.append(sentiment_score)

    return sentiments

@app.route('/')
def index():
    return render_template('form.html')

import re

@app.route('/analyze', methods=['POST'])
@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.form['url']
    
    if not url:
        return "Please enter a valid URL!"  
    
    reviews = scrape_reviews(url)
    sentiments = analyze_sentiment(reviews)
    
    pos_count = sum(1 for sentiment in sentiments if sentiment['compound'] > 0)
    neu_count = sum(1 for sentiment in sentiments if sentiment['compound'] == 0)
    neg_count = sum(1 for sentiment in sentiments if sentiment['compound'] < 0)
    
    labels = ['Positive', 'Neutral', 'Negative']
    counts = [pos_count, neu_count, neg_count]
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, counts, color=['green', 'gray', 'red'])
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.title('Sentiment Analysis Results')
    plt.savefig('static/sentiment_plot1.png')  

    review_snippets = [review.split('\n')[:3] for review in reviews] 

    review_data = zip(review_snippets, sentiments)
    
    return render_template('results.html', review_data=review_data, plot_image='static/sentiment_plot1.png')

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5002, threaded=True)
