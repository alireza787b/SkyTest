from datetime import datetime
import shutil
import zipfile
import bcrypt
from flask import make_response,jsonify, render_template, request, send_file, send_from_directory, url_for, redirect, flash
import json
import os

from weasyprint import HTML
from . import app, db
from config import DATABASE_PATH, TITLE, JSON_PATH, PROCEDURES_JSON_PATH, UPLOAD_FOLDER
from .utils import convert_query_to_dataframe, convert_to_time, create_test_directory, generate_procedure_html_content, generate_unique_proc_id, generate_unique_proc_title, save_uploaded_files, try_parse_time, generate_test_html_content
from app.models import get_model_columns, get_procedure_model, get_test_data_model
from app.forms import load_form_structure
import tempfile
import zipfile
import shutil
import pandas as pd
from io import BytesIO
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt

    
@app.route('/')
def dashboard():
    TestData = get_test_data_model()
    Procedure = get_procedure_model()
    num_procedures = Procedure.query.count()
    num_tests = TestData.query.count()
    return render_template('dashboard.html', num_procedures=num_procedures, num_tests=num_tests)


@app.route('/form', methods=['GET'])
def add_test():
    """Displays the form for data entry."""
    form_structure = load_form_structure(JSON_PATH)
    TestData = get_test_data_model()
    Procedure = get_procedure_model()
    
    if Procedure is None:
        flash("Error: Procedure model not found.", "error")
        return redirect(url_for('dashboard'))
    
    # Fetch all procedures and prepare a list of (id, title) tuples
    procedure_options = Procedure.query.with_entities(Procedure.id, Procedure.procedure_title).all()
    
    last_test = TestData.query.order_by(TestData.id.desc()).first()
    next_test_id = (last_test.id + 1) if last_test else 1
    current_date, current_time = datetime.now().strftime('%Y-%m-%d'), datetime.now().strftime('%H:%M')

    return render_template('add_test.html', formGroups=form_structure['formGroups'], next_test_id=next_test_id, 
                           current_date=current_date, current_time=current_time, procedure_options=procedure_options)

@app.route('/submit-form', methods=['POST'])
def submit_form():
    """Handles form submission and data persistence including file uploads."""
    form_structure, TestData = load_form_structure(JSON_PATH), get_test_data_model()
    if not TestData:
        flash("Error: TestData model not found.", "error")
        return redirect(url_for('dashboard'))

    new_entry = TestData()
    db.session.add(new_entry)
    db.session.flush()  # Temporarily save to get the test_id for file directory
    
    # Always create a directory for the new test
    test_dir = create_test_directory(new_entry.id)
    
    for field in (f for g in form_structure['formGroups'] for f in g['fields']):
        if field['type'] == 'file':
            continue
        value = request.form.get(field['name'], None)

        if field['type'] == 'date' and value:
            value = datetime.strptime(value, '%Y-%m-%d').date()
        elif field['type'] == 'time' and value:
            value = convert_to_time(value)  # Use the new conversion function
        elif field['type'] == 'number':
            value = float(value) if value else None  # Ensure proper handling of numeric fields

        if value is not None:  # Only set the attribute if value is not None
            setattr(new_entry, field['name'], value)

    # Handle file uploads
    uploaded_files = request.files.getlist('attachments')
    saved_files = save_uploaded_files(uploaded_files, new_entry.id)
    if saved_files:
        # Store comma-separated filenames in the database if files were uploaded
        new_entry.file_path = ",".join(saved_files)
    else:
        # Indicate no files were uploaded or just leave it empty
        new_entry.file_path = ""

    try:
        db.session.commit()
        flash('Test successfully submitted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error during submission: {e}", "error")

    return redirect(url_for('add_test'))


@app.route('/edit-test/<int:test_id>', methods=['GET', 'POST'])
def edit_test(test_id):
    TestData = get_test_data_model()
    test = TestData.query.get_or_404(test_id)

    # Fetch current files from the database
    current_files = test.file_path.split(',') if test.file_path else []
    Procedure = get_procedure_model()
    procedure_options = Procedure.query.with_entities(Procedure.id, Procedure.procedure_title).all()
    print("Procedure Options:", procedure_options)
    print("Current Test's Procedure ID:", test.procedure_id)



    if request.method == 'POST':
        # Files marked for removal
        files_to_remove = request.form.getlist('files_to_remove[]')

        # Remove selected files
        for filename in files_to_remove:
            if filename in current_files:
                try:
                    file_path = os.path.join(UPLOAD_FOLDER, str(test_id), filename)
                    os.remove(file_path)
                    current_files.remove(filename)  # Remove from the current files list
                except Exception as e:
                    flash(f'Error removing file {filename}: {e}', 'error')

        # Handle new file uploads
        new_files = request.files.getlist('new_files')
        if new_files:
            saved_files = save_uploaded_files(new_files, test_id)
            current_files.extend(saved_files)  # Add newly saved files to the list

        # Update the file_path field with the current state of files
        test.file_path = ','.join(current_files)

        # Process other form fields as before
        for field_name, field_value in request.form.items():
            # Exclude file handling fields and non-editable fields
            if field_name not in ['test_id', 'created_at', 'files_to_remove[]', 'new_files']:
                # Convert date fields
                if field_name == 'date' and field_value:
                    field_value = datetime.strptime(field_value, "%Y-%m-%d").date()
                # Convert time fields
                elif field_name == 'time' and field_value:
                    field_value = try_parse_time(field_value)
                # Handle numeric fields - convert to appropriate type or set to None if empty
                elif field_value.isdigit():
                    field_value = int(field_value) if field_value.isdigit() else field_value
                # For empty string values, you may decide to set them to None or keep as is depending on your requirement
                elif field_value == '':
                    field_value = None

                setattr(test, field_name, field_value)

        try:
            db.session.commit()
            flash('Test updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'error')

        return redirect(url_for('list_tests'))

    # Prepare existing test data for the form, including file information
    test_data = {column.name: getattr(test, column.name) for column in test.__table__.columns}
    # Include current file names as part of the form data
    test_data['files'] = current_files

    test_structure = load_form_structure(JSON_PATH)

    return render_template('edit_test.html', test=test, test_data=test_data, test_structure=test_structure,procedure_options=procedure_options)



@app.route('/delete-test/<int:test_id>', methods=['POST'])
def delete_test(test_id):
    TestData = get_test_data_model()
    test = TestData.query.get_or_404(test_id)  # Ensure TestData is correctly imported
    
    # Define the directory path for the test's files
    directory = os.path.join(UPLOAD_FOLDER, str(test_id))
    
    try:
        # Attempt to delete the test record
        db.session.delete(test)
        
        # If the directory exists, remove it and all its contents
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"Removed directory and all contents: {directory}")
        
        # Commit changes to the database
        db.session.commit()
        flash('Test successfully deleted!', 'success')
    except Exception as e:
        db.session.rollback()  # Roll back the database transaction in case of any error
        flash(f'Error deleting test: {str(e)}', 'error')
        print(f"Error deleting directory: {e}")
        
    return redirect(url_for('list_tests'))  # Adjust 'list_tests' to your actual view function that lists all tests


@app.route('/tests')
def list_tests():
    """Lists summaries of all tests."""
    TestData = get_test_data_model() 
    fields = [TestData.id, TestData.test_title, TestData.created_at if hasattr(TestData, 'date') else None]
    tests = TestData.query.with_entities(*[f for f in fields if f]).all()
    return render_template('tests_list.html', tests=tests)

@app.route('/test/<int:test_id>')
def view_test(test_id):
    """Displays detailed view of a single test."""
    TestData = get_test_data_model()
    Procedure = get_procedure_model()

    if not TestData or not Procedure:
        flash("Error: Models not found.", "error")
        return redirect(url_for('dashboard'))
    
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
                
            if field['name'] == 'attachments':
                continue

            if field['name'] == 'procedure_id':
                # Handle procedure ID and title together
                procedure_id_handled = True
                procedure = Procedure.query.filter_by(id=field_value).first()
                procedure_title = procedure.procedure_title if procedure else 'N/A'
                procedure_id = procedure.procedure_id if procedure else 'N/A'
                # Assuming you want the title right after the ID
                test_details[field['label']] = field_data
                test_details['Procedure Title'] = {'value': procedure_title}
                test_details['procedure_id'] = procedure_id
            elif not procedure_id_handled or field['name'] != 'procedure_id':
                test_details[field['label']] = field_data
                
     # Handle files
    filenames = test.file_path.split(',') if test.file_path else []
    # Assuming 'Files' label is not already used; adjust as needed
    test_details['Files'] = {'value': filenames, 'is_files': True}
    procedure_id = test_details['procedure_id']
    return render_template('test_detail.html', test_details=test_details, test_id=test_id, procedure_id=procedure_id)






#################
# Procedures Routes

@app.route('/add-procedure', methods=['GET'])
def add_procedure():
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
    # Assuming load_form_structure and get_procedure_model are defined elsewhere and imported correctly
    procedure_structure = load_form_structure(PROCEDURES_JSON_PATH)
    Procedure = get_procedure_model()
    if Procedure is None:
        flash("Error: Procedure model not found.", "error")
        return redirect(url_for('display_procedure_form'))

    new_procedure = Procedure()

    # Handling the unique ID and title
    submitted_id = request.form.get('procedure_id', None)
    submitted_title = request.form.get('procedure_title', None)
    unique_id = generate_unique_proc_id(Procedure, submitted_id)
    unique_title = generate_unique_proc_title(Procedure, submitted_title)
    setattr(new_procedure, 'procedure_id', unique_id)
    setattr(new_procedure, 'procedure_title', unique_title)
    
    # Processing other fields
    for field in (f for g in procedure_structure['procedureGroups'] for f in g['fields']):
        if field['name'] not in ['procedure_id', 'procedure_title']:
            field_value = request.form.get(field['name'], '')
            # Special handling for date fields
            if field['type'] == 'date' and field_value:
                # Convert string date to datetime.date object
                field_value = datetime.strptime(field_value, '%Y-%m-%d').date()
            elif field['type'] == 'float' and field_value:
                # Convert string to float
                field_value = float(field_value)
            elif not field_value:
                # Assign a default value or handle the empty string case
                field_value = None  # Or other appropriate default value
            setattr(new_procedure, field['name'], field_value)

    db.session.add(new_procedure)
    try:
        db.session.commit()
        flash('Procedure successfully added with unique ID and Title!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'error')
        
    return redirect(url_for('add_procedure'))

@app.route('/edit-procedure/<int:procedure_id>', methods=['GET', 'POST'])
def edit_procedure(procedure_id):
    Procedure = get_procedure_model()  # Assuming this gets your dynamic model
    procedure = Procedure.query.get_or_404(procedure_id)
    
    if request.method == 'POST':
        for field_name, value in request.form.items():
            # Skip non-editable fields
            if field_name in ['procedure_id', 'created_at']:
                continue

            # Convert empty strings to None for floats
            if value == '':
                    value = None  # General case for non-float fields

            # Special handling for date fields
            elif field_name == 'date_created':  # Adapt for any other date fields you have
                try:
                    value = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    value = None  # In case of invalid date string
                
            # Assign the value to the model
            setattr(procedure, field_name, value)
        
        db.session.commit()
        flash('Procedure updated successfully.', 'success')
        return redirect(url_for('list_procedures'))

    # Load initial form data
    procedure_data = {column.name: getattr(procedure, column.name) for column in procedure.__table__.columns}
    procedure_structure = load_form_structure(PROCEDURES_JSON_PATH)  # Load the structure for form rendering
    return render_template('edit_procedure.html', procedure=procedure, procedure_data=procedure_data, procedure_structure=procedure_structure)



@app.route('/procedures')
def list_procedures():
    Procedure = get_procedure_model()
    procedures = Procedure.query.order_by(Procedure.created_at).all()
    return render_template('procedures_list.html', procedures=procedures)


@app.route('/procedure/<int:procedure_id>')
def view_procedure(procedure_id):
    Procedure = get_procedure_model()
    if Procedure is None:
        flash("Error: Procedure model not found.", "error")
        return redirect(url_for('dashboard'))
    
    procedure = Procedure.query.get_or_404(procedure_id)
    procedure_structure = load_form_structure(PROCEDURES_JSON_PATH)  # Assuming this function can now handle both test and procedure JSON paths
    
    procedure_details = {}
    for group in procedure_structure['procedureGroups']:
        for field in group['fields']:
            field_label = field['label']
            field_name = field['name']
            field_value = getattr(procedure, field_name, "N/A")
            procedure_details[field_label] = field_value
    
    return render_template('procedure_detail.html', procedure_details=procedure_details, procedure_id = procedure_id)

@app.route('/delete-procedure/<int:procedure_id>', methods=['POST'])
def delete_procedure(procedure_id):
    Procedure = get_procedure_model()
    procedure = Procedure.query.get_or_404(procedure_id)
    
    try:
        db.session.delete(procedure)
        db.session.commit()
        flash('Procedure successfully deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting procedure: {str(e)}', 'error')
        
    return redirect(url_for('list_procedures'))

@app.route('/download-test/<int:test_id>/<filename>')
def download_file(test_id, filename):
    directory = os.path.join(UPLOAD_FOLDER, str(test_id))
    print(f"Attempting to download from: {directory}/{filename}")  # For debugging
    try:
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        print(f"Error: {e}")  # Log any error
        return "File not found", 404
    
    
@app.route('/procedure/<procedure_id>/export_pdf')
def export_procedure_pdf(procedure_id):
    ProcedureModel = get_procedure_model()
    procedure = ProcedureModel.query.get_or_404(procedure_id)

    # Load the procedure form structure from JSON configuration
    procedure_form_structure = load_form_structure(PROCEDURES_JSON_PATH)
    
    # Dynamically extract procedure details based on the form structure
    procedure_details = {}
    for group in procedure_form_structure['procedureGroups']:
        for field in group['fields']:
            field_name = field['name']
            # Assuming the field name directly corresponds to the model attribute
            field_value = getattr(procedure, field_name, 'N/A')
            procedure_details[field['label']] = field_value

    # Generate HTML content for PDF
    html_content = generate_procedure_html_content(procedure_details, procedure_id)
    pdf = HTML(string=html_content).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=procedure_{procedure_id}_details.pdf'

    return response





############
#import/export

@app.route('/data-management')
def data_management():
    # Render the Import/Export page template
    return render_template('import_export.html')



@app.route('/export_data')
def export_data():
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Copy the database file
        shutil.copy2(DATABASE_PATH, tmpdirname)
        
        # Ensure the attachments directory exists before copying
        attachments_backup_dir = os.path.join(tmpdirname, 'attachments')
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)  # Create the source attachments folder if it doesn't exist
        shutil.copytree(UPLOAD_FOLDER, attachments_backup_dir)
        
        # Copy the definitions directory
        definitions_backup_dir = os.path.join(tmpdirname, 'definitions')
        shutil.copytree('app/definitions', definitions_backup_dir)

        # Get the current date and time formatted as YYYY-MM-DD_HH-MM-SS
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create a zip file of the entire temporary directory (including the database, attachments, and definitions)
        # and include the current date and time in the backup filename
        backup_filename = f"backup_{current_time}.zip"
        backup_zip = shutil.make_archive(base_name=os.path.join(tempfile.gettempdir(), f"backup_{current_time}"), format='zip', root_dir=tmpdirname)
        
        return send_file(backup_zip, as_attachment=True, download_name=backup_filename)

@app.route('/import_data', methods=['POST'])
def import_data():
    if 'importFile' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('data_management'))

    file = request.files['importFile']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('data_management'))

    filename = secure_filename(file.filename)
    if not filename.endswith('.zip'):
        flash('Uploaded file is not a zip file', 'error')
        return redirect(url_for('data_management'))

    with tempfile.TemporaryDirectory() as tmpdirname:
        zip_path = os.path.join(tmpdirname, filename)
        file.save(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdirname)
        
        # Process the extracted contents
        try:
            # Database replacement
            extracted_db_path = os.path.join(tmpdirname, 'skytest.db')
            if os.path.exists(extracted_db_path):
                os.replace(extracted_db_path, DATABASE_PATH)  # Replace the existing DB with the new one
            
            # Attachments replacement
            extracted_attachments_path = os.path.join(tmpdirname, 'attachments')
            if os.path.exists(extracted_attachments_path):
                if os.path.exists(UPLOAD_FOLDER):
                    shutil.rmtree(UPLOAD_FOLDER)
                shutil.copytree(extracted_attachments_path, UPLOAD_FOLDER)
            
            # Definitions replacement
            extracted_definitions_path = os.path.join(tmpdirname, 'definitions')
            if os.path.exists(extracted_definitions_path):
                definitions_dest_path = os.path.join('app', 'definitions')
                if os.path.exists(definitions_dest_path):
                    shutil.rmtree(definitions_dest_path)
                shutil.copytree(extracted_definitions_path, definitions_dest_path)

            flash('Data import was successful! Please restart your Docker container, application, or server to apply the changes.', 'success')

            # Add logic here to restart the application if necessary
        except Exception as e:
            flash(f'An error occurred during the import: {e}', 'error')
            # Handle specific exceptions and cleanup if needed

    return redirect(url_for('data_management'))

@app.route('/test/<int:test_id>/export_pdf')
def export_test_pdf(test_id):
    TestData = get_test_data_model()
    # Simulating fetching test data and form structure
    test = TestData.query.get_or_404(test_id)
    form_structure = load_form_structure(JSON_PATH)
    
    # Dynamic HTML generation based on form structure and test data
    html_content = generate_test_html_content(form_structure, test)
    pdf = HTML(string=html_content).write_pdf()
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=test_{test_id}_details.pdf'
    
    return response





@app.route('/export_database')
def export_database():
    format_type = request.args.get('format', 'json')
    test_data_model = get_test_data_model()
    procedure_model = get_procedure_model()

    test_data_df = convert_query_to_dataframe(test_data_model.query.all(), column_order=get_model_columns(test_data_model))
    procedure_data_df = convert_query_to_dataframe(procedure_model.query.all(), column_order=get_model_columns(procedure_model))

    
    if format_type == 'excel':
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            test_data_df.to_excel(writer, sheet_name='Test Data', index=False)
            procedure_data_df.to_excel(writer, sheet_name='Procedure Data', index=False)
        output.seek(0)
        return send_file(output, download_name="database_export.xlsx", as_attachment=True, mimetype='application/vnd.ms-excel')
    else:  # JSON format
        # Create a zip file containing both JSON exports
        zip_output = BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zip_file:
            for name, df in [('test_data', test_data_df), ('procedure_data', procedure_data_df)]:
                # Use CustomJSONEncoder to serialize the DataFrame
                json_str = df.to_json(orient='records', date_format='iso')
                json_bytes = json_str.encode('utf-8')
                zip_file.writestr(f'{name}.json', json_bytes)
        
        zip_output.seek(0)
        return send_file(zip_output, download_name='database_export.zip', as_attachment=True, mimetype='application/zip')


@app.route('/procedure/<int:procedure_id>/tests')
def procedure_tests(procedure_id):
    TestData = get_test_data_model()
    Procedure = get_procedure_model()
    procedure = Procedure.query.get_or_404(procedure_id)  # Assuming Procedure is your model name
    tests = TestData.query.filter_by(procedure_id=procedure_id).all()
    return render_template('procedure_tests.html', tests=tests, procedure=procedure)


