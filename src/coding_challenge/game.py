# game.py
from typing import List, Tuple
import multiprocessing
import logging

from coding_challenge.agents import ItAgent, NotItAgent, Node
from coding_challenge.game_node import GameNodeWithGUI

def process_initial_positions(
    args_positions: List[int], N: int, M: int, num_not_it: int, num_it: int = 1
) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
    """
    Process the initial positions of agents.

    Args:
        args_positions (List[int]): List of positions as integers.
        N (int): Number of rows in the grid.
        M (int): Number of columns in the grid.
        num_not_it (int): Number of NotIt agents.
        num_it (int): Number of It agents.

    Returns:
        Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]: Positions of It and NotIt agents.
    """
    expected_num_agents = num_not_it + num_it

    if len(args_positions) % 2 != 0:
        raise ValueError("Number of positions must be pairs of x and y coordinates")

    if len(args_positions) != 2 * expected_num_agents:
        raise ValueError(
            f"Number of positions does not match the number of agents. Expected {expected_num_agents}, got {len(args_positions) // 2}"
        )

    not_it_agent_positions = []
    it_agent_positions = []

    for i in range(num_not_it):
        x, y = args_positions[2 * i], args_positions[2 * i + 1]
        if x < 0 or x >= M or y < 0 or y >= N:
            raise ValueError(f"Agents are located out of bounds")

        not_it_agent_positions.append((x, y))

    for i in range(num_not_it, num_not_it + num_it):
        x, y = args_positions[2 * i], args_positions[2 * i + 1]
        if x < 0 or x >= M or y < 0 or y >= N:
            raise ValueError(f"Agents are located out of bounds")

        it_agent_positions.append((x, y))

    return it_agent_positions, not_it_agent_positions


def launch_node(node: Node):
    """
    Helper function to launch a node in a separate process.
    """
    node.launch_node()


def setup_game(
    it_agent_positions: List[Tuple[int, int]],
    not_it_agent_positions: List[Tuple[int, int]],
    N: int,
    M: int,
):
    """
    Set up and launch the game with the specified agents and grid size.

    Args:
        it_agent_positions (List[Tuple[int, int]]): Positions of It agents.
        not_it_agent_positions (List[Tuple[int, int]]): Positions of NotIt agents.
        N (int): Number of rows in the grid.
        M (int): Number of columns in the grid.
    """
    num_agents = len(not_it_agent_positions) + len(it_agent_positions)
    nodes = []

    game_node = GameNodeWithGUI(num_agents, N, M)

    # Launch It agents
    for x, y in it_agent_positions:
        nodes.append(ItAgent(x, y, N, M))

    # Launch NotIt agents
    for x, y in not_it_agent_positions:
        nodes.append(NotItAgent(x, y, N, M))

    with multiprocessing.Pool(processes=len(nodes)) as pool:
        pool.map_async(launch_node, nodes)

        # Launch the game node
        game_node.launch_node()
            