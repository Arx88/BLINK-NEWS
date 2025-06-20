import unittest
import os
import json
import shutil
from datetime import datetime, timezone, timedelta # Keep for TestApiVoting and add timedelta for sorting tests
from flask import Flask
from functools import cmp_to_key # For potential direct model method calls if needed, though API testing is primary
from news_blink_backend.src.routes.api import init_api # Relative import for Flask app
from news_blink_backend.src.models.news import News # For direct interest calculation if needed for more precise test setup

# Existing TestApiVoting class (truncated for brevity in this plan, will be kept in the actual file)
class TestApiVoting(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        # Correct the path for Flask app config
        self.test_data_dir_voting = os.path.abspath("temp_test_blinks_data_voting_sorting_test") # Ensure unique name

        self.blinks_dir = os.path.join(self.test_data_dir_voting, 'blinks')
        self.articles_dir = os.path.join(self.test_data_dir_voting, 'articles')

        os.makedirs(self.blinks_dir, exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)

        self.app.config['APP_CONFIG'] = {'NEWS_MODEL_DATA_DIR': self.test_data_dir_voting}
        init_api(self.app) # Initialize routes
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.test_user_id = "test_user_123"

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
            "content": "Test content for blink.",
            "points": ["Point 1.", "Point 2."],
            "image": "test_image.png",
            "sources": [{"id": "src-1", "name": "Test Source"}],
            "urls": [{"type": "main", "url": f"http://example.com/{blink_id}"}],
            "category": "test-category"
        }
        blink_path = os.path.join(self.blinks_dir, f"{blink_id}.json")
        with open(blink_path, 'w') as f:
            json.dump(blink_content, f, indent=2)
        return blink_path

    def _read_blink_file_data(self, blink_id="test_vote_blink"):
        blink_path = os.path.join(self.blinks_dir, f"{blink_id}.json")
        if not os.path.exists(blink_path):
            return None
        with open(blink_path, 'r') as f:
            data = json.load(f)
        return data

    # --- All existing test methods from TestApiVoting go here ---
    def test_vote_first_like(self):
        blink_id = "first_like_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=0, user_votes={})
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': None})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['votes']['likes'], 1)
        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 1)

    def test_vote_first_dislike(self):
        blink_id = "first_dislike_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=0, user_votes={})
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'dislike', 'previousVote': None})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['votes']['dislikes'], 1)
        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['dislikes'], 1)

    def test_vote_change_like_to_dislike(self):
        blink_id = "change_like_to_dislike_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=1, dislikes=0, user_votes={self.test_user_id: "like"})
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'dislike', 'previousVote': 'like'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['votes']['likes'], 0)
        self.assertEqual(data['votes']['dislikes'], 1)
        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 0)
        self.assertEqual(file_data['votes']['dislikes'], 1)

    def test_vote_change_dislike_to_like(self):
        blink_id = "change_dislike_to_like_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=1, user_votes={self.test_user_id: "dislike"})
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': 'dislike'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['votes']['likes'], 1)
        self.assertEqual(data['votes']['dislikes'], 0)
        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 1)
        self.assertEqual(file_data['votes']['dislikes'], 0)

    def test_vote_repeated_like(self):
        blink_id = "repeated_like_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=1, dislikes=0, user_votes={self.test_user_id: "like"})
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': 'like'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['votes']['likes'], 1)
        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['likes'], 1)

    def test_vote_repeated_dislike(self):
        blink_id = "repeated_dislike_blink"
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=1, user_votes={self.test_user_id: "dislike"})
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'dislike', 'previousVote': 'dislike'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['votes']['dislikes'], 1)
        file_data = self._read_blink_file_data(blink_id)
        self.assertEqual(file_data['votes']['dislikes'], 1)

    def test_vote_on_nonexistent_blink(self):
        blink_id = "nonexistent_blink"
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': None})
        self.assertEqual(response.status_code, 404)

    def test_vote_with_invalid_vote_type(self):
        blink_id = "invalid_vote_type_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'invalid', 'previousVote': None})
        self.assertEqual(response.status_code, 400)

    def test_vote_with_invalid_previous_vote_type(self):
        blink_id = "invalid_prev_vote_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'voteType': 'like', 'previousVote': 'invalid'})
        self.assertEqual(response.status_code, 400)

    def test_vote_missing_vote_type(self):
        blink_id = "missing_vote_type_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'userId': self.test_user_id, 'previousVote': None})
        self.assertEqual(response.status_code, 400)

    def test_vote_missing_user_id(self):
        blink_id = "missing_user_id_blink"
        self._create_test_blink_file(blink_id=blink_id)
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={'voteType': 'like', 'previousVote': None})
        self.assertEqual(response.status_code, 400)

    def test_vote_remove_like(self):
        blink_id = "remove_like_test"
        # Setup: User has already liked this blink
        self._create_test_blink_file(blink_id=blink_id, likes=1, dislikes=0, user_votes={self.test_user_id: "like"})

        # Action: User clicks 'like' again to remove their vote
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={
            'userId': self.test_user_id,
            'voteType': 'like', # Intends to set 'like', but server sees previous 'like'
            'previousVote': 'like' # Client correctly indicates its last known state for this user
        })

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()

        # Assertions for response
        self.assertEqual(response_data['data']['votes']['likes'], 0, "Likes should be decremented in response")
        self.assertNotIn(self.test_user_id, response_data['data']['user_votes'], "User ID should be removed from user_votes in response")

        # Assertions for file data
        file_data = self._read_blink_file_data(blink_id)
        self.assertIsNotNone(file_data, "Blink file should exist")
        self.assertEqual(file_data['votes']['likes'], 0, "Likes should be decremented in file")
        self.assertNotIn(self.test_user_id, file_data['user_votes'], "User ID should be removed from user_votes in file")

    def test_vote_remove_dislike(self):
        blink_id = "remove_dislike_test"
        # Setup: User has already disliked this blink
        self._create_test_blink_file(blink_id=blink_id, likes=0, dislikes=1, user_votes={self.test_user_id: "dislike"})

        # Action: User clicks 'dislike' again to remove their vote
        response = self.client.post(f'/api/blinks/{blink_id}/vote', json={
            'userId': self.test_user_id,
            'voteType': 'dislike', # Intends to set 'dislike', but server sees previous 'dislike'
            'previousVote': 'dislike' # Client correctly indicates its last known state for this user
        })

        self.assertEqual(response.status_code, 200)
        response_data = response.get_json()

        # Assertions for response
        self.assertEqual(response_data['data']['votes']['dislikes'], 0, "Dislikes should be decremented in response")
        self.assertNotIn(self.test_user_id, response_data['data']['user_votes'], "User ID should be removed from user_votes in response")

        # Assertions for file data
        file_data = self._read_blink_file_data(blink_id)
        self.assertIsNotNone(file_data, "Blink file should exist")
        self.assertEqual(file_data['votes']['dislikes'], 0, "Dislikes should be decremented in file")
        self.assertNotIn(self.test_user_id, file_data['user_votes'], "User ID should be removed from user_votes in file")


class TestApiBlinkSorting(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        # Ensure a unique data directory for this test class
        self.test_data_dir_sorting = os.path.abspath("temp_test_blinks_data_sorting")

        self.blinks_dir = os.path.join(self.test_data_dir_sorting, 'blinks')
        self.articles_dir = os.path.join(self.test_data_dir_sorting, 'articles') # Though not directly used, good practice

        os.makedirs(self.blinks_dir, exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)

        self.app.config['APP_CONFIG'] = {'NEWS_MODEL_DATA_DIR': self.test_data_dir_sorting}
        init_api(self.app) # Initialize routes
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # For direct interest calculation if needed for complex assertions
        # self.news_model_instance = News(data_dir=self.test_data_dir_sorting) # Not strictly needed if only testing API response order

    def tearDown(self):
        self.app_context.pop()
        shutil.rmtree(self.test_data_dir_sorting)

    def _create_blink_file(self, blink_id, likes, dislikes, timestamp_iso_string, user_votes=None, title_prefix="Blink"):
        # Removed category and aiScore as they are not directly used by the specific sorting logic being tested
        # and aims to simplify the test setup to focus on votes and timestamp.
        if user_votes is None:
            user_votes = {} # Retained user_votes for now, though sorting doesn't use it directly.

        blink_data = {
            "id": blink_id,
            "title": f"{title_prefix} {blink_id}",
            "content": f"This is the content for {blink_id}.",
            "points": [f"Point 1 for {blink_id}", f"Point 2 for {blink_id}"],
            "image": f"http://example.com/images/{blink_id}.png",
            "timestamp": timestamp_iso_string, # Key changed to "timestamp"
            "votes": { # Votes are now nested
                "likes": likes,
                "dislikes": dislikes
            },
            "user_votes": user_votes,
            "sources": [{"id": "test-source", "name": "Test Source"}],
            "urls": [{"type": "main", "url": f"http://example.com/article/{blink_id}"}]
            # calculated_interest_score is added by the backend route before sorting, not in the file.
        }
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blink_data, f, ensure_ascii=False, indent=2)
        # Return the data for potential assertions if needed, though not strictly required by existing tests.
        return blink_data

    def test_sort_by_interest_descending(self):
        now = datetime.now(timezone.utc)
        # Calls to _create_blink_file updated to use timestamp_iso_string
        self._create_blink_file("b1", 10, 0, timestamp_iso_string=(now - timedelta(hours=1)).isoformat()) # High interest
        self._create_blink_file("b2", 5, 0, timestamp_iso_string=(now - timedelta(hours=2)).isoformat())  # Medium interest
        self._create_blink_file("b3", 1, 0, timestamp_iso_string=(now - timedelta(hours=3)).isoformat())  # Low interest
        self._create_blink_file("b4", 0, 5, timestamp_iso_string=(now - timedelta(hours=4)).isoformat())  # Negative interest

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()

        # Interest scores are calculated by the backend.
        # Example expected interest scores (actual values depend on backend's calculate_correct_interest):
        # b1: 10 likes, 0 dislikes -> 100%
        # b2: 5 likes, 0 dislikes -> 100% (if only likes considered and dislikes 0) or lower if total votes matter.
        # For calculate_correct_interest: (likes / (likes + dislikes)) * 100
        # b1: (10 / 10) * 100 = 100
        # b2: (5 / 5) * 100 = 100
        # b3: (1 / 1) * 100 = 100
        # b4: (0 / 5) * 100 = 0
        # The sorting logic in compare_blinks_custom prioritizes interest, then likes, then date.
        # Since b1, b2, b3 have 100% interest, they'll be sorted by likes: b1, b2, b3.
        # b4 has 0% interest.

        ids = [blink['id'] for blink in blinks]
        # Based on: interest (all 100 for b1,b2,b3), then likes (10,5,1), then date. b4 is last (0% interest).
        self.assertEqual(ids, ["b1", "b2", "b3", "b4"])


    def test_sort_rule_A_no_votes_by_date(self):
        now = datetime.now(timezone.utc)
        # Rule A candidates (0 votes, 0 interest)
        self._create_blink_file("ruleA_1", 0, 0, timestamp_iso_string=(now - timedelta(days=1)).isoformat(), title_prefix="RuleA") # Older
        self._create_blink_file("ruleA_2", 0, 0, timestamp_iso_string=now.isoformat(), title_prefix="RuleA") # Newer
        # Control: 0 interest but has votes (e.g. L=D)
        # calculate_correct_interest(5,5) = (5/10)*100 = 50%
        self._create_blink_file("control_0_interest", 5, 5, timestamp_iso_string=(now - timedelta(hours=1)).isoformat(), title_prefix="Control")

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()
        ids = [blink['id'] for blink in blinks]

        # calculate_correct_interest:
        # ruleA_1 (0,0) -> 50% (default for no votes)
        # ruleA_2 (0,0) -> 50% (default for no votes)
        # control_0_interest (5,5) -> (5/10)*100 = 50%
        # All have 50% interest.
        # Next tie-breaker: likes.
        # control_0_interest has 5 likes. ruleA_1 and ruleA_2 have 0 likes.
        # So, control_0_interest comes first.
        # Then ruleA_2 (newer) and ruleA_1 (older) are sorted by date.
        expected_ids = ["control_0_interest", "ruleA_2", "ruleA_1"]
        self.assertEqual(ids, expected_ids, f"Expected {expected_ids} but got {ids}")


    def test_sort_rule_B_zero_positive_multiple_negative_by_negative_asc(self):
        # This test's name and original intent might need re-evaluation based on the actual sorting logic.
        # The sorting is: Interest (desc), Likes (desc), Date (desc).
        # "Rule B" (0 likes, sort by dislikes asc) is not an explicit rule in compare_blinks_custom.
        now = datetime.now(timezone.utc)

        # Interest calculation: (likes / (likes + dislikes)) * 100. If likes+dislikes is 0, then 50.0.
        # b_neg1 (0L, 1D): (0 / 1) * 100 = 0%
        # b_neg3 (0L, 3D): (0 / 3) * 100 = 0%
        # b_neg5 (0L, 5D): (0 / 5) * 100 = 0%
        # b_neg3_alt_date (0L, 3D): (0 / 3) * 100 = 0%
        # All these have 0% interest and 0 likes. So they will be sorted by date descending.

        self._create_blink_file("b_neg1", 0, 1, timestamp_iso_string=(now - timedelta(hours=1)).isoformat(), title_prefix="RuleB")
        self._create_blink_file("b_neg3", 0, 3, timestamp_iso_string=(now - timedelta(hours=2)).isoformat(), title_prefix="RuleB")
        self._create_blink_file("b_neg5", 0, 5, timestamp_iso_string=(now - timedelta(hours=3)).isoformat(), title_prefix="RuleB")
        self._create_blink_file("b_neg3_alt_date", 0, 3, timestamp_iso_string=now.isoformat(), title_prefix="RuleBAlt") # Newest

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks_resp = response.get_json()
        ids = [blink['id'] for blink in blinks_resp]

        # All have 0% interest, 0 likes. Sorted by date descending.
        expected_order = ["b_neg3_alt_date", "b_neg1", "b_neg3", "b_neg5"]
        self.assertEqual(ids, expected_order, f"Expected {expected_order}, got {ids}")


    def test_sort_tie_break_by_publication_date(self):
        now = datetime.now(timezone.utc)
        # Create blinks with identical like/dislike counts
        # Interest for both (2L, 0D): (2/2)*100 = 100%
        # Likes are also identical (2). So, tie-break by date.
        self._create_blink_file("tie_date_older", 2, 0, timestamp_iso_string=(now - timedelta(days=1)).isoformat(), title_prefix="Tie")
        self._create_blink_file("tie_date_newer", 2, 0, timestamp_iso_string=now.isoformat(), title_prefix="Tie")

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()
        ids = [blink['id'] for blink in blinks]

        # Expected: newer date comes first
        self.assertEqual(ids, ["tie_date_newer", "tie_date_older"])

    def test_mixed_scenario_sorting(self):
        now = datetime.now(timezone.utc)
        # Create a diverse set of blinks
    def test_mixed_scenario_sorting(self):
        now = datetime.now(timezone.utc)

        # Interest scores based on calculate_correct_interest((L/(L+D))*100 or 50 for no votes):
        # 1. b_high_pos (10L, 0D): 100%
        self._create_blink_file("b_high_pos", 10, 0, timestamp_iso_string=(now - timedelta(hours=1)).isoformat())
        # 2. b_med_pos (5L, 0D): 100%
        self._create_blink_file("b_med_pos", 5, 0, timestamp_iso_string=(now - timedelta(hours=2)).isoformat())
        # 3. b_zero_votes (3L, 3D): 50%
        self._create_blink_file("b_zero_votes", 3, 3, timestamp_iso_string=(now - timedelta(hours=3)).isoformat())
        # 4. b_zero_novote_new (0L, 0D): 50% (default for no votes)
        self._create_blink_file("b_zero_novote_new", 0, 0, timestamp_iso_string=now.isoformat())
        # 5. b_zero_novote_old (0L, 0D): 50% (default for no votes)
        self._create_blink_file("b_zero_novote_old", 0, 0, timestamp_iso_string=(now - timedelta(days=1)).isoformat())
        # 6. b_neg_other (1L, 5D): (1/6)*100 = 16.66%
        self._create_blink_file("b_neg_other", 1, 5, timestamp_iso_string=(now - timedelta(hours=6)).isoformat())
        # 7. b_neg_few_dis (0L, 2D): 0%
        self._create_blink_file("b_neg_few_dis", 0, 2, timestamp_iso_string=(now - timedelta(hours=4)).isoformat())
        # 8. b_neg_more_dis (0L, 4D): 0%
        self._create_blink_file("b_neg_more_dis", 0, 4, timestamp_iso_string=(now - timedelta(hours=5)).isoformat())

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()
        ids = [blink['id'] for blink in blinks]

        # Expected order based on compare_blinks_custom (Interest DESC, Likes DESC, Date DESC):
        # 1. b_high_pos (100% Interest, 10 Likes)
        # 2. b_med_pos (100% Interest, 5 Likes)
        # 3. b_zero_votes (50% Interest, 3 Likes)
        # 4. b_zero_novote_new (50% Interest, 0 Likes, newer date)
        # 5. b_zero_novote_old (50% Interest, 0 Likes, older date)
        # 6. b_neg_other (16.66% Interest, 1 Like)
        # 7. b_neg_few_dis (0% Interest, 0 Likes, newer date between these two)
        # 8. b_neg_more_dis (0% Interest, 0 Likes, older date between these two)
        expected_ids = [
            "b_high_pos",
            "b_med_pos",
            "b_zero_votes",
            "b_zero_novote_new",
            "b_zero_novote_old",
            "b_neg_other",
            "b_neg_few_dis",
            "b_neg_more_dis"
        ]
        self.assertEqual(ids, expected_ids, f"Expected {expected_ids}, but got {ids}")

    def test_is_hot_property(self):
        now = datetime.now(timezone.utc)

        # Sub-test 1: 5 blinks (4 hot, 1 not)
        # To ensure predictable sort order, we'll primarily vary 'likes' assuming interest is directly proportional
        # or that likes act as a tie-breaker if interest calculation leads to ties.
        # For simplicity, let's assume higher likes = higher interest for this test setup.
        # All blinks will have 0 dislikes and recent, distinct publication dates to make 'likes' the dominant factor.

        # Clean up before this specific test section to ensure no old files interfere
        # This is a more robust way if not using unique IDs across all tests in the class
        if os.path.exists(self.blinks_dir):
            shutil.rmtree(self.blinks_dir)
        os.makedirs(self.blinks_dir, exist_ok=True)

        created_blinks_scenario1 = [
            self._create_blink_file("hot_b1", likes=10, dislikes=0, timestamp_iso_string=(now - timedelta(minutes=1)).isoformat()), # Expected Hot
            self._create_blink_file("hot_b2", likes=9, dislikes=0, timestamp_iso_string=(now - timedelta(minutes=2)).isoformat()),  # Expected Hot
            self._create_blink_file("hot_b3", likes=8, dislikes=0, timestamp_iso_string=(now - timedelta(minutes=3)).isoformat()),  # Expected Hot
            self._create_blink_file("hot_b4", likes=7, dislikes=0, timestamp_iso_string=(now - timedelta(minutes=4)).isoformat()),  # Expected Hot
            self._create_blink_file("hot_b5", likes=6, dislikes=0, timestamp_iso_string=(now - timedelta(minutes=5)).isoformat())   # Expected Not Hot
        ]

        response_5_blinks = self.client.get('/api/blinks')
        self.assertEqual(response_5_blinks.status_code, 200)
        blinks_5 = response_5_blinks.get_json()

        self.assertEqual(len(blinks_5), 5)

        # Check isHot status based on expected sort order (highest likes first)
        # The actual sorting logic in api.py will determine the order.
        # We assume here that likes=10 is first, likes=6 is last.

        # Create a mapping of ID to blink data for easier assertion
        blinks_5_map = {blink['id']: blink for blink in blinks_5}

        # IDs sorted by likes descending (which should be the order from API)
        expected_order_ids_scen1 = ["hot_b1", "hot_b2", "hot_b3", "hot_b4", "hot_b5"]

        for i, blink_id in enumerate(expected_order_ids_scen1):
            self.assertEqual(blinks_5[i]['id'], blink_id) # Verify API returned in expected order
            if i < 4:
                self.assertTrue(blinks_5[i].get('isHot'), f"Blink {blink_id} (index {i}) should be hot.")
            else:
                self.assertFalse(blinks_5[i].get('isHot'), f"Blink {blink_id} (index {i}) should not be hot.")

        # Sub-test 2: 2 blinks (both hot)
        # Clean up again for isolation, or use unique IDs. Using unique IDs here for simplicity.
        # No need to rm -rf if using unique IDs that don't clash with previous ones in this method.
        # However, to be absolutely sure for this sub-test, let's clean and recreate.
        if os.path.exists(self.blinks_dir): # Ensure clean slate for this sub-test
            shutil.rmtree(self.blinks_dir)
        os.makedirs(self.blinks_dir, exist_ok=True)

        created_blinks_scenario2 = [
            self._create_blink_file("hot_s2_b1", likes=10, dislikes=0, timestamp_iso_string=(now - timedelta(minutes=10)).isoformat()), # Expected Hot
            self._create_blink_file("hot_s2_b2", likes=9, dislikes=0, timestamp_iso_string=(now - timedelta(minutes=11)).isoformat())   # Expected Hot
        ]

        response_2_blinks = self.client.get('/api/blinks')
        self.assertEqual(response_2_blinks.status_code, 200)
        blinks_2 = response_2_blinks.get_json()

        self.assertEqual(len(blinks_2), 2)

        # Create a mapping of ID to blink data for easier assertion
        blinks_2_map = {blink['id']: blink for blink in blinks_2}
        expected_order_ids_scen2 = ["hot_s2_b1", "hot_s2_b2"]


        for i, blink_id in enumerate(expected_order_ids_scen2):
            self.assertEqual(blinks_2[i]['id'], blink_id) # Verify API returned in expected order
            self.assertTrue(blinks_2[i].get('isHot'), f"Blink {blink_id} (index {i}) should be hot in 2-blink scenario.")

    def test_sort_mixed_timezone_awareness(self):
        now_utc = datetime.now(timezone.utc)

        # All blinks have same likes/dislikes, so interest score will be identical.
        # Sorting will primarily depend on the timestamp after timezone correction.
        likes = 5
        dislikes = 0

        # 1. Aware, most recent
        self._create_blink_file(
            blink_id="aware_recent",
            likes=likes,
            dislikes=dislikes,
            timestamp_iso_string=(now_utc - timedelta(hours=1)).isoformat() # e.g., 2023-01-01T12:00:00+00:00
        )
        # 2. Naive, middle timestamp (when converted to UTC)
        # This format '%Y-%m-%dT%H:%M:%S' creates a naive datetime string
        self._create_blink_file(
            blink_id="naive_middle",
            likes=likes,
            dislikes=dislikes,
            timestamp_iso_string=(now_utc - timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S') # e.g., 2023-01-01T11:00:00 (naive)
        )
        # 3. Aware, oldest
        self._create_blink_file(
            blink_id="aware_oldest",
            likes=likes,
            dislikes=dislikes,
            timestamp_iso_string=(now_utc - timedelta(hours=3)).isoformat() # e.g., 2023-01-01T10:00:00+00:00
        )

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()

        ids = [blink['id'] for blink in blinks]

        # Expected order: aware_recent, naive_middle (correctly interpreted as UTC), aware_oldest
        # This is because compare_blinks_custom now makes naive datetimes UTC-aware.
        expected_ids = ["aware_recent", "naive_middle", "aware_oldest"]
        self.assertEqual(ids, expected_ids, f"Expected order {expected_ids}, but got {ids}")


if __name__ == '__main__':
    unittest.main()
