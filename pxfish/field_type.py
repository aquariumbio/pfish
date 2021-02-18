"""Functions for Creating Field Types and Allowable Field Types"""


def build(*, operation_type, definitions, role, session):
    """
    Adds defined field types to Operation Type

    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        role (String): input or output
        session (Session Object): Aquarium session object
    """
    field_types = []

    for field_type_definition in definitions[role + 's']:

        query = {
            'name': field_type_definition['name'],
            'parent_id': operation_type.id
        }
        field_type = session.FieldType.where(query)

        if field_type:
            field_types.append(field_type[0])
        else:
            ft = session.FieldType.new()
            ft.role = role
            ft.name = query['name']
            ft.ftype = 'sample'
            if field_type_definition['allowable_field_types']:
                ft.allowable_field_types = add_aft(
                            session=session, definitions=field_type_definition
                            )

            field_types.append(ft)

    operation_type.field_types = field_types

    session.utils.create_field_type(operation_type)


def add_aft(*, session, definitions):
    """
    Adds Sample and Object type names to Field Type Object

    Arguments:
        session (Session Object): Aquarium session object
        definitions (Dictionary): Data about Sample and Object types  
    """
    afts = []
    for aft in definitions['allowable_field_types']:

        sample_type = session.SampleType.new()
        object_type = session.ObjectType.new()

        sample_type.name = aft['sample_type']
        object_type.name = aft['object_type']
        afts.append({'sample_type': sample_type, 'object_type': object_type})
        breakpoint()
    return afts
