import unittest
from coding_challenge.game import process_initial_positions

class TestProcessInitialPositions(unittest.TestCase):
    def test_valid_positions(self):
        args_positions = [0, 0, 1, 1, 2, 2, 3, 3]
        num_not_it = 3
        num_it = 1
        N = 5
        M = 5
        it_positions, not_it_positions = process_initial_positions(args_positions, N, M, num_not_it, num_it)
        self.assertEqual(it_positions, [(3, 3)])
        self.assertEqual(not_it_positions, [(0, 0), (1, 1), (2, 2)])

    def test_invalid_positions_length(self):
        args_positions = [0, 0, 1, 1, 2, 2, 3]
        num_not_it = 3
        num_it = 1
        N = 5
        M = 5
        with self.assertRaises(ValueError):
            process_initial_positions(args_positions, N, M, num_not_it, num_it)

    def test_mismatch_positions_and_agents(self):
        args_positions = [0, 0, 1, 1, 2, 2]
        num_not_it = 3
        num_it = 1
        N = 5
        M = 5
        with self.assertRaises(ValueError):
            process_initial_positions(args_positions, N, M, num_not_it, num_it)

    def test_out_of_bounds_positions(self):
        args_positions = [0, 0, 1, 1, 2, 2, 5, 5]
        num_not_it = 3
        num_it = 1
        N = 5
        M = 5
        with self.assertRaises(ValueError):
            process_initial_positions(args_positions, N, M, num_not_it, num_it)

if __name__ == "__main__":
    unittest.main()
