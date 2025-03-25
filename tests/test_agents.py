import threading
import lcm
import time
from coding_challenge.agents import NotItAgent, ItAgent
import unittest
import coding_challenge.messages as messages
import random

random.seed(0) # set seed for reproducibility

time_sleep_s = 1e-2

class TestNotItAgent(unittest.TestCase):
    def setUp(self):
        self.N = 10
        self.M = 10
        self.lc = lcm.LCM()
        self.agent = NotItAgent(0, 0, self.N, self.M)
        self.thread = threading.Thread(target=self.agent.launch_node)
        self.thread.start()
        time.sleep(time_sleep_s)

    def tearDown(self):
        self.agent.stop_node()
        self.thread.join()

    def test_game_start(self):
        msg = messages.game_start_t()
        self.lc.publish("game_start", msg.encode())
        time.sleep(time_sleep_s)
        self.assertTrue(self.agent._is_game_running)

    def test_game_stop(self):
        self.test_game_start()

        stop_msg = messages.game_stop_t()
        self.lc.publish("game_stop", stop_msg.encode())
        time.sleep(time_sleep_s)
        self.assertFalse(self.agent._is_game_running)
        self.assertFalse(self.agent.running)

    def test_game_freeze_agent(self):
        self.test_game_start()

        msg = messages.game_freeze_agent_t()
        msg.agent_id = self.agent.agent_id
        self.lc.publish("game_freeze_agent", msg.encode())
        time.sleep(time_sleep_s)
        self.assertFalse(self.agent.running)
    
    def test_get_random_adjacent_cell(self):
        for _ in range(10):
            cell = self.agent.get_random_adjacent_cell(self.N, self.M)
            self.assertGreaterEqual(cell[0], 0)
            self.assertLess(cell[0], self.N)
            self.assertGreaterEqual(cell[1], 0)
            self.assertLess(cell[1], self.M)

class TestItAgent(unittest.TestCase):
    def setUp(self):
        self.N = 10
        self.M = 10
        self.lc = lcm.LCM()
        self.agent = ItAgent(0, 0, self.N, self.M)
        self.thread = threading.Thread(target=self.agent.launch_node)
        self.thread.start()
        time.sleep(time_sleep_s)

    def tearDown(self):
        self.agent.stop_node()
        self.thread.join()

    def test_game_start(self):
        msg = messages.game_start_t()
        self.lc.publish("game_start", msg.encode())
        time.sleep(time_sleep_s)
        self.assertTrue(self.agent._is_game_running)

    def test_game_stop(self):
        self.test_game_start()

        stop_msg = messages.game_stop_t()
        self.lc.publish("game_stop", stop_msg.encode())
        time.sleep(time_sleep_s)
        self.assertFalse(self.agent._is_game_running)
        self.assertFalse(self.agent.running)

    def test_agent_move_handler(self):
        self.test_game_start()

        msg = messages.agent_move_t()
        msg.agent_id = "some_id"
        msg.x = 5
        msg.y = 5
        self.lc.publish("agent_move", msg.encode())
        time.sleep(time_sleep_s)
        target = self.agent.target
        self.assertIsNotNone(target)
        self.assertEqual(target[0], 5)
        self.assertEqual(target[1], 5)

    def test_get_action(self):
        self.agent.target = (5, 5)
        self.agent.current_position_x = self.N
        self.agent.current_position_y = self.M
        action = self.agent.get_action()


if __name__ == "__main__":
    unittest.main()