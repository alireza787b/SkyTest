from os.path import exists
import os
from app import db, app
from app.db_init import create_models_from_json

def initialize_database(json_path, replace_existing=False):
    """
    Documentation...
    """
    # Setting up an application context
    with app.app_context():
        # Adjusted for direct app and db usage
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_exists = exists(db_path)

        if db_exists and not replace_existing:
            print("Database already exists. Use replace_existing=True to recreate it.")
            return

        if replace_existing or not db_exists:
            if db_exists:
                print("Replacing the existing database.")
            else:
                print("Creating a new database.")

            db.drop_all()
            db.create_all()
            create_models_from_json(json_path)

            print(f"Database initialization complete. Structure defined in '{json_path}' has been applied.")

# Ensure the database file path is absolute to prevent issues in different environments
database_file_path = os.path.join(os.path.dirname(__file__), 'app/skytest.db')

# Execute database initialization within the application context
initialize_database('app/definitions/form_structure.json', replace_existing=True)



