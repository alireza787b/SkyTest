from datetime import datetime
from flask import render_template, request, url_for, redirect, flash
import json
import os
from . import app, db
from .db_init import dynamic_models
from config import TITLE, JSON_PATH

def load_form_structure():
    # Adjust the path if your 'definitions' directory location changes
    form_structure_path = JSON_PATH
    with open(form_structure_path, 'r') as json_file:
        form_structure = json.load(json_file)
    return form_structure  # Return the entire structure, including groups

@app.route('/')
def home():
    page_title = TITLE # Or fetch from config.py if you decide to include it there
    return render_template('index.html', page_title=page_title)


@app.route('/form', methods=['GET'])
def display_form():
    form_structure = load_form_structure()
    TestData = dynamic_models.get('TestData')
    
    # Query for the latest test entry to calculate the next Test ID
    last_test = TestData.query.order_by(TestData.id.desc()).first()
    next_test_id = (last_test.id + 1) if last_test else 1
    
    # Generate current date and time
    current_date = datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M')

    return render_template('add_test.html', formGroups=form_structure['formGroups'],
                           next_test_id=next_test_id, current_date=current_date, current_time=current_time)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Load the form structure to know what fields we expect
    form_structure = load_form_structure()
    expected_fields = [field for group in form_structure['formGroups'] for field in group['fields']]

    TestData = dynamic_models.get('TestData')
    if TestData is None:
        return "Error: TestData model not found.", 404

    new_entry = TestData()

    for field in expected_fields:
        field_name = field['name']
        field_value = request.form.get(field_name, None)

        # Convert empty string to None for float fields, or use a default float value
        if field['type'] == 'number' and field_value == '':
            field_value = None  # or a default value like 0.0, if appropriate

        if hasattr(new_entry, field_name):
            setattr(new_entry, field_name, field_value)

    db.session.add(new_entry)
    db.session.commit()
    flash('Test successfully submitted!', 'success')  # 'success' is a category you can use in the template

    return redirect(url_for('display_form'))

@app.route('/data')
def display_data():
    TestData = dynamic_models.get('TestData')
    data_entries = TestData.query.all()
    return render_template('data.html', entries=data_entries)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    TestData = dynamic_models.get('TestData')
    entry_to_delete = TestData.query.get_or_404(id)
    db.session.delete(entry_to_delete)
    db.session.commit()
    return redirect(url_for('display_data'))



@app.route('/tests')
def list_tests():
    TestData = dynamic_models.get('TestData')
    fields = [TestData.id, TestData.test_title]
    # Conditionally add the 'date' field if it exists in the model
    if hasattr(TestData, 'date'):
        fields.append(TestData.date)
    tests = TestData.query.with_entities(*fields).all()
    return render_template('tests_list.html', tests=tests)

@app.route('/test/<int:test_id>')
def view_test(test_id):
    TestData = dynamic_models.get('TestData')
    if TestData is None:
        flash("Error: TestData model not found.", "error")
        return redirect(url_for('index'))
    
    test = TestData.query.get_or_404(test_id)
    form_structure = load_form_structure()

    test_details = {}
    for group in form_structure['formGroups']:
        for field in group['fields']:
            field_name = field['name']
            test_details[field['label']] = getattr(test, field_name, "N/A") or "N/A"
    
    return render_template('test_detail.html', test_details=test_details, title=field['label'])