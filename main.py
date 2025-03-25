# game.py
import argparse

from coding_challenge.game import setup_game, process_initial_positions

def parse_args():
    parser = argparse.ArgumentParser(description="Distributed Freeze Tag Game")
    parser.add_argument("--width", type=int, required=True, help="Width of the game board")
    parser.add_argument("--height", type=int, required=True, help="Height of the game board")
    parser.add_argument("--num-not-it", type=int, required=True, help="Number of NotIt agents")
    parser.add_argument("--positions", nargs='+', type=int, required=True, help="Initial positions of agents in the format: x1 y1 x2 y2 ... x_it y_it")
    return parser.parse_args()

def main(args):
    """
    Main function to parse arguments and launch the required nodes.
    """
    it_agent_position, not_it_agent_positions = process_initial_positions(args.positions, args.height, args.width, args.num_not_it)
    setup_game(it_agent_position, not_it_agent_positions, args.height, args.width)
    
if __name__ == "__main__":
    main(parse_args())
