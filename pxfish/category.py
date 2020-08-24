"""
Functions for retrieving categories
"""
import logging
import os
import operation_type
import library
from paths import create_named_path


def is_category(path): # come back to this
    """Checks path to see if it leads to a category directory."""
    if not os.path.isdir(path):
        return False

    entries = os.listdir(path)
    return set(entries) <= {'libraries', 'operation_types'}


def pull(*, session, path, name):
    """
    Retrieves all Libraries and Operation Types within a category.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the path where the files will be written
        name (String): the category name
    """
    operation_types = session.OperationType.where({"category": name})
    libraries = session.Library.where({"category": name})

    if not operation_types and not libraries:
        logging.error("Category {} was not found.".format(name))

    for op_type in operation_types:
        operation_type.write_files(session=session, path=path,
                                   operation_type=op_type)

    for lib in libraries:
        library.write_files(path=path, library=lib)


def push(*, session, path):
    """
    Finds all library and operation type files in a specific category.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the path the category
    """
    category_entries = os.listdir(path)
    for directory_entry in category_entries:
        files = os.listdir(os.path.join(path, directory_entry))
        if directory_entry == 'libraries':
            for name in files:
                library.push(
                    session=session,
                    path=create_named_path(
                            path, name, subdirectory='libraries')
                )
        elif directory_entry == 'operation_types':
            for name in files:
                operation_type.push(
                    session=session,
                    path=create_named_path(
                            path, name, subdirectory='operation_types')
                )
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                directory_entry,
                path
            ))


def run_tests(*, session, path, name):
    """
    Runs tests for all library and operation type files in a specific category.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): path to category
        name (String): name of the category to be tested
    """
    category_entries = os.listdir(path)
    for subdirectory_entry in category_entries:
        path = os.path.join(path, subdirectory_entry)

        if subdirectory_entry == "libraries":
            logging.warning("Tests not available for libraries")

        elif subdirectory_entry == "operation_types":
            files = os.listdir(path)
            print(files)
            for filename in files:
                entry_path = os.path.join(path, filename)
                operation_type.run_test(
                        session=session, path=entry_path,
                        category=name, name=filename)
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                subdirectory_entry,
                path
            ))
