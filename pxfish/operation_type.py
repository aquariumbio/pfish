"""
Functions for pushing, pulling, and creating Operation Types in Aquarium.
"""

import json
import logging
import os
from paths import (
    create_named_path,
    create_operation_path,
    create_library_path,
    makedirectory
)
from code import (
        write_code
)
from definition import (
        write_definition_json,
)


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
    pull(path, operation_types=retrieved_operation_type)


def write_operation_type(path, operation_type):
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


def field_type_list(field_types, role):
    """
    Returns the sublist of field types with the given role.

    Arguments:
      field_types (list): the list of field types
      role (string): the role of field types to be returned

    Returns:
      list: the sublist of field_types that have the role
    """
    ft_list = []
    for field_type in field_types:
        if field_type.role == role:
            ft_ser = {
                "name": field_type.name,
                "part": field_type.part,
                "array": field_type.array,
                "routing": field_type.routing
            }
            ft_list.append(ft_ser)
    return ft_list

