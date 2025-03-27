import argparse
from bigquery_sentiment_pipeline import run_bigquery_pipeline
from local_demo_nlp_sentiment_pipeline import run_local_pipeline

def main():
    parser = argparse.ArgumentParser(description="Run NLP pipeline tasks.")
    parser.add_argument(
        '--task', 
        type=str, 
        default='bigquery', 
        help='Task to run. Default is "bigquery".'
    )
    args = parser.parse_args()
    
    if args.task == 'bigquery':
        run_bigquery_pipeline()
    elif args.task == 'local':
        run_local_pipeline()
    else:
        print(f"Task '{args.task}' not recognized. Running default task.")
        run_bigquery_pipeline()

if __name__ == "__main__":
    main()