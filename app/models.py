# models.py
from .db_init import dynamic_models

def get_test_data_model():
    return dynamic_models.get('TestData')

def get_procedure_model():
    return dynamic_models.get('Procedure')
