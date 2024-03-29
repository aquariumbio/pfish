"""
Functions for pulling Object Types in Aquarium.
"""

import json
import logging
import pathlib
import os

from paths import (
    create_named_path,
    makedirectory,
    simplename
)


def exists(*, session, object_type):
    """
    Checks whether an Object Type named in definition exists in Aquarium
    """
    object_type = session.ObjectType.where({'name': object_type})
    return bool(object_type)


def get_sample_type_id(session, sample_type_name):
    """Gets Sample Type ID to be associated with Object Type"""
    # TODO: If ST doesn't exist, create it?
    sample_type = session.SampleType.where({'name': sample_type_name})
    if sample_type:
        return sample_type[0].id
    return None


def create(*, session, object_type, path):
    """
    Creates a new Object Type in Aquarium
    """
    path = pathlib.PurePath(path).parts[0]
    path = create_named_path(path, 'object_types')
    try:
        data_dict = read(path=path, object_type=object_type)
    except FileNotFoundError:
        return

    # TODO: try except for File not Found Error
    obj_type = session.ObjectType.new(
        name=data_dict['name'],
        description=data_dict['description'],
        min=data_dict['min'],
        max=data_dict['max'],
        handler=data_dict.get('handler', ""),
        safety=data_dict['safety'],
        clean_up=data_dict['clean up'],
        data=data_dict['data'],
        vendor=data_dict['vendor'],
        unit=data_dict['unit'],
        cost=data_dict['cost'],
        release_method=data_dict['release method'],
        release_description=data_dict['release description'],
        image=data_dict['image'],
        prefix=data_dict['prefix'],
        rows=data_dict['rows'],
        columns=data_dict['columns']
        )

    sample_type_name = data_dict.get('sample_type', None)
    if sample_type_name:
        sample_type_id = get_sample_type_id(
            session=session,
            sample_type_name=sample_type_name
            )
        obj_type.sample_type_id = sample_type_id
    obj_type.save()


def read(*, path, object_type):
    """
    Reads the json file for the indicated object type
    """
    object_type = simplename(object_type) + ".json"
    file_path = os.path.join(path, object_type)

    try:
        with open(file_path) as file:
            data_dict = json.load(file)
    except FileNotFoundError as error:
        logging.warning(
            'Error %s reading expected code file %s', error, 'definition.json')
        raise FileNotFoundError
    return data_dict


# TODO: update so this doesn't rewrite the same file repeatedly
def write_files(*, path, object_type):
    """
    Writes the files associated with the object_type to the path.

    Arguments:
        path (String): the path to where the files will be written
        object_type (ObjectType): the object type being written
    """
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
        "columns": object_type.columns,
        "sample_type": None
    }

    if object_type.sample_type:
        object_type_ser["sample_type"] = object_type.sample_type.name

    name = simplename(object_type_ser['name'])

    file_path = (os.path.join(path, "{}.json".format(name)))

    with open(file_path, 'w') as file:
        file.write(json.dumps(object_type_ser, indent=2))

    logging.info('Writing object type %s', object_type.name)
