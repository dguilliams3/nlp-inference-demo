import os
import yaml
import torch
import numpy as np
from transformers import pipeline
from typing import Any, Dict, List, Tuple
from logging_config import setup_logging

# Intiiate Logging
logger = setup_logging()

def load_config(config_file: str) -> Dict[str, Any]:
    """Load configuration from a YAML file."""
    with open(config_file, "r") as file:
        config = yaml.safe_load(file)
    return config

def analyze_sentiments(texts: List[str], task: str, model: str, device: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Analyze sentiment of multiple texts using the specified model."""
    classifier = pipeline(task, model=model, device=device)
    results = classifier(texts)

    sentiments = [res["label"] for res in results]
    scores = [res["score"] for res in results]

    summary = {
        "Positive Count": sentiments.count("POSITIVE"),
        "Negative Count": sentiments.count("NEGATIVE"),
        "Avg Confidence": float(np.mean(scores)),
        "Max Confidence": float(np.max(scores)),
        "Min Confidence": float(np.min(scores)),
        "Strongest Sentiment": texts[np.argmax(scores)]
    }

    return results, summary

def run_local_pipeline() -> None:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    config = load_config(config_path)

    task = config.get("task")
    model = config.get("model")
    sample_texts = config.get("sample_texts")

    device = 0 if torch.cuda.is_available() else -1
    logger.info(f"Using device: {device}")
    
    results, summary = analyze_sentiments(sample_texts, task, model, device)

    logger.info("Detailed Sentiment Analysis:")
    for text, result in zip(sample_texts, results):
        logger.info("- %s -> %s (Confidence: %.4f)", text, result['label'], result['score'])

    logger.info("Summary Statistics:")
    for key, value in summary.items():
        logger.info("%s: %s", key, value)

if __name__ == "__main__":
    run_local_pipeline()
