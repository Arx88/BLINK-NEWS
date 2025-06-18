from flask import Blueprint, jsonify, request, current_app
from ....models.news import News
from ..services.news_service import NewsService
from ..config import Config
from ..logger_config import app_logger # Import the configured logger

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)

news_manager = News(data_dir='data')
news_service_external = NewsService(api_key=Config.NEWS_API_KEY)

@api_bp.route('/health', methods=['GET'])
def health_check():
    app_logger.info("Health check endpoint called.")
    return jsonify({"status": "ok"}), 200

@api_bp.route('/news', methods=['GET'])
def get_external_news():
    country = request.args.get('country', default='us')
    category = request.args.get('category', default='general')
    app_logger.info(f"External news request: country={country}, category={category}")
    params = {'country': country, 'category': category}
    try:
        articles = news_service_external.get_news(**params)
        app_logger.info(f"External news request successful, found {len(articles) if isinstance(articles, list) else 'N/A'} articles.")
        return jsonify(articles)
    except Exception as e:
        app_logger.error(f"Error fetching external news: country={country}, category={category}. Error: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch external news"}), 500

@api_bp.route('/blinks', methods=['GET'])
def get_all_blinks_route():
    user_id = request.args.get('userId', None)
    app_logger.info(f"Get all blinks request: userId='{user_id}'")
    try:
        all_blinks = news_manager.get_all_blinks(user_id=user_id)
        app_logger.info(f"Successfully retrieved {len(all_blinks)} blinks for userId='{user_id}'.")
        return jsonify(all_blinks)
    except Exception as e:
        app_logger.error(f"Error in /blinks route for userId='{user_id}'. Error: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve blinks"}), 500

@api_bp.route('/blinks/<string:article_id>', methods=['GET'])
def get_blink_route(article_id):
    user_id = request.args.get('userId', None)
    app_logger.info(f"Get blink request: article_id='{article_id}', userId='{user_id}'")
    try:
        blink = news_manager.get_blink(article_id)
        if not blink:
            app_logger.warning(f"Blink not found: article_id='{article_id}'")
            return jsonify({"error": "Blink not found"}), 404

        app_logger.debug(f"Blink found: article_id='{article_id}'. Calculating interest and user status.")
        blink['interestPercentage'] = news_manager.calculate_interest_percentage(blink)
        if user_id:
            blink['currentUserVoteStatus'] = news_manager._get_user_vote_status(blink, user_id)
        else:
            blink['currentUserVoteStatus'] = None

        app_logger.info(f"Successfully retrieved blink: article_id='{article_id}', interest={blink['interestPercentage']:.2f}%, userVote='{blink['currentUserVoteStatus']}'.")
        return jsonify(blink)
    except Exception as e:
        app_logger.error(f"Error in /blinks/{article_id} route for userId='{user_id}'. Error: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve blink"}), 500

@api_bp.route('/blinks/<string:article_id>/vote', methods=['POST'])
def vote_on_blink_route(article_id):
    app_logger.info(f"Vote request for article_id='{article_id}'. Raw request data: {request.data}")
    data = request.get_json()
    if not data:
        app_logger.warning(f"Missing JSON data in vote request for article_id='{article_id}'.")
        return jsonify({"error": "Missing JSON data in request"}), 400

    user_id = data.get('userId')
    vote_type = data.get('voteType')
    app_logger.info(f"Processing vote for article_id='{article_id}', userId='{user_id}', voteType='{vote_type}'.")

    if not user_id or not vote_type:
        app_logger.warning(f"Missing 'userId' or 'voteType' in vote request body for article_id='{article_id}'. Body: {data}")
        return jsonify({"error": "Missing 'userId' or 'voteType' in request body"}), 400

    if vote_type not in ['positive', 'negative']:
        app_logger.warning(f"Invalid 'voteType' ('{vote_type}') in vote request for article_id='{article_id}'. Body: {data}")
        return jsonify({"error": "Invalid 'voteType'. Must be 'positive' or 'negative'."}), 400

    try:
        updated_blink = news_manager.process_vote(article_id, user_id, vote_type)
        if not updated_blink:
            app_logger.warning(f"process_vote returned None for article_id='{article_id}', userId='{user_id}', voteType='{vote_type}'. Blink might not exist or save failed.")
            return jsonify({"error": "Failed to process vote or blink not found"}), 404

        app_logger.debug(f"Vote processed for article_id='{article_id}'. Calculating interest and user status for response.")
        updated_blink['interestPercentage'] = news_manager.calculate_interest_percentage(updated_blink)
        updated_blink['currentUserVoteStatus'] = news_manager._get_user_vote_status(updated_blink, user_id)

        app_logger.info(f"Vote successful for article_id='{article_id}', userId='{user_id}', voteType='{vote_type}'. New interest: {updated_blink['interestPercentage']:.2f}%.")
        return jsonify(updated_blink)
    except Exception as e:
        app_logger.error(f"Error in /blinks/{article_id}/vote route for userId='{user_id}', voteType='{vote_type}'. Error: {e}", exc_info=True)
        return jsonify({"error": "Failed to process vote"}), 500
