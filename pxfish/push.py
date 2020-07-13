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
    Locates the library to be pushed

    Arguments:
        aq (Session Object): Aquarium session object
        category_path (String): the path to the category containing the library
        library (string): the Library containing the files to be pushed
    """

    path = create_library_path(category_path, library_name)
    push(aq, path, ['source'])


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


def create_new_operation_type(aq, path, category, operation_type_name):
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
    new_operation_type.field_types = {}
    aq.utils.create_operation_type(new_operation_type)


def create_code_objects(aq, component_names):
    """
    Creates code objects for each named component.

    Arguments:
        aq (Session Object): Aquarium session object
        component_names (List): names of code components
    """
    code_objects = {}
    for name in component_names:
        code_objects[name] = aq.Code.new(name=name, content='')
    return code_objects


def select_category(aq, category_path):
    """
    Finds all Libraries and Operation Types in a specific category

    Arguments:
        aq (Session Object): Aquarium session object
        category_path (String): the directory path for the category
    """
    category_entries = os.listdir(category_path)
    for directory_entry in category_entries:
        files = os.listdir(os.path.join(category_path, directory_entry))
        if directory_entry == 'libraries':
            for name in files:
                select_library(aq, category_path, name)
        elif directory_entry == 'operation_types':
            for name in files:
                select_operation_type(aq, category_path, name)
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                directory_entry,
                category_path
            ))


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
