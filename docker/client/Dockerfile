# Use the Python 3.8 image
FROM python:3.8

# Set the working directory
WORKDIR /app

# Copy the Python dependencies
COPY Code/client/requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the agent script into the Docker image
COPY Code/client/agent.py /app/agent.py

# Run the agent script when the container starts
CMD ["python", "/app/agent.py"]