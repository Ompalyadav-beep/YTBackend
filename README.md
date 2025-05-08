# YouTube Dashboard Backend

This is the backend API for the YouTube Dashboard application. It provides endpoints for fetching trending YouTube videos, searching for videos, and more.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```
   playwright install chromium
   ```

3. Run the application:
   ```
   python app.py
   ```

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following settings:
   - Name: youtube-dashboard-backend (or your preferred name)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt && playwright install chromium`
   - Start Command: `gunicorn app:app`
   - Environment Variables:
     - PORT: 8000 (or your preferred port)

4. Click "Create Web Service"

## API Endpoints

- `GET /`: Health check endpoint
- `GET /api/videos`: Get trending videos
- `GET /api/graph-data`: Get data for graph visualization
- `GET /search?query=<query>`: Search for videos in trending data
- `GET /scrape_youtube?query=<query>`: Search for videos on YouTube
- `POST /refresh`: Refresh trending data

## CORS Configuration

The API is configured to allow requests from the following origins:
- http://127.0.0.1:5500 (local development)
- http://localhost:5500 (local development)
- https://cosmic-belekoy-dd73ee.netlify.app (Netlify deployment)
- https://youtube-dashboard.netlify.app (Netlify deployment)

If you deploy the frontend to a different domain, make sure to update the CORS configuration in `app.py`.
# YTBackend
