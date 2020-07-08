"""
Functions for retrieving categories
"""
import logging
from operation_type import (
    select_operation_type,
    write_operation_type
)
from library import (
    select_library,
    write_library
)


def get_category(aq, path, category):
    """
    Retrieves all the Libraries and Operation Types within a category

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the files will be written
        category (String): the category name
    """
    operation_types = aq.OperationType.where({"category": category})
    libraries = aq.Library.where({"category": category})
    pull(path, operation_types=operation_types, libraries=libraries)

# This is currently just a repeat of what happnes in all 
def pull(path, operation_types=[], libraries=[]):
    """
    Pulls OperationType and/or Library files from the Aquarium instance.

    Arguments:
        path (String): the path for the directory where files should be written
        operation_types (List): list of OperationTypes whose files to pull
        libraries (List): list of Libraries whose files to pull
    """
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

