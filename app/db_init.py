import json
from app import db

dynamic_models = {}

def create_models_from_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
        
        # Define attributes for a single model class
        model_attributes = {'__tablename__': 'test_data', '__table_args__': {'extend_existing': True}}  # Use a generic table name
        model_attributes['id'] = db.Column(db.Integer, primary_key=True)
        
        # Iterate through all groups and fields to add them to the model attributes
        for group in data['formGroups']:
            for field in group['fields']:
                field_name = field['name'].lower().replace(" ", "_")
                field_type = field['type']
                if field_type == 'text':
                    model_attributes[field_name] = db.Column(db.String(255))
                elif field_type == 'number':
                    model_attributes[field_name] = db.Column(db.Float)
                elif field_type == 'textarea':
                    model_attributes[field_name] = db.Column(db.Text)
                # Add more field types as needed
        
        # Create a single model class using the aggregated model attributes
        model_class = type('TestData', (db.Model,), model_attributes)
        dynamic_models['TestData'] = model_class
