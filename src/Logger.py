import logging

# Configure logging
# Configure logging with a custom format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'  # Custom format to exclude "root"
)
logger = logging.getLogger()

def set_logging_level(verbose):
    if verbose == 0:
        logger.setLevel(logging.ERROR)  # Only show errors
    elif verbose == 1:
        logger.setLevel(logging.INFO)   # Show info messages
    elif verbose == 2:
        logger.setLevel(logging.DEBUG)  # Show all messages