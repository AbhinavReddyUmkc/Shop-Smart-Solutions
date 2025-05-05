import logging
import os
import sys
from datetime import datetime

# Configure logging
def setup_logger():
    """Set up application logging"""
    log_dir = 'logs'
    
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Define log file path with timestamp
    timestamp = datetime.now().strftime('%Y%m%d')
    log_file = os.path.join(log_dir, f'application_{timestamp}.log')
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler for logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Create logger object
logger = setup_logger()

def log_info(message):
    """Log info level message"""
    logger.info(message)

def log_error(message, exc_info=False):
    """Log error level message"""
    logger.error(message, exc_info=exc_info)

def log_warning(message):
    """Log warning level message"""
    logger.warning(message)