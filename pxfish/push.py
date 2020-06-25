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
    Locates the Operation Type to be pushed

    Arguments:
        aq (Session Object): Aquarium session object
        category_path (String): the path to the category containing the Operation Type 
        operation_type_name (String): the Operation Type containing the files to be pushed
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
        category (String): The category that will contain the new Operation Type
        operation_type_name (String): name of the Operation Type
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


def create_code_objects(aq, component_names):
    """
    Creates code objects for each file associated with a Library or Operation Type

    Arguments:
        aq (Session Object): Aquarium session object
        component_names (List): Names of files for which code objects will be created
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
        category_path (String): the path to the category containing the Library or Operation Type
    """
    files = os.listdir(category_path)
    for file in files:
        if file == 'libraries':
            libraries = os.listdir(os.path.join(category_path, 'libraries'))
            for name in libraries:
                select_library(aq, category_path, name)
        elif file == 'operation_types':
            operation_types = os.listdir(os.path.join(category_path, 'operation_types'))
            for name in operation_types:
                select_operation_type(aq, category_path, name)
        else:
            pass

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

    # TODO; create test file if it doesn't exist?

        except FileNotFoundError as error:
            logging.warning(
                "Error {} writing file {} file does not exist".format(
                    error, file_name))
            return

        user_id = aq.User.where({"login": aq.login}) 
        
        if name == 'source':
            parent_object = aq.Library.where({"category": definitions['category'], "name": definitions['name']})
        else: 
            parent_object = aq.OperationType.where({"category": definitions['category'], "name": definitions['name']})
       
        
        if not parent_object:
            logging.warning(
                 "There is no database entry for {} in category {} in your database".format(
                     definitions['category'], definitions['name']))
            return 
        
        new_code = aq.Code.new(
            name=name,
            parent_id=parent_object[0].id,
            parent_class=definitions['parent_class'],
            user_id=user_id,
            content=read_file
        )
        
        logging.info("writing file {}".format(parent_object.name))
        
        aq.utils.update_code(new_code)
