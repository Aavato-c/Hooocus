import logging
import os
import random
import string

if not os.path.exists('logs'):
    os.makedirs('logs')
    
class LoggingUtil:
    def __init__(self, name: str = None):
        if not name:
            name = "_"
            self.logger = logging.getLogger(name)
            if os.path.exists('logs/combined_2.log'):
                os.remove('logs/combined_2.log')
        else:
            self.logger = logging.getLogger(name)
        self.logger.propagate = False # Prevents double logging
        self.logger.setLevel(logging.DEBUG)
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(module)s:%(lineno)d:\t%(message)s', datefmt='%m%d:%H:%M:%S')
        #file_handler = logging.FileHandler('logs/combined_2.log')
        #file_handler.setLevel(logging.DEBUG)
        #file_handler.setFormatter(formatter)
        #self.logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(stream_handler)
        




    def get_logger(self):
        return self.logger