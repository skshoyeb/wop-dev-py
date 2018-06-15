from flask import Flask, request
from flask_cors import CORS, cross_origin
import json
import base64
import requests
import logging
from db import add_to_fb, user_signup, get_posts, user_login, get_user_data, update_favs, upload_to_storage
from textAnalysis import get_sentiment_info

app = Flask(__name__)
CORS(app)


def get_as_base64(url):
    return base64.b64encode(requests.get(url).content)

@app.route('/')
def default():
    return 'Hello, World!'

@app.route('/add-positive-backup', methods=["POST"])
def add_positive_backup():

    req = json.loads(request.data)
    card = json.loads(req['data'])

    sentiment_info = get_sentiment_info(card)
    if sentiment_info == 'positive':
        add_to_fb(card)
    return sentiment_info


@app.route('/add-positive', methods=["POST"])
def add_positive():
    imageFile = request.files.get("imageFile")
    req = request.form
    card = {}
    card['title'] = req.get("title")
    card['content'] = req.get("content")
    card['image'] = req.get("image")
    
    sentiment_info = get_sentiment_info(card)
    if sentiment_info == 'positive':
        add_to_fb(card, imageFile)
    response = {}
    response['sentiment_info'] = sentiment_info
    response['card'] = card
    jsonres = json.dumps(response)
    return jsonres

@app.route('/upload-image', methods=["POST"])
def upload_image():
    image = request.files['imageFile']
    return upload_to_storage(image,'file',image.filename)
    
@app.route('/get-positives', methods=["GET"])
def get_positives():
    #req = json.loads(request.data)
    #data = json.loads(req['data'])
    return get_posts()

@app.route('/sign-up', methods=["POST"])
def sign_up():
    req = json.loads(request.data)
    user = json.loads(req['user'])
    return user_signup(user)

@app.route('/log-in', methods=["POST"])
def log_in():
    req = json.loads(request.data)
    user = json.loads(req['user'])
    return user_login(user)

@app.route('/get-user-info', methods=["POST"])
def get_user_info():
    req = json.loads(request.data)
    user = json.loads(req['user'])
    return get_user_data(user)

@app.route('/update-favorites', methods=["POST"])
def update_favorites():
    req = json.loads(request.data)
    card = json.loads(req['card'])
    return update_favs(card)

@app.route('/save-image', methods=["POST"])
def save_image():
    req = json.loads(request.data)
    url =req['url']
    return upload_to_storage(url)

if __name__ == '__main__':
    app.run('0.0.0.0')