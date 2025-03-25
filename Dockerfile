FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt update && apt install -y make libglib2.0-0
RUN apt-get update && apt-get install python3-tk -y
ADD ./ /app
WORKDIR /app

RUN make build
RUN uv build 

ENTRYPOINT ["uv", "run", "main.py"]

