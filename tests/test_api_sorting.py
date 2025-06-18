import unittest
import os
import json
import shutil
from datetime import datetime, timezone, timedelta

from models.news import News # The class to test

# Helper to calculate interest for test assertions (mirrors backend's calculate_interest_percentage)
# Note: The actual calculate_interest_percentage is in the News class and will be used by get_all_blinks.
# This helper is for validating expected interest values if needed during test writing, not for the SUT.
def calculate_expected_interest(positive, negative, confidence_factor_c=5):
    total_votes = positive + negative
    net_vote_difference = positive - negative
    if total_votes == 0:
        return 0.0
    # Original formula: (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0
    # Simplified for direct comparison with interestPercentage values from the class:
    interest = (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0
    return interest

class TestNewsSortingLogic(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = "temp_test_blinks_data_sorting" # Unique name
        self.blinks_dir = os.path.join(self.test_data_dir, "blinks")
        os.makedirs(self.blinks_dir, exist_ok=True)
        self.news_manager = News(data_dir=self.test_data_dir)
        # Mock current time for consistent publishedAt if not specified
        self.now = datetime.now(timezone.utc)


    def tearDown(self):
        # pass # Optional: inspect directory after tests
        shutil.rmtree(self.test_data_dir)

    def _create_blink_file(self, blink_id, positive_votes, negative_votes, published_at_iso, title="Test Blink"):
        # published_at_iso should be a string like "2023-01-01T10:00:00Z"
        blink_data = {
            "id": blink_id,
            "title": title,
            "publishedAt": published_at_iso,
            "votes": {"positive": positive_votes, "negative": negative_votes},
            "user_votes": {}, # Essential as per findings
            "content": "Test content.",
            "points": ["Point 1"],
            "image": "image.png",
            "sources": [{"id": "src1", "name": "Source 1"}],
            "urls": [{"type": "main", "url": "http://example.com"}],
            "category": "test"
        }
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(blink_data, f, indent=2)
        # print(f"Created blink: {blink_id}, P:{positive_votes}, N:{negative_votes}, Date:{published_at_iso}, Interest:{calculate_expected_interest(positive_votes, negative_votes):.2f}%")


    def test_primary_sort_by_interest_desc(self):
        self._create_blink_file("C_low", 1, 0, (self.now - timedelta(hours=2)).isoformat())  # Interest: (1 / (1+5))*100 = 16.67
        self._create_blink_file("A_high", 10, 0, (self.now - timedelta(hours=1)).isoformat()) # Interest: (10 / (10+5))*100 = 66.67
        self._create_blink_file("B_mid", 5, 0, self.now.isoformat())  # Interest: (5 / (5+5))*100 = 50.0

        sorted_blinks = self.news_manager.get_all_blinks()
        sorted_ids = [b['id'] for b in sorted_blinks]
        self.assertEqual(sorted_ids, ["A_high", "B_mid", "C_low"])

    def test_general_tie_break_by_date_desc_when_interest_equal(self):
        # All have same interest: (5 / (5+2+5))*100 = (3 / 12)*100 = 25%
        self._create_blink_file("B_older", 5, 2, (self.now - timedelta(hours=2)).isoformat())
        self._create_blink_file("A_newest", 5, 2, self.now.isoformat())
        self._create_blink_file("C_mid_time", 5, 2, (self.now - timedelta(hours=1)).isoformat())

        sorted_blinks = self.news_manager.get_all_blinks()
        sorted_ids = [b['id'] for b in sorted_blinks]
        self.assertEqual(sorted_ids, ["A_newest", "C_mid_time", "B_older"])

    def test_rule_a_both_zero_interest_zero_votes_sort_by_date_desc(self):
        # Rule A: 0 interest, 0 positive, 0 negative. Interest will be 0.0 for both.
        self._create_blink_file("RA_older", 0, 0, (self.now - timedelta(hours=1)).isoformat())
        self._create_blink_file("RA_newer", 0, 0, self.now.isoformat())

        sorted_blinks = self.news_manager.get_all_blinks()
        sorted_ids = [b['id'] for b in sorted_blinks]
        self.assertEqual(sorted_ids, ["RA_newer", "RA_older"])

    def test_rule_b_both_zero_pos_many_neg_sort_by_neg_asc_then_date_desc(self):
        # Rule B: 0 positive, >0 negative. Interest will be negative.
        # RB1: 0P, 2N -> (-2/(2+5))*100 = -28.57%
        # RB2: 0P, 5N -> (-5/(5+5))*100 = -50.0%
        # RB3: 0P, 2N -> (-2/(2+5))*100 = -28.57% (tie with RB1 on neg_votes, use date)

        # Primary sort is interest DESC. So RB1 and RB3 (less negative interest) come before RB2.
        self._create_blink_file("RB1_2N_older", 0, 2, (self.now - timedelta(hours=1)).isoformat())
        self._create_blink_file("RB2_5N", 0, 5, self.now.isoformat())
        self._create_blink_file("RB3_2N_newer", 0, 2, self.now.isoformat())

        # Expected order due to compare_blinks logic for Rule B:
        # 1. Interest primary: RB1, RB3 (-28.57%) before RB2 (-50%)
        # 2. For RB1 & RB3 (tied interest): both are Rule B.
        #    Rule B sorts by negative_votes ASC. Both have 2.
        #    Then by date DESC. RB3_2N_newer comes before RB1_2N_older.
        # So, final order: RB3_2N_newer, RB1_2N_older, RB2_5N.

        sorted_blinks = self.news_manager.get_all_blinks()
        sorted_ids = [b['id'] for b in sorted_blinks]
        # print([(b['id'], b['interestPercentage'], b['votes']['negative']) for b in sorted_blinks])
        self.assertEqual(sorted_ids, ["RB3_2N_newer", "RB1_2N_older", "RB2_5N"])


    def test_sorting_hierarchy_general_0_vs_rule_a_vs_rule_b(self):
        # All these will have 0.0 or negative interestPercentage.
        # GEN_0_eq: 5P, 5N -> (0 / (10+5)) * 100 = 0.0% (General 0% interest)
        # RA_0_0:   0P, 0N -> 0.0% (Rule A)
        # RB_0_2:   0P, 2N -> (-2 / (2+5)) * 100 = -28.57% (Rule B)

        # Based on compare_blinks logic:
        # - GEN_0_eq (0.0%) vs RA_0_0 (0.0%): Interest tied. Neither is Rule A against the other if one has votes.
        #   The logic for "is_b1_rule_a_criteria and not is_b2_rule_a_criteria" (where b2 has votes but 0% interest) means Rule A comes after.
        #   So GEN_0_eq comes before RA_0_0.
        # - RA_0_0 (0.0%) vs RB_0_2 (-28.57%): RA_0_0 has higher interest. So RA_0_0 comes before RB_0_2.
        # - GEN_0_eq (0.0%) vs RB_0_2 (-28.57%): GEN_0_eq has higher interest. So GEN_0_eq comes before RB_0_2.

        # Expected order: GEN_0_eq, RA_0_0, RB_0_2
        # Dates are set to be non-conflicting if primary logic holds.
        self._create_blink_file("RA_0_0",   0, 0, (self.now - timedelta(hours=1)).isoformat())
        self._create_blink_file("GEN_0_eq", 5, 5, self.now.isoformat())
        self._create_blink_file("RB_0_2",   0, 2, (self.now - timedelta(hours=2)).isoformat())

        sorted_blinks = self.news_manager.get_all_blinks()
        sorted_ids = [b['id'] for b in sorted_blinks]
        # print([(b['id'], b['interestPercentage'], b['votes']['positive'], b['votes']['negative']) for b in sorted_blinks])
        self.assertEqual(sorted_ids, ["GEN_0_eq", "RA_0_0", "RB_0_2"])

    def test_rule_a_vs_rule_b_direct_same_date_0_interest(self):
        # Rule A: 0P, 0N -> 0.0% interest
        # Rule B: 0P, 2N -> -28.57% interest
        # Rule A should come before Rule B due to higher interest score.
        common_date = self.now.isoformat()
        self._create_blink_file("RA_rule_A", 0, 0, common_date)
        self._create_blink_file("RB_rule_B", 0, 2, common_date)

        sorted_blinks = self.news_manager.get_all_blinks()
        sorted_ids = [b['id'] for b in sorted_blinks]
        self.assertEqual(sorted_ids, ["RA_rule_A", "RB_rule_B"])


    def test_complex_scenario_all_rules(self):
        # High Interest: 10P, 0N -> 66.67%
        # Mid Interest:  5P, 0N  -> 50.0%
        # General 0% A:  5P, 5N (bal), date_newest -> 0.0%
        # General 0% B:  5P, 5N (bal), date_oldest -> 0.0%
        # Rule A 1:      0P, 0N, date_newest -> 0.0%
        # Rule A 2:      0P, 0N, date_oldest -> 0.0%
        # Rule B 1:      0P, 2N (fewer neg), date_newest -> -28.57%
        # Rule B 2:      0P, 2N (fewer neg), date_oldest -> -28.57%
        # Rule B 3:      0P, 5N (more neg) -> -50.0%
        # Negative Interest: 1P, 10N -> (1-10)/(11+5)*100 = -9/16*100 = -56.25%

        date_1 = (self.now - timedelta(days=1)).isoformat() # oldest
        date_2 = (self.now - timedelta(hours=12)).isoformat()
        date_3 = (self.now - timedelta(hours=6)).isoformat()
        date_4 = self.now.isoformat() # newest

        self._create_blink_file("NEG_interest", 1, 10, date_1) # -56.25%
        self._create_blink_file("RB3_0P_5N",    0, 5,  date_2) # -50.0% (Rule B)
        self._create_blink_file("MID_interest", 5, 0,  date_3) # 50.0%
        self._create_blink_file("RA1_0P_0N_new",0, 0,  date_4) # 0.0% (Rule A)
        self._create_blink_file("GEN_0_bal_new",5, 5,  date_4) # 0.0% (General)
        self._create_blink_file("RB1_0P_2N_new",0, 2,  date_4) # -28.57% (Rule B)
        self._create_blink_file("HIGH_interest",10,0,  date_2) # 66.67%
        self._create_blink_file("RA2_0P_0N_old",0, 0,  date_1) # 0.0% (Rule A)
        self._create_blink_file("GEN_0_bal_old",5, 5,  date_1) # 0.0% (General)
        self._create_blink_file("RB2_0P_2N_old",0, 2,  date_1) # -28.57% (Rule B)

        # Expected Order:
        # 1. HIGH_interest (66.67%)
        # 2. MID_interest (50.0%)
        # ---- 0.0% Interest Group (Sorted by sub-rules then date DESC) ----
        # 3. GEN_0_bal_new (General 0%, date_newest)
        # 4. GEN_0_bal_old (General 0%, date_oldest)
        #    (General 0% comes before Rule A as per logic: `is_b1_rule_a_criteria and not is_b2_rule_a_criteria` -> Rule A comes after)
        # 5. RA1_0P_0N_new (Rule A, date_newest)
        # 6. RA2_0P_0N_old (Rule A, date_oldest)
        #    (Rule A comes before Rule B because 0.0% interest > negative interest from Rule B)
        # ---- Negative Interest Group (Sorted by interest DESC, then Rule B logic, then date DESC) ----
        # 7. RB1_0P_2N_new (Rule B, -28.57%, 2N, date_newest)
        # 8. RB2_0P_2N_old (Rule B, -28.57%, 2N, date_oldest)
        #    (Rule B items with same interest: fewer negative votes first, then newer date first)
        # 9. RB3_0P_5N    (Rule B, -50.0%, 5N)
        # 10. NEG_interest (-56.25%)

        sorted_blinks = self.news_manager.get_all_blinks()
        sorted_ids = [b['id'] for b in sorted_blinks]

        # For debugging if the complex test fails:
        # for b in sorted_blinks:
        #     print(f"ID: {b['id']}, Interest: {b['interestPercentage']:.2f}%, P: {b['votes']['positive']}, N: {b['votes']['negative']}, Date: {b['publishedAt']}")

        expected_order = [
            "HIGH_interest", "MID_interest",
            "GEN_0_bal_new", "GEN_0_bal_old",
            "RA1_0P_0N_new", "RA2_0P_0N_old",
            "RB1_0P_2N_new", "RB2_0P_2N_old",
            "RB3_0P_5N", "NEG_interest"
        ]
        self.assertEqual(sorted_ids, expected_order)

# Keep TestApiVoting and its necessary imports (Flask, init_api)
from flask import Flask
from routes.api import init_api

class TestApiVoting(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        # Using a dedicated temporary directory for voting tests to avoid conflicts
        self.test_data_dir_voting = "temp_test_blinks_data_voting"
        self.actual_data_dir_blinks = os.path.join(self.test_data_dir_voting, 'blinks')
        self.articles_dir_voting = os.path.join(self.test_data_dir_voting, 'articles') # For article sync
        os.makedirs(self.actual_data_dir_blinks, exist_ok=True)
        os.makedirs(self.articles_dir_voting, exist_ok=True)

        # Configure the app to use this temporary data directory for News model instances
        self.app.config['APP_CONFIG'] = {'NEWS_MODEL_DATA_DIR': self.test_data_dir_voting}

        init_api(self.app) # Registers /api blueprint, including /blinks/.../vote

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()
        # Clean up the dedicated temporary directory for voting tests
        shutil.rmtree(self.test_data_dir_voting)


    def _create_test_blink_file(self, blink_id="test_vote_blink", positive_votes=0, negative_votes=0, published_at_str="2023-01-01T00:00:00Z"):
        blink_content = {
            "id": blink_id,
            "title": "Test Blink for Voting",
            "publishedAt": published_at_str,
            "votes": {"positive": positive_votes, "negative": negative_votes},
            "user_votes": {}, # Add user_votes for consistency
            "categories": ["test"], # Renamed from 'category'
            "content": "Test content",
            "points": ["Point 1"],
            "image": "test.png",
            "sources": [{"id":"s1", "name":"Source 1"}], # Ensure sources is a list of dicts
            "urls": [{"type":"main", "url":"http://example.com/test"}] # Ensure urls is a list of dicts
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
        return data.get("votes"), data.get("user_votes")


    def test_vote_first_positive_standard_backend(self):
        self._create_test_blink_file(positive_votes=0, negative_votes=0)
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'positive', 'userId': 'user1'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()['data']
        self.assertEqual(data['votes']['positive'], 1)
        self.assertEqual(data['votes']['negative'], 0)
        self.assertEqual(data['currentUserVoteStatus'], 'positive')

        file_votes, user_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['positive'], 1)
        self.assertEqual(user_votes['user1'], 'positive')

    def test_vote_first_negative_standard_backend(self):
        self._create_test_blink_file(positive_votes=0, negative_votes=0)
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'negative', 'userId': 'user1'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()['data']
        self.assertEqual(data['votes']['positive'], 0)
        self.assertEqual(data['votes']['negative'], 1)
        self.assertEqual(data['currentUserVoteStatus'], 'negative')

        file_votes, user_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['negative'], 1)
        self.assertEqual(user_votes['user1'], 'negative')

    def test_vote_change_positive_to_negative_standard_backend(self):
        # User1 already voted positive
        blink_path = os.path.join(self.actual_data_dir_blinks, "test_vote_blink.json")
        blink_content = {
            "id": "test_vote_blink", "title": "Test", "publishedAt": "2023-01-01T00:00:00Z",
            "votes": {"positive": 1, "negative": 0},
            "user_votes": {"user1": "positive"},
            "categories": ["test"], "content": "Test", "points": [], "image": "", "sources": [], "urls": []
        }
        with open(blink_path, 'w') as f: json.dump(blink_content, f)

        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'negative', 'userId': 'user1'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()['data']
        self.assertEqual(data['votes']['positive'], 0)
        self.assertEqual(data['votes']['negative'], 1)
        self.assertEqual(data['currentUserVoteStatus'], 'negative')

        file_votes, user_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['positive'], 0)
        self.assertEqual(file_votes['negative'], 1)
        self.assertEqual(user_votes['user1'], 'negative')

    def test_vote_remove_positive_vote_standard_backend(self):
        # User1 already voted positive, now sends positive again to remove vote (neutral)
        blink_path = os.path.join(self.actual_data_dir_blinks, "test_vote_blink.json")
        blink_content = {
            "id": "test_vote_blink", "title": "Test", "publishedAt": "2023-01-01T00:00:00Z",
            "votes": {"positive": 1, "negative": 0},
            "user_votes": {"user1": "positive"},
            "categories": ["test"], "content": "Test", "points": [], "image": "", "sources": [], "urls": []
        }
        with open(blink_path, 'w') as f: json.dump(blink_content, f)

        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'positive', 'userId': 'user1'})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()['data']
        self.assertEqual(data['votes']['positive'], 0) # Vote removed
        self.assertEqual(data['votes']['negative'], 0)
        self.assertIsNone(data['currentUserVoteStatus']) # Vote becomes neutral

        file_votes, user_votes = self._read_blink_file_votes()
        self.assertEqual(file_votes['positive'], 0)
        self.assertNotIn('user1', user_votes or {})


    def test_vote_on_nonexistent_blink(self):
        response = self.client.post('/api/blinks/nonexistent_blink_test_id/vote', json={'voteType': 'positive', 'userId': 'user1'})
        self.assertEqual(response.status_code, 404) # Assuming API returns 404
        data = response.get_json()
        self.assertIn('Blink not found', data['error'])

    def test_vote_with_invalid_vote_type(self):
        self._create_test_blink_file()
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'invalid', 'userId': 'user1'})
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Invalid voteType', data['error']) # Assuming 'positive' or 'negative'

    def test_vote_missing_user_id(self):
        self._create_test_blink_file()
        response = self.client.post('/api/blinks/test_vote_blink/vote', json={'voteType': 'positive'}) # Missing userId
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('Missing userId', data['error'])


if __name__ == '__main__':
    unittest.main()
