from datetime import datetime
from flask import render_template, request, url_for, redirect, flash
import json
import os
from . import app, db
from config import TITLE, JSON_PATH, PROCEDURES_JSON_PATH
from .utils import generate_unique_proc_id, generate_unique_proc_title
from app.models import get_procedure_model, get_test_data_model
from app.forms import load_form_structure

@app.route('/')
def home():
    """Render the home page with configurable title."""
    return render_template('index.html', page_title=TITLE)

@app.route('/form', methods=['GET'])
def display_form():
    """Displays the form for data entry."""
    form_structure = load_form_structure(JSON_PATH)
    TestData = get_test_data_model()
    Procedure = get_procedure_model()
    
    if Procedure is None:
        flash("Error: Procedure model not found.", "error")
        return redirect(url_for('home'))
    
    # Fetch all procedures and prepare a list of (id, title) tuples
    procedure_options = Procedure.query.with_entities(Procedure.id, Procedure.title).all()
    
    last_test = TestData.query.order_by(TestData.id.desc()).first()
    next_test_id = (last_test.id + 1) if last_test else 1
    current_date, current_time = datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M')

    return render_template('add_test.html', formGroups=form_structure['formGroups'], next_test_id=next_test_id, 
                           current_date=current_date, current_time=current_time, procedure_options=procedure_options)


@app.route('/submit-form', methods=['POST'])
def submit_form():
    """Handles form submission and data persistence."""
    form_structure, TestData = load_form_structure(JSON_PATH), get_test_data_model()
    if not TestData:
        flash("Error: TestData model not found.", "error")
        return redirect(url_for('home'))

    new_entry = TestData()
    for field in (f for g in form_structure['formGroups'] for f in g['fields']):
        value = request.form.get(field['name'], None)
        setattr(new_entry, field['name'], None if field['type'] == 'number' and not value else value)
    
    db.session.add(new_entry)
    db.session.commit()
    flash('Test successfully submitted!', 'success')
    return redirect(url_for('display_form'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    """Deletes a specific data entry."""
    TestData = get_test_data_model()
    db.session.delete(TestData.query.get_or_404(id))
    db.session.commit()
    return redirect(url_for('display_data'))

@app.route('/tests')
def list_tests():
    """Lists summaries of all tests."""
    TestData = get_test_data_model() 
    fields = [TestData.id, TestData.test_title, TestData.date if hasattr(TestData, 'date') else None]
    tests = TestData.query.with_entities(*[f for f in fields if f]).all()
    return render_template('tests_list.html', tests=tests)

@app.route('/test/<int:test_id>')
def view_test(test_id):
    """Displays detailed view of a single test."""
    TestData = get_test_data_model()
    Procedure = get_procedure_model()

    if not TestData or not Procedure:
        flash("Error: Models not found.", "error")
        return redirect(url_for('home'))
    
    test = TestData.query.get_or_404(test_id)
    form_structure = load_form_structure(JSON_PATH)
    test_details = {}

    # Flag to mark if we have handled the procedure ID
    procedure_id_handled = False

    for group in form_structure['formGroups']:
        for field in group['fields']:
            field_value = getattr(test, field['name'], "N/A") or "N/A"
            field_data = {"value": field_value}

            if 'unit' in field:
                field_data['unit'] = field['unit']

            if field['name'] == 'procedure_id':
                # Handle procedure ID and title together
                procedure_id_handled = True
                procedure = Procedure.query.filter_by(id=field_value).first()
                procedure_title = procedure.title if procedure else 'N/A'
                # Assuming you want the title right after the ID
                test_details[field['label']] = field_data
                test_details['Procedure Title'] = {'value': procedure_title}
            elif not procedure_id_handled or field['name'] != 'procedure_id':
                test_details[field['label']] = field_data

    return render_template('test_detail.html', test_details=test_details)






#################
# Procedures Routes

@app.route('/add-procedure', methods=['GET'])
def display_procedure_form():
    procedure_structure = load_form_structure(PROCEDURES_JSON_PATH)  # Assuming this function can handle both tests and procedure JSON paths
    Procedure = get_procedure_model()
    
    last_procedure = Procedure.query.order_by(Procedure.id.desc()).first() if Procedure else None
    next_id = last_procedure.id + 1 if last_procedure else 1
    today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date in the correct format
    
    return render_template('add_procedure.html', 
                           procedureGroups=procedure_structure['procedureGroups'], 
                           next_id=next_id, 
                           today_date=today_date)


@app.route('/submit-procedure', methods=['POST'])
def submit_procedure():
    procedure_structure = load_form_structure(PROCEDURES_JSON_PATH)
    Procedure = get_procedure_model()
    if Procedure is None:
        flash("Error: Procedure model not found.", "error")
        return redirect(url_for('display_procedure_form'))

    new_procedure = Procedure()

    submitted_id = request.form.get('procedure_id', None)
    submitted_title = request.form.get('title', None)

    # Generate unique ID and title
    unique_id = generate_unique_proc_id(Procedure, submitted_id)
    unique_title = generate_unique_proc_title(Procedure, submitted_title)

    # Set the unique ID and title along with other fields
    setattr(new_procedure, 'procedure_id', unique_id)
    setattr(new_procedure, 'title', unique_title)
    
    for field in (f for g in procedure_structure['procedureGroups'] for f in g['fields']):
        if field['name'] not in ['procedure_id', 'title']:
            field_value = request.form.get(field['name'], '')
            if field_value == '':
                # Assign a default value or handle the empty string case
                if field['type'] == 'float':
                    field_value = 0.0
                else:
                    field_value = None
            setattr(new_procedure, field['name'], field_value)

    db.session.add(new_procedure)
    db.session.commit()
    flash('Procedure successfully added with unique ID and Title!', 'success')
    return redirect(url_for('display_procedure_form'))


@app.route('/procedures')
def list_procedures():
    Procedure = get_procedure_model()
    procedures = Procedure.query.all()
    return render_template('procedures_list.html', procedures=procedures)

@app.route('/procedure/<int:procedure_id>')
def view_procedure(procedure_id):
    Procedure = get_procedure_model()
    if Procedure is None:
        flash("Error: Procedure model not found.", "error")
        return redirect(url_for('home'))
    
    procedure = Procedure.query.get_or_404(procedure_id)
    procedure_structure = load_form_structure(PROCEDURES_JSON_PATH)  # Assuming this function can now handle both test and procedure JSON paths
    
    procedure_details = {}
    for group in procedure_structure['procedureGroups']:
        for field in group['fields']:
            field_label = field['label']
            field_name = field['name']
            field_value = getattr(procedure, field_name, "N/A")
            procedure_details[field_label] = field_value
    
    return render_template('procedure_detail.html', procedure_details=procedure_details)

