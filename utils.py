import re
import os
# Regular expression for a valid filename
VALID_FILENAME_RE = r'^[\w,\s-]+\.[A-Za-z]{2,}$'

def is_valid_filename(filename: str) -> bool:
    return re.match(VALID_FILENAME_RE, filename) is not None

def ensure_directory_exists(directory: str):
    if not os.path.exists(directory):
        os.makedirs(directory)
