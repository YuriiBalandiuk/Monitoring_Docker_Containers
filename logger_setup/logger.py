"""
The module is responsible for creating logs for monitoring execution
"""

import sys
import logging

from logging.handlers import RotatingFileHandler


logger = logging.getLogger("ContainerMonitor")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - \
                              %(levelname)s - %(message)s')

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = RotatingFileHandler("../container_monitor.log",
                                   maxBytes=1024 * 1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
