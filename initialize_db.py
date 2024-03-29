from os.path import exists
import os
from app import db, app
from app.db_init import create_models_from_json
from config import JSON_PATH, PROCEDURES_JSON_PATH  # Ensure PROCEDURES_JSON_PATH is defined in config.py

def initialize_database(tests_json_path, procedures_json_path, replace_existing=False):
    """
    Initializes the database with tables based on the provided JSON structures for tests and procedures.
    
    :param tests_json_path: Path to the JSON file defining the structure of the tests table.
    :param procedures_json_path: Path to the JSON file defining the structure of the procedures table.
    :param replace_existing: If True, replaces the existing database. Otherwise, initializes only if the database does not exist.
    """
    # Setting up an application context
    with app.app_context():
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_exists = exists(db_path)

        if db_exists and not replace_existing:
            print("Database already exists. Use replace_existing=True to recreate it.")
            return

        if replace_existing or not db_exists:
            print("Replacing the existing database." if db_exists else "Creating a new database.")
            
            # Dynamically create models for both tests and procedures before dropping or creating tables
            create_models_from_json(tests_json_path, 'TestData', 'test_data')
            create_models_from_json(procedures_json_path, 'Procedure', 'procedure_data')
            
            db.drop_all()
            db.create_all()

            print("Database initialization complete.")

# Make sure to pass both JSON paths to the function
initialize_database(JSON_PATH, PROCEDURES_JSON_PATH, replace_existing=False)
