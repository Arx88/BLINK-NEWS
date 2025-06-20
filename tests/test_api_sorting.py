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

    def _create_blink_file(self, blink_id, likes, dislikes, published_at_iso_string, user_votes=None, title_prefix="Blink", category="general", aiScore=95):
        if user_votes is None:
            user_votes = {}

        blink_data = {
            "id": blink_id,
            "title": f"{title_prefix} {blink_id}",
            "content": f"This is the content for {blink_id}.",
            "points": [f"Point 1 for {blink_id}", f"Point 2 for {blink_id}"],
            "image": f"http://example.com/images/{blink_id}.png",
            "publishedAt": published_at_iso_string,
            "category": category,
            "aiScore": aiScore,
            "votes": {"likes": likes, "dislikes": dislikes},
            "user_votes": user_votes,
            "sources": [{"id": "test-source", "name": "Test Source"}],
            "urls": [{"type": "main", "url": f"http://example.com/article/{blink_id}"}]
            # interestPercentage is calculated by the backend, not stored in file
        }
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blink_data, f, ensure_ascii=False, indent=2)
        return blink_data # Return the data for easy access to expected values

    def test_sort_by_interest_descending(self):
        now = datetime.now(timezone.utc)
        self._create_blink_file("b1", 10, 0, (now - timedelta(hours=1)).isoformat()) # High interest
        self._create_blink_file("b2", 5, 0, (now - timedelta(hours=2)).isoformat())  # Medium interest
        self._create_blink_file("b3", 1, 0, (now - timedelta(hours=3)).isoformat())  # Low interest
        self._create_blink_file("b4", 0, 5, (now - timedelta(hours=4)).isoformat())  # Negative interest

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()

        # Assuming C=5 for interest: (L-D)/(L+D+C)*100
        # b1: (10-0)/(10+0+5)*100 = 10/15*100 = 66.66
        # b2: (5-0)/(5+0+5)*100 = 5/10*100 = 50.00
        # b3: (1-0)/(1+0+5)*100 = 1/6*100 = 16.66
        # b4: (0-5)/(0+5+5)*100 = -5/10*100 = -50.00

        ids = [blink['id'] for blink in blinks]
        self.assertEqual(ids, ["b1", "b2", "b3", "b4"])

    def test_sort_rule_A_no_votes_by_date(self):
        now = datetime.now(timezone.utc)
        # Rule A candidates (0 votes, 0 interest)
        self._create_blink_file("ruleA_1", 0, 0, (now - timedelta(days=1)).isoformat(), title_prefix="RuleA") # Older
        self._create_blink_file("ruleA_2", 0, 0, now.isoformat(), title_prefix="RuleA") # Newer
        # Control: 0 interest but has votes (e.g. L=D)
        self._create_blink_file("control_0_interest", 5, 5, (now - timedelta(hours=1)).isoformat(), title_prefix="Control") # Interest (5-5)/(5+5+5) = 0

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()
        ids = [blink['id'] for blink in blinks]

        # Expected: RuleA blinks come first if their specific condition (0 interest AND 0 votes) is prioritized
        # over 0 interest with votes. Within RuleA, newest first.
        # Then the control blink.
        # The exact order depends on the _compare_blinks logic for when interest_a == 0 and interest_b == 0.
        # Based on prompt: "the Rule A blink (no votes) comes first" if one qualifies and other doesn't (even if both 0 interest).
        # If both are Rule A, then by date.
        # So, ruleA_2 (newest, no votes) should be first, then ruleA_1 (older, no votes)
        # Then control_0_interest (0 interest, but has votes)

        # Find indices
        idx_ruleA_1 = -1
        idx_ruleA_2 = -1
        idx_control_0 = -1
        for i, blink in enumerate(blinks):
            if blink['id'] == "ruleA_1": idx_ruleA_1 = i
            elif blink['id'] == "ruleA_2": idx_ruleA_2 = i
            elif blink['id'] == "control_0_interest": idx_control_0 = i

        self.assertTrue(idx_ruleA_2 < idx_ruleA_1, "Newer Rule A (no votes) should come before older Rule A")
        self.assertTrue(idx_ruleA_1 < idx_control_0, "Rule A blinks (no votes) should come before 0-interest-with-votes blinks")


    def test_sort_rule_B_zero_positive_multiple_negative_by_negative_asc(self):
        now = datetime.now(timezone.utc)
        # Rule B candidates (0 likes, >0 dislikes). All will have negative interest.
        # Interest: (0-D)/(D+5)*100
        # b_neg1: (0-1)/(1+5)*100 = -1/6*100 = -16.66
        # b_neg3: (0-3)/(3+5)*100 = -3/8*100 = -37.5
        # b_neg5: (0-5)/(5+5)*100 = -5/10*100 = -50.0
        # Rule B is: if tied by interest (which they are NOT here directly, but they are all in the "0 likes" category)
        # then sort by dislikes ascending.
        # However, the primary sort is interest descending. So -16.66 (b_neg1) is highest.
        self._create_blink_file("b_neg1", 0, 1, (now - timedelta(hours=1)).isoformat(), title_prefix="RuleB") # -16.66% interest
        self._create_blink_file("b_neg3", 0, 3, (now - timedelta(hours=2)).isoformat(), title_prefix="RuleB") # -37.5% interest
        self._create_blink_file("b_neg5", 0, 5, (now - timedelta(hours=3)).isoformat(), title_prefix="RuleB") # -50% interest

        # Add another blink with 0 likes, 3 dislikes, but a much different date to see if date tie-breaks if interest is identical
        self._create_blink_file("b_neg3_alt_date", 0, 3, now.isoformat(), title_prefix="RuleBAlt") # Also -37.5% interest, but newer

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks_resp = response.get_json()
        ids = [blink['id'] for blink in blinks_resp]

        # Expected order: b_neg1 (least negative interest), then b_neg3_alt_date (newer, -37.5%), then b_neg3 (older, -37.5%), then b_neg5 (most negative interest)
        # Rule B (sort by dislikes ascending) should apply if interest percentages are *identical* AND both are Rule B candidates.
        # Here, b_neg3 and b_neg3_alt_date have identical interest AND are Rule B candidates.
        # Their dislikes are also identical (3). So they should be sorted by date descending.
        expected_order = ["b_neg1", "b_neg3_alt_date", "b_neg3", "b_neg5"]
        self.assertEqual(ids, expected_order, f"Expected {expected_order}, got {ids}")


    def test_sort_tie_break_by_publication_date(self):
        now = datetime.now(timezone.utc)
        # Create blinks with identical like/dislike counts (so same interest)
        # Interest for both: (2-0)/(2+0+5)*100 = 2/7*100 = 28.57%
        self._create_blink_file("tie_date_older", 2, 0, (now - timedelta(days=1)).isoformat(), title_prefix="Tie")
        self._create_blink_file("tie_date_newer", 2, 0, now.isoformat(), title_prefix="Tie")

        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()
        ids = [blink['id'] for blink in blinks]

        # Expected: newer date comes first
        self.assertEqual(ids, ["tie_date_newer", "tie_date_older"])

    def test_mixed_scenario_sorting(self):
        now = datetime.now(timezone.utc)
        # Create a diverse set of blinks
        # 1. High positive interest: b_high_pos (10L, 0D) -> (10/15)*100 = 66.66%
        self._create_blink_file("b_high_pos", 10, 0, (now - timedelta(hours=1)).isoformat())
        # 2. Medium positive interest: b_med_pos (5L, 0D) -> (5/10)*100 = 50%
        self._create_blink_file("b_med_pos", 5, 0, (now - timedelta(hours=2)).isoformat())
        # 3. Zero interest (no votes), newer: b_zero_novote_new (0L, 0D) -> 0%
        self._create_blink_file("b_zero_novote_new", 0, 0, now.isoformat())
        # 4. Zero interest (no votes), older: b_zero_novote_old (0L, 0D) -> 0%
        self._create_blink_file("b_zero_novote_old", 0, 0, (now - timedelta(days=1)).isoformat())
        # 5. Zero interest (votes): b_zero_votes (3L, 3D) -> (0/11)*100 = 0%
        self._create_blink_file("b_zero_votes", 3, 3, (now - timedelta(hours=3)).isoformat())
        # 6. Negative interest (0 positive, multiple negative), fewer dislikes: b_neg_few_dis (0L, 2D) -> (-2/7)*100 = -28.57%
        self._create_blink_file("b_neg_few_dis", 0, 2, (now - timedelta(hours=4)).isoformat())
        # 7. Negative interest (0 positive, multiple negative), more dislikes: b_neg_more_dis (0L, 4D) -> (-4/9)*100 = -44.44%
        self._create_blink_file("b_neg_more_dis", 0, 4, (now - timedelta(hours=5)).isoformat())
        # 8. Other negative interest (some likes but more dislikes): b_neg_other (1L, 5D) -> (-4/11)*100 = -36.36%
        self._create_blink_file("b_neg_other", 1, 5, (now - timedelta(hours=6)).isoformat())


        response = self.client.get('/api/blinks')
        self.assertEqual(response.status_code, 200)
        blinks = response.get_json()
        ids = [blink['id'] for blink in blinks]

        # Expected order:
        # 1. b_high_pos (66.66%)
        # 2. b_med_pos (50%)
        # 3. b_zero_novote_new (0%, Rule A, newer)
        # 4. b_zero_novote_old (0%, Rule A, older)
        # 5. b_zero_votes (0%, has votes, comes after Rule A per logic)
        # 6. b_neg_few_dis (-28.57%, Rule B candidate)
        # 7. b_neg_other (-36.36%, not Rule B candidate but higher interest than b_neg_more_dis)
        # 8. b_neg_more_dis (-44.44%, Rule B candidate)
        # Rule B sorting (dislikes ASC) applies if interest is tied *and* both qualify for Rule B.
        # Here interests are different for b_neg_few_dis and b_neg_more_dis, so primary interest sort applies.

        expected_ids = [
            "b_high_pos",
            "b_med_pos",
            "b_zero_novote_new",
            "b_zero_novote_old",
            "b_zero_votes",
            "b_neg_few_dis",
            "b_neg_other",
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
            self._create_blink_file("hot_b1", likes=10, dislikes=0, published_at_iso_string=(now - timedelta(minutes=1)).isoformat()), # Expected Hot
            self._create_blink_file("hot_b2", likes=9, dislikes=0, published_at_iso_string=(now - timedelta(minutes=2)).isoformat()),  # Expected Hot
            self._create_blink_file("hot_b3", likes=8, dislikes=0, published_at_iso_string=(now - timedelta(minutes=3)).isoformat()),  # Expected Hot
            self._create_blink_file("hot_b4", likes=7, dislikes=0, published_at_iso_string=(now - timedelta(minutes=4)).isoformat()),  # Expected Hot
            self._create_blink_file("hot_b5", likes=6, dislikes=0, published_at_iso_string=(now - timedelta(minutes=5)).isoformat())   # Expected Not Hot
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
            self._create_blink_file("hot_s2_b1", likes=10, dislikes=0, published_at_iso_string=(now - timedelta(minutes=10)).isoformat()), # Expected Hot
            self._create_blink_file("hot_s2_b2", likes=9, dislikes=0, published_at_iso_string=(now - timedelta(minutes=11)).isoformat())   # Expected Hot
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


if __name__ == '__main__':
    unittest.main()
