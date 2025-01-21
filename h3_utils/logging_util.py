import os, sys
rootdir = os.path.abspath(__file__).split("Hooocus")[0]+"Hooocus"
sys.path.append(rootdir)


import logging
import os
import random
import string
from logging.handlers import RotatingFileHandler

if not os.path.exists('logs'):
    os.makedirs('logs')

from consts import LOGGING_LEVEL_STREAM, LOGGING_LEVEL_FILE, SHOULD_LOG_PERFORMANCE


class PerfLogger:
    def __init__(self, name = "perf"):
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        self.logger = logging.getLogger(f"{name}_{random_chars}")
        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(module)s:%(lineno)d:\t%(message)s', datefmt='%m%d:%H:%M:%S')
        self.logger.setLevel(logging.INFO)
        f_handler = logging.FileHandler(f'{rootdir}/logs/perfomance.log')
        f_handler.setFormatter(formatter)
        self.logger.addHandler(f_handler)

    def get_logger(self):
        return self.logger

class LoggingUtil:
    def __init__(self, name):
        random_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        name_appended=name+random_chars


        self.logger = logging.getLogger(name_appended)
        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(module)s:%(lineno)d:\t%(message)s', datefmt='%m%d:%H:%M:%S')
        self.logger.setLevel(logging.DEBUG)
        
        file_handler = RotatingFileHandler(f'{rootdir}/logs/h3comb.log', maxBytes=50_000_000, backupCount=3) # 50 MB
        #file_handler = logging.FileHandler(f'{rootdir}/logs/h3comb.log')
        file_handler.setLevel(LOGGING_LEVEL_FILE)
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(LOGGING_LEVEL_STREAM)
        
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        return self.logger

