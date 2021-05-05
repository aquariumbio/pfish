"""
Functions for retrieving categories
"""
import logging
import os
import operation_type
import library
import object_type
import sample_type
from paths import create_named_path


def is_category(path):
    """Checks path to see if it leads to a category directory."""

    try:
        entries = os.listdir(path)
    except NotADirectoryError:
        logging.warning('%s is not a directory', path)
        return False

    return not set(entries).isdisjoint({'libraries', 'operation_types'})


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
        logging.error('Category %s was not found.', name)

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
    if not is_category(path):
        logging.warning('No valid pfish category at %s', path)
        return

    category_entries = os.listdir(path)

    for directory_entry in category_entries:
        try:
            files = os.listdir(os.path.join(path, directory_entry))
        except NotADirectoryError:
            logging.warning('%s is not a directory', directory_entry)
            continue

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
            logging.warning('Unexpected directory entry %s in %s',
                            directory_entry, path)


def run_tests(*, session, path, name, timeout: int = None):
    """
    Runs tests for all library and operation type files in a specific category.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): path to category
        name (String): name of the category to be tested
        timeout (Int): time (seconds) to wait for test result
    """
    # TODO: another place to catch NotADirectoryError and other errors
    category_entries = os.listdir(path)
    for subdirectory_entry in category_entries:

        if subdirectory_entry == 'libraries':
            logging.warning('Tests not available for libraries')

        elif subdirectory_entry == 'operation_types':
            path = os.path.join(path, subdirectory_entry)
            files = os.listdir(path)
            for filename in files:
                logging.info('Testing Operation Type %s', filename)
                entry_path = os.path.join(path, filename)
                operation_type.run_test(
                    session=session,
                    path=entry_path,
                    category=name,
                    name=filename,
                    timeout=timeout
                )
        else:
            logging.warning(
                'Unexpected directory entry %s in %s',
                subdirectory_entry,
                path
            )
