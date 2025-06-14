"""
AIDA Scraper Celery Worker Startup Script
"""
import logging
import os
import sys
from celery import Celery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("worker.log")
    ]
)
logger = logging.getLogger(__name__)

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Celery app from tasks module
from app.tasks.celery_app import celery_app

def start_worker():
    """
    Start the Celery worker
    """
    logger.info("Starting Celery worker")
    
    # Set worker arguments
    worker_args = [
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--pool=threads',
        '--hostname=worker@%h'
    ]
    
    # Start worker
    celery_app.worker_main(worker_args)

if __name__ == "__main__":
    start_worker() 