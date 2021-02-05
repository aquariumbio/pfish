"""
Functions for pushing, pulling, and creating Library files.
"""

import json
import logging
import os
import code
import definition

from paths import (
    create_named_path,
    makedirectory
)
from definition import (
    write_library_definition_json
)


def is_library(path):
    """Checks whether definiton file is at path, and is for a library"""
    if not os.path.isdir(path):
        return False

    try:
        def_dict = definition.read(path)
    except FileNotFoundError:
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


def get_code_file_names():
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
        code.write(path=library_path, file_name=file_name, code_object=code_object)
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
    code_objects = code.create_code_objects(
        session=session, component_names=get_code_file_names()
        )
    new_library = session.Library.new(
        name=name,
        category=category,
        source=code_objects['source'])
    session.utils.create_library(new_library)


def push(*, session, path):
    """
    Pushes files to the Aquarium instance.

    Arguments:
        session (Session Object): Aquarium session object
        path (String): path to files to be pushed
    """
    definitions = definition.read(path)

    user_id = session.User.where({"login": session.login})
    query = {
        "category": definitions['category'],
        "name": definitions['name']
    }

    parent_object = session.Library.where(query)
    component_names = ['source']

    if not parent_object:
        create(session=session, path=path, category=definitions['category'],
               name=definitions['name'])
        parent_object = session.Library.where(query)
        # TODO: handle case where create failed
        return

    for name in component_names:
        read_file = code.read(path=path, name=name)
        if read_file is None:
            return

        new_code = session.Code.new(
            name=name,
            parent_id=parent_object[0].id,
            parent_class=definitions['parent_class'],
            user_id=user_id,
            content=read_file
        )

        logging.info('writing file %s', parent_object[0].name)

        session.utils.update_code(new_code)


def run_test(*, session, category, name):
    logging.error("Library tests are not currently available")
