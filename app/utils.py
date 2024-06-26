# utils.py

from datetime import datetime, time
import json
import os
import qrcode

from flask import flash, url_for

from app.models import get_procedure_title_by_id
from config import UPLOAD_FOLDER
from werkzeug.utils import secure_filename

from flask import request
from io import BytesIO
import base64
from pandas import DataFrame


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
    while Procedure.query.filter_by(procedure_title=unique_title).first():
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
    
def generate_qr_data_uri(item_id, report_type):
    """
    Generates a QR code as a data URI for the given item ID and report type.

    Parameters:
    - item_id (str or int): The unique identifier for the item (test or procedure).
    - report_type (str): The type of report, e.g., 'test' or 'procedure'.

    Returns:
    - str: A data URI representing the QR code image.
    """
    # Dynamically construct the URL based on the report type
    base_url = request.url_root.rstrip('/')  # Ensure there's no trailing slash
    if report_type == 'test':
        qr_data = f"{base_url}/test/{item_id}"
    elif report_type == 'procedure':
        qr_data = f"{base_url}/procedure/{item_id}"
    else:
        raise ValueError("Invalid report type specified")

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    
    # Convert QR code image to data URI
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    data_uri = f"data:image/png;base64,{img_str}"
    
    return data_uri


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


def generate_procedure_html_content(procedure_details, procedure_id):
    qr_code_data_uri = generate_qr_data_uri(procedure_id, report_type='procedure')

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Procedure Detail</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; color: #0056b3; font-size: 24px; }}
            .qr-code img {{ width: 80px; height: 80px; float: right; }}
            .metadata, .footer {{ margin-top: 20px; }}
            p, .footer {{ margin: 10px 0; line-height: 1.6; }}
            ul {{ margin-left: 20px; list-style-type: disc; }}
            .footer {{ text-align: center; font-size: 0.8em; margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Procedure Detail Report: {procedure_details.get('Title', 'N/A')}</h1>
            <div class="qr-code">
                <img src="{qr_code_data_uri}" alt="QR Code">
            </div>
        </div>
        <div class="metadata">
            <p><strong>Procedure ID:</strong> {procedure_id}</p>
    """

    for label, value in procedure_details.items():
        html += f"<p><strong>{label}:</strong> {value or 'N/A'}</p>"

    html += """
        </div>
    """
    # Footer with the current date
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    html += f'<div class="footer">Report generated by SkyTest on: {current_date}</div>'
    html += "</body></html>"
    return html



def generate_test_html_content(form_structure, test):
    # Assuming test_id is an attribute of the test object
    qr_code_data_uri = generate_qr_data_uri(test.test_id, 'test')

    # Minor adjustments for QR size and alignment, and improvements in the layout
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flight Test Detail</title>
        <style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
            .header h1 {{ margin: 0; color: #0056b3; font-size: 24px; }}
            .qr-code img {{ width: 80px; height: 80px; }}
            .metadata {{ margin-top: 20px; }}
            .metadata p, .footer {{ margin: 10px 0; line-height: 1.6; }}
            ul {{ margin-left: 20px; list-style-type: disc; }}
            .footer {{ text-align: center; font-size: 0.8em; margin-top: 40px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Flight Test Log Report</h1>
            <div class="qr-code">
                <img src="{qr_code_data_uri}" alt="QR Code">
            </div>
        </div>
        <h2>{getattr(test, 'test_title', 'N/A')}</h2>
    """

    # Proceed with generating the metadata section as before
    html += '<div class="metadata">'
    for group in form_structure['formGroups']:
        for field in group['fields']:
            field_value = getattr(test, field['name'], "N/A")
            if field['name'] == 'attachments':
                # Adjusting to handle file_path instead of attachments
                field_value = test.file_path
                files_list = field_value.split(',') if field_value else []
                files_html = "<ul>" + "".join([f"<li>{file}</li>" for file in files_list]) + "</ul>"
                html += f"<p><strong>{field['label']}:</strong> {files_html}</p>"
            elif field['name'] == 'procedure_id':
                procedure_title = get_procedure_title_by_id(field_value) if field_value else "N/A"
                html += f"<p><strong>Procedure ID:</strong> {field_value}</p>"
                html += f"<p><strong>Procedure Title:</strong> {procedure_title}</p>"
            else:
                html += f"<p><strong>{field['label']}:</strong> {field_value}</p>"
    html += '</div>'
    
    # Footer with the current date
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    html += f'<div class="footer">Report generated by SkyTest on: {current_date}</div>'
    html += "</body></html>"
    return html


from pandas import DataFrame

def convert_query_to_dataframe(query_results, column_order=None):
    """
    Convert database query results to a pandas DataFrame, preserving column order.

    Parameters:
    - query_results: The result of a database query.
    - column_order: Optional. A list of column names in the desired order.

    Returns:
    - DataFrame: A pandas DataFrame containing the query results.
    """
    # Create a list of dictionaries. Each dictionary represents a row from the query results.
    data = [row.__dict__ for row in query_results]

    if column_order is None and len(data) > 0:
        # Attempt to determine column order dynamically from the first result if not provided
        column_order = list(data[0].keys())
        # Remove '_sa_instance_state' from the order, if present
        column_order = [col for col in column_order if col != '_sa_instance_state']

    # Convert the list of dictionaries to a pandas DataFrame using the specified column order
    df = DataFrame(data, columns=column_order)

    return df


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, time):
            return obj.strftime('%H:%M:%S')
        return json.JSONEncoder.default(self, obj)