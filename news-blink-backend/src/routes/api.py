from flask import Blueprint, jsonify, request, current_app
# Assuming News model is in root/models/news.py
# Adjust the import path based on actual file location and python path execution context
# If api.py is in news-blink-backend/src/routes/ and models/ is at root:
from ....models.news import News
from ..services.news_service import NewsService # For existing /api/news
from ..config import Config # For existing /api/news

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)

# Initialize the News data manager for blinks
# This assumes the application's root directory contains the 'data' folder.
# If running Flask app from project root, 'data' should be accessible.
# Otherwise, an absolute path or a path configured via Flask app config might be better.
news_manager = News(data_dir='data')

# Health check route (existing)
@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return jsonify({"status": "ok"}), 200

# Existing route for external news (modified for clarity if needed, but largely untouched)
news_service_external = NewsService(api_key=Config.NEWS_API_KEY)
@api_bp.route('/news', methods=['GET'])
def get_external_news(): # Renamed function for clarity from get_news to avoid confusion
    """
    Route to get news articles from external News API.
    Uses NewsService to fetch news based on query parameters.
    """
    params = {
        'country': request.args.get('country', default='us'),
        'category': request.args.get('category', default='general')
    }
    try:
        articles = news_service_external.get_news(**params)
        return jsonify(articles)
    except Exception as e:
        # current_app.logger.error(f"Error fetching external news: {e}")
        print(f"Error fetching external news: {e}") # Using print for now if logger not set up
        return jsonify({"error": "Failed to fetch external news"}), 500

# --- New Blink Routes ---

@api_bp.route('/blinks', methods=['GET'])
def get_all_blinks_route():
    """
    Route to get all blinks, sorted according to predefined logic.
    Accepts an optional 'userId' query parameter.
    """
    user_id = request.args.get('userId', None)
    try:
        all_blinks = news_manager.get_all_blinks(user_id=user_id)
        return jsonify(all_blinks)
    except Exception as e:
        # current_app.logger.error(f"Error in /blinks route: {e}")
        print(f"Error in /blinks route: {e}")
        return jsonify({"error": "Failed to retrieve blinks"}), 500

@api_bp.route('/blinks/<string:article_id>', methods=['GET'])
def get_blink_route(article_id):
    """
    Route to get a specific blink by its ID.
    Accepts an optional 'userId' query parameter.
    """
    user_id = request.args.get('userId', None)
    try:
        blink = news_manager.get_blink(article_id)
        if not blink:
            return jsonify({"error": "Blink not found"}), 404

        # Add interest percentage and current user vote status
        blink['interestPercentage'] = news_manager.calculate_interest_percentage(blink) # C factor defaults to 5
        if user_id:
            blink['currentUserVoteStatus'] = news_manager._get_user_vote_status(blink, user_id)
        else:
            blink['currentUserVoteStatus'] = None

        return jsonify(blink)
    except Exception as e:
        # current_app.logger.error(f"Error in /blinks/<article_id> route: {e}")
        print(f"Error in /blinks/<article_id> route: {e}")
        return jsonify({"error": "Failed to retrieve blink"}), 500

@api_bp.route('/blinks/<string:article_id>/vote', methods=['POST'])
def vote_on_blink_route(article_id):
    """
    Route to vote on a specific blink.
    Expects JSON body: {"userId": "some_user_id", "voteType": "positive" | "negative"}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data in request"}), 400

    user_id = data.get('userId')
    vote_type = data.get('voteType') # Should be 'positive' or 'negative'

    if not user_id or not vote_type:
        return jsonify({"error": "Missing 'userId' or 'voteType' in request body"}), 400

    if vote_type not in ['positive', 'negative']:
        return jsonify({"error": "Invalid 'voteType'. Must be 'positive' or 'negative'."}), 400

    try:
        updated_blink = news_manager.process_vote(article_id, user_id, vote_type)
        if not updated_blink:
            # process_vote might return None if blink not found or save failed
            return jsonify({"error": "Failed to process vote or blink not found"}), 404

        # Add interest percentage and current user vote status to the response,
        # as process_vote returns the blink before these are added by get_all_blinks or get_blink routes
        updated_blink['interestPercentage'] = news_manager.calculate_interest_percentage(updated_blink)
        updated_blink['currentUserVoteStatus'] = news_manager._get_user_vote_status(updated_blink, user_id)

        return jsonify(updated_blink)
    except Exception as e:
        # current_app.logger.error(f"Error in /blinks/<article_id>/vote route: {e}")
        print(f"Error in /blinks/<article_id>/vote route: {e}")
        return jsonify({"error": "Failed to process vote"}), 500
