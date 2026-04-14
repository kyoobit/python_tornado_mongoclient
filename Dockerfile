# podman build --tag tornado-mongoclient:v1 .
# podman run --rm --interactive --tty --name mongoclient tornado-mongoclient:v1 --help
# podman run --rm --detach --tty --publish 8892:8892/tcp --name mongoclient tornado-mongoclient:v1 --verbose
FROM docker.io/library/python:slim

# Set the working directory to /app
WORKDIR /app

# Install uv using the official installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Add the Python files for the application
COPY pyproject.toml uv.lock README.md *.py ./

# Set uv to use the .cache directory
ENV UV_CACHE_DIR=/app/.cache/uv

# Install Python dependencies
RUN uv sync --frozen --no-cache

# Add a user account
# No need to run as root in the container
RUN adduser --disabled-password --disabled-login --no-create-home mongoclient

# No need to run as root in the container
USER mongoclient

# Set the command to run on start up
ENTRYPOINT ["uv", "run",  "/app/cli.py"]
CMD ["--help"]
