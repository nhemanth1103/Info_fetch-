import os
import logging
from flask import Flask, jsonify, request, render_template
from shopify_scraper import ShopifyScraper

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

@app.route('/')
def index():
    """Render the main interface for testing the API"""
    return render_template('index.html')

@app.route('/fetch_insights', methods=['POST'])
def fetch_insights():
    """
    API endpoint to fetch insights from a Shopify store
    Accepts JSON with 'website_url' parameter
    Returns structured JSON with store insights
    """
    try:
        # Get website URL from request
        data = request.get_json()
        if not data or 'website_url' not in data:
            return jsonify({'error': 'website_url parameter is required'}), 400
        
        website_url = data['website_url'].strip()
        if not website_url:
            return jsonify({'error': 'website_url cannot be empty'}), 400
        
        # Initialize scraper and fetch insights
        scraper = ShopifyScraper()
        insights = scraper.scrape_store(website_url)
        
        return jsonify(insights), 200
        
    except Exception as e:
        app.logger.error(f"Error fetching insights: {str(e)}")
        return jsonify({'error': 'Internal server error occurred'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
