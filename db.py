# firestore

import json
import os
import google.cloud
import logging
import datetime
import requests
from imgHandler import upload_to_storage
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service.json"

fireBaseDB = firestore.Client()
positivesDB = fireBaseDB.collection(u'posts')
usersDB = fireBaseDB.collection(u'users')
fbTransaction = fireBaseDB.transaction()

global positives_cache
global positives_cache_expire_at

positives_cache = []
positives_cache_expire_at = ''

def add_to_fb(card, imageFile):
    date_today = datetime.datetime.today()
    image_url = ''
    if card['title']:
        content = card['title']
    elif card['content']:
        content = card['content']
    card['date'] = date_today.strftime('%d/%m/%y')
    card['id'] = content[:10].replace(' ', '-') + '/' + date_today.strftime('%Y/%m/%d/%H%M%S%f')
    card['timestamp'] = date_today.strftime('%Y%m%d%H%M%S%f');
    docId = card['id'].replace('/','-')
    
    if imageFile:
        image_url = upload_to_storage(imageFile,u'file',docId)
    elif card['image']:
        image_url = upload_to_storage(card['image'],u'url',docId)
    print(image_url)
    card['image'] = image_url
    if image_url:
        split = image_url.split('.appspot.com/')
        card['thumb'] = '.appspot.com/thumb_'.join(split)
        print(card['thumb'])
    #if card['image']:
        #image_url = upload_to_storage(card['image'],u'url',docId)
        #card['image'] = image_url
    
    doc_ref = positivesDB.document(docId)
    doc_ref.set(card)
    return card

@firestore.transactional
def update_to_firestore(transaction, doc_ref, key, val):
    snapshot = doc_ref.get(transaction=transaction)
    return transaction.update(doc_ref, {
        key: val
    })

def add_to_firestore(doc_ref, data):
    return doc_ref.set(doc_ref, data)

def get_posts():
    all_posts = []
    posts = positivesDB.order_by(u'timestamp', direction=firestore.Query.DESCENDING).get()
    for doc in posts:
        all_posts.append(doc.to_dict())

    return json.dumps(all_posts)

def get_posts_backup(data):
    #min_posts = data['count'] or 4
    #offset = data['offset'] or 0
    #positives_cache_expiry_period = 600
    limit_val = data['limit'] or 1
    all_posts = []
    
    if data['timestamp'] != '':
        posts = positivesDB.order_by(u'timestamp', direction=firestore.Query.DESCENDING).start_after({
            u'timestamp': data['timestamp']
        }).limit(limit_val).get()
    else:
        posts = positivesDB.limit(limit_val).get()
    for doc in posts:
        all_posts.append(doc.to_dict())

    return json.dumps(all_posts)

def get_filtered_posts_backup(data):
    min_posts = data['minPosts'] or 10
    max_past_days = 60
    positives_cache_expiry_period = 600
    all_posts = []
    if data['type'] == 'date':
        if data['query'] == 'today':
            positives_expired = False
            date_today = datetime.datetime.today()
            global positives_cache
            global positives_cache_expire_at

            if positives_cache_expire_at:
                if (date_today - positives_cache_expire_at)/datetime.timedelta(minutes=1) < positives_cache_expiry_period:
                    positives_expired = True

            if len(positives_cache) and positives_expired is not False:
                all_posts = positives_cache
            else:
                date_today_formatted = date_today.strftime('%d/%m/%y')
                days_searched_for = 0
                positives_cache_expire_at = date_today
                while len(all_posts) < min_posts and days_searched_for < max_past_days:
                    posts = positivesDB.where(u'date', u'==', date_today_formatted).get()
                    for doc in posts:
                        if len(all_posts) < min_posts:
                            all_posts.append(doc.to_dict())
                    date_today = date_today - datetime.timedelta(days=1)
                    date_today_formatted = date_today.strftime('%d/%m/%y')
                    days_searched_for += 1
                positives_cache = all_posts

    elif data['type'] == 'id':
        posts = positivesDB.where(u'id', u'==', data['query']).get()
        for doc in posts:
            all_posts.append(doc.to_dict())

    return json.dumps(all_posts)


def user_signup(user):
    email = user['email']
    password = user['password']
    newuser = auth.create_user_with_email_and_password(email, password)
    return json.dumps(newuser)

def user_login(user):
    email = user['email']
    password = user['password']
    try:
        loggedInUser = auth.sign_in_with_email_and_password(email, password)
        return json.dumps(loggedInUser)
    except (requests.exceptions.HTTPError) as e:
        return json.dumps(e)

def get_user_data(user):
    user_id = user['user_id']
    user_doc_ref = usersDB.document(user_id)
    try:
        user_doc = user_doc_ref.get()
        return json.dumps(user_doc.to_dict())
    except google.cloud.exceptions.NotFound:
        return '{}'

def update_favs(card):
    
    user_id = card['user_id']
    card_id = card["card_id"]
    user_favorites = card["user_favorites"]

    #fav_doc_ref = positivesDB.document(get_document_id(card_id))
    #update_to_firestore(fbTransaction, fav_doc_ref, u'favoritedBy',favoritedBy)

    post_doc_ref = positivesDB.document(get_document_id(card_id))
    fav_collection = post_doc_ref.collection(u'favoritedBy')
    try:
        fav_doc_ref = fav_collection.document(user_id)
        fav_doc_ref.get()
        fav_doc_ref.delete()
    except google.cloud.exceptions.NotFound:
        fav_doc_ref.set({
            u'id': user_id
        })

    user_doc_ref = usersDB.document(user_id)
    try:
        user_doc_ref.get()
        update_to_firestore(fbTransaction, user_doc_ref, u'favorites',user_favorites)
    except google.cloud.exceptions.NotFound:
        card_data = {
            u'favorites': user_favorites
        }
        user_doc_ref.set(card_data)
    
    return 'success'
