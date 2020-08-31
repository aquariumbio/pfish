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
    write_definition_json
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
            "No Operation Type named {} in Category {}".format(
                name, category)
        )
        return

    return retrieved_operation_type[0]


def pull(*, session, path, category, name):
    """Retrieves operation types, and calls function to write the files"""
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
    logging.info("writing operation type {}".format(operation_type.name))

    category_path = create_named_path(path, operation_type.category)
    makedirectory(category_path)

    path = create_named_path(
        category_path, operation_type.name, subdirectory='operation_types')

    makedirectory(path)
    code_names = operation_type_code_names()

    write_definition_json(
        os.path.join(path, 'definition.json'),
        operation_type
    )

    for name in code_names:
        code_object = operation_type.code(name)

        if not code_object and name != "test":
            logging.warning(
                "Missing {} code for operation type {} -- creating file".format(
                    operation_type.name, name)
            )

            create_code_object(
                    session=session,
                    name=name,
                    operation_type=operation_type
                    )

    # TODO: add something so it pulls the new text once it creates the file
        file_name = "{}.rb".format(name)

        try:
            code.write(path=path, file_name=file_name, code_object=code_object)
        except OSError as error:
            logging.warning(
                "Error {} writing file {} for operation type {}".format(
                    error, file_name, operation_type.name))
            continue
        except UnicodeError as error:
            message = "Encoding error {} writing file {} for operation type {}"
            logging.warning(
                message.format(
                    error, file_name, operation_type.name))
            continue


def operation_type_code_names():
    """Returns names of code objects associated with operation types."""
    return ['protocol', 'precondition', 'cost_model', 'documentation', 'test']


def create(*, session, path, category, name):
    """
    Creates new operation type on the Aquarium instance.
    Note: does not create the files locally, they need to be pulled.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the directory path where the new files will be written
        category (String): the category for the operation type
        name (String): name of the operation type
    """
    code_objects = create_code_objects(session=session, 
                                        component_names=operation_type_code_names())
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
        logging.warning(
            "No {} {}/{} on {}".format(
                parent_type_name,
                definitions['category'],
                definitions['name'],
               # TODO: make the following specific to user instance
                "Aquarium instance"
            )
        )
        return

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

        logging.info("writing file {}".format(parent_object[0].name))

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
    logging.info("Sending request for {}".format(name))

    push(session=session, path=path)

    retrieved_operation_type = get_operation_type(
                                session=session, category=category, name=name)

    response = session._aqhttp.get("test/run/{}".format(retrieved_operation_type.id))
    parse_test_response(response)
    return
