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

from code_component import (
    create_code_object,
    create_code_objects
)
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
    """Checks whether definition file exists and is for an Operation Type """
    try:
        def_dict = definition.read(path)
    except NotADirectoryError:
        logging.warning('%s is not a directory', path)
        return False
    except FileNotFoundError:
        logging.warning('No definition file at %s', path)
        return False

    return definition.is_operation_type(def_dict)


def get_operation_type(*, session, category, name):
    """
    Retrieves a single Operation Type Object.

    Arguments:
        session (Session Object): Aquarium session object
        category (String): The category the OperationType is in
        name (String): The name of the OperationType to be retrieved
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

    return retrieved_operation_type[0]


def pull(*, session, path, category, name):
    """
    Retrieves operation type.
    Calls function to write associated files
    """
    retrieved_operation_type = get_operation_type(
        session=session,
        category=category, name=name)

    object_types = retrieved_operation_type.object_type()
    sample_types = retrieved_operation_type.sample_type()

    for obj_type in object_types:
        object_type.write_files(path=path, object_type=obj_type)

    for samp_type in sample_types:
        sample_type.write_files(path=path, sample_type=samp_type)

    write_files(session=session, path=path,
                operation_type=retrieved_operation_type)

# TODO Fix this so you're not passing an empty list as the default
def write_files(*, session, path, operation_type, sample_types=[], object_types=[]):
    """
    Writes the files associated with the operation_type to the path.

    Arguments:
        session (Session Object): Aquarium Session object
        path (String): the path to where the files will be written
        operation_type (OperationType): the operation type being written
    """
    logging.info('Writing operation type %s', operation_type.name)

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
            create_code_object(
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
    Creates new operation type on the Aquarium instance.
    Note: does not create the files locally, they need to be pulled.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the directory path where the new files will be written
        category (String): the category for the operation type
        name (String): name of the operation type
        field_types (List): field types associated with new operation type.
                            Defaults to empty list
    """
    code_objects = create_code_objects(session=session,
                                       component_names=all_component_names(),
                                       default_text=default_text)
    new_operation_type = session.OperationType.new(
        name=name,
        category=category,
        protocol=code_objects['protocol'],
        precondition=code_objects['precondition'],
        documentation=code_objects['documentation'],
        cost_model=code_objects['cost_model'],
        test=code_objects['test'])

    new_operation_type.field_types = field_types
    session.utils.create_operation_type(new_operation_type)


def push(*, session, path, force, component_names=all_component_names()):
    """
    Pushes files to the Aquarium instance

    Arguments:
        session (Session Object): Aquarium session object
        path (String): Directory where files are to be found
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
        create(session=session, path=path, category=definitions['category'],
               name=definitions['name'], default_text=False)
        parent_object = session.OperationType.where(query)

    if definitions['inputs'] or definitions['outputs']:
        # Check for Valid Field Types
        if not field_type.types_valid(
                definitions=definitions,
                operation_type=parent_object[0],
                force=force,
                session=session):
            return

        field_type.build(
                definitions=definitions,
                operation_type=parent_object[0], path=path, session=session)

    # TODO: Split out code creation to a seperate function
    for name in component_names:
        read_file = code_component.read(path=path, name=name)
        if read_file is None:
            return

        new_code = session.Code.new(
            name=name,
            parent_id=parent_object[0].id,
            parent_class=definitions['parent_class'],
            user_id=user_id,
            content=read_file
        )

        logging.info('pushing file %s', parent_object[0].name)

        session.utils.update_code(new_code)


def run_test(*, session, path, category, name):
    """
    Run tests for specified operation type.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): Path to file
        category (String): Category operation type is found in
        name (String): name of the Operation Type to be tested
    """
    logging.info('Sending request to test %s', name)
    push(
        session=session, path=path,
        component_names=test_component_names()
        )

    retrieved_operation_type = get_operation_type(
        session=session, category=category, name=name)

    response = session._aqhttp.get(
        "test/run/{}".format(retrieved_operation_type.id))

    write_test_response(response=response, path=path)
    parse_test_response(response=response, file_path=path)
