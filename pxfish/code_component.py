"""
Functions for writing code to files, or creating code objects
"""
import logging
import os


def write(*, path, file_name, code_object):
    """
    Writes the content of the aquarium code object to the given path.

    Arguments:
      path (string): the path of the file to be written
      file_name (string): the name of the file to be written
      code_object (Code): the code object to be written
    """
    file_path = os.path.join(path, file_name)
    with open(file_path, 'w') as file:
        file.write(code_object.content)


def create_code_objects(*, session, component_names):
    """
    Creates code objects for each named component.

    Arguments:
        session (Session Object): Aquarium session object
        component_names (List): names of code components

    Returns:
        code_objects (Dictionary): Dictionary with component names as keys
        and Code objects as values.
    """
    code_objects = {}

    for name in component_names:
        default_content = add_default_content(name)
        code_objects[name] = session.Code.new(
            name=name, content=default_content)
    return code_objects


def add_default_content(name):
    """
    Retrieves default content for code files.

    Arguments:
        name (String): name of code file whose contents to retrieve
    """
    path = os.path.normpath(
        os.path.join(os.environ.get('SCRIPT_DIR') or '', 'protocol_templates')
    )
    return read(path=path, name=name)


def update_code_objects(component_names, parent_object, parent_class, user_id, session, path):
    """Replaces text of existing code objects with newest versions"""
    for name in component_names:
        read_file = read(path=path, name=name)
        if read_file is None:
            logging.warning('Code Component File %s was not found', name)
            return

        new_code = session.Code.new(
            name=name,
            parent_id=parent_object.id,
            parent_class=parent_class,
            user_id=user_id,
            content=read_file
        )

        logging.info('writing file %s to instance', parent_object.name)

        session.utils.update_code(new_code)


def create_code_object(*, session, name, operation_type):
    """
    Creates a single code object for an existing operation type.

    Arguments:
        session (Session Object): Aquarium session object
        name (String): name of the code object to be created
        operation_type (Operation Type): operation type code object links to
    """
# TODO: is this function needed?
    data = {}
    data['id'] = operation_type.id
    data['content'] = add_default_content(name)
    data['name'] = name

    logging.info('sending request for %s', operation_type.name)
    session._aqhttp.post("operation_types/code", json_data=data)


def read(*, path, name):
    """
    Reads file at given location.

    Arguments:
        path (String): path to file
        name (String): name of file

        Raises:
            FileNotFoundError: file not located on given path
    """
    file_name = "{}.rb".format(name)
    try:
        with open(os.path.join(path, file_name)) as file:
            return file.read()
    except FileNotFoundError as error:
        logging.warning(
            'Error %s reading expected code file %s', error, file_name)
        return None
