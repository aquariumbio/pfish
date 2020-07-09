import json

def field_type_list(field_types, role):
    """
    Returns the sublist of field types with the given role.

    Arguments:
      field_types (list): the list of field types
      role (string): the role of field types to be returned

    Returns:
      list: the sublist of field_types that have the role
    """
    ft_list = []
    for field_type in field_types:
        if field_type.role == role:
            ft_ser = {
                "name": field_type.name,
                "part": field_type.part,
                "array": field_type.array,
                "routing": field_type.routing
            }
            ft_list.append(ft_ser)
    return ft_list

def write_definition_json(file_path, operation_type):
    """
    Writes the definition of the operation_type as JSON to the given file path.

    Arguments:
      file_path (string): the path of the file to write
      operation_type (OperationType): the operation type for definition
    """
    ot_ser = {}
    ot_ser["id"] = operation_type.id
    ot_ser["name"] = operation_type.name
    ot_ser["parent_class"] = "OperationType"
    ot_ser["category"] = operation_type.category
    ot_ser["inputs"] = field_type_list(operation_type.field_types, 'input')
    ot_ser["outputs"] = field_type_list(operation_type.field_types, 'output')
    ot_ser["on_the_fly"] = operation_type.on_the_fly
    ot_ser["user_id"] = operation_type.protocol.user_id

    with open(file_path, 'w') as file:
        file.write(json.dumps(ot_ser, indent=2))


def write_library_definition_json(file_path, library):
    """
    Writes the definition of library as JSON to the given file path.

    Arguments:
      file_path (string): the path to the file as written
      library (Library): the library for which the definition should be written
    """
    library_ser = {}
    library_ser["id"] = library.id
    library_ser["name"] = library.name
    library_ser["parent_class"] = "Library"
    library_ser["category"] = library.category
    library_ser["user_id"] = library.source.user_id

    with open(file_path, 'w') as file:
        file.write(json.dumps(library_ser, indent=2))

