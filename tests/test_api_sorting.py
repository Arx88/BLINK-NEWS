import unittest
from flask import Flask
# Import the refactored sort key function from routes.api
from routes.api import _sort_blinks_key as sort_key_under_test

# The local sort_key_for_testing function is removed.
# Tests will now use the imported sort_key_under_test.

class TestApiSorting(unittest.TestCase):

    def setUp(self):
        """Set up a Flask application context before each test."""
        self.app = Flask(__name__)
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Remove the Flask application context after each test."""
        self.app_context.pop()

    def test_blink_with_zero_likes_and_zero_dislikes(self):
        """
        Test Case 1: Blink with 0 likes and 0 dislikes.
        Expected output from sort_key: (0.0, 0, -timestamp).
        -dislikes for 0 dislikes is 0.
        Timestamp is negated for 0% interest blinks.
        """
        blink = {'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': 100}
        expected_key_output = (0.0, 0, -100) # Timestamp is negated
        self.assertEqual(sort_key_under_test(blink), expected_key_output)

    def test_blinks_zero_interest_sorted_by_dislikes_ascending(self):
        """
        Test Case 2: Blinks with 0% interest sorted by dislikes (ascending).
        """
        blink_A = {'id': 'A', 'votes': {'likes': 0, 'dislikes': 10}, 'timestamp': 100} # Interest 0%
        blink_B = {'id': 'B', 'votes': {'likes': 0, 'dislikes': 5}, 'timestamp': 200}  # Interest 0%
        blink_C = {'id': 'C', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': 300}  # Interest 0%, 0 votes

        # sort_key_under_test(blink_A) -> (0.0, -10, 100)
        # sort_key_under_test(blink_B) -> (0.0, -5, 200)
        # sort_key_under_test(blink_A) -> (0.0, -10, -100) # Timestamps are negated
        # sort_key_under_test(blink_B) -> (0.0, -5, -200)  # Timestamps are negated
        # sort_key_under_test(blink_C) -> (0.0, 0, -300)   # Timestamps are negated

        blinks = [blink_A, blink_B, blink_C]
        blinks.sort(key=sort_key_under_test, reverse=True)

        # Expected order: C, B, A (dislikes ascending, then timestamp ascending)
        # C: (0.0, 0, -300)
        # B: (0.0, -5, -200)  -> 0 > -5, so C before B
        # A: (0.0, -10, -100) -> -5 > -10, so B before A
        # Within same dislikes, -timestamp means older items (smaller original ts) come first.
        # Example: if C1 had ts 300 and C2 had ts 350, both 0 dislikes.
        # C1 key: (0.0, 0, -300), C2 key: (0.0, 0, -350)
        # Sorted reverse: C1 (-300) comes before C2 (-350) because -300 > -350. This means 300 before 350 (ascending).
        expected_order_ids = ['C', 'B', 'A']
        self.assertEqual([b['id'] for b in blinks], expected_order_ids)

    def test_blinks_zero_interest_same_dislikes_sorted_by_timestamp_ascending(self):
        """
        Test Case 3: Blinks with 0% interest and same dislikes, sorted by timestamp (ascending).
        Timestamp is ascending because the key returns -timestamp and sort is reverse=True.
        """
        blink_D = {'id': 'D', 'votes': {'likes': 0, 'dislikes': 5}, 'timestamp': 100} # Interest 0%
        blink_E = {'id': 'E', 'votes': {'likes': 0, 'dislikes': 5}, 'timestamp': 300} # Interest 0%
        blink_F = {'id': 'F', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': 200} # Interest 0%, 0 votes
        blink_G = {'id': 'G', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': 400} # Interest 0%, 0 votes

        # sort_key_under_test(blink_D) -> (0.0, -5, -100)
        # sort_key_under_test(blink_E) -> (0.0, -5, -300)
        # sort_key_under_test(blink_F) -> (0.0, 0, -200)
        # sort_key_under_test(blink_G) -> (0.0, 0, -400)

        blinks = [blink_D, blink_E, blink_F, blink_G] # Original order for test stability
        blinks.sort(key=sort_key_under_test, reverse=True)

        # Expected order: F, G, D, E
        # Grouped by dislikes (ascending due to -dislikes and reverse=True): (0,0) then (5,5)
        # F (0.0, 0, -200)
        # G (0.0, 0, -400)
        #   Within 0 dislikes: F then G because -200 > -400 (meaning timestamp 200 before 400 - ascending)
        # D (0.0, -5, -100)
        # E (0.0, -5, -300)
        #   Within 5 dislikes: D then E because -100 > -300 (meaning timestamp 100 before 300 - ascending)
        # Overall: F, G (0 dislikes group), then D, E (-5 dislikes group, which comes after 0 due to -5 vs 0)
        expected_order_ids = ['F', 'G', 'D', 'E']
        self.assertEqual([b['id'] for b in blinks], expected_order_ids)

    def test_blinks_with_different_interest_scores(self):
        """
        Test Case 4: Blinks with different interest scores are sorted correctly.
        """
        blink_H = {'id': 'H', 'votes': {'likes': 10, 'dislikes': 10}, 'timestamp': 100} # Interest 0.5
        blink_I = {'id': 'I', 'votes': {'likes': 20, 'dislikes': 0}, 'timestamp': 200}  # Interest 1.0
        blink_J = {'id': 'J', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': 300}   # Interest 0.0

        # sort_key_under_test(blink_H) -> (0.5, 10, 100)
        # sort_key_under_test(blink_I) -> (1.0, 20, 200)
        # sort_key_under_test(blink_J) -> (0.0, 0, -300) # Timestamp is negated

        blinks = [blink_H, blink_I, blink_J]
        blinks.sort(key=sort_key_under_test, reverse=True)

        # Expected order: I, H, J
        # I (1.0, 20, 200)
        # H (0.5, 10, 100)
        # J (0.0, 0, 300)
        expected_order_ids = ['I', 'H', 'J']
        self.assertEqual([b['id'] for b in blinks], expected_order_ids)

    def test_blinks_same_nonzero_interest_sorted_by_likes_then_timestamp(self):
        """
        Test Case 5: Blinks with same non-zero interest score, sorted by likes (desc), then timestamp (desc).
        """
        blink_K = {'id': 'K', 'votes': {'likes': 10, 'dislikes': 10}, 'timestamp': 100} # Interest 0.5, 10 likes
        blink_L = {'id': 'L', 'votes': {'likes': 5, 'dislikes': 5}, 'timestamp': 300}   # Interest 0.5, 5 likes
        blink_M = {'id': 'M', 'votes': {'likes': 10, 'dislikes': 10}, 'timestamp': 200} # Interest 0.5, 10 likes

        # sort_key_under_test(blink_K) -> (0.5, 10, 100)
        # sort_key_under_test(blink_L) -> (0.5, 5, 300)
        # sort_key_under_test(blink_M) -> (0.5, 10, 200)

        blinks = [blink_K, blink_L, blink_M]
        blinks.sort(key=sort_key_under_test, reverse=True)

        # Expected order: M, K, L
        # M (0.5, 10, 200)
        # K (0.5, 10, 100) -> M vs K: M by timestamp (200 > 100)
        # L (0.5, 5, 300)  -> K vs L: K by likes (10 > 5)
        expected_order_ids = ['M', 'K', 'L']
        self.assertEqual([b['id'] for b in blinks], expected_order_ids)

    def test_string_numerical_timestamps_conversion(self):
        """
        Test Case 6: Blinks with string-formatted numerical timestamps are correctly converted and sorted.
        Especially for 0% interest where timestamp is negated.
        """
        blink_S1 = {'id': 'S1', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': "100"} # 0% interest
        blink_S2 = {'id': 'S2', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': "50"}  # 0% interest
        blink_S3 = {'id': 'S3', 'votes': {'likes': 1, 'dislikes': 1}, 'timestamp': "200"} # 0.5% interest

        # Expected keys after float conversion and negation for 0% interest:
        # sort_key_under_test(blink_S1) -> (0.0, 0, -100.0)
        # sort_key_under_test(blink_S2) -> (0.0, 0, -50.0)
        # sort_key_under_test(blink_S3) -> (0.5, 1, 200.0)

        blinks = [blink_S1, blink_S2, blink_S3]
        blinks.sort(key=sort_key_under_test, reverse=True)

        # Expected order: S3 (by interest), then S2 (older), then S1 (newer)
        # S3: (0.5, 1, 200.0)
        # S2: (0.0, 0, -50.0)  (older, -50.0 > -100.0)
        # S1: (0.0, 0, -100.0)
        expected_order_ids = ['S3', 'S2', 'S1']
        self.assertEqual([b['id'] for b in blinks], expected_order_ids)

        # Also check key output directly for one case
        self.assertEqual(sort_key_under_test(blink_S1), (0.0, 0, -100.0))
        self.assertEqual(sort_key_under_test(blink_S2), (0.0, 0, -50.0))
        self.assertEqual(sort_key_under_test(blink_S3), (0.5, 1, 200.0))

    def test_invalid_or_missing_timestamps_default_to_zero(self):
        """
        Test Case 7: Blinks with non-numeric string or missing timestamps default to 0.0
        and are sorted predictably.
        """
        blink_INV1 = {'id': 'INV1', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': "invalid_date"} # 0% interest
        blink_INV2 = {'id': 'INV2', 'votes': {'likes': 0, 'dislikes': 0}} # Missing timestamp, 0% interest
        blink_INV3 = {'id': 'INV3', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': "10"} # Valid string ts
        blink_INV4 = {'id': 'INV4', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': -10} # Valid negative ts

        # Expected keys after float conversion and potential defaulting:
        # sort_key_under_test(blink_INV1) -> (0.0, 0, -0.0) -> (0.0, 0, 0.0)
        # sort_key_under_test(blink_INV2) -> (0.0, 0, -0.0) -> (0.0, 0, 0.0) (default for missing is 0, then float(0))
        # sort_key_under_test(blink_INV3) -> (0.0, 0, -10.0)
        # sort_key_under_test(blink_INV4) -> (0.0, 0, 10.0) (since -(-10) = 10)

        # Check key output directly
        self.assertEqual(sort_key_under_test(blink_INV1), (0.0, 0, -0.0)) # or (0.0, 0, 0.0)
        self.assertEqual(sort_key_under_test(blink_INV2), (0.0, 0, -0.0)) # or (0.0, 0, 0.0)
        self.assertEqual(sort_key_under_test(blink_INV3), (0.0, 0, -10.0))
        self.assertEqual(sort_key_under_test(blink_INV4), (0.0, 0, 10.0))


        blinks = [blink_INV1, blink_INV2, blink_INV3, blink_INV4]
        blinks.sort(key=sort_key_under_test, reverse=True)

        # Expected order: INV4, then INV1/INV2 (tie, order among them can be unstable), then INV3
        # INV4: (0.0, 0, 10.0)  (most positive -timestamp)
        # INV1: (0.0, 0, -0.0)
        # INV2: (0.0, 0, -0.0)
        # INV3: (0.0, 0, -10.0) (most negative -timestamp)

        # We can only reliably check parts of the order due to INV1/INV2 tie
        self.assertEqual(blinks[0]['id'], 'INV4')
        self.assertEqual(blinks[3]['id'], 'INV3')
        # Check that INV1 and INV2 are in the middle
        self.assertIn(blinks[1]['id'], ['INV1', 'INV2'])
        self.assertIn(blinks[2]['id'], ['INV1', 'INV2'])
        self.assertNotEqual(blinks[1]['id'], blinks[2]['id'])

    def test_non_integer_string_votes_default_to_zero(self):
        """
        Test Case 8: Blinks with non-integer string votes default to 0 for sorting.
        This simulates data quality issues for vote counts.
        """
        # Blink NV1: True 1 dislike, should be last among these 0%
        blink_NV1 = {'id': 'NV1', 'votes': {'likes': 0, 'dislikes': 1}, 'timestamp': 100}
        # Blink NV2: Dislikes is an empty string, should default to 0 dislikes
        blink_NV2 = {'id': 'NV2', 'votes': {'likes': 0, 'dislikes': ""}, 'timestamp': 200}
        # Blink NV3: Likes is "abc", should default to 0 likes. Dislikes is 0.
        blink_NV3 = {'id': 'NV3', 'votes': {'likes': "abc", 'dislikes': 0}, 'timestamp': 50}
        # Blink NV4: True 0 dislikes, for comparison
        blink_NV4 = {'id': 'NV4', 'votes': {'likes': 0, 'dislikes': 0}, 'timestamp': 150}

        # Expected keys:
        # NV1: (0.0, -1, -100.0)  (True 1 dislike)
        # NV2: (0.0, 0, -200.0)   (Dislikes "" -> 0)
        # NV3: (0.0, 0, -50.0)    (Likes "abc" -> 0, Dislikes 0)
        # NV4: (0.0, 0, -150.0)   (True 0 dislikes)

        # Check individual key generation to confirm defaulting
        self.assertEqual(sort_key_under_test(blink_NV1), (0.0, -1, -100.0))
        # For NV2, raw_dislikes is "", int("") fails, dislikes becomes 0.
        self.assertEqual(sort_key_under_test(blink_NV2), (0.0, 0, -200.0))
        # For NV3, raw_likes is "abc", int("abc") fails, likes becomes 0.
        # Interest is 0 / (0 + 0) which is 0. Dislikes is 0.
        self.assertEqual(sort_key_under_test(blink_NV3), (0.0, 0, -50.0))
        self.assertEqual(sort_key_under_test(blink_NV4), (0.0, 0, -150.0))

        blinks = [blink_NV1, blink_NV2, blink_NV3, blink_NV4]
        # Sort order:
        # 1. Blinks with 0 effective dislikes (NV3, NV4, NV2), sorted by timestamp ascending (-ts descending)
        #    NV3 (-50.0)
        #    NV4 (-150.0)
        #    NV2 (-200.0)
        # 2. Blink with 1 dislike (NV1)
        #    NV1 (-100.0 for ts, but -1 for dislikes makes it last)
        blinks.sort(key=sort_key_under_test, reverse=True)

        expected_order_ids = ['NV3', 'NV4', 'NV2', 'NV1']
        self.assertEqual([b['id'] for b in blinks], expected_order_ids)

if __name__ == '__main__':
    unittest.main()

import json
import os
import shutil
from routes.api import init_api # To initialize our api_bp
# from models.news import News # To interact with news_model paths if needed (not used in final approach)

class TestApiVoting(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        # Using actual data dir for blinks, careful with test blink IDs and cleanup.
        # The 'actual_data_dir_blinks' will be the 'data/blinks' directory in the project root.
        # Path is constructed relative to this test file's location (tests/test_api_sorting.py)
        # So, os.path.dirname(__file__) is /app/tests
        # os.path.dirname(os.path.dirname(__file__)) is /app
        self.actual_data_dir_blinks = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'blinks')

        # Ensure the actual blinks directory exists (it should, but good practice)
        os.makedirs(self.actual_data_dir_blinks, exist_ok=True)

        # Configure the app
        self.app.config['APP_CONFIG'] = {} # Minimal config for init_api
        # Potentially, if news_model uses app.config['DATA_DIR'] or similar:
        # self.app.config['DATA_DIR'] = self.test_data_dir

        init_api(self.app) # Registers /api blueprint, including /blinks/.../vote

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        # Clean up any created test files in the actual data dir
        test_blink_path = os.path.join(self.actual_data_dir_blinks, 'test_vote_blink.json')
        if os.path.exists(test_blink_path):
            os.remove(test_blink_path)

        # Cleanup for the article file potentially created by vote_on_blink
        # The path for articles would be parallel to blinks dir: data/articles/
        article_path = os.path.join(os.path.dirname(self.actual_data_dir_blinks), 'articles', 'test_vote_blink.json')
        if os.path.exists(article_path):
            os.remove(article_path)


    def _create_test_blink_file(self, blink_id="test_vote_blink", likes=0, dislikes=0, timestamp=1234567890):
        # Ensure votes is a dict, even if likes/dislikes are 0
        blink_content = {
            "id": blink_id,
            "title": "Test Blink for Voting",
            "timestamp": timestamp, # Add timestamp, might be used by some internal logic indirectly
            "votes": {"likes": likes, "dislikes": dislikes},
            "categories": ["test"],
            "content": "Test content",
            "points": ["Point 1"],
            "image": "test.png",
            "sources": ["test_source"],
            "urls": ["http://example.com/test"]
        }
        blink_path = os.path.join(self.actual_data_dir_blinks, f"{blink_id}.json")
        with open(blink_path, 'w') as f:
            json.dump(blink_content, f, indent=2)
        return blink_path

    def _read_blink_file_votes(self, blink_id="test_vote_blink"):
        blink_path = os.path.join(self.actual_data_dir_blinks, f"{blink_id}.json")
        if not os.path.exists(blink_path):
            return None
        with open(blink_path, 'r') as f:
            data = json.load(f)
        return data.get("votes")

    def test_vote_first_like(self):
        self._create_test_blink_file(likes=0, dislikes=0)
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'like'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['data']['votes']['likes'], 1)
        self.assertEqual(data['data']['votes']['dislikes'], 0)
        file_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['likes'], 1)
        self.assertEqual(file_votes['dislikes'], 0)

    def test_vote_first_dislike(self):
        self._create_test_blink_file(likes=0, dislikes=0)
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'dislike'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['data']['votes']['likes'], 0)
        self.assertEqual(data['data']['votes']['dislikes'], 1)
        file_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['likes'], 0)
        self.assertEqual(file_votes['dislikes'], 1)

    def test_vote_change_like_to_dislike(self):
        self._create_test_blink_file(likes=1, dislikes=0) # Start with a like
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'dislike'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['data']['votes']['likes'], 0)
        self.assertEqual(data['data']['votes']['dislikes'], 1)
        file_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['likes'], 0)
        self.assertEqual(file_votes['dislikes'], 1)

    def test_vote_change_dislike_to_like(self):
        self._create_test_blink_file(likes=0, dislikes=1) # Start with a dislike
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'like'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['data']['votes']['likes'], 1)
        self.assertEqual(data['data']['votes']['dislikes'], 0)
        file_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['likes'], 1)
        self.assertEqual(file_votes['dislikes'], 0)

    def test_vote_repeated_like_increments(self):
        self._create_test_blink_file(likes=1, dislikes=0) # Start with a like
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'like'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        # Current backend logic: likes becomes 1+1=2, dislikes remains 0.
        self.assertEqual(data['data']['votes']['likes'], 2)
        self.assertEqual(data['data']['votes']['dislikes'], 0)
        file_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['likes'], 2)
        self.assertEqual(file_votes['dislikes'], 0)

    def test_vote_on_nonexistent_blink(self):
        response = self.client.post('/api/blinks/nonexistent_blink_test_id/vote', json={'voteType': 'like'})
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn('Blink not found', data['error'])

    def test_vote_with_invalid_vote_type(self):
        self._create_test_blink_file(likes=0, dislikes=0)
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'invalid'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Invalid voteType', data['error'])

    def test_vote_missing_vote_type(self):
        self._create_test_blink_file(likes=0, dislikes=0)
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Missing voteType', data['error'])
