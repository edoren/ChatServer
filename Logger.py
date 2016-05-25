import sys
import logging


formatter = logging.Formatter(
    fmt="%(asctime)s [%(name)s] [%(levelname)s] %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S"
)

console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)


# The configuration for the logging.Logger instances
def GetLogger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console)
    return logger
