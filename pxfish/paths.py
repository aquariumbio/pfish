"""
Utilities for creating paths and directories
"""

import os
import re


def makedirectory(directory_name):
    """
    Create the directory with the given name.

    Arguments:
      directory_name (string): the name of the directory
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def simplename(name):
    """
    Convert operation/library name to a string for use as a file name.
    Replaces whitespace to underscores and changes characters to lowercase.

    Arguments:
      name (string): the name to convert

    Returns:
      string: the converted string
    """
    return re.sub(r'\W|^(?=\d)', '_', name).lower()


def create_named_path(path, name):
    """
    Create a path for a named object (operation type/library).
    Joins the canonical form of the object name to the base path.
    The canonical name is created using the simplename function.

    Note: does not create the directory.

    Arguments:
      path (string): the base path
      name (string): the name of the object

    Returns:
      string: the path of the named object
    """
    return os.path.join(path, simplename(name))


def create_library_path(category_path, library_name):
    """
    Create a path for a library within the directory for a category.

    Note: does not create the directory.

    Arguments:
      category_path (string): the path for the category
      library_name (string): the name of the library

    Returns:
      string: the path of the library
    """
    return create_named_path(
        os.path.join(category_path, 'libraries'),
        library_name
    )


def create_operation_path(category_path, operation_type_name):
    """
    Create a path for an operation type within the directory for a category.

    Note: does not create the directory.

    Arguments:
      category_path (string): the path for the category
      operation_type_name (string): the name of the operation type

    Returns:
      string: the path of the operation type
    """
    return create_named_path(
        os.path.join(category_path, 'operation_types'),
        operation_type_name
    )

