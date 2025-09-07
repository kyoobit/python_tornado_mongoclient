# podman build --tag tornado-mongoclient:v1 .
# podman run --rm --interactive --tty --name mongoclient tornado-mongoclient:v1 --help
# podman run --rm --detach --tty --publish 8892:8892/tcp --name mongoclient tornado-mongoclient:v1 --verbose
FROM docker.io/library/python:slim

# Set the working directory to /app
WORKDIR /app

# Add the Python files for the application
COPY *.py .

# Install the required Python modules
COPY requirements.txt .
RUN python3 -m pip install --requirement requirements.txt

# Add a user account
# No need to run as root in the container
RUN adduser --disabled-password --disabled-login --no-create-home mongoclient

# Run all future commands as mongoclient
USER mongoclient

# Set the command to run on start up
ENTRYPOINT ["python3", "/app/cli.py"]
CMD ["--help"]
