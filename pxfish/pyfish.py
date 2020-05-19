"""Script to download OperationType definitions from the aquarium instance set in the config.py file."""

import sys
import os
import argparse
import re
import json
from resources import resources
from pydent import AqSession 

sys.path.append('./pydent')

def makedirectory(directory_name):
    """
    Create the directory with the given name.

    Arguments:
      directory_name (string): the name of the directory
    """
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

def simplename(name):
    """
    Converts operation/library name to a string simplified for use as a file name.

    Arguments:
      name (string): the operation or lbrary name

    Returns:
      string: the string constructed by converting whitespace to underscores and is lowercase.
   """
    return re.sub('\W|^(?=\d)', '_', name).lower()

def write_code(path, file_name, code_object):
    """
    Writes the aquarium code object to the given path.

    Arguments:
      path (string): the path of the file to be written
      file_name (string): the name of the file to be written
      code_object (Code): the code object
    """
    if code_object != None:
        file_path = os.path.join(path, file_name)
        with open(file_path, 'w') as file:
            file.write(code_object.content)

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
    Writes the definition of operation_type as JSON to the given file path.

    Arguments:
      file_path (string): the path of the file to write
      operation_type (OperationType): the operation type for which the definition should be written
    """
    print("writing operation type {}".format(operation_type.id)) 
    ot_ser = {}
    ot_ser["id"] = operation_type.id
    ot_ser["name"] = operation_type.name
    #ot_ser["code_name"] = operation_type.protocol.name
    ot_ser["parent_class"] = "OperationType"
    ot_ser["category"] = operation_type.category
    ot_ser["inputs"] = field_type_list(operation_type.field_types, 'input')
    ot_ser["outputs"] = field_type_list(operation_type.field_types, 'output')
    ot_ser["on_the_fly"] = operation_type.on_the_fly
    if operation_type.protocol: 
        ot_ser["user_id"] = operation_type.protocol.user_id
    else: 
        print("operation type {} has no associated protocol".format(operation_type.id))

    with open(file_path, 'w') as file:
        file.write(json.dumps(ot_ser))

def write_library_definition_json(file_path, library):
    """
    Writes the definition of library as JSON to the given file path.

    Arguments:
        file_path (string): the path of the file to write
        library (Library): the library for which the definition should be written
    """
    print("writing library {}".format(library.id))
    ot_ser = {}
    ot_ser["id"] = library.id
    ot_ser["name"] = library.name
    ot_ser["parent_class"] = "Library"
    ot_ser["code_name"] = library.source.name
    ot_ser["category"] = library.category
    ot_ser["user_id"] = library.source.user_id
    
    with open(file_path, 'w') as file:
        file.write(json.dumps(ot_ser))

def write_operation_type(path, operation_type):
    """
    Writes the files for the operation_type to the path.

    Arguments:
      path (string): the path to which the files should be written
      operation_type (OperationType): the operation type being written
    """
    category_path = os.path.join(path, simplename(operation_type.category))
    makedirectory(category_path)
    path = os.path.join(category_path, 'operation_types', simplename(operation_type.name))
    makedirectory(path)
    write_code(path, 'protocol.rb', operation_type.code("protocol"))
    write_code(path, 'precondition.rb', operation_type.code("precondition"))
    write_code(path, 'cost_model.rb', operation_type.code("cost_model"))
    write_code(path, 'documentation.md', operation_type.code("documentation"))
    write_definition_json(os.path.join(path, 'definition.json'), operation_type)

def write_library(path, library):
    """
    Writes the files for the library to the path.

    Arguments:
      path (string): the path to which the files should be written
      library (Library): the library for which the code will be written
    """
    print("writing library") 
    category_path = os.path.join(path, simplename(library.category))
    makedirectory(category_path)
    library_path = os.path.join(category_path, 'libraries', simplename(library.name))
    makedirectory(library_path)

    code_object = library.code("source")
    write_code(library_path, 'source.rb', code_object)
    write_library_definition_json(os.path.join(library_path, 'definition.json'), library)

def open_aquarium_session():
    """
    Starts Aquarium Session
    """
    aq = AqSession(
        resources['aquarium']['login'],
        resources['aquarium']['password'],
        resources['aquarium']['url']
        ) 
    return aq

def pull_category(directory, category):
    operation_types = aq.OperationType.where( { "category": category } )
    libraries = aq.Library.where( { "category": category } )

def pull_operation_type(directory, category, operation_type:
    operation_types = aq.OperationType.where({ "category": category, "name": op_type_or_library } )
    libraries = aq.Library.where( { "category": category, "name": op_type_or_library } ) 

def pull_all(directory):
    operation_types = aq.OperationType.all()
    libraries = aq.Library.all()

def pull(directory, category, op_type_or_library):
    """
    Retrieves the OperationType definitions from the Aquarium instance.

    Arguments:
      directory (string): the path for the directory where files should be written
    """
    aq = open_aquarium_session()

    path = os.path.normpath(directory) # creates string with dir name
    makedirectory(path)

    if category and not op_type_or_library:
        pull_category(directory, category)
    elif op_type_or_library:
        pull_operation_type(directory, category, operation_type) 
    else:
        pull_all(directory)

    for operation_type in operation_types: 
        write_operation_type(path, operation_type)

    for library in libraries:
        write_library(path, library)

def push(directory, category, code_type, op_type_or_library):
    # make a code object - pull data from json file with aq.Code.new -- and with code data
    # but contents need to get added in from wherever you saved it
    aq = open_aquarium_session()
    # need better way to put this together, but this will do for now.
    current_directory = directory + "/" + category + "/" + code_type + "/" + op_type_or_library

    print(current_directory)
    #current_directory = os.path.abspath(os.getcwd())

    if code_type == library:
        files_to_write = ['library.rb']
    else:
        files_to_write = ['cost_model.rb', 'documentation.md', 'precondition.rb', 'protocol.rb']
        with open(current_directory + '/definition.json') as f:
            definitions = json.load(f)

    for file_name in files_to_write:
         
        with open(current_directory + '/' + file_name) as f:
             read_file = f.read()

        new_code = aq.Code.new(
                 name=file_name[:-3], # Code Object Name 'protocol, library, cost_model, etc.'
                 parent_id=definitions['id'], # OperationType or Library id 
                 parent_class=definitions['parent_class'],   # 'OperationType' or 'Library'
                 user_id=definitions['user_id'], # User ID from Code object 
                 content=read_file # Contents of file  
                )
        aq.utils.update_code(new_code)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["push", "pull"], help="indicate if you want to push files or pull them.")  
    # If you want to pull all Files, type pull <directory_name>
    parser.add_argument("directory", help="the directory to which pulled files should be written")
    parser.add_argument("-c", "--category", help="the category on Aquarium where your operation_type/library is located")
    parser.add_argument("-l", "--library", help="the library you want to pull")
    parser.add_argument("-o", "--operation_type", help="the operation_type you want to pull")
    
    # if you wish to pull just one folder, e.g. "Hydra Husbandry", type pyfish.py pull <directory_name> -f "Hydra Husbandry"
    # if you wish to pull just one operation type or library, e.g. "Clean Hydra", type pyfish.py pull <directory_name> -f "Hydra Husbandry" -o "Clean Hydra" 
    # if you want to push files to Aquarium:
    # for a library: pyfish.py push <directory_name> -c <category_name> -l <library_name>
    # pyfish.py push MyDirectory -c "Hydra Husbandry" -l "Husbandry Library"
    # for an operation_type: pyfish.py push <directory_name> -f <category_name> -o <operation_type_name>
    # pyfish.py push MyDirectory -c "Hydra Husbandry" -o "Husbandry Operation Type Name" 
    args = parser.parse_args()
    
    if args.library: 
        library_or_optype = args.library
        code_type = "library"
    elif args.operation_type:
        library_or_optype = args.operation_type
        code_type = "protocol" 
    else:
        library_or_optype = None
        code_type=None

    if args.action == 'push':
        push(args.directory, args.folder, code_type, library_or_optype)
    else:
        pull(args.directory, args.folder, args.operation_type)

if __name__ == "__main__":
    main()
