import os
import secrets

import sys
from uuid import uuid4
from datetime import datetime

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # To solve the problem of importing modules from different directories
sys.path.insert(0,parentdir) 

def get_uuid() -> str:
    return str(uuid4())

def get_key_urlsafe(length: int = 32) -> str:
    """Get a urlsafe key of a given length"""
    key = secrets.token_urlsafe(length)
    return key

def get_timestamp() -> float:
    """Get the current timestamp as unix timestamp"""
    return datetime.now().timestamp()
