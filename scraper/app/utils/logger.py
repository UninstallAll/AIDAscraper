"""
Logger utility module
"""
import logging
import os
from logging.handlers import RotatingFileHandler

def get_job_logger(job_id: int, level: int = logging.INFO) -> logging.Logger:
    """
    Get or create a logger for a specific job
    
    Args:
        job_id: Job ID
        level: Log level
        
    Returns:
        logging.Logger: Job logger
    """
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create job logger
    logger_name = f"job_{job_id}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    
    # Check if handlers already exist
    if not logger.handlers:
        # Create file handler
        log_file = os.path.join(logs_dir, f"job_{job_id}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        
        # Set formatter for handler
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger 