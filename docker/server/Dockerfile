# Use the Alpine 3.19.1 image
FROM alpine:3.19
# Set the working directory
WORKDIR /app
# Update packages and install python3, pip, libpq, libpq-dev, gcc, musl-dev and python3-dev
RUN apk add --no-cache tzdata
ENV TZ=America/Chicago
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN apk update && \
    apk add --no-cache python3 py3-pip libpq libpq-dev gcc musl-dev python3-dev
# Install the Python dependencies
COPY Code/Server/requirements.txt /app/
RUN pip install --no-cache-dir --break-system-packages -r /app/requirements.txt
# Remove pip, libpq-dev, gcc, musl-dev and python3-dev
RUN apk del py3-pip libpq-dev gcc musl-dev python3-dev
# Copy the server script into the Docker image
COPY Code/Server/server.py /app/server.py
COPY Code/Server/my_database.py /app/my_database.py
# Run the server script when the container starts
CMD ["python3", "/app/server.py"]