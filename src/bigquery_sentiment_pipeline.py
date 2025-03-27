import os
import yaml
import random
import datetime
import torch
import logging
from transformers import pipeline
from google.cloud import bigquery
from typing import Any, Dict, List

# Setup basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config

def load_bigquery_client() -> bigquery.Client:
    """
    Create and return a BigQuery client.
    Expects GOOGLE_APPLICATION_CREDENTIALS to be set to the path of a service account key JSON.
    """
    try:
        client = bigquery.Client()
        logger.info("BigQuery client loaded successfully.")
        return client
    except Exception as e:
        logger.error("Failed to create BigQuery client: %s", e)
        raise

def fetch_reviews(client: bigquery.Client, dataset: str, reviews_table: str, limit: int = 5) -> List[Any]:
    """
    Fetch a limited number of reviews from the nlp_demo_reviews table.
    
    Parameters:
        client (bigquery.Client): Authenticated BigQuery client.
        dataset (str): Name of the dataset (e.g., 'distilbert_demo').
        reviews_table (str): Name of the reviews table (e.g., 'nlp_demo_reviews').
        limit (int): Number of rows to fetch.

    Returns:
        List of rows, each row with review_id and review_text fields.
    """
    query = f"""
        SELECT review_id, review_text
        FROM `{client.project}.{dataset}.{reviews_table}`
        LIMIT {limit}
    """
    try:
        query_job = client.query(query)
        results = list(query_job.result())
        logger.info("Fetched %d reviews from BigQuery.", len(results))
        return results
    except Exception as e:
        logger.error("Error fetching reviews: %s", e)
        raise

def insert_sentiment_results(client: bigquery.Client, dataset: str, sentiment_table: str, rows: List[Dict[str, Any]]) -> None:
    """
    Insert sentiment analysis results into the nlp_demo_sentiments table.
    
    Parameters:
        client (bigquery.Client): Authenticated BigQuery client.
        dataset (str): Name of the dataset.
        sentiment_table (str): Name of the sentiments table (e.g., 'nlp_demo_sentiments').
        rows (List[Dict]): Each dict must match the schema columns:
                           sentiment_id, review_id, sentiment_label, sentiment_score, model_name, processed_at
    """
    table_ref = client.dataset(dataset).table(sentiment_table)
    try:
        errors = client.insert_rows_json(table_ref, rows)
        if errors:
            logger.error("Encountered errors while inserting rows: %s", errors)
        else:
            logger.info("Data inserted successfully into %s.", sentiment_table)
    except Exception as e:
        logger.error("Exception during data insertion: %s", e)
        raise

def run_bigquery_pipeline() -> None:
    """
    Execute the BigQuery sentiment analysis pipeline:
      - Load configuration.
      - Connect to BigQuery.
      - Fetch reviews.
      - Run sentiment analysis.
      - Insert results back into BigQuery.
    """
    # Load configuration from config.yaml
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    config = load_config(config_path)
    bq_config = config.get("bigquery")

    client = load_bigquery_client()

    # Fetch reviews from BigQuery
    reviews = fetch_reviews(
        client,
        bq_config["dataset"],         # e.g. 'distilbert_demo'
        bq_config["reviews_table"],     # e.g. 'nlp_demo_reviews'
        limit=5
    )

    # Set up the sentiment analysis pipeline using the real model
    task = config.get("task")
    model = config.get("model")
    device = 0 if torch.cuda.is_available() else -1

    # Process all review texts at once
    review_texts = [row.review_text for row in reviews]
    classifier = pipeline(task, model=model, device=device)
    results = classifier(review_texts)

    sentiment_rows = []
    for idx, row in enumerate(reviews):
        review_id = row.review_id
        result = results[idx]
        sentiment = result["label"]
        score = result["score"]

        # Generate a random sentiment_id for demonstration purposes.
        sentiment_id = random.randint(100000, 999999)
        processed_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

        sentiment_rows.append({
            "sentiment_id": sentiment_id,
            "review_id": review_id,
            "sentiment_label": sentiment,
            "sentiment_score": score,
            "model_name": model,
            "processed_at": processed_at
        })

        logger.info("Processed review %s: %s (score=%.4f)", review_id, sentiment, score)

    insert_sentiment_results(
        client,
        bq_config["dataset"],
        bq_config["sentiment_table"],
        sentiment_rows
    )

if __name__ == "__main__":
    run_bigquery_pipeline()
