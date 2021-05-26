"""
Functions for pushing, pulling, and creating Operation Types in Aquarium.
"""

import logging
import os
import code_component
import definition
import field_type
import object_type
import sample_type

from definition import (
    write_definition_json,
)
from paths import (
    create_named_path,
    makedirectory
)
from protocol_test import (
    parse_test_response,
    write_test_response
)


def is_operation_type(path):
    """Checks whether definition file exists and is for an Operation Type"""
    try:
        def_dict = definition.read(path)
    except NotADirectoryError:
        logging.warning('%s is not a directory', path)
        return False
    except FileNotFoundError:
        logging.warning('No definition file at %s', path)
        return False

    return definition.is_operation_type(def_dict)


def get_associated_types(*, path, operation_type):
    """
    Retrieves object or sample types associated with the given operation type
    """

    object_types = operation_type.object_type()
    sample_types = operation_type.sample_type()

    for obj_type in object_types:
        if obj_type:
            object_type.write_files(path=path, object_type=obj_type)

    for samp_type in sample_types:
        if samp_type:
            sample_type.write_files(path=path, sample_type=samp_type)


def pull(*, session, path, category, name):
    """
    Retrieves operation type
    Passes operation type to write_files
    """
    retrieved_operation_type = session.OperationType.where(
        {
            'category': category,
            'name': name
        }
    )

    if not retrieved_operation_type:
        logging.warning(
            'No Operation Type named %s in Category %s',
            name, category)
        return

    write_files(session=session, path=path,
                operation_type=retrieved_operation_type[0])


def write_files(*, session, path, operation_type):
    """
    Writes the files associated with the operation_type to the path.

    Arguments:
        session (Session Object): Aquarium Session object
        path (String): the path to where the files will be written
        operation_type (OperationType): the operation type being written
    """
    logging.info('Writing operation type %s', operation_type.name)
    get_associated_types(path=path, operation_type=operation_type)

    category_path = create_named_path(path, operation_type.category)
    makedirectory(category_path)

    path = create_named_path(
        category_path, operation_type.name, subdirectory='operation_types')

    makedirectory(path)
    code_names = all_component_names()

    for name in code_names:
        code_object = operation_type.code(name)
        if not code_object:
            logging.warning(
                'Missing %s code for operation type %s -- creating file',
                operation_type.name, name)
            code_component.create_code_object(
                session=session,
                name=name,
                operation_type=operation_type
            )
            code_object = operation_type.code(name)

        file_name = "{}.rb".format(name)

        try:
            code_component.write(
                path=path,
                file_name=file_name,
                code_object=code_object
            )
        except OSError as error:
            logging.warning(
                'Error %s writing file %s for operation type %s',
                error, file_name, operation_type.name)
            continue
        except UnicodeError as error:
            logging.warning(
                'Encoding error %s writing file %s for operation type %s',
                error, file_name, operation_type.name)
            continue
    write_definition_json(
        os.path.join(path, 'definition.json'),
        operation_type
    )


def all_component_names():
    """Returns names of code objects associated with operation types."""
    return ['protocol', 'test', 'precondition', 'cost_model', 'documentation']


def test_component_names():
    """
    Returns names of operation type components needed when running a test.
    """
    return ['protocol', 'test']


def create(*, session, path, category, name, default_text=True, field_types=[]):
    """
    Creates a new operation type on the Aquarium instance.
    Note: does not create the files locally, they need to be pulled.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): The directory path where the new files will be written
        category (String): The category for the operation type
        name (String): The name of the operation type
        field_types (List): Field types associated with the new operation type.
                            Defaults to empty list
    """
    code_objects = code_component.create_code_objects(
        session=session,
        component_names=all_component_names(),
        default_text=default_text)

    new_operation_type = session.OperationType.new(
        name=name,
        category=category,
        protocol=code_objects['protocol'],
        precondition=code_objects['precondition'],
        documentation=code_objects['documentation'],
        cost_model=code_objects['cost_model'],
        test=code_objects['test']
        )

    new_operation_type.field_types = field_types
    session.utils.create_operation_type(new_operation_type)


def push(*, session, path, force=False, component_names=all_component_names()):
    """
    Pushes files to the Aquarium instance

    Arguments:
        session (Session Object): Aquarium session object
        path (String): Directory where files are to be found
        force (Boolean): If set, overrides conflict checks for Field Types
        component_names (List): Files to include as part of OT
    """
    if not is_operation_type(path):
        logging.warning('No Operation Type at %s', path)
        return

    definitions = definition.read(path)

    user_id = session.User.where({'login': session.login})
    query = {
        'category': definitions['category'],
        'name': definitions['name']
    }

    parent_object = session.OperationType.where(query)

    # TODO: Shouldn't finish create if there are FT conflicts
    if not parent_object:
        logging.info('Operation Type %s not found in instance, creating it now.', definitions['name'])
        create(session=session, path=path, category=definitions['category'],
               name=definitions['name'], default_text=False)
        parent_object = session.OperationType.where(query)


    if definition.has_field_types(definitions):
        if not force and not field_type.types_valid(
                definitions=definitions,
                operation_type=parent_object[0],
                session=session):
            return
        field_types = build_associated_types(
            definitions=definitions,
            operation_type=parent_object[0],
            session=session,
            path=path
            )

        parent_object[0].field_types = field_types
        session.utils.update_operation_type(parent_object[0])

    create_code_objects(
        component_names=component_names,
        parent_object=parent_object[0], user_id=user_id,
        session=session, path=path
        )


def build_associated_types(*, definitions, operation_type, session, path):
    """
    Creates any needed Field Types, AFTs and/or Sample or Object Types
    """
    field_types = definitions['inputs'] + definitions['outputs']
    allowable_field_types = definition.allowable_field_types(field_types)

    if allowable_field_types:
        field_type.check_sample_and_object_types(
            session=session,
            path=path,
            sample_object_pairs=allowable_field_types
            )

    field_type_list = field_type.build_field_type_list(
        definitions=definitions,
        operation_type=operation_type,
        path=path,
        session=session)

    return field_type_list


def create_code_objects(component_names, parent_object, user_id, session, path):
    """Creates updated code objects for Operation Type"""
    for name in component_names:
        read_file = code_component.read(path=path, name=name)
        if read_file is None:
            return

        new_code = session.Code.new(
            name=name,
            parent_id=parent_object.id,
            parent_class="OperationType",
            user_id=user_id,
            content=read_file
        )

        logging.info('pushing file %s for operation type %s', name, parent_object.name)
        session.utils.update_code(new_code)


def run_test(*, session, path, category, name, timeout: int = None):
    """
    Runs tests for specified operation type.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): Path to file
        category (String): Category operation type is found in
        name (String): Name of the Operation Type to be tested
        timeout (Int): Time (seconds) to wait for test result
    """
    logging.info('Sending request to test %s', name)
    push(
        session=session, path=path, force=False,
        component_names=test_component_names()
    )

    retrieved_operation_type = session.OperationType.where(
        {
            'category': category,
            'name': name
        }
    )

    if not retrieved_operation_type:
        logging.warning(
            'No Operation Type named %s in Category %s',
            name, category)

    response = session._aqhttp.get(
        "test/run/{}".format(retrieved_operation_type.id),
        timeout
    )

    write_test_response(response=response, path=path)
    parse_test_response(response=response, file_path=path)
