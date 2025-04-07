import logging
from logging.handlers import RotatingFileHandler
import time
from datetime import datetime

# Configure logging with rotation
def setup_logging():
    # Create a rotating file handler
    handler = RotatingFileHandler(
        filename='logs/threat_events.log',
        maxBytes=10*1024*1024,  # 10MB per file
        backupCount=5,          # Keep 5 backup files
        encoding='utf-8',
        delay=False
    )
    
    # Set formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(threat)s] Risk:%(risk_score)d - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger('threat_detection')
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    return logger

# Initialize logger
threat_logger = setup_logging()

def log_threat(threat, risk_score, additional_info=None):
    """Enhanced threat logging with structured data"""
    extra = {
        'threat': threat,
        'risk_score': risk_score,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    log_msg = f"{threat} detected"
    if additional_info:
        log_msg += f" | Details: {additional_info}"
    
    threat_logger.info(
        log_msg,
        extra=extra
    )

# Example usage
log_threat("DDoS Attack", 30, "Inbound traffic from 192.168.1.100 exceeding thresholds")
log_threat("SQL Injection Attempt", 75, "Detected in /login.php endpoint")
