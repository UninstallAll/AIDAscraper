#!/usr/bin/env python
"""
AIDA Scraper Startup Script
"""
import argparse
import logging
import sys
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scraper.log")
    ]
)
logger = logging.getLogger(__name__)

# Import after logging is configured
from app.db.database import Base, engine

def initialize_database():
    """
    Initialize the database by creating all tables
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        sys.exit(1)


def start_api_server(host="0.0.0.0", port=8000, reload=True):
    """
    Start the FastAPI server
    
    Args:
        host (str): Host to bind the server to
        port (int): Port to bind the server to
        reload (bool): Whether to enable auto-reload
    """
    logger.info(f"Starting API server at http://{host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


def main():
    """
    Main function to parse arguments and execute commands
    """
    parser = argparse.ArgumentParser(description="AIDA Scraper Startup Script")
    parser.add_argument("--init-db", action="store_true", help="Initialize the database")
    parser.add_argument("--start-api", action="store_true", help="Start the API server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the API server to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind the API server to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload for the API server")
    
    args = parser.parse_args()
    
    if args.init_db:
        initialize_database()
    
    if args.start_api:
        start_api_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    
    if not (args.init_db or args.start_api):
        parser.print_help()


if __name__ == "__main__":
    main() 