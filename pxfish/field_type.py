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
        path
        session (Session Object): Aquarium session object
    """
    query = {
        'name': definition['name'],
        'parent_id': operation_type.id,
        'role': role
    }
    retrieved_field_type = session.FieldType.where(query)
    # [<FT Object>]
    # if ft exists, but not all afts exist, need to add the new ones
    # This is only ever dealing with One Field Type
    if retrieved_field_type:
        # if it has PCR, check for afts in definition
        for sample_obj_pair in retrieved_field_type['allowable_field_types']:
            if sample_obj_pair not in definition['allowable_field_types']:
                retrieved_field_type['allowable_field_types'].append(add_aft())

                # just want to add any that aren't already in there
                # for aft in definitions
                # if match with existing, append existing
                # if no match, append new
                # change add aft function so the iteration happens before
                # for aft in definition:
                # if aft in rtf.afts:
                    # continue
                # Else:
                    # create and append new aft
            # afts:
            # [<AFT Object>, <AFT Object>]
            # for each AFT Object -- .sample_type
            # gets <sample_type object> that you can then compare
            breakpoint()
        field_type = retrieved_field_type[0]
    else:
        field_type = session.FieldType.new()
        field_type.role = role
        field_type.array = definition['array']
        field_type.part = definition['part']
        field_type.routing = definition['routing']
        field_type.name = query['name']
        field_type.ftype = definition['ftype']
        field_type.allowable_field_types = [
            add_aft(
                aft_def=aft, session=session, path=path
                )
            for aft in definition['allowable_field_types']]
    return field_type


def build(*, operation_type, definitions, path, session):
    """
    Adds defined field types to Operation Type

    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        path
        session (Session Object): Aquarium session object
    """

    field_types = []
    # go through each FT definition
    for field_type_definition in definitions['inputs']:
        field_types.append( # add each one
            add_field_type(
                operation_type=operation_type,
                definition=field_type_definition,
                role='input',
                path=path,
                session=session
                )
        )

    for field_type_definition in definitions['outputs']:
        field_types.append(
                add_field_type(
                operation_type=operation_type,
                definition=field_type_definition,
                role='output', 
                path=path, 
                session=session)
        )

    operation_type.field_types = field_types

    session.utils.update_operation_type(operation_type)

    
def add_aft(*, aft_def, session, path):
    """
    Adds Sample and Object type names to Field Type Object

    Arguments:
        session (Session Object): Aquarium session object
        aft_def (Dictionary): Data about Sample and Object types
    """
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
    
    return {'sample_type': sampl_type, 'object_type': obj_type}


def equivalent(*, field_type, definition):
    """
    Compares a field type object with a definition.
    Arguments:
        field_type (Field Type Object): Type currently saved in Aquarium
        definition (Dictionary): Type Data saved locally
    Returns True if equivalent, False otherwise.
    """
    extant_field_types = field_type_list(
        field_types=[field_type])[0]
    
    # Check for matching info -- e.g. routing info, part etc.
    for key, ft_value in definition.items():
        # if the key leads to an AFT, compare those seperately
        if key == 'allowable_field_types':
            # if type exists in Aquarium, but not in def, don't push
            if len(extant_field_types['allowable_field_types']) > len(ft_value):
                return False
            # if type exists in both places
            # OR type only exists in definition file, push
            for sample_obj_pair in extant_field_types['allowable_field_types']:
                if sample_obj_pair not in ft_value:
                    return False
            continue

        if extant_field_types[key] != ft_value:
            return False
    return True


def check_for_conflicts(*, field_types, definitions, force):
    """
    Compares data in defintion file to data stored in an Aquarium Instance
    Arguments:
        field_types (List): Field Types retrieved from Aquarium
        defintions (Dictionary): data about field types stored in defintion file
        force (Boolean): if set, override conflict checks
    returns:
        conflicts (Dictionary): Field Types in both places with differing data (Conflict)
        local_diff (Dictionary): Field Types in definition file Only (Ones to Push)
        aquarium_diff_names (Dictionary): Field Types in Aquarium Only (Don't push)
    """
    # Map FT Name: <Ft Object> 
    type_map = {field_type.name: field_type for field_type in field_types}
    local_diff = dict()
    match_names = set()
    conflicts = dict()

    for definition in definitions:
        name = definition['name']
        if name in type_map:
            # if FT NAME is in definition, add it to match list
            match_names.add(name)
            # Then check for matching information fields
            if not force and not equivalent(
                    field_type=type_map[name],
                    definition=definition
                    ):

                    conflicts[name] = definition
        else:
            local_diff[name] = definition

    aquarium_diff_names = set(type_map.keys()).difference(match_names)

    return (aquarium_diff_names, conflicts, local_diff)


def types_valid(*, operation_type, definitions, force, session):
    """
    Compares an Operation Type's Field Types to those in the Definitions file
    If a Field Type only exists in Instance Type, stops push for Operation Type
    Arguments:
        operation_type (Operation Type): parent object
        definitions (Dictionary): data about field types
        force (Boolean): if set, overrides conflict checks
        session (Session Object): Aquarium session object
    """
    # get all the existing field types for the OT 
    field_types = session.FieldType.where({'parent_id': operation_type.id})

    # Check for AQ FTs no in def file, as well as conflicting info 
    missing_inputs, input_conflicts, valid_inputs = check_for_conflicts(
        field_types=[t for t in field_types if t.role == 'input'],
        definitions=definitions['inputs'],
        force=force
    )
    missing_outputs, output_conflicts, valid_outputs = check_for_conflicts(
        field_types=[t for t in field_types if t.role == 'output'],
        definitions=definitions['outputs'],
        force=force
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
#TODO This will let you override everything -- is that what I want it to do?
    if messages:
        messages = ' '.join(messages)
        logging.warning(
            'The Following Field Type Conflict(s) exist: \n %s. \
        Operation Type %s will not be pushed. To override this and replace instance data with data from your definition file, run push again with the force flag (-f, --force) set.',
        messages, operation_type.name
            )
        return False

    return True
