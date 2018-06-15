# Text Analysis and Sentiment Info
from textblob import TextBlob

def get_sentiment_info(card):
    text_to_test = ''
    if card['title']:
        text_to_test = text_to_test + card['title']

    if card['content']:
        text_to_test = text_to_test + card['content']

    text = text_to_test
    analysis = TextBlob(text)
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    else:
        return 'negative'