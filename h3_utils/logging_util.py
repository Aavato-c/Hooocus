import logging
import os
import random
import string
from logging.handlers import RotatingFileHandler
if not os.path.exists('logs'):
    os.makedirs('logs')


class LoggingUtil:
    def __init__(self, name: str = None, log_to_file: bool = False):
        self.log_to_file = log_to_file
        if not name:
            name = "_"
            self.logger = logging.getLogger(name)
            if os.path.exists('logs/combined.log'):
                os.remove('logs/combined.log')
        else:
            self.logger = logging.getLogger(name)

        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(module)s:%(lineno)d:\t%(message)s', datefmt='%m%d:%H:%M:%S')
        
        if self.log_to_file:
            file_handler = RotatingFileHandler('logs/combined.log', maxBytes=5_000_000, backupCount=3) # 5MB
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger
