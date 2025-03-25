# Pivot Robotics Coding Challenge

This project is a coding challenge for Pivot Robotics. It includes a game simulation with agents that move on a grid. The project uses `uv`, a fast python package manager, for building and running the application.

## Docker

To get started with the project, follow these steps:

1. **Build the Docker image**:
    ```sh
    sudo docker build -t pivot_robotics_challenge .
    ```

2. **Run the Docker container**:
    ```sh
    sudo docker run -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix/:/tmp/.X11-unix pivot_robotics_challenge --width 10 --height 5 --num-not-it 2 --positions 3 4 9 1 0 0
    ```

## Building and running from source

To build the project from source, ensure you have the following dependencies installed:
- `python >= 3.12`
- `uv`
- `make`

Then, build the package with:
```sh
make build
```

Run the game with:
```sh
uv run main.py --width 20 --height 15 --num-not-it 2 --positions 3 5 10 12 0 0
```

## Future Improvements

The following improvements are suggested for the next version of this project:
- Use a custom logger to log agent and game steps.
- Define custom exceptions for the game.
