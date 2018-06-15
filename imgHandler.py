# storage
import json
import os
import google.cloud
import datetime
import requests
from google.cloud import storage
from PIL import Image
#from urllib.parse import unquote

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./service.json"

storageDB = storage.Client()
bucket = storageDB.get_bucket('wop-dev.appspot.com')

def _check_extension(filename):
    if ('.' not in filename):
        raise BadRequest("{0} has an invalid name or extension".format(filename))
        
def _safe_filename(url):
    filename = url[url.rfind("/")+1:]
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
    basename, extension = filename.rsplit('.', 1)
    return "{0}-{1}.{2}".format(basename, date, extension)

def upload_url(url, filename):
    #bucket.upload_from_file(image)
    print(url)
    _check_extension(url)
    filename = _safe_filename(url)
    
    image_data = requests.get(url).content
    #img = Image.open(BytesIO(response.content))
    blob = bucket.blob(filename)
    blob.upload_from_string(
        image_data,
        content_type='image/jpg'
    )
    blob.make_public()
    return blob.public_url

def upload_thumb(image, filename):
    #filename = _safe_filename(filename)
    image_data = Image.open(image)
    image_data.thumbnail([400, 400], Image.ANTIALIAS)
    blob = bucket.blob(filename)
    blob.upload_from_file(
        image_data,
        content_type='image/jpg'
    )
    blob.make_public()
    return blob.public_url

def upload_image(image_data, filename):
    #filename = _safe_filename(filename)
    blob = bucket.blob(filename)
    blob.upload_from_file(
        image_data,
        content_type='image/jpg'
    )
    blob.make_public()
    return blob.public_url

def upload_to_storage(image_data, image_type, image_name):
    #bucket.upload_from_file(image)
    if image_type == "url":
        return upload_url(image_data, image_name)
    else:
        #upload_thumb(image_data, image_name)
        return upload_image(image_data, image_name)
    
