"""
The module is responsible for creating logs for monitoring execution
"""
import os
import sys
import logging
from logging.handlers import RotatingFileHandler

base_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(base_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

log_path = os.path.join(log_dir, "monitoring_containers.log")

logger = logging.getLogger("MonitoringContainers")
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = RotatingFileHandler(log_path, maxBytes=1024*1024, backupCount=5)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("Logger initialized and file handler is working!")