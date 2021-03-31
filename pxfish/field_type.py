"""Functions for Creating Field Types and Allowable Field Types"""

import logging
import sample_type
import object_type
from definition import (
        field_type_list
        )

def add_field_type(*, operation_type, definition, role, path, session):
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
        'parent_id': operation_type.id,
        'role': role
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
        ft.ftype = definition['ftype']
        ft.allowable_field_types = add_aft(
            definition=definition, path=path, session=session
        )
    return ft


def build(*, operation_type, definitions, path, session):
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
            role='input', path=path, session=session)
        )

    for field_type_definition in definitions['outputs']:
        field_types.append(add_field_type(
            operation_type=operation_type,
            definition=field_type_definition,
            role='output', path=path, session=session)
        )

    operation_type.field_types = field_types

    session.utils.update_operation_type(operation_type)


def add_aft(*, session, definition, path):
    """
    Adds Sample and Object type names to Field Type Object

    Arguments:
        session (Session Object): Aquarium session object
        definition (Dictionary): Data about Sample and Object types
    """
    afts = []
    for aft in definition['allowable_field_types']:
        if sample_type.exists(
                session=session,
                sample_type=aft['sample_type']
                ):
            sampl_type = session.SampleType.new()
            sampl_type.name = aft['sample_type']
        else:
            sampl_type = sample_type.create(
                session=session,
                sample_type=aft['sample_type'],
                path=path
                        )
        if object_type.exists(
                session=session,
                object_type=aft['object_type']):
            obj_type = session.ObjectType.new()
            obj_type.name = aft['object_type']
        else:
            obj_type = object_type.create(
                session=session,
                object_type=aft['object_type'],
                path=path
                )
        afts.append({'sample_type': sampl_type, 'object_type': obj_type})

    return afts


def equivalent(*, field_type, definition):
    """
    Compares a field type object with a definition.
    Arguments:
        field_type (Field Type Object): Type currently saved in Aquarium
        definition (Dictionary): Type Data saved locally
    Returns True if equivalent, False otherwise.
    """
    field_type_data = field_type_list(
            field_types=[field_type])
    for k, v in definition.items():
        if field_type_data[0][k] != v:
            return False
    return True


def check_for_conflicts(*, field_types, definitions):
    """
    Compares data in defintion file to data stored in an Aquarium Instance
    Arguments:
        field_types (List): Field Types retrieved from Aquarium
        defintions (Dictionary): data about field types stored in defintion file
    returns:
        conflicts (Dictionary): Field Types in both places with differing data (Conflict)
        local_diff (Dictionary): Field Types in definition file Only
        aquarium_diff_names (Dictionary): Field Types in Aquarium Only (Missing I/O)
    """
    type_map = {field_type.name: field_type for field_type in field_types}
    local_diff = dict()
    match_names = set()
    conflicts = dict()

    for definition in definitions:
        name = definition['name']
        if name in type_map:
            match_names.add(name)
            # TODO: Fix equivelance check so it will let you add ST and OT to existing FTs
            if not equivalent(field_type=type_map[name], definition=definition):
                conflicts[name] = definition
        else:
            local_diff[name] = definition

    aquarium_diff_names = set(type_map.keys()).difference(match_names)

    return (aquarium_diff_names, conflicts, local_diff)


def types_valid(*, operation_type, definitions, session):
    """
    Compares an Operation Type's Field Types to those in the Definitions file
    If a Field Type only exists in Instance Type, stops push for Operation Type
    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        session (Session Object): Aquarium session object
    """
    field_types = session.FieldType.where({'parent_id': operation_type.id})

    # Should also check for object and sample type conflicts
    missing_inputs, input_conflicts, valid_inputs = check_for_conflicts(
        field_types=[t for t in field_types if t.role == 'input'],
        definitions=definitions['inputs']
    )
    missing_outputs, output_conflicts, valid_outputs = check_for_conflicts(
        field_types=[t for t in field_types if t.role == 'output'],
        definitions=definitions['outputs']
    )

    messages = []

    if missing_inputs or missing_outputs:
        for conflict in missing_inputs:
            messages.append(f'Aquarium Field Type Input, {conflict}, \
            is not in your definition file.\n')
        for conflict in missing_outputs:
            messages.append(f'Aquarium Field Type Output, {conflict}, \
            is not in your definition file.\n')

    if input_conflicts or output_conflicts:
        for conflict in input_conflicts:
            messages.append(f'There is a data conflict between the Aquarium Field Type \
            Definition of Input, {conflict}, and your local definition\n')
        for conflict in output_conflicts:
            messages.append(f'There is a data conflict between the Aquarium Field Type \
            Definition of Output, {conflict}, and your local definition\n')

    if messages:
        messages = ' '.join(messages)
        logging.warning(
            'The Following Field Type Conflict(s) exist:\n %s. \
            Operation Type %s will not be pushed\n',
            messages, operation_type.name
            )
        return False

    return True
