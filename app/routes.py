from flask import render_template, request, url_for, redirect
from . import app  # Import the app instance from your package's __init__.py
import json
import os

def load_form_structure():
    # Adjust the path if your 'definitions' directory location changes
    form_structure_path = os.path.join(app.root_path, 'definitions', 'form_structure.json')
    with open(form_structure_path, 'r') as json_file:
        form_structure = json.load(json_file)
    return form_structure  # Return the entire structure, including groups



@app.route('/form', methods=['GET'])
def display_form():
    form_structure = load_form_structure()
    # Adjust the template variable to reflect the structure with groups
    return render_template('index.html', formGroups=form_structure['formGroups'])


@app.route('/submit-form', methods=['POST'])
def submit_form():
    form_structure = load_form_structure()
    # Flatten the fields from all groups for processing
    all_fields = [field for group in form_structure['formGroups'] for field in group['fields']]
    submitted_data = {field['name']: request.form.get(field['name']) for field in all_fields}
    print(submitted_data)  # Placeholder for actual data processing logic
    # Redirect after processing the submission
    return redirect(url_for('display_form'))

