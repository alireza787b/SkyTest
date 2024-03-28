import json
from app import db

def create_models_from_json(json_path):
    with open(json_path) as json_file:
        data = json.load(json_file)
        for group in data['formGroups']:
            fields = group['fields']
            model_attributes = {'__tablename__': group['groupTitle'].lower().replace(" ", "_")}
            model_attributes['id'] = db.Column(db.Integer, primary_key=True)
            for field in fields:
                field_name = field['name'].lower().replace(" ", "_")
                field_type = field['type']
                if field_type == 'text':
                    model_attributes[field_name] = db.Column(db.String(255))
                elif field_type == 'number':
                    model_attributes[field_name] = db.Column(db.Float)
                elif field_type == 'textarea':
                    model_attributes[field_name] = db.Column(db.Text)
                # Add more field types as needed
            model_class = type(group['groupTitle'].replace(" ", ""), (db.Model,), model_attributes)
            globals()[group['groupTitle'].replace(" ", "")] = model_class
