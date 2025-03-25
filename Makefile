build:
	cd src/ && uv run lcm-gen -p coding_challenge/*.lcm
	uv build
test:
	uv run pytest -s -v tests
run:
	uv run main.py --width 20 --height 15 --num-not-it 2 --positions 3 5 10 12 0 0

run-long:
	uv run main.py --width 10 --height 10 --num-not-it 6 --positions 0 0 0 0 0 1 1 1 1 1 1 1 9 9