import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log file path with timestamp
LOG_FILE = os.path.join(LOG_DIR, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# Create formatters
CONSOLE_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

FILE_FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create logger
logger = logging.getLogger('ai_assistant')
logger.setLevel(logging.DEBUG)  # Set to lowest level to capture all logs

# Prevent duplicate logs
if logger.handlers:
    logger.handlers.clear()

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Show INFO and above in console
console_handler.setFormatter(CONSOLE_FORMATTER)

# File handler with rotation (max 10MB, keep 5 backup files)
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.DEBUG)  # Log everything to file
file_handler.setFormatter(FILE_FORMATTER)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Set levels for third-party libraries to reduce noise
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('langchain').setLevel(logging.WARNING)
logging.getLogger('langgraph').setLevel(logging.WARNING)


def get_logger(name: str = None):
    """
    Get a logger instance. If name is provided, returns a child logger.
    
    Args:
        name: Optional name for the logger (e.g., 'graph', 'streamlit_app')
    
    Returns:
        Logger instance
    """
    if name:
        return logger.getChild(name)
    return logger


# Example usage
if __name__ == "__main__":
    # Test the logger
    test_logger = get_logger("test")
    
    test_logger.debug("This is a DEBUG message")
    test_logger.info("This is an INFO message")
    test_logger.warning("This is a WARNING message")
    test_logger.error("This is an ERROR message")
    test_logger.critical("This is a CRITICAL message")
    
    print(f"\n✅ Logger initialized successfully!")
    print(f"📁 Log file: {LOG_FILE}")

