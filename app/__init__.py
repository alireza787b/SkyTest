from datetime import datetime, timedelta
import json
from flask import Flask, flash
from flask_sqlalchemy import SQLAlchemy
from config import JSON_PATH, SESSION_TIME_MIN
import os
from flask import session, redirect, url_for, request, render_template
from werkzeug.security import check_password_hash, generate_password_hash

from config import PASSWORD_FILE

# Initialize the Flask application and SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skytest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=SESSION_TIME_MIN)  # Session duration

db = SQLAlchemy(app)

# Important: Import create_models_from_json after db is defined
from app.db_init import create_models_from_json
create_models_from_json(JSON_PATH, 'TestData', 'test_data')

from . import routes





@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None  # Define an error variable to hold potential login errors

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if os.path.exists(PASSWORD_FILE):
            with open(PASSWORD_FILE, 'r') as file:
                data = json.load(file)
                user = next((u for u in data.get('users', []) if u['username'] == username), None)
            
            if user and check_password_hash(user['password_hash'], password):
                session['authenticated'] = True
                session['user_mode'] = user['user_mode']
                session.permanent = True
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password. Please try again.'
        else:
            new_user = {
                "username": username,
                "password_hash": generate_password_hash(password),
                "user_mode": "admin",  # Default user mode
                "date_registered": datetime.utcnow().isoformat()
            }
            data = {"users": [new_user]}
            with open(PASSWORD_FILE, 'w') as file:
                json.dump(data, file, indent=4)
            
            session['authenticated'] = True
            session['user_mode'] = new_user['user_mode']
            session.permanent = True
            flash('Admin account created. You are now logged in.', 'success')
            return redirect(url_for('dashboard'))

    return render_template('login.html', error=error)



@app.before_request
def require_login():
    if not session.get('authenticated') and request.endpoint != 'login':
        return redirect(url_for('login'))