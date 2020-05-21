"""Script to download OperationType definitions from the aquarium instance set in the config.py file."""

import sys
import os
import argparse
import re
import json
import logging
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
    Writes the definition of the operation_type as JSON to the given file path.

    Arguments:
      file_path (string): the path of the file to write 
      operation_type (OperationType): the operation type whose definition will be written
    """
#    print("writing operation type {}".format(operation_type.name)) 
    ot_ser = {}
    ot_ser["id"] = operation_type.id
    ot_ser["name"] = operation_type.name
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
      file_path (string): the path to the file as written
      library (Library): the library for which the definition should be written
    """
#    print("writing library {}".format(library.name))
    library_ser = {}
    library_ser["id"] = library.id
    library_ser["name"] = library.name
    library_ser["parent_class"] = "Library"
    library_ser["category"] = library.category
    library_ser["user_id"] = library.source.user_id
    
    with open(file_path, 'w') as file:
        file.write(json.dumps(library_ser))

def write_operation_type(path, operation_type):
    """
    Writes the files associated with the operation_type to the path.

    Arguments:
      path (string): the path to where the files will be written
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
      path (string): the path of the file to write 
      library (Library): the library whose definition will be written
    """
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

def get_library(aq, path, category, library):
    """
    Retrieves a single Library

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the file will be written
        category (String): The category the Library is in
        library (String): The Library to be retreived
    """
    library = aq.Library.where( { "category": category, "name": library } )
    pull(path, operation_types=[], libraries=library)

def get_operation_type(aq, path, category, operation_type):
    """
    Retrieves a single Operation Type 

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the file will be written
        category (String): The category the OperationType is in
        operation_type (String): The OperationType to be retreived
    """
    operation_type = aq.OperationType.where({ "category": category, "name": operation_type } )
    pull(path, operation_types=operation_type)

def get_category(aq, path, category):
    """
    Retrieves all the Libraries and Operation Types within a category

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the files will be written
        category (String): The category the Operation Types and Libraries are in
    """
    operation_types = aq.OperationType.where( { "category": category } )
    libraries = aq.Library.where( { "category": category } )
    pull(path, operation_types=operation_types, libraries=libraries)
    
def get_all_optypes_and_libraries(aq, path):
    """
    Retrieves all Operation Types and Libraries 

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the files will be written
    """
    operation_types = aq.OperationType.all()
    libraries = aq.Library.all()
    pull(path, operation_types, libraries)

def pull(path, operation_types=[], libraries=[]):
    """
    Pulls OperationType and/or Library files from the Aquarium instance.

    Arguments:
        path (String): the path for the directory where files should be written
        operation_types (List): list of OperationTypes whose files to pull
        libraries (List): list of Liraries whose files to pull
    """
    for operation_type in operation_types: 
        write_operation_type(path, operation_type)

    for library in libraries:
        write_library(path, library)

def push_library(aq, path, category, library):
    current_directory = os.path.join(path, category, "libraries", library)
    push(aq, current_directory, ['source.rb'])

def push_operation_type(aq, path, category, operation_type):
    current_directory = os.path.join(path, category, "operation_types", operation_type)
    push(aq, current_directory, ['cost_model.rb', 'documentation.md', 'precondition.rb', 'protocol.rb'])

def push(aq, directory, files_to_write):
    
    with open(os.path.join(directory, 'definition.json')) as f:
        definitions = json.load(f)

    for file_name in files_to_write:
        with open(os.path.join(directory, file_name)) as f:
             read_file = f.read()

        new_code = aq.Code.new(
                 name=os.path.splitext(file_name)[0],
                 parent_id=definitions['id'],
                 parent_class=definitions['parent_class'],
                 user_id=definitions['user_id'],
                 content=read_file
                )

        aq.utils.update_code(new_code)

def main():
    parser = argparse.ArgumentParser(description="Pull or Push files from/to Aquarium")
    parser.add_argument("action", choices=["push", "pull"], help="Indicate if you want to push files or pull them.")  
    parser.add_argument("-d", "--directory", help="The name of the directory where the files should be written. If the directory does not already exist, it will be created")
    parser.add_argument("-c", "--category", help="The Aquarium category where the OperationType or Library is located")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-l", "--library", help="the Library you want to pull")
    group.add_argument("-o", "--operation_type", help="the Operation Type you want to pull")
   
    args = parser.parse_args()
    
    if not args.directory:
        args.directory = os.getcwd()

    aq = open_aquarium_session()

    path = os.path.normpath(args.directory)
    makedirectory(path)

    if args.action == 'pull':
        if args.library: 
            get_library(aq, path, args.category, args.library) 
        elif args.operation_type:
            get_operation_type(aq, path, args.category, args.operation_type)
        elif args.category: 
            get_category(aq, path, args.category)
        else:
            get_all_optypes_and_libraries(aq, path)
    elif args.action == 'push':
        if args.library and args.category:
            push_library(aq, args.directory, args.category, args.library)
        elif args.operation_type and args.category:
            push_operation_type(aq, args.directory, args.category, args.operation_type)
        else:
            logging.warning("You must enter a Category and either a Library Name or an OperationType name in order to push. See pyfish.py -h for help.")
    else:
        logging.warning("You must indicate whether you would like to 'push' or 'pull'")

if __name__ == "__main__":
    main()
