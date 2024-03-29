from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import JSON_PATH
import os

# Initialize the Flask application and SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skytest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Important: Import create_models_from_json after db is defined
from app.db_init import create_models_from_json
create_models_from_json(JSON_PATH, 'TestData', 'test_data')

from . import routes
