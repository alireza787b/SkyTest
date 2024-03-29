import json
from app import db
from config import JSON_PATH, PROCEDURES_JSON_PATH
dynamic_models = {}

def create_models_from_json(json_path, model_name, table_name):
    with open(json_path) as json_file:
        data = json.load(json_file)
        
        # Define attributes for a model class dynamically based on the provided table_name
        model_attributes = {'__tablename__': table_name, '__table_args__': {'extend_existing': True}}
        model_attributes['id'] = db.Column(db.Integer, primary_key=True)
        
        # Determine the appropriate group key ('formGroups' for tests, 'procedureGroups' for procedures)
        group_key = 'formGroups' if 'formGroups' in data else 'procedureGroups'
        
        # Iterate through all groups and fields to add them to the model attributes
        for group in data[group_key]:
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
        model_class = type(model_name, (db.Model,), model_attributes)
        dynamic_models[model_name] = model_class

# Example usage:
create_models_from_json(JSON_PATH, 'TestData', 'test_data')
create_models_from_json(PROCEDURES_JSON_PATH, 'Procedure', 'procedure_data')
