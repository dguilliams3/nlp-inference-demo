# Use a slim Python image
FROM python:3.8-slim

# Set a working directory
WORKDIR /app

# Install system dependencies and upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code and configuration
COPY . .

# (Optional) Expose a port if you later add an API server (e.g., EXPOSE 8080)

# Define non-sensitive environment variables; sensitive ones will be provided externally
ENV CONFIG_FILE=config.yaml

# Run the application using the entrypoint script with a task argument
CMD ["python", "src/entrypoint.py", "--task", "bigquery"]