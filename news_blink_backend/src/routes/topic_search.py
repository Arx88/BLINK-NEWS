import asyncio
import json
import logging
import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from ..models.superior_note_generator import SuperiorNoteGenerator
from ..models.topic_searcher import TopicSearcher

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for topic search routes
topic_search_bp = Blueprint('topic_search', __name__)

# Directory to save search results and notes
RESULTS_DIR = os.path.join(os.getcwd(), "search_results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# In-memory storage for task statuses (replace with a more robust solution for production)
task_statuses = {}

async def perform_search_and_generate_notes(topic: str, task_id: str):
    """
    Asynchronously performs a topic search, generates notes, and saves them.
    Updates task status in `task_statuses`.
    """
    try:
        task_statuses[task_id] = {"status": "in_progress", "message": "Starting topic search..."}

        # Initialize models
        topic_searcher = TopicSearcher()
        note_generator = SuperiorNoteGenerator()

        # Perform search
        task_statuses[task_id]["message"] = f"Searching for topic: {topic}"
        search_results = await topic_searcher.search(topic)

        # Save search results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_results_filename = f"{topic.replace(' ', '_')}_{timestamp}_search_results.json"
        search_results_path = os.path.join(RESULTS_DIR, search_results_filename)
        with open(search_results_path, 'w') as f:
            json.dump(search_results, f, indent=4)
        logger.info(f"Search results saved to {search_results_path}")
        task_statuses[task_id]["search_results_file"] = search_results_path

        # Generate superior notes
        task_statuses[task_id]["message"] = "Generating superior notes..."
        notes = await note_generator.generate_superior_notes(search_results, topic)

        # Save notes
        notes_filename = f"{topic.replace(' ', '_')}_{timestamp}_notes.json"
        notes_path = os.path.join(RESULTS_DIR, notes_filename)
        with open(notes_path, 'w') as f:
            json.dump(notes, f, indent=4)
        logger.info(f"Notes saved to {notes_path}")
        task_statuses[task_id]["notes_file"] = notes_path

        task_statuses[task_id].update({"status": "completed", "message": "Search and note generation completed."})

    except Exception as e:
        logger.error(f"Error in task {task_id}: {e}")
        task_statuses[task_id].update({"status": "error", "message": str(e)})

@topic_search_bp.route('/start_topic_search', methods=['POST'])
def start_topic_search():
    """
    Starts an asynchronous topic search and note generation task.
    Returns a task ID to track the status.
    """
    data = request.json
    topic = data.get('topic')

    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    task_id = f"task_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    asyncio.create_task(perform_search_and_generate_notes(topic, task_id))

    return jsonify({"message": "Topic search started.", "task_id": task_id}), 202

@topic_search_bp.route('/topic_search_status/<task_id>', methods=['GET'])
def topic_search_status(task_id: str):
    """
    Returns the status of a topic search task.
    """
    status = task_statuses.get(task_id)
    if not status:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(status)

# Example of how to integrate this blueprint in your main Flask app:
# from flask import Flask
# app = Flask(__name__)
# app.register_blueprint(topic_search_bp, url_prefix='/search')

# if __name__ == '__main__':
#     # This is for demonstration if you run this file directly.
#     # In a real app, use a proper WSGI server like Gunicorn.
#     app.run(debug=True, port=5001)
