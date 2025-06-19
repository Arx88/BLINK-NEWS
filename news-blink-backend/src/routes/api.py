import json # Ensure json is imported
from flask import Blueprint, jsonify, request, current_app
from ....models.news import News
from ..services.news_service import NewsService
from ..config import Config
from ..logger_config import app_logger # Import the configured logger

# Create a Blueprint for API routes
api_bp = Blueprint('api', __name__)

# news_manager = News(data_dir='data') # Removed global instantiation

def get_news_manager():
    data_dir = 'data' # Default
    if current_app and 'APP_CONFIG' in current_app.config and 'NEWS_MODEL_DATA_DIR' in current_app.config['APP_CONFIG']:
        data_dir = current_app.config['APP_CONFIG']['NEWS_MODEL_DATA_DIR']
        # Use a distinct logger message for when config is actually used
        app_logger.info(f"get_news_manager: Using NEWS_MODEL_DATA_DIR from app_config: {data_dir}")
    else:
        # This will log if current_app is not available or config is not set
        app_logger.info(f"get_news_manager: Using default data_dir='{data_dir}'. current_app available: {bool(current_app)}")
        if current_app and 'APP_CONFIG' not in current_app.config:
            app_logger.info("get_news_manager: 'APP_CONFIG' not in current_app.config.")
        elif current_app and 'NEWS_MODEL_DATA_DIR' not in current_app.config.get('APP_CONFIG', {}):
            app_logger.info("get_news_manager: 'NEWS_MODEL_DATA_DIR' not in current_app.config['APP_CONFIG'].")

    return News(data_dir=data_dir)

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
        news_manager_instance = get_news_manager()
        all_blinks = news_manager_instance.get_all_blinks(user_id=user_id)

        blinks_for_json = []
        for blink_data in all_blinks:
            # Ensure all expected frontend fields are present
            new_blink = {
                'id': blink_data.get('id'),
                'title': blink_data.get('title'),
                'image': blink_data.get('image'),
                'points': blink_data.get('points', []),
                'category': blink_data.get('category'),
                'isHot': blink_data.get('isHot', False), # Default if missing
                'readTime': blink_data.get('readTime'),
                'publishedAt': blink_data.get('publishedAt'), # This will still be the 1970 date if source is missing
                'aiScore': blink_data.get('aiScore'), # Optional, so .get() is fine
                'votes': blink_data.get('votes', {'likes': 0, 'dislikes': 0}), # Default if missing
                'sources': blink_data.get('sources', []), # Default if missing
                'content': blink_data.get('content'), # Optional
                'currentUserVoteStatus': blink_data.get('currentUserVoteStatus'), # Should be None if not applicable
                'interestPercentage': float(blink_data.get('interestPercentage', 0.0)) # Explicitly cast and default
            }
            blinks_for_json.append(new_blink)

        app_logger.info(f"Successfully retrieved and reconstructed {len(blinks_for_json)} blinks for userId='{user_id}'.")

        if blinks_for_json:
            app_logger.debug(f"[API get_all_blinks_route] First item in blinks_for_json (pre-jsonify): {blinks_for_json[0]}")
        else:
            app_logger.debug("[API get_all_blinks_route] blinks_for_json is empty.")

        # ----- START INTENSIVE DEBUG LOGGING -----
        app_logger.debug(f"[API ROUTE DEBUG] blinks_for_json contains {len(blinks_for_json)} items. Logging details for first 3 (or fewer):")
        for i, temp_blink in enumerate(blinks_for_json[:3]): # Log first 3
            if isinstance(temp_blink, dict): # Ensure item is a dictionary
                interest_val = temp_blink.get('interestPercentage')
                app_logger.debug(
                    f"[API ROUTE DEBUG] Item {i}: ID {temp_blink.get('id')}, "
                    f"interestPercentage TYPE: {type(interest_val)}, VALUE: {interest_val}, "
                    f"PublishedAt TYPE: {type(temp_blink.get('publishedAt'))}, VALUE: {temp_blink.get('publishedAt')}"
                )
            else:
                app_logger.debug(f"[API ROUTE DEBUG] Item {i} is not a dict: {temp_blink}")

        # Attempt to manually serialize a sample to JSON
        if blinks_for_json: # Check if list is not empty
            try:
                # Create a sample that only includes 'id' and 'interestPercentage' for brevity and focus
                sample_for_json_dumps = []
                for temp_blink_sample in blinks_for_json[:3]: # Take first 3 again for sample
                    if isinstance(temp_blink_sample, dict):
                        sample_for_json_dumps.append({
                            'id': temp_blink_sample.get('id'),
                            'interestPercentage': temp_blink_sample.get('interestPercentage'),
                            'publishedAt': temp_blink_sample.get('publishedAt'),
                            'votes': temp_blink_sample.get('votes')
                        })
                    else: # if an item is not a dict, represent it as a string or placeholder
                        sample_for_json_dumps.append(str(temp_blink_sample))

                json_string_sample = json.dumps(sample_for_json_dumps)
                app_logger.debug(f"[API ROUTE DEBUG] Manually serialized sample (first 3 items, selected fields): {json_string_sample}")
            except Exception as e:
                app_logger.error(f"[API ROUTE DEBUG] Error manually serializing to JSON: {e}", exc_info=True)
        else:
            app_logger.debug("[API ROUTE DEBUG] blinks_for_json is empty, skipping manual JSON serialization sample.")
        # ----- END INTENSIVE DEBUG LOGGING -----

        return jsonify(blinks_for_json)
    except Exception as e:
        app_logger.error(f"Error in /blinks route for userId='{user_id}'. Error: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve blinks"}), 500

@api_bp.route('/blinks/<string:article_id>', methods=['GET'])
def get_blink_route(article_id):
    user_id = request.args.get('userId', None)
    app_logger.info(f"Get blink request: article_id='{article_id}', userId='{user_id}'")
    try:
        news_manager_instance = get_news_manager()
        # Call the updated News.get_blink method, passing user_id
        blink = news_manager_instance.get_blink(article_id, user_id=user_id)

        if not blink:
            app_logger.warning(f"Blink not found: article_id='{article_id}' (called by get_blink_route)")
            return jsonify({"error": "Blink not found"}), 404

        # 'interestPercentage' is no longer calculated here or added by News.get_blink.
        # 'currentUserVoteStatus' is now directly included by news_manager.get_blink.

        # If 'interestPercentage' is still desired on this specific endpoint, it can be calculated here.
        # For now, assuming it's not added as per overall plan to move calcs to frontend.
        # If it IS needed: blink['interestPercentage'] = news_manager.calculate_interest_percentage(blink)
        blink['interestPercentage'] = news_manager_instance.calculate_interest_percentage(blink)

        app_logger.info(f"Successfully retrieved blink via get_blink_route: article_id='{article_id}', UserVote='{blink.get('currentUserVoteStatus')}', Votes={blink.get('votes')}, Interest={blink.get('interestPercentage'):.2f}%.")
        return jsonify(blink)
    except Exception as e:
        app_logger.error(f"Error in /blinks/{article_id} route for userId='{user_id}'. Error: {e}", exc_info=True)
        return jsonify({"error": "Failed to retrieve blink"}), 500

@api_bp.route('/blinks/<string:article_id>/vote', methods=['POST'])
def vote_on_blink_route(article_id):
    app_logger.info(f"[VOTE_DEBUG] Entered vote_on_blink_route for article_id='{article_id}'. Raw request data: {request.data}")
    data = request.get_json()
    if not data:
        app_logger.warning(f"[VOTE_DEBUG] Missing JSON data for article_id='{article_id}'.")
        return jsonify({"error": "Invalid JSON"}), 400

    user_id = data.get('userId')
    vote_type = data.get('voteType') # Expected 'like' or 'dislike'
    previous_vote = data.get('previousVote') # Expected 'like', 'dislike', or None

    app_logger.info(f"[VOTE_DEBUG] Extracted from JSON for article_id='{article_id}': userId='{user_id}', voteType='{vote_type}', previousVote='{previous_vote}'.")

    if not user_id or not vote_type:
        app_logger.warning(f"[VOTE_DEBUG] Missing 'userId' or 'voteType' for article_id='{article_id}'. Body: {data}")
        return jsonify({"error": "Missing 'userId' or 'voteType' in request body"}), 400

    app_logger.info(f"[VOTE_DEBUG] About to validate voteType ('{vote_type}') for article_id='{article_id}'. Expected values: ['like', 'dislike'].")
    if vote_type not in ['like', 'dislike']:
        app_logger.warning(f"[VOTE_DEBUG] Validation FAILED for voteType ('{vote_type}') for article_id='{article_id}'. Expected ['like', 'dislike']. Sending 400 error.")
        return jsonify({"error": "Invalid voteType. Must be 'like' or 'dislike'"}), 400

    # Validate previousVote if provided
    if previous_vote is not None and previous_vote not in ['like', 'dislike']:
        app_logger.warning(f"[VOTE_DEBUG] Validation FAILED for previousVote ('{previous_vote}') for article_id='{article_id}'. Expected ['like', 'dislike', None]. Sending 400 error.")
        return jsonify({"error": "Invalid previousVote. Must be 'like', 'dislike', or null."}), 400

    app_logger.info(f"[VOTE_DEBUG] voteType ('{vote_type}') and previousVote ('{previous_vote}') for article_id='{article_id}' passed validation. Calling news_manager.process_user_vote.")

    try:
        news_manager_instance = get_news_manager()
        # Call the new method in models.news
        updated_blink_data = news_manager_instance.process_user_vote(article_id, user_id, vote_type, previous_vote)

        if not updated_blink_data:
            # Distinguish between blink not found and other processing errors if possible,
            # but process_user_vote currently returns None for multiple failure types.
            app_logger.warning(f"[VOTE_DEBUG] news_manager.process_user_vote returned None for article_id='{article_id}'. Blink might not exist or internal error during processing.")
            # Assuming a general failure case for now. If process_user_vote could differentiate file not found vs. save error, status codes could be more specific.
            return jsonify({"error": "Blink not found or failed to process vote"}), 404 # 404 implies blink itself not found, 500 for other errors.

        # news_manager.process_user_vote now adds/updates 'currentUserVoteStatus'
        # It also calculates and adds 'interestPercentage'
        # No need to recalculate interest here if process_user_vote handles it.
        # However, process_user_vote as defined in the prompt does NOT recalculate interest.
        # Let's add it here for consistency with previous API behavior.
        updated_blink_data['interestPercentage'] = news_manager_instance.calculate_interest_percentage(updated_blink_data)

        app_logger.info(f"[VOTE_DEBUG] Vote successful for article_id='{article_id}'. Votes: {updated_blink_data.get('votes')}, UserVote: {updated_blink_data.get('currentUserVoteStatus')}, New Interest: {updated_blink_data.get('interestPercentage'):.2f}%")
        return jsonify(updated_blink_data), 200

    except Exception as e:
        app_logger.error(f"[VOTE_DEBUG] Exception during vote processing for article_id='{article_id}': {e}", exc_info=True)
        return jsonify({"error": "Server error processing vote"}), 500
