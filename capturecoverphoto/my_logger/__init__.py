import sys
import logging
from logging import handlers

FORMATTER = '%(asctime)s: %(filename)s >> %(levelname)s - %(message)s'


def get_logger(name, level=logging.DEBUG, disabled=True,
               file_prefix='debug', formatter=FORMATTER):

    logger = logging.getLogger(name)

    if disabled:
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.disabled = disabled
        return logger

    if logger.handlers:
        return logger

    formatter = logging.Formatter(formatter)

    if sys.platform == "win32":
        logging_handler = handlers.TimedRotatingFileHandler(
            "{}_{}_win.log".format(name, file_prefix),
            when='h',
            interval=1,
            backupCount=1)
    else:
        logging_handler = handlers.TimedRotatingFileHandler(
            "{}_{}.log".format(name, file_prefix),
            when='h',
            interval=1,
            backupCount=1)

    logging_handler.setFormatter(formatter)
    logger.addHandler(logging_handler)
    logger.setLevel(level)
    logger.info("{} LOGGING ON...".format(name))
    return logger
