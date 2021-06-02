"""Functions for Creating Field Types and Allowable Field Types"""

import logging
import sample_type
import object_type
from definition import (
        serialize_field_types
        )


def build_field_type_list(*, operation_type, definitions, force=False, session):
    """
    Creates a list of Field Type objects to add to Operation Type

    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        session (Session Object): Aquarium session object

    Returns:
        List of Field Types
    """

    field_types = []
    # TODO: Simplify this so it's not so repetative
    for field_type_definition in definitions['inputs']:
        field_types.append(
            build_field_type(
                operation_type=operation_type,
                definition=field_type_definition,
                role='input',
                force=force,
                session=session
                )
        )

    for field_type_definition in definitions['outputs']:
        field_types.append(
            build_field_type(
                operation_type=operation_type,
                definition=field_type_definition,
                role='output',
                force=force,
                session=session)
        )

    return field_types


def build_field_type(*, operation_type, definition, role=None, force=False, session):
    """
    Retrieves or Creates Field Type Objects

    Arguments:
        operation_type (Operation Type): parent object
        definition (Dictionary): data about field types
        role (String): input or output
        path (String): path to operation type
        session (Session Object): Aquarium session object

    Returns:
        Field Type object
    """
    query = {
        'name': definition['name'],
        'parent_id': operation_type.id,
        'role': role,
    }

    aquarium_field_type = session.FieldType.where(query)

    if aquarium_field_type:
        field_type = aquarium_field_type[0]

        if force:
            aquarium_field_type = update(
                definition=definition,
                role=role,
                field_type=field_type
                )
        all_afts = build_aft_list(
            session=session,
            field_type=field_type,
            definition=definition
            )

        field_type.allowable_field_types = all_afts

    else:
        field_type = create(definition=definition, role=role, session=session)
        field_type.allowable_field_types = [
            build_aft(
                aft_def=aft, session=session
                )
            for aft in definition['allowable_field_types']]

    return field_type


def build_aft_list(*, session, field_type, definition):
    """
    Creates a list of existing and new AFTs

    Arguments:
        field_type (Field Type Object): the field type
        definition (Dictionary): data about field types
        session (Session Object): Aquarium session object

    Returns:
        List of all AFTs for Field Type
    """
    all_afts = field_type.allowable_field_types # afts connected to pydent object

    extant_afts = serialize_field_types(field_types=[field_type])[0]['allowable_field_types']

    for sample_obj_pair in definition['allowable_field_types']:
        if sample_obj_pair not in extant_afts:
            new_aft = build_aft(aft_def=sample_obj_pair, session=session)
            all_afts.append(new_aft)

    return all_afts


def build_aft(*, aft_def, session):
    """
    Adds Sample and Object Type objects to list of AFTs

    Arguments:
        session (Session Object): Aquarium session object
        aft_def (Dictionary): Data about Sample and Object types
    """
    sampl_type = session.SampleType.new()
    sampl_type.name = aft_def['sample_type']

    obj_type = session.ObjectType.new()
    obj_type.name = aft_def['object_type']

    return {'sample_type': sampl_type, 'object_type': obj_type}


def create(*, definition, role=None, session):
    """Creates New Field Type Proxy Object"""
    field_type = session.FieldType.new()
    field_type = update(definition=definition, role=role, field_type=field_type)
    return field_type


def update(*, definition, role=None, field_type):
    """
    Updates Field Type Data based on Defintion File
    Only runs for newly created field types or
    if Force Flag is set
    """
    field_type.role = role
    field_type.name = definition.get('name')
    field_type.part = definition.get('part', None)
    field_type.array = definition.get('array', None)
    field_type.routing = definition.get('routing', None)
    field_type.ftype = definition.get('ftype', 'sample')
    field_type.choices = definition.get('choices', None)
    field_type.required = definition.get('required', None)
    return field_type


def check_sample_and_object_types(*, session, path, sample_object_pairs):
    """
    Checks if all sample and object types in definition file exist in Aquarium
 
    Arguments:
        sample_object_pairs (List): List of sample/object pairs
        session (Session Object): Aquarium session object
        path (String): path to Operation Type
    """

    smpl_types = {aft['sample_type'] for aft in sample_object_pairs}
    obj_types = {aft['object_type'] for aft in sample_object_pairs}

    for smpl_type in smpl_types:
        if not sample_type.exists(session=session, sample_type=smpl_type):
            sample_type.create(
                session=session,
                sample_type=smpl_type,
                path=path
            )

    for obj_type in obj_types:
        if not object_type.exists(session=session, object_type=obj_type):
            object_type.create(
                session=session,
                object_type=obj_type,
                path=path
            )


def equivalent(*, aquarium_field_type, definition):
    """
    Compares an Aquarium field type object with its local definition

    Arguments:
        field_type (Field Type Object): Type currently saved in Aquarium
        definition (Dictionary): Type Data saved locally

    Returns:
        diff(Dictionary): Details on what data differs, if any
    """
    aquarium_field_type = serialize_field_types(
        field_types=[aquarium_field_type])[0]

    all_keys = aquarium_field_type.keys() | definition.keys()

    diff = {}
    for key in all_keys:
        aquarium_values = aquarium_field_type.get(key, None)
        local_values = definition.get(key, None)
        if aquarium_values != local_values:
            diff[key] = [aquarium_values, local_values]

    return diff


def check_for_conflicts(*, aquarium_field_types, definitions):
    """
    Compares data in definition file to data stored in an Aquarium Instance

    Arguments:
        aquarium_field_types (List): Field Types retrieved from Aquarium
        definitions (List): data about field types stored in definition file

    Returns:
        conflicts (Dictionary): Field Types in both places with differing data (Conflict)
        types_missing_locally (Dictionary): Field Types in Aquarium Only (Don't push)
        new_types (Dictionary): Local Field Types to create in Aquarium
    """
    aquarium_type_map = {field_type.name: field_type for field_type in aquarium_field_types}
    # TODO fix this so it's not repetative -- just have a function that gets things in right format
    local_type_map = {field_type['name']: field_type for field_type in definitions}

    new_types = dict()
    match_names = set()
    conflicts = dict()

    for aq_ft_name in aquarium_type_map:
        if aq_ft_name in local_type_map.keys():
            match_names.add(aq_ft_name)
            diff = equivalent(
                aquarium_field_type=aquarium_type_map[aq_ft_name],
                definition=local_type_map[aq_ft_name]
            )
            if diff:
                conflicts[aq_ft_name] = diff
        else:
            new_types[aq_ft_name] = local_type_map.get(aq_ft_name, None)

    types_missing_locally = set(aquarium_type_map.keys()).difference(match_names)

    return (types_missing_locally, conflicts, new_types)


def types_valid(*, operation_type, definitions, session):
    """
    Compares an Operation Type's Field Types to those in the Definitions file
    Reports conflicts to user

    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        session (Session Object): Aquarium session object

    Returns:
        bool (type validity)
    """
    aquarium_field_types = session.FieldType.where({'parent_id': operation_type.id})

    missing_inputs, input_conflicts, valid_inputs = check_for_conflicts(
        aquarium_field_types=[t for t in aquarium_field_types if t.role == 'input'],
        definitions=definitions['inputs'],
    )

    missing_outputs, output_conflicts, valid_outputs = check_for_conflicts(
        aquarium_field_types=[t for t in aquarium_field_types if t.role == 'output'],
        definitions=definitions['outputs'],
    )
 # TODO: Update & Simplify Messages
    messages = []

    if missing_inputs or missing_outputs:
        for conflict in missing_inputs:
            messages.append(
                (f'Aquarium Field Type Input, "{conflict}", '
                 'is not in your local definition file.\n')
            )
        for conflict in missing_outputs:
            messages.append((f'Aquarium Field Type Output, "{conflict}",'
                             'is not in your local definition file.\n'))

    if input_conflicts or output_conflicts:
        for conflict, details in input_conflicts.items():
            messages.append(
                ('There are one or more data conflicts between the Aquarium Field Type '
                 f'Definition of Input, "{conflict}", and your local definition.\n')
                )

            for detail, difference in details.items():
                messages.append(
                        f'Field "{detail}": aquarium value: "{difference[0]}", \nlocal value:  "{difference[1]}"\n')

        for conflict, details in output_conflicts.items():
            messages.append(
                ('There are one or more data conflicts between the Aquarium Field Type '
                 f'Definition of Output, "{conflict}", and your local definition.\n')
                )

            for detail, difference in details.items():
                messages.append(
                        f'Field "{detail}": aquarium value: "{difference[0]}", local value:  "{difference[1]}"\n')

    if messages:
        messages = ' '.join(messages)
        logging.warning(
            '\nThe Following Field Type Conflict(s) exist: \n %s', messages)
        logging.warning(
            'Operation Type "%s" will not be pushed.', operation_type.name)
        logging.info(
            'To override this and replace instance data with data from your definition file,\n \
            push the operation type with the force flag (-f, --force) set.')
        return False

    return True
