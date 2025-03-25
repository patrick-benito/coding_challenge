from typing import Tuple, Dict, List, TypeAlias, TypedDict, Callable
import time
import random
from uuid import uuid4
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

from coding_challenge.node import Node
import coding_challenge.messages as messages

class AgentState(TypedDict):
    type: str
    x: int
    y: int

GameBoard: TypeAlias = List[List[List[str]]]
AgentId: TypeAlias = str
AgentsDict: TypeAlias = Dict[AgentId, AgentState]

class GameNode(Node):
    """
    A class to represent the game node which manages the game state and agents.
    """

    def __init__(self, num_agents: int, N: int, M: int, rate_hz: float = 1.0, on_update: Callable[[AgentsDict], None] = None):
        """
        Initialize the GameNode with the given parameters.

        Args:
            num_agents (int): The number of agents in the game.
            N (int): The number of rows in the grid.
            M (int): The number of columns in the grid.
            rate_hz (float): The rate in Hz at which the game state is updated.
            on_update (Callable[[GameBoard], None]): A callback function that is called when the game state is updated.
        """
        print("Creating GameNode")

        super().__init__()
        self.rate_hz = rate_hz
        self.num_agents = num_agents
        self.N = N
        self.M = M
        self.on_update = on_update

        self.agents: AgentsDict = {}
        self.game_board: List[List[List[str]]] = [
            [[] for _ in range(M)] for _ in range(N)
        ]  # Assume NxM game board

        self.num_it_agents = 0
        self.num_not_it_agents = 0
        self.has_game_started = False

    def agent_start_handler(self, _channel: str, data: bytes):
        msg = messages.agent_start_t.decode(data)

        if msg.agent_id in self.agents:
            return

        if msg.agent_type == "it":
            self.num_it_agents += 1
        elif msg.agent_type == "not_it":
            self.num_not_it_agents += 1
        else:
            print(f"Agent {msg.agent_id} has an invalid type.")
            return self.stop_node()

        self.agents[msg.agent_id] = {"type": msg.agent_type}

        self.set_agent_position(msg.agent_id, msg.x, msg.y)

        if len(self.agents) == self.num_agents:
            self.publish("game_start", messages.game_start_t())
            print("Game started")
            self.has_game_started = True

        if self.on_update is not None:
            self.on_update(self.agents)

    def agent_move_handler(self, _channel: str, data: bytes):
        msg = messages.agent_move_t.decode(data)
        if msg.agent_id not in self.agents:
            print(f"Agent {msg.agent_id} was never initialized.")
            return self.stop_node()

        agent_state = self.agents[msg.agent_id]
        self.set_agent_position(msg.agent_id, msg.x, msg.y)
        self.verify_interception(agent_state)
        self.verify_game_over()

    def agent_stop_handler(self, _channel: str, data: bytes):
        msg = messages.agent_stop_t.decode(data)

        if msg.agent_id not in self.agents:
            print(f"Agent {msg.agent_id} was never initialized.")
            self.stop_node()

        agent = self.agents[msg.agent_id]
        x, y = agent["x"], agent["y"]
        self.game_board[y][x].remove(msg.agent_id)

        if agent["type"] == "it":
            self.num_it_agents -= 1
        elif agent["type"] == "not_it":
            self.num_not_it_agents -= 1

        if self.num_not_it_agents == 0:
            print("All NotIt agents have been frozen")
            self.publish("game_stop", messages.game_stop_t())
            self.stop_node()

        del self.agents[msg.agent_id]

        if self.on_update is not None:
            self.on_update(self.agents)

    def verify_game_over(self):
        if len(self.agents) == 1:
            print("Game over")
            self.stop_node()

    def verify_interception(self, agent_state: AgentState):
        """
        Verify if an interception has occurred.

        Args:
            agent_state (AgentState): The state of the agent.
        """
        x, y = agent_state["x"], agent_state["y"]

        is_there_it = False

        for agent_id in self.game_board[y][x]:
            if self.agents[agent_id]["type"] == "it":
                is_there_it = True
                break

        if is_there_it:
            for agent_id in self.game_board[y][x]:
                if self.agents[agent_id]["type"] == "not_it":
                    msg = messages.game_freeze_agent_t()
                    msg.agent_id = agent_id
                    self.publish("game_freeze_agent", msg)

    def set_agent_position(self, agent_id: str, x: int, y: int):
        """
        Set the position of an agent on the game board.

        Args:
            agent_id (str): The ID of the agent.
            x (int): The x-coordinate of the agent's position.
            y (int): The y-coordinate of the agent's position.
        """
        agent = self.agents[agent_id]

        if "x" in agent and "y" in agent:
            self.game_board[agent["y"]][agent["x"]].remove(agent_id)

        if x < 0 or x >= self.M or y < 0 or y >= self.N:
            print(f"Agent {agent_id} is located out of bounds")
            return self.stop_node()

        self.game_board[y][x].append(agent_id)
        agent["x"] = x
        agent["y"] = y
        
        if self.on_update is not None:
            self.on_update(self.agents)

    def on_start(self):
        self.subscribe("agent_move", self.agent_move_handler)
        self.subscribe("agent_start", self.agent_start_handler)
        self.subscribe("agent_stop", self.agent_stop_handler)

    def run(self, timeout_s: float = 10.0):
        """
        Run the game loop.

        Args:
            timeout_s (float): The timeout in seconds for waiting for agents to subscribe.
        """
        start_time = time.time()
        while self.running:
            if not self.has_game_started and len(self.agents) < self.num_agents and time.time() - start_time > timeout_s:
                print("Timeout waiting for agents to subscribe")
                self.stop_node()
                return

            time.sleep(1.0 / self.rate_hz)

    def on_stop(self):
        msg = messages.game_stop_t()
        self.publish("game_stop", msg)
        print("Game stopped")


class GameNodeWithGUI(GameNode):
    """
    A class to represent the game node with a GUI for visualization.
    """
    def __init__(self, num_agents: int, N: int, M: int, rate_hz: float = 1.0):
        """
        Initialize the GameNode with the given parameters.

        Args:
            num_agents (int): The number of agents in the game.
            N (int): The number of rows in the grid.
            M (int): The number of columns in the grid.
            rate_hz (float): The rate in Hz at which the game state is updated.
        """
        super().__init__(num_agents, N, M, rate_hz)
        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(-1, self.M)
        self.ax.set_ylim(-1, self.N)
        
        self.scatter_not_it = self.ax.scatter([], [], c='red', s=100)
        self.scatter_it = self.ax.scatter([], [], c='blue', s=100)
        self.ax.legend(["NotIt", "It"])
        self.ax.set_aspect('equal')
        
        self.ax.set_xticks(np.arange(0, self.M, 1))
        self.ax.set_yticks(np.arange(0, self.N, 1))
        self.ax.grid(True)

    def update_plot(self, frame):
        """
        Update the plot with the new agent positions, triggered by Matplotlib animation.
        """
        if not self.running:
            plt.close(self.fig)
            return self.scatter_not_it, self.scatter_it

        try:
            agents = self.agents

            x_data = [agent["x"] for agent in agents.values() if agent["type"] == "not_it"]
            y_data = [agent["y"] for agent in agents.values() if agent["type"] == "not_it"]
            self.scatter_not_it.set_offsets(np.c_[x_data, y_data])

            x_data = [agent["x"] for agent in agents.values() if agent["type"] == "it"]
            y_data = [agent["y"] for agent in agents.values() if agent["type"] == "it"]
            self.scatter_it.set_offsets(np.c_[x_data, y_data])

        except Exception as e:
            plt.close(self.fig)
            return self.scatter_not_it, self.scatter_it

        return self.scatter_not_it, self.scatter_it

    def start_gui(self, timeout_s: float = 10.0):
        """
        Start the GUI for the game.
        
        Args:
            timeout_s (float): The timeout in seconds for waiting for the thread to start.
        """
        start_time = time.time()
        while not self.running:
            if self.num_agents and time.time() - start_time > timeout_s:
                print("Timeout waiting for thread to start")
                self.stop_node()
                return

            time.sleep(1.0 / self.rate_hz)

        self.ani = FuncAnimation(
            self.fig, self.update_plot, interval=100, blit=True, cache_frame_data=False
        )

        plt.show()
    
    def run(self, timeout_s: float = 10.0):
        """
        Run the GUI before the game loop.

        Args:
            timeout_s (float): The timeout in seconds for waiting for agents to subscribe.
        """
       
        self.start_gui()
        super().run(timeout_s)
        plt.close(self.fig)
