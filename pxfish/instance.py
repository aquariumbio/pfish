"""Functions to pull or push all files in a directory"""

import logging
import os
import category
import definition
import library
import operation_type
import object_type
import sample_type

from category import is_category


def pull(*, session, path):
    """
    Pulls OperationType and/or Library files from the Aquarium instance.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the path where the files will be written
    """
    operation_types = session.OperationType.all()
    libraries = session.Library.all()
    object_types = session.ObjectType.all()
    sample_types = session.SampleType.all()

    for op_type in operation_types:
        operation_type.write_files(
            session=session,
            path=path,
            operation_type=op_type)

    # TODO: might need to add session back in if we add library tests
    for lib in libraries:
        library.write_files(path=path, library=lib)

    for obj_type in object_types:
        object_type.write_files(path=path, object_type=obj_type)

    for sam_type in sample_types:
        sample_type.write_files(path=path, sample_type=sam_type)


def push(*, session, path):
    """
    Pushes all files in directory to instance.

    If the path isn't a directory, returns.

    Arguments:
        session (Session): Aquarium session object
        path (String): path to directory
    """
    if not os.path.isdir(path):
        logging.warning('Path %s is not a directory. Cannot push', path)
        return

    if is_category(path):
        category.push(session=session, path=path)
        return

    if definition.has_definition(path):
        def_dict = definition.read(path)
        if definition.is_operation_type(def_dict):
            operation_type.push(session=session, path=path)
        elif definition.is_library(def_dict):
            library.push(session=session, path=path)
        return

    categories = os.listdir(path)  # get all categories in the directory
    dir_entries = [entry for entry in categories
                   if os.path.isdir(os.path.join(path, entry))]

    if not dir_entries:
        logging.warning('Nothing to push in path %s', path)
        return

    for entry in dir_entries:
        # TODO: account for errors coming back from category?
        entry_path = os.path.join(path, entry)
        category.push(session=session, path=entry_path)


def run_tests(*, session, path):
    """
    Runs tests on all operation types in directory

    Arguments:
        session (Session): Aquarium session object
        path (String): path to directory
    """
    if not os.path.isdir(path):
        logging.warning(
            'Path %s is not a directory. Cannot run tests', path)
        return

    # TODO: change get operation type to work without a category?
    if definition.has_definition(path):
        def_dict = definition.read(path)
        if definition.is_operation_type(def_dict):
            operation_type.run_test(
                session=session,
                path=path,
                category=definition.category,
                name=definition.name
            )
        elif definition.is_library(def_dict):
            library.run_test(
                session=session,
                path=path,
                category=definition.category,
                name=definition.name
            )
        return

    if is_category(path):
        name = os.path.basename(path)
        category.run_tests(session=session, path=path, name=name)
        return

    entries = os.listdir(path)
    dir_entries = [entry for entry in entries if os.path.isdir(
        os.path.join(path, entry))]

    if not dir_entries:
        logging.warning('Nothing to test in path %s', path)
        return

    for entry in dir_entries:
        entry_path = os.path.join(path, entry)
        if is_category(entry_path):
            category.run_tests(session=session, path=entry_path, name=entry)
