# Existing configurations
import os


TITLE = "SkyTest Documentation Platform"

# Path to the JSON structure for tests
JSON_PATH = "app/definitions/tests_structure.json"

# Adding path to the JSON structure for procedures
PROCEDURES_JSON_PATH = "app/definitions/procedures_structure.json"

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'attachments')

# Add these configurations to your config.py
DATABASE_PATH = os.path.join("instance", 'skytest.db')
