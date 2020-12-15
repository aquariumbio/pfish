"""
Utilities for creating paths and directories
"""

import os
import re


def makedirectory(directory_name):
    """
    Creates the directory with the given name.

    Arguments:
      directory_name (String): the name of the directory
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)


def simplename(name):
    """
    Converts operation/library name to a string for use as a file name.
    Replaces whitespace to underscores and changes characters to lowercase.

    Arguments:
      name (string): the name to convert

    Returns:
      string: the converted string
    """
    return re.sub(r'\W|^(?=\d)', '_', name).lower()


def create_named_path(path, name, subdirectory=None):
    """
    Creates a path for a named object (operation type/library).
    Joins the canonical form of the object name to the base path.
    The canonical name is created using the simplename function.

    Note: does not create the directory.

    Arguments:
      path (String): the base path
      name (String): the name of the object
      subdirectory (String): name for subdirectory, if any (default=None)

    Returns:
      string: the path of the named object
    """
    if subdirectory:
        path = os.path.join(path, subdirectory)
    return os.path.join(path, simplename(name))
