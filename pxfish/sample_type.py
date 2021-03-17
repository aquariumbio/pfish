"""Functions for pulling Sample Types in Aquarium."""

import json
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
    data_dict = read(path=path, sample_type=sample_type)
    # use data_dict to create type
    query = {
            'name':  data_dict['name'],
            'description': data_dict['description']
            }

    s = session.SampleType(query)
    s.save()
    return s


def read(*, path, sample_type):
    # path will be directory/category/operation_types/ot
    # needs to be directory/sample_types/ot.json
    # needs to read file in object types folder
    # needs path and file name (sample type name simplified)
    # But, Sample Names are Case Sensitive, so our simplify method can create conflicts
    # path should be Dir/sample_types/file.json
    file_path = os.path.join(path, 'definition.json')
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
