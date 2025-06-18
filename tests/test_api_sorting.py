import unittest
import os
import json
import shutil
from datetime import datetime, timezone # Keep for TestApiVoting
from flask import Flask
from routes.api import init_api # For TestApiVoting
# from models.news import News # No longer needed directly by these specific API tests if API encapsulates all logic

# News class is implicitly tested via the API calls to news_manager instance in api.py

class TestApiVoting(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.test_data_dir_voting = "temp_test_blinks_data_voting"
        # Correctly set actual_data_dir_blinks to be inside test_data_dir_voting
        self.blinks_dir = os.path.join(self.test_data_dir_voting, 'blinks')
        self.articles_dir = os.path.join(self.test_data_dir_voting, 'articles')

        os.makedirs(self.blinks_dir, exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)

        # This configuration tells the News instance (created within api.py's scope)
        # to use this temporary directory.
        self.app.config['APP_CONFIG'] = {'NEWS_MODEL_DATA_DIR': self.test_data_dir_voting}

        init_api(self.app)

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.test_user_id = "test_user_123" # Define a consistent user ID

    def tearDown(self):
        self.app_context.pop()
        shutil.rmtree(self.test_data_dir_voting)

    def _create_test_blink_file(self, blink_id="test_vote_blink", likes=0, dislikes=0, user_votes=None, published_at_str=None):
        if published_at_str is None:
            published_at_str = datetime.now(timezone.utc).isoformat()
        if user_votes is None:
            user_votes = {}

        blink_content = {
            "id": blink_id,
            "title": f"Test Blink {blink_id}",
            "publishedAt": published_at_str,
            "votes": {"likes": likes, "dislikes": dislikes},
            "user_votes": user_votes,
            # Adding other fields that News.get_blink might expect or initialize
            "content": "Test content for blink.",
            "points": ["Point 1.", "Point 2."],
            "image": "test_image.png",
            "sources": [{"id": "src-1", "name": "Test Source"}],
            "urls": [{"type": "main", "url": f"http://example.com/{blink_id}"}],
            "category": "test-category"
        }
        # Use self.blinks_dir which is correctly set in setUp
        blink_path = os.path.join(self.blinks_dir, f"{blink_id}.json")
        with open(blink_path, 'w') as f:
            json.dump(blink_content, f, indent=2)
        return blink_path

    def _read_blink_file_data(self, blink_id="test_vote_blink"):
        # Use self.blinks_dir
        blink_path = os.path.join(self.blinks_dir, f"{blink_id}.json")
        if not os.path.exists(blink_path):
            return None
        with open(blink_path, 'r') as f:
            data = json.load(f)
        return data

    def test_vote_first_like(self):
        blink_id = "first_like_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=0, user_votes={})

        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': None})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['votes']['likes'], 1)
        self.assertEqual(data['votes']['dislikes'], 0)
        self.assertEqual(data['currentUserVoteStatus'], 'like')

        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 1)
        self.assertEqual(file_data['votes']['dislikes'], 0)
        self.assertEqual(file_data['user_votes'][self.test_user_id], 'like')

    def test_vote_first_dislike(self):
        blink_id = "first_dislike_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=0, user_votes={})

        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'dislike', 'previousVote': None})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['votes']['likes'], 0)
        self.assertEqual(data['votes']['dislikes'], 1)
        self.assertEqual(data['currentUserVoteStatus'], 'dislike')

        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 0)
        self.assertEqual(file_data['votes']['dislikes'], 1)
        self.assertEqual(file_data['user_votes'][self.test_user_id], 'dislike')

    def test_vote_change_like_to_dislike(self):
        blink_id = "change_like_to_dislike_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=1, dislikes=0, user_votes={self.test_user_id: "like"})

        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'dislike', 'previousVote': 'like'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['votes']['likes'], 0)
        self.assertEqual(data['votes']['dislikes'], 1)
        self.assertEqual(data['currentUserVoteStatus'], 'dislike')

        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 0)
        self.assertEqual(file_data['votes']['dislikes'], 1)
        self.assertEqual(file_data['user_votes'][self.test_user_id], 'dislike')

    def test_vote_change_dislike_to_like(self):
        blink_id = "change_dislike_to_like_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=1, user_votes={self.test_user_id: "dislike"})

        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': 'dislike'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['votes']['likes'], 1)
        self.assertEqual(data['votes']['dislikes'], 0)
        self.assertEqual(data['currentUserVoteStatus'], 'like')

        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 1)
        self.assertEqual(file_data['votes']['dislikes'], 0)
        self.assertEqual(file_data['user_votes'][self.test_user_id], 'like')

    def test_vote_repeated_like(self):
        blink_id = "repeated_like_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=1, dislikes=0, user_votes={self.test_user_id: "like"})

        # User clicks 'like' again, having already liked it.
        # previousVote is 'like', new voteType is 'like'.
        # Based on models.News.process_user_vote, this should result in no change.
        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': 'like'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['votes']['likes'], 1)
        self.assertEqual(data['votes']['dislikes'], 0)
        self.assertEqual(data['currentUserVoteStatus'], 'like') # Still 'like'

        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 1)
        self.assertEqual(file_data['votes']['dislikes'], 0)
        self.assertEqual(file_data['user_votes'][self.test_user_id], 'like')

    def test_vote_repeated_dislike(self):
        blink_id = "repeated_dislike_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=1, user_votes={self.test_user_id: "dislike"})

        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'dislike', 'previousVote': 'dislike'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()

        self.assertEqual(data['votes']['likes'], 0)
        self.assertEqual(data['votes']['dislikes'], 1)
        self.assertEqual(data['currentUserVoteStatus'], 'dislike')

        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 0)
        self.assertEqual(file_data['votes']['dislikes'], 1)
        self.assertEqual(file_data['user_votes'][self.test_user_id], 'dislike')

    def test_vote_on_nonexistent_blink(self):
        blink_id = "nonexistent_blink"
        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': None})
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertEqual(data['error'], "Blink not found or failed to process vote") # Changed to assertEqual

    def test_vote_with_invalid_vote_type(self):
        blink_id = "invalid_vote_type_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'invalid', 'previousVote': None})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Invalid voteType. Must be 'like' or 'dislike'") # Ensured exact match

    def test_vote_with_invalid_previous_vote_type(self):
        blink_id = "invalid_prev_vote_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': 'invalid'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Invalid previousVote. Must be 'like', 'dislike', or null.") # Ensured exact match

    def test_vote_missing_vote_type(self):
        blink_id = "missing_vote_type_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'userId': self.test_user_id, 'previousVote': None}) # voteType omitted
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Missing 'userId' or 'voteType' in request body") # This assertion is correct based on api.py

    def test_vote_missing_user_id(self):
        blink_id = "missing_user_id_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote',
                                    json={'voteType': 'like', 'previousVote': None}) # userId omitted
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], "Missing 'userId' or 'voteType' in request body")

if __name__ == '__main__':
    unittest.main()
