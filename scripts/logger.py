import logging
from pathlib import Path


def get_logger(name: str = 'ecommerce', level: int = logging.INFO, logfile: str = None):
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    fmt = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    if logfile:
        Path(logfile).parent.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(logfile)
        fh.setLevel(level)
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
