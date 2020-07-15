"""
Functions for pushing, pulling, and creating Operation Types in Aquarium.
"""

import json
import logging
import os
from paths import (
    create_named_path,
    create_library_path,
    makedirectory
)
from code import (
    create_code_objects,
    write_code
)
from definition import write_definition_json


def create_operation_path(category_path, operation_type_name):
    """
    Create a path for an operation type within the directory for a category.

    Note: does not create the directory.

    Arguments:
      category_path (string): the path for the category
      operation_type_name (string): the name of the operation type

    Returns:
      string: the path of the operation type
    """
    return create_named_path(
        os.path.join(category_path, 'operation_types'),
        operation_type_name
    )


def get_operation_type(aq, path, category, operation_type):
    """
    Retrieves a single Operation Type Object

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the file will be written
        category (String): The category the OperationType is in
        operation_type (String): The OperationType to be retrieved
    """
    retrieved_operation_type = aq.OperationType.where(
        {
            "category": category,
            "name": operation_type
        }
    )
    if not retrieved_operation_type:
        logging.warning(
            "No Operation Type named {} in Category {}".format(
                operation_type, category)
        )
        return
    write_files(path, retrieved_operation_type[0])


def write_files(path, operation_type):
    """
    Writes the files associated with the operation_type to the path.

    Arguments:
      path (string): the path to where the files will be written
      operation_type (OperationType): the operation type being written
    """
    logging.info("writing operation type {}".format(operation_type.name))

    category_path = create_named_path(path, operation_type.category)
    makedirectory(category_path)
    
    path = create_operation_path(category_path, operation_type.name)
    makedirectory(path)
    
    code_names = operation_type_code_names()

    for name in code_names:
        code_object = operation_type.code(name)
        if not code_object:
            logging.warning(
                "Missing {} code for operation type {}".format(
                    operation_type.name, name)
            )
            continue

        file_name = "{}.rb".format(name)
        try:
            write_code(path, file_name, code_object)
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

    write_definition_json(
        os.path.join(path, 'definition.json'),
        operation_type
    )


def operation_type_code_names():
    return ['protocol', 'precondition', 'cost_model', 'documentation', 'test']


def select_operation_type(aq, category_path, operation_type_name):
    """
    Locates the operation type to be pushed

    Arguments:
        aq (Session Object): Aquarium session object
        category_path (String): the directory path for the category
        operation_type_name (String): the name of the operation type
    """
    path = create_operation_path(category_path, operation_type_name)
    push(aq, path, operation_type_code_names())


def create(aq, path, category, operation_type_name):
    """
    Creates new operation type on the Aquarium instance.
    Note: does not create the files locally, they need to be pulled.

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the directory path where the new files will be written
        category (String): the category for the operation type
        operation_type_name (String): name of the operation type
    """
    code_objects = create_code_objects(aq, operation_type_code_names())
    new_operation_type = aq.OperationType.new(
        name=operation_type_name,
        category=category,
        protocol=code_objects['protocol'],
        precondition=code_objects['precondition'],
        documentation=code_objects['documentation'],
        cost_model=code_objects['cost_model'])
    new_operation_type.field_types = [] 
    aq.utils.create_operation_type(new_operation_type)


def push(aq, directory_path, component_names):
    """
    Pushes files to the Aquarium instance

    Arguments:
        aq (Session Object): Aquarium session object
        directory_path (String): Directory where files are to be found
        component_names (List): List of files to push
    """
    with open(os.path.join(directory_path, 'definition.json')) as f:
        definitions = json.load(f)

    for name in component_names:
        file_name = "{}.rb".format(name)
        try:
            with open(os.path.join(directory_path, file_name)) as f:
                read_file = f.read()

        # TODO: create test file if it doesn't exist?

        except FileNotFoundError as error:
            logging.warning(
                "Error {} writing file {} file does not exist".format(
                    error, file_name))
            return

        user_id = aq.User.where({"login": aq.login})

        query = {
            "category": definitions['category'],
            "name": definitions['name']
        }
        if name == 'source':
            parent_object = aq.Library.where(query)
            parent_type_name = 'library'
        else:
            parent_object = aq.OperationType.where(query)
            parent_type_name = 'operation type'

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

        new_code = aq.Code.new(
            name=name,
            parent_id=parent_object[0].id,
            parent_class=definitions['parent_class'],
            user_id=user_id,
            content=read_file
        )

        logging.info("writing file {}".format(parent_object[0].name))

        aq.utils.update_code(new_code)


def run_test(*, session, path, name):
    logging.error("testing is not currently supported")
    # raw code would be
    # result = session._aqhttp.get("test/run/{}".format(operation_type.id))
    pass
