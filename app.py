from flask import Flask, request, jsonify, session, redirect, url_for
import pandas as pd
import asyncio
import csv
import threading
import os
from search_scraper import scrape_youtube_search
from trending import scrape_trending
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'e3a1bba8b50e463fa53a1d0d3ffbd1b2'
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

import asyncio
import subprocess

# Ensure Playwright browsers are installed at runtime
async def install_browsers():
    subprocess.run(["playwright", "install", "chromium"])

asyncio.run(install_browsers())

# --- CORS Configuration ---
# Allow requests from your frontend's origin.
# For development, you can be permissive, but be more specific in production.
CORS(app, supports_credentials=True, origins=[
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "null",
    "https://cosmic-belekoy-dd73ee.netlify.app",
    "https://youtube-dashboard.netlify.app",
    "https://glittering-torrone-6c12c8.netlify.app"
])

def load_trending_data():
    data = []
    try:
        with open('./data/trending_IN.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print("Error: trending_IN.csv not found. Make sure it's in the 'data' directory.")
    return data

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower()
    data = load_trending_data()
    if not data:
         return jsonify({"error": "Trending data not available or file not found", "results": [], "not_found": True, "query": query}), 500
    matches = [video for video in data if query in video['title'].lower()]
    if matches:
        return jsonify({"results": matches, "not_found": False})
    else:
        return jsonify({"results": [], "not_found": True, "query": query})

@app.route('/scrape_youtube', methods=['GET'])
def scrape_youtube():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Query is required"}), 400
    try:
        scraped_results = scrape_youtube_search(query)
        return jsonify({"results": scraped_results})
    except Exception as e:
        return jsonify({"error": f"Scraping failed: {str(e)}"}), 500

@app.route('/refresh', methods=['POST'])
def refresh_trending():
    def run_scraper():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(scrape_trending("IN", 100))
        finally:
            loop.close()

    threading.Thread(target=run_scraper).start()
    return jsonify({'message': 'Trending data refresh initiated!'})

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        if username == 'admin' and password == 'admin123':
            session['user'] = username
            return jsonify({"message": "Login successful", "user": username}), 200
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    user = session.pop('user', None)
    if user:
        return jsonify({"message": "Logout successful"}), 200
    return jsonify({"message": "No active session to log out from"}), 200

@app.route('/api/check-session', methods=['GET'])
def check_session():
    if 'user' in session:
        return jsonify({"isLoggedIn": True, "user": session['user']}), 200
    return jsonify({"isLoggedIn": False}), 200

@app.route('/api/videos', methods=['GET'])
def get_videos():
    try:
        df = pd.read_csv('./data/trending_IN.csv')
    except FileNotFoundError:
        return jsonify({"error": "Trending data file not found."}), 500

    df = df.rename(columns={
        'title': 'title',
        'channelTitle': 'channel',
        'viewCount': 'views',
        'publishedAt': 'published',
        'videoUrl': 'url',
        'videoId': 'videoId'
    })
    videos = df[['title', 'channel', 'views', 'published', 'url']].to_dict(orient='records')
    return jsonify(videos)

@app.route('/api/graph-data', methods=['GET'])
def graph_data():
    try:
        df = pd.read_csv('./data/trending_IN.csv')
    except FileNotFoundError:
        return jsonify({"error": "Trending data file not found."}), 500

    def parse_views(view_str):
        try:
            if pd.isna(view_str): return 0
            view_str = str(view_str).replace(' views', '').strip()
            if 'K' in view_str:
                return int(float(view_str.replace('K', '')) * 1_000)
            elif 'M' in view_str:
                return int(float(view_str.replace('M', '')) * 1_000_000)
            elif 'B' in view_str:
                return int(float(view_str.replace('B', '')) * 1_000_000_000)
            else:
                return int(str(view_str).replace(',', ''))
        except:
            return 0

    df['viewCount'] = df['viewCount'].apply(parse_views)
    top20 = df.sort_values(by='viewCount', ascending=False).head(20)
    labels = top20['title'].tolist()
    data = top20['viewCount'].tolist()
    return jsonify({'labels': labels, 'data': data})

# Add a root route for health check
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "YouTube Dashboard API is running"}), 200

if __name__ == '__main__':
    # Use environment variables for production or default for development
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
