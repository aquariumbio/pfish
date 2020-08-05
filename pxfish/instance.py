import category
import definition
import library
import logging
import operation_type
import os

from category import is_category


def pull(*, session, path):
    """
    Pulls OperationType and/or Library files from the Aquarium instance.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the path to where the files will be written
    """
    operation_types = session.OperationType.all()
    libraries = session.Library.all()
    for op_type in operation_types:
        operation_type.write_files(session=session, path=path, operation_type=op_type)

    for lib in libraries:
        library.write_files(session=session, path=path, library=lib)


def push(*, session, path):
    """
    """
    if not os.path.isdir(path):
        logging.warning("Path {} is not a directory. Cannot push".format(path))
        return

    if definition.has_definition(path):
        def_dict = definition.read(path)
        if definition.is_operation_type(def_dict):
            operation_type.push(session=session, path=path)
        elif definition.is_library(def_dict):
            library.push(session=session, path=path)
        return

    if is_category(path):
        category.push(session, path)
        return

    entries = os.listdir(path)
    dir_entries = [entry for entry in entries if os.path.isdir(entry)]
    if not dir_entries:
        logging.warning("Nothing to push in path {}".format(path))
        return

    for entry in dir_entries:
        entry_path = os.path.join(path, entry)
        if is_category(entry_path):
            category.push(session=session, path=entry_path)


def run_tests(*, session, path):
    if not os.path.isdir(path):
        logging.warning(
            "Path {} is not a directory. Cannot run tests".format(path))
        return

    if definition.has_definition(path):
        def_dict = definition.read(path)
        if definition.is_operation_type(def_dict):
            operation_type.run_test(session=session, path=path)
        elif definition.is_library(def_dict):
            library.run_test(session=session, path=path)
        return

    if is_category(path):
        category.run_test(session=session, path=path)
        return

    entries = os.listdir(path)
    dir_entries = [entry for entry in entries if os.path.isdir(entry)]
    if not dir_entries:
        logging.warning("Nothing to push in path {}".format(path))
        return

    for entry in dir_entries:
        entry_path = os.path.join(path, entry)
        if is_category(entry_path):
            category.run_test(session=session, path=entry_path)
