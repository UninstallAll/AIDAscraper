"""
Log handler module for spiders
"""
import logging
import os
from logging import LogRecord
from logging.handlers import RotatingFileHandler
from typing import Optional


class JobLogFormatter(logging.Formatter):
    """
    Custom log formatter for job logs
    """
    def format(self, record: LogRecord) -> str:
        """
        Format log record
        
        Args:
            record: Log record
            
        Returns:
            str: Formatted log message
        """
        # Add job ID to log message
        if not hasattr(record, 'job_id') and hasattr(record, 'name'):
            if '_' in record.name:
                try:
                    record.job_id = record.name.split('_')[-1]
                except (IndexError, ValueError):
                    record.job_id = 'unknown'
            else:
                record.job_id = 'unknown'
                
        return super().format(record)


def setup_job_logger(job_id: int, level: int = logging.INFO) -> logging.Logger:
    """
    Set up logger for a specific job
    
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
        formatter = JobLogFormatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )
        
        # Set formatter for handler
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(file_handler)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        logger.info(f"Job logger initialized for job ID: {job_id}")
    
    return logger 