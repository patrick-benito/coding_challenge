from typing import Tuple, Optional
import time
import random
from names_generator import generate_name

from coding_challenge.node import Node
import coding_challenge.messages as messages


class Agent(Node):
    """
    Base class for all agents.
    """

    def __init__(
        self,
        agent_type: str,
        initial_position_x: int,
        initial_position_y: int,
        N: int,
        M: int,
        rate_hz: float,
    ):
        """
        Initialize the agent with the given parameters.
        Args:
            agent_type (str): The type of the agent.
            initial_position_x (int): The initial x-coordinate of the agent.
            initial_position_y (int): The initial y-coordinate of the agent.
            N (int): Number of rows in the grid.
            M (int): Number of columns in the grid.
            rate_hz (float): The rate in Hz at which the agent operates.
        """
        super().__init__()

        self.agent_id = generate_name()
        self.agent_type = agent_type
        self.current_position_x = initial_position_x
        self.current_position_y = initial_position_y
        self.rate_hz = rate_hz

        self.N = N
        self.M = M

        self._is_game_running = False
        self.game_state = None

        print(
            f"Agent {self.agent_id} of type {self.agent_type} created at position ({initial_position_x}, {initial_position_y})"
        )

    def game_start_handler(self, _channel, data: bytes):
        self._is_game_running = True

    def game_stop_handler(self, _channel, data: bytes):
        self._is_game_running = False
        self.running = False

    def game_freeze_agent_handler(self, _channel, data: bytes):
        msg = messages.game_freeze_agent_t.decode(data)
        if msg.agent_id == self.agent_id:
            self._is_game_running = False
            self.running = False
            print(f"Agent {self.agent_id} has been frozen")

    def game_state_handler(self, _channel, data: bytes):
        msg = messages.game_state_t.decode(data)
        self.game_state = msg.game_state

    def send_agent_start(self):
        msg = messages.agent_start_t()
        msg.agent_id = self.agent_id
        msg.agent_type = self.agent_type
        msg.x = int(self.current_position_x)
        msg.y = int(self.current_position_y)
        
        self.publish("agent_start", msg)

    def on_start(self):
        self.subscribe("game_start", self.game_start_handler)
        self.subscribe("game_stop", self.game_stop_handler)
        self.subscribe("game_freeze_agent", self.game_freeze_agent_handler)
        self.subscribe("game_state", self.game_state_handler)
    
    def run(self):
        while self.running:
            start_time = time.time()

            if self._is_game_running:
                self.step()
            else:
                print(f"Agent {self.agent_id} is waiting for the game to start")
                self.send_agent_start()

            elapsed_time = time.time() - start_time
            time.sleep(max(0, 1.0 / self.rate_hz - elapsed_time))

    def on_stop(self):
        msg = messages.agent_stop_t()
        msg.agent_id = self.agent_id
        self.publish("agent_stop", msg)

    def move(self, x: int, y: int):
        """
        Move the agent to the given position.
        Args:
            x (int): The x-coordinate of the new position.
            y (int): The y-coordinate of the new position.
        """
        msg = messages.agent_move_t()
        msg.agent_id = self.agent_id
        msg.x = int(x)
        msg.y = int(y)
        self.current_position_x = x
        self.current_position_y = y

        self.publish("agent_move", msg)

    def get_current_position(self) -> Tuple[int, int]:
        """
        Get the current position of the agent.
        Returns:
            Tuple[int, int]: The x and y coordinates of the agent.
        """
        return self.current_position_x, self.current_position_y

    def step(self):
        """
        Perform one step of the agent's logic.
        """
        raise NotImplementedError


class NotItAgent(Agent):
    """
    NotItAgent that moves randomly.
    """

    def __init__(
        self,
        initial_position_x: int,
        initial_position_y: int,
        N: int,
        M: int,
        rate_hz: Optional[float] = 1.0,
    ):
        """
        Initialize the agent with the given parameters.
        Args:
            initial_position_x (int): The initial x-coordinate of the agent.
            initial_position_y (int): The initial y-coordinate of the agent.
            N (int): Number of rows in the grid.
            M (int): Number of columns in the grid.
            rate_hz (Optional[float]): The rate in Hz at which the agent operates. Defaults to 1.0 Hz.
        """
        super().__init__(
            "not_it", initial_position_x, initial_position_y, N, M, rate_hz
        )

    def get_random_adjacent_cell(self, x: int, y: int) -> Tuple[int, int]:
        """
        Get a random adjacent cell to the given cell.
        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.
        Returns:
            Tuple[int, int]: The x and y coordinates of the adjacent cell.
        """
        x_action = random.choice([-1, 0, 1])
        y_action = random.choice([-1, 0, 1])

        new_x = x + x_action
        new_y = y + y_action

        if new_x < 0 or new_x >= self.M or new_y < 0 or new_y >= self.N:
            return self.get_random_adjacent_cell(x, y)

        return new_x, new_y

    def step(self):
        """
        Move to a random adjacent cell in the grid.
        """
        x, y = self.get_current_position()
        new_x, new_y = self.get_random_adjacent_cell(x, y)
        self.move(new_x, new_y)


class ItAgent(Agent):
    """
    ItAgent that moves towards the closest agent.
    """

    def __init__(
        self,
        initial_position_x: int,
        initial_position_y: int,
        N: int,
        M: int,
        rate_hz: Optional[
            float
        ] = 2.0,  # Currently set to 2 Hz, as described in the challenge
    ):
        """
        Initialize the agent with the given parameters.
        Args:
            initial_position_x (int): The initial x-coordinate of the agent.
            initial_position_y (int): The initial y-coordinate of the agent.
            N (int): Number of rows in the grid.
            M (int): Number of columns in the grid.
            rate_hz (Optional[float]): The rate in Hz at which the agent operates. Defaults to 2 Hz.
        """
        super().__init__("it", initial_position_x, initial_position_y, N, M, rate_hz)
        self.target = None
        self.distance_squared_to_target = float("inf")
        self.target_id = None

    def on_start(self):
        """
        Subscribe to the agent_move and agent_stop messages.
        """
        self.subscribe("agent_move", self.agent_move_handler)
        self.subscribe("game_freeze_agent", self.agent_stop_handler)
        super().on_start()

    def agent_stop_handler(self, _channel, data: bytes):
        """
        Handle the agent_stop message. Reset the target if the target agent is out of the game.
        """
        msg = messages.game_freeze_agent_t.decode(data)
        if msg.agent_id == self.target_id:
            self.target_id = None
            self.target = None
            self.distance_squared_to_target = float("inf")

    def agent_move_handler(self, _channel, data: bytes):
        """
        Handle the agent_move message. Update the current target based on the closest agent.
        """

        msg = messages.agent_move_t.decode(data)
        if msg.agent_id == self.agent_id:
            return

        distance_squared = self.get_squared_distance_to_position(msg.x, msg.y)
        if (
            msg.agent_id == self.target_id
            or distance_squared < self.distance_squared_to_target
        ):
            self.target_id = msg.agent_id
            self.distance_squared_to_target = distance_squared
            self.target = (msg.x, msg.y)
            return

    def get_squared_distance_to_position(self, x: int, y: int) -> float:
        """
        Get the distance to a position.
        """
        return (self.current_position_x - x) ** 2 + (self.current_position_y - y) ** 2

    def get_action(self) -> Tuple[int, int]:
        """
        Get the action to move towards the target.
        Returns:
            Tuple[int, int]: The x and y coordinates of the resulting action.
        """
        x, y = self.get_current_position()
        target_x, target_y = self.target

        # Move towards the target, clipping the action to [-1, 1]
        x_action = max(-1, min(1, target_x - x))
        y_action = max(-1, min(1, target_y - y))

        new_x, new_y = x + x_action, y + y_action

        if new_x < 0 or new_x >= self.M or new_y < 0 or new_y >= self.N:
            return x, y

        return new_x, new_y

    def step(self):
        """ "
        Move towards the target agent if there is one.
        """
        if self.target is not None:
            new_x, new_y = self.get_action()
            self.move(new_x, new_y)
