import logging

def getLogger(name):
    logger = logging.getLogger(name=name)
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    return logger;
