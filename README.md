## WOP - Python Server for Sentiment Analysis and Database Handling

# DEPENDENCIES for setup
1. Python
2. pip

## Initial setup for Development

# Install all the dependencies using the following commands:
pip install Flask
pip install flask-cors --upgrade
pip install --upgrade google-cloud-firestore
pip install textblob
python -m textblob.download_corpora
pip install Pillow

# serve at localhost:5000
python main.py
