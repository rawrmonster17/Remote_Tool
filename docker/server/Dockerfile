# Use the Alpine 3.19.1 image
FROM alpine:3.19.1

# Set the working directory
WORKDIR /app

# Update packages and install python3 and pip
RUN apk update && \
    apk add --no-cache python3 py3-pip

# Install the Python dependencies
COPY Code/Server/requirements.txt /app/
RUN pip install --no-cache-dir --break-system-packages -r /app/requirements.txt

# Remove pip
RUN apk del py3-pip

# Copy the server script into the Docker image
COPY Code/Server/server.py /app/server.py

# Run the server script when the container starts
CMD ["python3", "/app/server.py"]