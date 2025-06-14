from flask import Blueprint, jsonify, request

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Health check route
@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return jsonify({"status": "ok"}), 200

# TODO: Add other API routes here
from ..services.news_service import NewsService
from ..config import Config
news_service = NewsService(api_key=Config.NEWS_API_KEY)
@api_bp.route('/news', methods=['GET'])
def get_news():
    """
    Route to get news articles.
    It uses NewsService to fetch news based on query parameters.
    """
    # Parameters for fetching news, can be passed as query arguments
    params = {
        'country': request.args.get('country', default='us'),
        'category': request.args.get('category', default='general')
    }
    try:
        articles = news_service.get_news(**params)
        return jsonify(articles)
    except Exception as e:
        # Log the exception for debugging
        # current_app.logger.error(f"Error fetching news: {e}")
        return jsonify({"error": "Failed to fetch news"}), 500
