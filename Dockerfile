# Use a slim Python image
FROM python:3.8-slim

# Set the working directory to /app inside the container
WORKDIR /app

# Install system dependencies and upgrade pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the entire project (includes .env, /src, /credentials, etc.)
COPY . .

# (Optional) Expose a port if you later add an API server (e.g., EXPOSE 8080)

# Define non-sensitive environment variables.
# The CONFIG_FILE environment variable points to your configuration file.
# Note: .env (with sensitive values) is located in the root and can be overridden or mounted externally.
ENV CONFIG_FILE=config/config.yaml

# (Optional) For added security in production, consider running as a non-root user.
# RUN adduser --disabled-password myuser
# USER myuser

# Run the application using the entrypoint script with a task argument.
# This launches the pipeline using the scripts in the /src directory.
CMD ["python", "src/entrypoint.py", "--task", "bigquery"]
