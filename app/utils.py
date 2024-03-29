# utils.py

from datetime import datetime

def generate_unique_proc_id(Procedure, submitted_id):
    """Generates a unique ID by incrementing submitted_id until it's unique."""
    unique_id = submitted_id
    counter = 1
    while Procedure.query.filter_by(procedure_id=unique_id).first():
        unique_id = f"{submitted_id}-{counter}"
        counter += 1
    return unique_id

def generate_unique_proc_title(Procedure, submitted_title):
    """Generates a unique title by appending '-i' to the title if it already exists."""
    unique_title = submitted_title
    counter = 2  # Start from 2 since the first duplicate should be '-2'
    while Procedure.query.filter_by(title=unique_title).first():
        unique_title = f"{submitted_title}-{counter}"
        counter += 1
    return unique_title


def try_parse_time(time_str):
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    return None  # Or raise an exception, log an error, etc.

