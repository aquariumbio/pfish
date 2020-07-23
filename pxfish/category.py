"""
Functions for retrieving categories
"""
import logging
import os
import operation_type
import library
from paths import create_named_path


def is_category(path):
    if not os.path.isdir(path):
        return False

    entries = os.listdir(path)
    return set(entries) <= {'libraries', 'operation_types'}


def pull_category(session, path, category):
    """
    Retrieves all the Libraries and Operation Types within a category

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the path to where the files will be written
        category (String): the category name
    """
    operation_types = session.OperationType.where({"category": category})
    libraries = session.Library.where({"category": category})

    if not operation_types and not libraries:
        logging.error("Category {} was not found.".format(category))

    for op_type in operation_types:
        operation_type.write_files(path, op_type)

    for lib in libraries:
        library.write_files(path, lib)


def push(session, category_path):
    """
    Finds and pushes all library and operation type files in a specific category

    Arguments:
        session (Session Object): Aquarium session object
        category_path (String): the directory path for the category
    """
    category_entries = os.listdir(category_path)
    for directory_entry in category_entries:
        files = os.listdir(os.path.join(category_path, directory_entry))
        if directory_entry == 'libraries':
            for name in files:
                library.push(
                    session,
                    library.create_library_path(category_path, name)
                )
        elif directory_entry == 'operation_types':
            for name in files:
                operation_type.push(
                    session,
                    operation_type.create_operation_path(category_path, name)
                )
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                directory_entry,
                category_path
            ))


def get_tests(*, session, category):
    """
    Finds all library and operation type files in a specific category

    Arguments:
        session (Session Object): Aquarium session object
        category_path (String): the directory path for the category
    """
    operation_types = session.OperationType.where({"category": category})
    
    for op_type in operation_types:
        logging.info("Testing Operation Type {}.".format(op_type.name))
        operation_type.run_test(session, op_type)


