# src/nlp_demo.py

import os
import yaml
import torch
from transformers import pipeline
import numpy as np

def load_config(config_file: str):
    """Load configuration from a YAML file."""
    with open(config_file, "r") as file:
        return yaml.safe_load(file)

def analyze_sentiments(texts, task, model, device):
    """Analyze sentiment of multiple texts."""
    classifier = pipeline(task, model=model, device=device)
    results = classifier(texts)

    # Summary statistics
    sentiments = [res["label"] for res in results]
    scores = [res["score"] for res in results]

    return results, {
        "Positive Count": sentiments.count("POSITIVE"),
        "Negative Count": sentiments.count("NEGATIVE"),
        "Avg Confidence": np.mean(scores),
        "Max Confidence": np.max(scores),
        "Min Confidence": np.min(scores),
        "Strongest Sentiment": texts[np.argmax(scores)]
    }
    
def run_local_pipeline():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
    config = load_config(config_path)

    task = config.get("task")
    model = config.get("model")
    sample_texts = config.get("sample_texts")

    device = 0 if torch.cuda.is_available() else -1
    results, summary = analyze_sentiments(sample_texts, task, model, device)

    print("\nDetailed Sentiment Analysis:")
    for text, result in zip(sample_texts, results):
        print(f"- {text} → {result['label']} (Confidence: {result['score']:.4f})")

    print("\nSummary Statistics:")
    for key, value in summary.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    run_local_pipeline()
