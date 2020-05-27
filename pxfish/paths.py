"""Functions for creating directories and directory paths"""

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
    return os.path.join(path, simplename(name))


def create_library_path(category_path, library_name):
    return create_named_path(
        os.path.join(category_path, 'libraries'),
        library_name
    )


def create_operation_path(category_path, operation_type_name):
    return create_named_path(
        os.path.join(category_path, 'operation_types'),
        operation_type_name
    )


def operation_type_code_names():
    return ['protocol', 'precondition', 'cost_model', 'documentation', 'test']

