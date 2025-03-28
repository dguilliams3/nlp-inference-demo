import os
import logging
import sys

def setup_logging(log_name="pipeline.log"):
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, log_name)

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")

    # Fix the console logging error on Windows (cp1252 can't print Unicode arrows)
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    stream_handler.setStream(open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            file_handler,
            stream_handler
        ]
    )
    return logging.getLogger(__name__)
