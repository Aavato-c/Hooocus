import os
import logging
import dotenv

dotenv.load_dotenv(override=True)


SERVER_URL = os.environ.get("SERVER_URL")
if SERVER_URL is None:
    raise ValueError("SERVER_URL is not set.")

ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION = os.environ.get("ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION", None)
if ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION is None:
    raise ValueError("ACCEPTED_API_TOKEN_FOR_IMAGE_GENERATION is not set.")

# Sqlite
DB_URL = os.environ.get("DB_URL")
if DB_URL is None:
    raise ValueError("DB_URL is not set.")

DB_URL_TEST = os.environ.get("DB_URL_TEST")
if DB_URL_TEST is None:
    raise ValueError("DB_URL_TEST is not set.")

LOGGING_LEVEL_STREAM = logging.WARNING
LOGGING_LEVEL_FILE = logging.INFO

IMAGEN_BACKEND_PORT = 8111
IMAGEN_BACKEND_URL = "http://127.0.0.1:8111"



TESTING = False

