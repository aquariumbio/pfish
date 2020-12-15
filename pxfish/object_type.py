"""
Functions for pulling Object Types in Aquarium.
"""

import json
import logging
import os

from paths import (
    create_named_path,
    makedirectory,
    simplename
)


def write_files(*, path, object_type):
    """
    Writes the files associated with the object_type to the path.

    Arguments:
        path (String): the path to where the files will be written
        object_type (ObjectType): the object type being written
    """
    logging.info('writing object type %s', object_type.name)

    path = create_named_path(path, 'object_types')

    makedirectory(path)

    object_type_ser = {
        "name": object_type.name,
        "description": object_type.description,
        "min": object_type.min,
        "max": object_type.max,
        "handler": object_type.handler,
        "safety": object_type.safety,
        "clean up": object_type.cleanup,
        "data": object_type.data,
        "vendor": object_type.vendor,
        "unit": object_type.unit,
        "cost": object_type.cost,
        "release method": object_type.release_method,
        "release description": object_type.release_description,
        "image": object_type.image,
        "prefix": object_type.prefix,
        "rows": object_type.rows,
        "columns": object_type.columns
    }

    name = simplename(object_type_ser['name'])

    file_path = (os.path.join(path, "{}.json".format(name)))

    with open(file_path, 'w') as file:
        file.write(json.dumps(object_type_ser, indent=2))
