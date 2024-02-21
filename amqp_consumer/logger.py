import logging


def setup_logger(name, level=logging.INFO):
    """Sets up a logger for a given module."""
    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(level)  # Set the logging level

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Add formatter to ch
    ch.setFormatter(formatter)

    # Add ch to logger
    if not logger.handlers:
        logger.addHandler(ch)

    return logger
