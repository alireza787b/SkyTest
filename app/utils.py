# utils.py

from datetime import datetime
import os

from flask import flash

from config import UPLOAD_FOLDER
from werkzeug.utils import secure_filename


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


def convert_to_time(time_str):
    """
    Converts a string to a datetime.time object. Returns None if conversion fails.
    """
    if not time_str:
        return None  # Immediately return None if the input is empty or None
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return None



def create_test_directory(test_id):
    """
    Creates a directory for a specific test to store files.
    """
    base_dir = os.path.join(UPLOAD_FOLDER, str(test_id))
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def save_uploaded_files(uploaded_files, test_id):
    print("Uploaded Files:", uploaded_files)  # Debug: Print uploaded files info

    test_dir = create_test_directory(test_id)
    saved_files = []

    for file in uploaded_files:
        if file:
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = secure_filename(f"{timestamp}_{file.filename}")
            file_path = os.path.join(test_dir, filename)
            print("Saving File:", file_path)  # Debug: Print the path where the file will be saved
            file.save(file_path)
            saved_files.append(filename)

    return saved_files
