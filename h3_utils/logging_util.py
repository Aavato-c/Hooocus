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


def format_table_from_str(table: list):
    """
    table = [
    ["", "Man Utd", "Man City", "T Hotspur"],
    ["Man Utd", 1, 0, 0],
    ["Man City", 1, 1, 0],
    ["T Hotspur", 0, 1, 2],
    ]
       
    """
    longest_cols = [
        (max([len(str(row[i])) for row in table]) + 3)
        for i in range(len(table[0]))
    ]
    row_format = "".join(["{:>" + str(longest_col) + "}" for longest_col in longest_cols])
    print_str = ""
    for row in table:
        print_str += row_format.format(*row) + "\n"

    return print_str

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

