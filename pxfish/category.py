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


def pull(*, session, path, name):
    """
    Retrieves all the Libraries and Operation Types within a category

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the path to where the files will be written
        name (String): the category name
    """
    operation_types = session.OperationType.where({"category": name})
    libraries = session.Library.where({"category": name})

    if not operation_types and not libraries:
        logging.error("Category {} was not found.".format(name))

    for op_type in operation_types:
        operation_type.write_files(session=session, path=path, operation_type=op_type)

    for lib in libraries:
        library.write_files(session=session, path=path, library=lib)


def push(*, session, path):
    """
    Finds and pushes all library and operation type files in a specific category

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the directory path for the category
    """
    category_entries = os.listdir(path)
    for directory_entry in category_entries:
        files = os.listdir(os.path.join(path, directory_entry))
        if directory_entry == 'libraries':
            for name in files:
                library.push(
                    session=session,
                    path=create_named_path(path, name, subdirectory='libraries')
                )
        elif directory_entry == 'operation_types':
            for name in files:
                operation_type.push(
                    session=session,
                    path=create_named_path(path, name, subdirectory='operation_types')
                )
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                directory_entry,
                path
            ))


def run_tests(*, session, path, name):
    """
    Finds all library and operation type files in a specific category

    Arguments:
        session (Session Object): Aquarium session object
        path (String): path to category directory
        name (String): the name of the category to be tested
    """
    category_entries = os.listdir(path) # lists, operation_types and libraries 

    for subdirectory_entry in category_entries:
        path = os.path.join(path, subdirectory_entry) # dir/category/operation_types 

        if subdirectory_entry == "libraries":
            logging.warning("Tests not available for libraries") 

        elif subdirectory_entry == "operation_types":
            files = os.listdir(path) # list op types rna_seq, make_media, etc.
            for filename in files:
                path = os.path.join(path, filename) # dir/category/operation_types/rna_seq
                operation_type.run_test(session=session, path=path, category=name, name=filename)
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                subdirectory_entry,
                path
            ))
