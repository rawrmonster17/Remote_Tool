# Use the Alpine 3.19.1 image
FROM alpine:3.19
# Set the working directory
WORKDIR /app
# Update packages and install python3, pip, libpq, libpq-dev, gcc, musl-dev and python3-dev
RUN apk update && \
    apk add --no-cache python3 py3-pip libpq libpq-dev gcc musl-dev python3-dev
# Install the Python dependencies after setting up the virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY Code/Server/requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
# Remove pip, libpq-dev, gcc, musl-dev and python3-dev
RUN apk del py3-pip libpq-dev gcc musl-dev python3-dev
RUN pip uninstall -y pip
# Copy the server script into the Docker image
COPY Code/Server/server.py /app/server.py
COPY Code/Server/my_database.py /app/my_database.py
# Run the server script when the container starts
CMD ["python3", "/app/server.py"]