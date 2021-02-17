"""Functions for Creating Field Types and Allowable Field Types"""

import logging

#field_type.create(
#                definitions=definitions, role='input',
#                operation_type=parent_object[0], session=session)
#
def create(*, operation_type, definitions, role, session):
    """
    Finds Field Types from Definition file
    If the types are not in the database, creates them

    Arguments:
        operation_type (): ot -- parent object
        definitions (): definition file
        role (): input or output
        session (Session Object): Aquarium session object
        path (String): Directory where files are to be found
    """
    field_types = []

    for field_type_definition in definitions['inputs']:
        if field_type_definition['allowable_field_types']:
            query = {
                'name': field_type_definition['name'],
                'parent_id': operation_type.id
            }
        # TODO: What happens if FTs have been added to your instance,
        # but they are not in the list
        field_type = session.FieldType.where(query)

        if field_type:
            field_types.append(field_type[0])
        else:
            ft = session.FieldType.new()
            ft.role = role
            ft.name = query['name']
            ft.ftype = 'sample'
            if field_type_definition['allowable_field_types']:
                ft.allowable_field_types = create_aft(session=session, definition=field_type_definition) 
                
            field_types.append(ft)

    operation_type.field_types = field_types

    session.utils.create_field_type(operation_type)


def create_aft(*, session, definition):
    """
    Run tests for specified operation type.

    Arguments:
        session (Session Object): Aquarium session object
        definition (String): name of the Operation Type to be tested
    """
    sample_type = session.SampleType.new()
    object_type = session.ObjectType.new()

    sample_type.name = definition['allowable_field_types'][0]['sample_type']
    object_type.name = definition['allowable_field_types'][0]['object_type']

    return [{'sample_type': smpl_type, 'object_type': obj_type}]
    #logging.info('Sending request to test %s', name)
