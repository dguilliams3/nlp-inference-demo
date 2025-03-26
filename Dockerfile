# Use a slim Python image
FROM python:3.8-slim

# Set a working directory
WORKDIR /app

# Install system dependencies (if any) and upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code and configuration
COPY . .

# Expose any required port (if our app is serving an API, for example)
# EXPOSE 8080

# Define environment variables (these can be overridden at runtime)
ENV CONFIG_FILE=config.yaml
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/<credentials file name>.json

# Run the application
# Here, we assume that we are running the BigQuery integration script
CMD ["python", "src/entrypoint.py", "--task", "bigquery"]
