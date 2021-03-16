"""
Functions for pulling Sample Types in Aquarium.
"""

import json
import logging
import os
import definition

from paths import (
    create_named_path,
    makedirectory,
    simplename
)


def exists(*, session, smpl_type):
    """
    Checks whether a Sample Type named in definition exists in Aquarium
    """
    # TODO: we are not currently storing the description in the definition file
    sample_type = session.SampleType.where({'name': smpl_type})
    
    if sample_type:
        return True
    else:
        return False


def create(*, session, smpl_type):
    """
    Creates a new Sample Type in Aquarium
    """
    s = session.SampleType(name=smpl_type, description="fake")
    s.save()
    return s


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
        'description': sample_type.description
    }

    name = simplename(sample_type_ser['name'])

    file_path = (os.path.join(path, "{}.json".format(name)))
    with open(file_path, 'w') as file:
        file.write(json.dumps(sample_type_ser, indent=2))
