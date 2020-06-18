"""
Functions for pushing Library and Operation Type files to Aquarium
"""

import json
import logging
import os
from operation_types import (
    operation_type_code_names
)
from paths import (
    create_library_path,
    create_operation_path
)


def select_library(aq, category_path, library_name):
    """
    Locates the library files to be pushed

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path for the directory where files should be written
        category (String): the category where the Library is to be found
        library (string): the Library whose files will be pushed
    """
    path = create_library_path(category_path, library_name)
    push(aq, path, ['source'])


def select_operation_type(aq, category_path, operation_type_name):
    """
    Locates the Operation Type whose files will be pushed

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path for the directory where files should be written
        category (String): the category where the Library is to be found
        library (string): the Library whose files will be pushed
    """
    path = create_operation_path(category_path, operation_type_name)
    push(aq, path, operation_type_code_names())


def create_new_operation_type(aq, path, category, operation_type_name):
    """
    Creates new operation type on the Aquarium instance.
    Note: does not create the files locally, they need to be pulled.

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the directory path where the new files will be written
        category (String): The category that will contain the operation type
        operation_type_name (String): name of the operation type
    """
    code_objects = create_code_objects(
        aq, category, operation_type_code_names())
    new_operation_type = aq.OperationType.new(
        name=operation_type_name,
        category=category,
        protocol=code_objects['protocol'],
        precondition=code_objects['precondition'],
        documentation=code_objects['documentation'],
        cost_model=code_objects['cost_model'])
    new_operation_type.field_types = {}
    aq.utils.create_operation_type(new_operation_type)


def create_code_objects(aq, category, component_names):
    code_objects = {}
    for name in component_names:
        code_objects[name] = aq.Code.new(name=name, content='')
    return code_objects


def push(aq, directory, component_names):
    """
    Pushes files to the Aquarium instance

    Arguments:
        aq (Session Object): Aquarium session object
        directory (String): Directory where files are to be found
        files_to_write (List): List of files to push
    """
    with open(os.path.join(directory, 'definition.json')) as f:
        definitions = json.load(f)
    print("hello")
    for name in component_names:
        file_name = "{}.rb".format(name)
        try:
            with open(os.path.join(directory, file_name)) as f:
                read_file = f.read()

        except FileNotFoundError as error:
            logging.warning(
                "Error {} writing file {} file does not exist".format(
                    error, file_name))
            continue

        if name == 'source':
            local_id = aq.Library.where({"category": definitions['category'], "name": definitions['name']})
            user_id = local_id[0].source.user_id
        else: 
            local_id = aq.OperationType.where({"category": definitions['category'], "name": definitions['name']})
            user_id = local_id[0].protocol.user_id

        new_code = aq.Code.new(
            name=name,
            parent_id=local_id[0].id,
            parent_class=definitions['parent_class'],
            user_id=user_id,
            content=read_file
        )

        aq.utils.update_code(new_code)
