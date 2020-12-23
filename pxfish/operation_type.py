"""
Functions for pushing, pulling, and creating Operation Types in Aquarium.
"""

import logging
import os
import code
import definition

from code import (
    create_code_object,
    create_code_objects
)
from definition import (
    write_definition_json,
    has_definition
)
from paths import (
    create_named_path,
    makedirectory
)
from protocol_test import (
    parse_test_response
)


def is_operation_type(path):
    if not os.path.isdir(path):
        return False

    try:
        def_dict = definition.read(path)
    except FileNotFoundError:
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
            "category": category,
            "name": name
        }
    )
    if not retrieved_operation_type:
        logging.warning(
            'No Operation Type named %s in Category %s',
            name, category)
        return

    return retrieved_operation_type[0]


def pull(*, session, path, category, name):
    """Retrieves operation type, and calls function to write the associated files"""
    retrieved_operation_type = get_operation_type(
        session=session,
        category=category, name=name)
    write_files(session=session, path=path,
                operation_type=retrieved_operation_type)


def write_files(*, session, path, operation_type):
    """
    Writes the files associated with the operation_type to the path.

    Arguments:
        session (Session Object): Aquarium Session object
        path (String): the path to where the files will be written
        operation_type (OperationType): the operation type being written
    """
    logging.info('writing operation type %s', operation_type.name)

    category_path = create_named_path(path, operation_type.category)
    makedirectory(category_path)

    path = create_named_path(
        category_path, operation_type.name, subdirectory='operation_types')

    makedirectory(path)
    code_names = operation_type_code_names()

    for name in code_names:
        code_object = operation_type.code(name)
        if not code_object:
            logging.warning(
                'Missing %s code for operation type %s -- creating file', operation_type.name, name)
            create_code_object(
                session=session,
                name=name,
                operation_type=operation_type
            )
            code_object = operation_type.code(name)

        file_name = "{}.rb".format(name)

        try:
            code.write(path=path, file_name=file_name, code_object=code_object)
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


def operation_type_code_names():
    """Returns names of code objects associated with operation types."""
    return ['protocol', 'precondition', 'cost_model', 'documentation', 'test']


def create(*, session, path, category, name, default_text=True):
    """
    Creates new operation type on the Aquarium instance.
    Note: does not create the files locally, they need to be pulled.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the directory path where the new files will be written
        category (String): the category for the operation type
        name (String): name of the operation type
    """
    # set this method so it will only create the objects you need? Or else do that in the create_code_objects part
    # and call create_code_objects with defaults=True where alternative is passing your own text from files
    # when this is called, you can say whether to pull from the file or to use defaults for each object
    code_objects = create_code_objects(session=session,
                                       component_names=operation_type_code_names(),
                                       default_text=default_text)
    new_operation_type = session.OperationType.new(
        name=name,
        category=category,
        protocol=code_objects['protocol'],
        precondition=code_objects['precondition'],
        documentation=code_objects['documentation'],
        cost_model=code_objects['cost_model'],
        test=code_objects['test'])
    new_operation_type.field_types = []
    session.utils.create_operation_type(new_operation_type)


def push(*, session, path):
    """
    Pushes files to the Aquarium instance

    Arguments:
        session (Session Object): Aquarium session object
        path (String): Directory where files are to be found
    """
    if not definition.has_definition(path):
        logging.warning("A Definition file is required to push to aquarium")
        return

    definitions = definition.read(path)

    user_id = session.User.where({"login": session.login})
    query = {
        "category": definitions['category'],
        "name": definitions['name']
    }

    parent_object = session.OperationType.where(query)
    parent_type_name = 'operation type'
    component_names = operation_type_code_names()

# TODO: Change so it only pushes test file when testing

    if not parent_object:
        create(session=session, path=path, category=definitions['category'],
               name=definitions['name'], default_text=False)
        parent_object = session.OperationType.where(query)

    for name in component_names:
        read_file = code.read(path=path, name=name)
        if read_file is None:
            return

        new_code = session.Code.new(
            name=name,
            parent_id=parent_object[0].id,
            parent_class=definitions['parent_class'],
            user_id=user_id,
            content=read_file
        )

        logging.info('writing file %s', parent_object[0].name)

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
    logging.info('Sending request for %s', name)

    push(session=session, path=path)

    retrieved_operation_type = get_operation_type(
        session=session, category=category, name=name)

    response = session._aqhttp.get(
        "test/run/{}".format(retrieved_operation_type.id))
    parse_test_response(response)
    # return
