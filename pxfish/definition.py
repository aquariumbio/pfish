"""Functions to create definition files with library or operation type data"""
import json
import logging
import os
from typing import Dict


def has_definition(path) -> bool:
    return 'definition.json' in os.listdir(path)


def has_field_types(definitions) -> bool:
    return bool(definitions['inputs'] or definitions['outputs'])


def is_library(obj: Dict) -> bool:
    logging.info('Checking whether Definition File is for a Library.')
    return obj['parent_class'] == 'Library'


def is_operation_type(obj: Dict) -> bool:
    logging.info('Checking whether Definition File is for an Operation Type.')
    return obj['parent_class'] == 'OperationType'


def allowable_field_types(field_types: list) -> list:
    """
    Creates a list of allowable field types from definition file
    """
    allowable_field_types = []
    for field_type in field_types:
        if field_type['allowable_field_types']:
            allowable_field_types.extend(field_type['allowable_field_types'])
    return allowable_field_types


def category(obj: Dict) -> str:
    return obj['category']


def name(obj: Dict) -> str:
    return obj['name']


def serialize_field_types(field_types):
    """
    Returns data about each field type in dictionary format

    Arguments:
      field_types (List): the list of pydent field type objects

    Returns:
      list: list of serialized data for each field_type
    """
    #TODO: Distinguish Parameters from other inputs/outputs
    ft_list = []
    for field_type in field_types:
        ft_ser = {
            'name': field_type.name,
            'part': field_type.part,
            'array': field_type.array,
            'routing': field_type.routing,
            'ftype': field_type.ftype,
            'choices': field_type.choices,
            'required': field_type.required
            }
        if field_type.parent_class == "OperationType":
            allowable_field_types = serialize_allowable_field_types(field_type.allowable_field_types)
            ft_ser['allowable_field_types'] = allowable_field_types

        ft_list.append(ft_ser)
    return ft_list


def serialize_allowable_field_types(allowable_field_types):
    """
    Arguments:
      allowable_field_types (List): list of AFTs associated with Field Type

    Returns:
      object_and_sample_types (List): list of object and sample types associated with AFT
    """
    object_and_sample_types = []
    for aft in allowable_field_types:
        ser = {}
        if aft.sample_type:
            ser['sample_type'] = aft.sample_type.name

        if aft.object_type:
            ser['object_type'] = aft.object_type.name

        object_and_sample_types.append(ser)

    return object_and_sample_types


def write_definition_json(file_path, operation_type):
    """
    Writes the definition of the operation_type as JSON to the given file path.

    Arguments:
      file_path (string): the path of the file to write
      operation_type (OperationType): the operation type being defined
    """
    ot_ser = {}
    ot_ser['name'] = operation_type.name
    ot_ser['parent_class'] = 'OperationType'
    ot_ser['category'] = operation_type.category
    ot_ser['inputs'] = serialize_field_types(
            [ft for ft in operation_type.field_types if ft.role == 'input']
            )
    ot_ser['outputs'] = serialize_field_types(
            [ft for ft in operation_type.field_types if ft.role == 'output']
            )
    ot_ser['on_the_fly'] = operation_type.on_the_fly
    ot_ser['user_id'] = operation_type.protocol.user_id

    with open(file_path, 'w') as file:
        file.write(json.dumps(ot_ser, indent=2))


def write_library_definition_json(file_path, library):
    """
    Writes the definition of library as JSON to the given file path.

    Arguments:
      file_path (String): the path to the file as written
      library (Library): the library for which the definition should be written
    """
    library_ser = {}
    library_ser['name'] = library.name
    library_ser['parent_class'] = 'Library'
    library_ser['category'] = library.category
    library_ser['user_id'] = library.source.user_id

    with open(file_path, 'w') as file:
        file.write(json.dumps(library_ser, indent=2))


def read(path):
    """
    Reads definition.json file at given location.

    Arguments:
        path (String): path to definition file
    """
    file_path = os.path.join(path, 'definition.json')

    with open(file_path) as file:
        definition = json.load(file)

    return definition
