# Use Ubuntu 22.04 as the base image
FROM ubuntu:22.04

# Set the working directory in the container
WORKDIR /app

# Update packages and install python3 and pip
RUN apt-get update -y && \
    apt-get install -y python3-pip && \
    pip3 install --upgrade pip

# Copy the requirements.txt file into the Docker image
COPY Code/Server/requirements.txt /app/requirements.txt

# Install the Python dependencies
RUN pip3 install -r /app/requirements.txt

# Run the server script when the container starts
CMD ["python3", "/app/server.py"]