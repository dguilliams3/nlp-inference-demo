# NLP Inference Demo with BigQuery Integration

This repository demonstrates an end-to-end NLP inference pipeline that uses a Hugging Face sentiment analysis model (DistilBERT) to process review texts. It fetches raw reviews from Google BigQuery, performs sentiment analysis, and writes the results (with confidence scores, labels, and timestamps) back to BigQuery. The project is fully containerized using Docker and deployed on AWS Elastic Beanstalk with CI/CD managed by GitHub Actions.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Dockerization](#dockerization)
- [Local Testing](#local-testing)
- [Deployment to AWS](#deployment-to-aws)
- [CI/CD Pipeline](#cicd-pipeline)
- [Further Enhancements](#further-enhancements)
- [License](#license)

## Overview

- **NLP Inference:** Uses a Hugging Face sentiment analysis pipeline to classify review texts.
- **BigQuery Integration:** Fetches raw review data from a BigQuery table, processes it, and then writes sentiment results back.
- **Containerized Application:** Built with Docker (using `python:3.8-slim`) for easy deployment.
- **CI/CD:** Automated testing, building, and deployment via GitHub Actions.
- **Cloud Deployment:** Deployed to AWS Elastic Beanstalk.

## Project Structure

```
NLP_Inference_MVP/
│
├── config/
│   └── config.yaml          # Configuration file for model and BigQuery settings
│
├── src/
│   ├── bigquery_sentiment_pipeline.py  # Main module containing the pipeline logic
│   └── entrypoint.py        # Entry point that calls the pipeline function
│
├── credentials/             # Directory containing your Google Cloud credentials JSON
│   └── geometric-bay-454914-j5-0f652e53f7e1.json
│
├── .dockerignore            # Excludes local artifacts (e.g., venv, .git, __pycache__)
├── Dockerfile               # Instructions to build the Docker image
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Prerequisites

- **Docker:** Install [Docker Desktop](https://www.docker.com/get-started) on your machine.
- **Git:** Ensure Git is installed and configured.
- **AWS Account:** For deploying to AWS Elastic Beanstalk.
- **Google Cloud Project:** With BigQuery enabled and service account credentials generated.

## Configuration

- **config/config.yaml:**  
  Contains settings for the Hugging Face model, task, sample texts, and BigQuery table details.
  
- **Environment Variables:**  
  The Dockerfile sets:
  - `CONFIG_FILE` (if used by your code)
  - `GOOGLE_APPLICATION_CREDENTIALS` is set to `/app/credentials/geometric-bay-454914-j5-0f652e53f7e1.json`.

## Dockerization

The Dockerfile is designed to:
1. Use the lightweight `python:3.8-slim` image.
2. Install system dependencies and upgrade pip.
3. Copy `requirements.txt` and install all dependencies.
4. Copy your source code and configuration files.
5. Set necessary environment variables.
6. Run your application via the entrypoint script.

### Dockerfile Example

```dockerfile
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

# Define environment variables (can be overridden at runtime)
ENV CONFIG_FILE=config.yaml
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/geometric-bay-454914-j5-0f652e53f7e1.json

# Run the application using the entrypoint script with a task argument
CMD ["python", "src/entrypoint.py", "--task", "bigquery"]
```

## Local Testing

1. **Build the Docker Image:**

   ```bash
   docker build -t nlp_demo:latest .
   ```

2. **Run the Docker Container:**

   In PowerShell (using proper path escaping):

   ```powershell
   docker run -v "${PWD}\\credentials:/app/credentials" nlp_demo:latest
   ```

3. **Debugging:**

   To debug inside the container:

   ```bash
   docker run -it nlp_demo:latest /bin/bash
   ```

## Deployment to AWS

### Using AWS Elastic Beanstalk

1. **Install the EB CLI:**  
   Follow the instructions [here](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html).

2. **Initialize Your EB Application:**

   ```bash
   eb init --platform docker --region <your-region>
   ```

3. **Create an Environment:**

   ```bash
   eb create nlp-demo-env
   ```

4. **Deploy Your Application:**

   ```bash
   eb deploy
   ```

Elastic Beanstalk will create and manage the necessary resources.

## CI/CD Pipeline

The project uses GitHub Actions to automate the build, push, and deployment process.

### GitHub Actions Workflow

The workflow is defined in `.github/workflows/deploy.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      # (Optional) Remove or comment out tests if none are present:
      # - name: Run Tests
      #   run: |
      #     pytest

      - name: Build Docker Image
        run: docker build -t nlp_demo:latest .

      - name: Push Docker Image to Docker Hub
        env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
        run: |
          echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
          docker tag nlp_demo:latest dguilliams3/nlp_demo:latest
          docker push dguilliams3/nlp_demo:latest

      - name: Deploy to AWS Elastic Beanstalk
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_DEFAULT_REGION: ${{ secrets.AWS_DEFAULT_REGION }}
        run: |
          pip install awsebcli
          eb init -p docker nlp-demo --region $AWS_DEFAULT_REGION
          eb deploy nlp-demo-env
```

### Adding Secrets

1. In your GitHub repository, navigate to **Settings → Secrets and variables → Actions**.
2. Add these secrets:
   - `DOCKER_USERNAME`: `dguilliams3`
   - `DOCKER_PASSWORD`: your Docker Hub password or token
   - `AWS_ACCESS_KEY_ID`: Your AWS IAM access key
   - `AWS_SECRET_ACCESS_KEY`: Your AWS IAM secret key
   - `AWS_DEFAULT_REGION`: e.g., `us-west-2`

Every push to the `main` branch will trigger this workflow, automatically rebuilding your Docker image, pushing it to Docker Hub, and deploying it to AWS Elastic Beanstalk.

## Further Enhancements

- **Caching:**  
  Consider configuring Docker BuildKit caching to reduce rebuild times.

- **Long-Running Service:**  
  Right now, the application runs a one-shot process. To turn it into an API or persistent service, update your code and add a `HEALTHCHECK` to the Dockerfile.

- **Improved Logging and Modularity:**  
  Enhance your entrypoint and pipeline modules to support more tasks or better error handling.

- **Monitoring:**  
  Integrate AWS CloudWatch or another logging/monitoring tool to keep track of deployments and application behavior.