import json


def load_form_structure(structure_json):
    """Loads the form structure from a JSON file."""
    with open(structure_json, 'r') as json_file:
        return json.load(json_file)