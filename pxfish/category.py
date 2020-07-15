"""
Functions for retrieving categories
"""
import logging
import os
import operation_type
import library


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

    for op_type in operation_types:
        operation_type.write_files(path, op_type)

    for lib in libraries:
        library.write_files(path, lib)


def select_category(aq, category_path):
    """
    Finds all library and operation type files in a specific category

    Arguments:
        aq (Session Object): Aquarium session object
        category_path (String): the directory path for the category
    """
    category_entries = os.listdir(category_path)
    for directory_entry in category_entries:
        files = os.listdir(os.path.join(category_path, directory_entry))
        if directory_entry == 'libraries':
            for name in files:
                library.select_library(aq, category_path, name)
        elif directory_entry == 'operation_types':
            for name in files:
                operation_type.select_operation_type(aq, category_path, name)
        else:
            logging.warning("Unexpected directory entry {} in {}".format(
                directory_entry,
                category_path
            ))


def run_test(*, session, path):
    logging.error("category tests are not currently available")
