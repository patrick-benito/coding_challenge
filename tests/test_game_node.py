import threading
import lcm
import time
from coding_challenge.agents import NotItAgent
import unittest
import coding_challenge.messages as messages

time_sleep_s = 1e-2

class TestGameNode(unittest.TestCase):
    def setUp(self):
        self.lc = lcm.LCM()
        self.agent = NotItAgent(0, 0, 10, 10)
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

if __name__ == "__main__":
    unittest.main()