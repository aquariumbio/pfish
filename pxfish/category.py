"""
Functions for retrieving categories
"""
import logging
import os
from operation_type import (
    select_operation_type,
    write_operation_type
)
from library import (
    select_library,
    write_library
)


def pull_category(aq, path, category):
    """
    Retrieves all the Libraries and Operation Types within a category

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the files will be written
        category (String): the category name
    """
    operation_types = aq.OperationType.where({"category": category})
    libraries = aq.Library.where({"category": category})
    
    if not operation_types and not libraries:
        logging.error("Category {} was not found.".format(category))
    
    for operation_type in operation_types:
        write_operation_type(path, operation_type)

    for library in libraries:
        write_library(path, library)


def select_category(aq, category_path):
    """
    Finds all Libraries and Operation Types in a specific category

    Arguments:
        aq (Session Object): Aquarium session object
        category_path (String): the directory path for the category
    """
    category_entries = os.listdir(category_path)
    print(category_entries)
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

