# Use an official Python runtime as a parent image
FROM python:3.10.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the necessary files into the container
COPY http_server.py /app/
COPY custom_functions.py /app/
COPY requirements.txt /app/

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the http_server.py file
CMD ["python", "http_server.py"]