# models.py
from .db_init import dynamic_models

def get_test_data_model():
    return dynamic_models.get('TestData')

def get_procedure_model():
    return dynamic_models.get('Procedure')


def get_test_title_by_id(test_id: str) -> str:
    """Returns the title of a test given its ID, using the dynamic Test Data model."""
    TestModel = get_test_data_model()
    if TestModel:
        test = TestModel.query.filter_by(test_id=test_id).first()
        return getattr(test, 'test_title', None)
    return None

def get_test_id_by_title(test_title: str) -> str:
    """Returns the ID of a test given its title, using the dynamic Test Data model."""
    TestModel = get_test_data_model()
    if TestModel:
        test = TestModel.query.filter_by(test_title=test_title).first()
        return getattr(test, 'test_id', None)
    return None

def get_procedure_title_by_id(procedure_id: str) -> str:
    """Returns the title of a procedure given its ID, using the dynamic Procedure model."""
    ProcedureModel = get_procedure_model()
    if ProcedureModel:
        procedure = ProcedureModel.query.filter_by(procedure_id=procedure_id).first()
        return getattr(procedure, 'procedure_title', None)
    return None

def get_procedure_id_by_title(procedure_title: str) -> str:
    """Returns the ID of a procedure given its title, using the dynamic Procedure model."""
    ProcedureModel = get_procedure_model()
    if ProcedureModel:
        procedure = ProcedureModel.query.filter_by(procedure_title=procedure_title).first()
        return getattr(procedure, 'procedure_id', None)
    return None

def get_model_columns(model):
    """
    Retrieve the column names from an SQLAlchemy model in the order they're defined.
    """
    return [column.name for column in model.__table__.columns]
