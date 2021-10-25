"""
Functions for pushing, pulling, and creating Library files.
"""

import logging
import os
import code_component
import definition

from paths import (
    create_named_path,
    makedirectory
)
from definition import (
    write_library_definition_json
)


def is_library(path):
    """Checks whether definition file exists and is for a library"""

    try:
        def_dict = definition.read(path)
    except NotADirectoryError:
        logging.warning('%s is not a directory', path)
        return False
    except FileNotFoundError:
        logging.warning('No definition file at %s', path)
        return False

    return definition.is_library(def_dict)


def pull(*, session, path, category, name):
    """
    Retrieves a single Library Object.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the path where the file will be written
        category (String): The category the Library is in
        name (String): The name of the Library to be retrieved
    """
    retrieved_library = session.Library.where(
        {
            "category": category,
            "name": name
        }
    )
    if not retrieved_library:
        logging.warning(
            'No Library named %s in Category %s', name, category)
        return

    write_files(path=path, library=retrieved_library[0])


def get_component_names():
    """Gets code file names associated with library"""
    return ['source']


def write_files(*, path, library):
    """
    Writes the files for the library to the path.

    Arguments:
      path (string): the path of the file to write
      library (Library): the library whose definition will be written
    """
    logging.info('writing library %s', library.name)

    category_path = create_named_path(path, library.category)
    makedirectory(category_path)

    library_path = create_named_path(
        category_path, library.name, subdirectory="libraries")

    makedirectory(library_path)

    code_object = library.code("source")

    if not code_object:
        logging.warning(
            'Ignored library %s missing library code', library.name)

    file_name = 'source.rb'

    try:
        code_component.write(
            path=library_path,
            file_name=file_name,
            code_object=code_object
        )
    except OSError as error:
        logging.warning('Error %s writing file %s for library %s',
                        error, file_name, library.name)
    except UnicodeError as error:
        logging.warning(
            'Encoding error %s writing file %s for library %s',
            error, file_name, library.name)

    write_library_definition_json(
        os.path.join(
            library_path, 'definition.json'
        ), library)


def create(*, session, path, category, name):
    """
    Creates new library on the Aquarium instance.
    Note: does not create the files locally, they need to be pulled.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): the directory path where the new files will be written
        category (String): the category for the operation type
        name (String): name of the library to be created
    """
    code_objects = code_component.create_code_objects(
        session=session, component_names=get_component_names()
    )
    new_library = session.Library.new(
        name=name,
        category=category,
        source=code_objects['source'])

    logging.info('Creating new library, %s ', name)

    session.utils.create_library(new_library)


def push(*, session, path):
    """
    Pushes files to the Aquarium instance.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): path to files to be pushed
    """
    if not is_library(path):
        logging.warning('No Library at %s', path)
        return

    definitions = definition.read(path)

    user_id = session.User.where({"login": session.login})
    query = {
        "category": definitions['category'],
        "name": definitions['name']
    }

    parent_object = session.Library.where(query)
    component_names = ['source']

    if not parent_object:
        logging.info('Library %s not found on this instance. Creating it now.', query['name'])
        create(session=session, path=path, category=definitions['category'],
               name=definitions['name'])
        parent_object = session.Library.where(query)
    # TODO: handle case where create failed
    code_component.update_code_objects(
        component_names=component_names,
        parent_object=parent_object[0],
        parent_class="Library",
        user_id=user_id,
        session=session,
        path=path
        )


def run_test(*, session, path, category, name, timeout: int = None):
    logging.error("Library tests are not currently available")
