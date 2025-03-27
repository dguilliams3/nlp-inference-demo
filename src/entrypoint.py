import argparse
import logging
from bigquery_sentiment_pipeline import run_bigquery_pipeline
from local_demo_nlp_sentiment_pipeline import run_local_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Run NLP pipeline tasks.")
    parser.add_argument(
        '--task', 
        type=str, 
        default='bigquery', 
        help='Task to run. Options: "bigquery", "local".'
    )
    args = parser.parse_args()
    
    if args.task == 'bigquery':
        run_bigquery_pipeline()
    elif args.task == 'local':
        run_local_pipeline()
    else:
        logger.warning("Task '%s' not recognized. Running default task (bigquery).", args.task)
        run_bigquery_pipeline()

if __name__ == "__main__":
    main()
