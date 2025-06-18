import unittest
# Import the refactored sort key function from routes.api
from routes.api import _sort_blinks_key as sort_key_under_test

# The local sort_key_for_testing function is removed.
# Tests will now use the imported sort_key_under_test.

class TestApiSorting(unittest.TestCase):

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

if __name__ == '__main__':
    unittest.main()
