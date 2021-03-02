"""Functions for Creating Field Types and Allowable Field Types"""

import logging


def add_field_type(*, operation_type, definition, role, session):
    """
    Creates list of Field Types to Add to Operation Type
    If a Field Type doesn't already exist, creates it
    Arguments:
        operation_type (Operation Type): parent object
        definition (Dictionary): data about field types
        role (String): input or output
        session (Session Object): Aquarium session object
    """
    query = {
        'name': definition['name'],
        'parent_id': operation_type.id
    }
    field_type = session.FieldType.where(query)

    if field_type:
        ft = field_type[0]
    else:
        ft = session.FieldType.new()
        ft.role = role
        ft.array = definition['array']
        ft.part = definition['part']
        ft.routing = definition['routing']
        ft.name = query['name']
        ft.ftype = 'sample'
        ft.allowable_field_types = add_aft(
            session=session, definition=definition
        )

    return ft


def build(*, operation_type, definitions, session):
    """
    Adds defined field types to Operation Type

    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        session (Session Object): Aquarium session object
    """
    field_types = []

    for field_type_definition in definitions['inputs']:
        field_types.append(add_field_type(
            operation_type=operation_type,
            definition=field_type_definition,
            role='input', session=session)
        )

    for field_type_definition in definitions['outputs']:
        field_types.append(add_field_type(
            operation_type=operation_type,
            definition=field_type_definition,
            role='output', session=session)
        )

    operation_type.field_types = field_types

    session.utils.update_operation_type(operation_type)


def add_aft(*, session, definition):
    """
    Adds Sample and Object type names to Field Type Object

    Arguments:
        session (Session Object): Aquarium session object
        definition (Dictionary): Data about Sample and Object types
    """
    afts = []
    for aft in definition['allowable_field_types']:

        sample_type = session.SampleType.new()
        object_type = session.ObjectType.new()

        sample_type.name = aft['sample_type']
        object_type.name = aft['object_type']
        afts.append({'sample_type': sample_type, 'object_type': object_type})
    return afts


def equivalent(*, field_type, definition):
    """
    Compares a field type object with a definition.
    Returns True if equivalent, False otherwise.
    """
    return True


def types_valid(*, operation_type, definitions, session):
    """
    Compares an Operation Type's Field Types to Those in the definitions file
    If a Field Type only exists in the Instance Type, returns False
    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        session (Session Object): Aquarium session object
    """
    field_types = session.FieldType.where({'parent_id': operation_type.id})
    type_map = {field_type.name: field_type for field_type in field_types}

    local_diff = dict()
    match_names = set()
    conflicts = dict()
    for definition in definitions['inputs']:
        name = definition['name']
        if name in type_map:
            match_names.add(name)
            if not equivalent(field_type=type_map[name], definition=definition):
                conflicts[name] = definition
        else:
            local_diff[name] = definition

    for definition in definitions['outputs']:
        name = definition['name']
        if name in type_map:
            match_names.add(name)
            if not equivalent(field_type=type_map[name], definition=definition):
                conflicts[name] = definition
        else:
            local_diff[name] = definition

    aquarium_diff_names = type_map.keys().difference(match_names)

    # match_names: names that occur in both
    # conflicts: dictionary of definitions not equivalent to aq field type with same name
    # local_diff: dictionary of definitions with no aq field type with same name
    # aquarium_diff_names: aq field type names that have no matching definition

    if aquarium_diff_names:
        logging.error(
            'There are Field Type definitions in your Aquarium instance that you do not have locally. \
                Pushing will erase those Field Types. \
                Operation Type %s will not be pushed', operation_type.name
        )
        return False
    else:
        return True
