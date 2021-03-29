"""Functions for pulling Sample Types in Aquarium."""

import json
import pathlib
import logging
import os
import definition

from paths import (
    create_named_path,
    makedirectory,
    simplename
)


def exists(*, session, sample_type):
    """
    Checks whether a Sample Type named in definition exists in Aquarium
    """
    # TODO: we are not currently storing the description in the definition file
    sample_type = session.SampleType.where({'name': sample_type})
    return bool(sample_type)


def create(*, session, sample_type, path):
    """
    Creates a new Sample Type in Aquarium
    """
    path = pathlib.PurePath(path).parts[0]
    path = create_named_path(path, 'sample_types')

    data_dict = read(path=path, sample_type=sample_type)
    # TODO: try except for File not Found Error
    smpl_type = session.SampleType.new(name=data_dict['name'], description=data_dict['description'])
    smpl_type.save()
    return smpl_type


def read(*, path, sample_type):
    """
    Reads the json file for the indicated sample type
    """
    sample_type = simplename(sample_type) + ".json"
    file_path = os.path.join(path, sample_type)

    try:
        with open(file_path) as file:
            data_dict = json.load(file)
    except FileNotFoundError as error:
        logging.warning(
            'Error %s reading expected code file %s', error, 'definition.json')
    return data_dict


def write_files(*, path, sample_type):
    """
    Writes the files associated with the sample_type to the path.

    Arguments:
        path (String): the path to where the files will be written
        sample_type (ObjectType): the object type being written
    """
    logging.info('writing sample type %s', sample_type.name)

    path = create_named_path(path, 'sample_types')

    makedirectory(path)

    sample_type_ser = {
        'name': sample_type.name,
        'description': sample_type.description,
        'field_types': definition.field_type_list(sample_type.field_types)
    }

    name = simplename(sample_type_ser['name'])

    file_path = (os.path.join(path, "{}.json".format(name)))
    with open(file_path, 'w') as file:
        file.write(json.dumps(sample_type_ser, indent=2))
