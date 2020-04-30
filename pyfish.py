"""Script to download OperationType definitions from the aquarium instance set in the config.py file."""

import sys
import os
import argparse
import re
import json
from resources import resources

from pydent import AqSession 
# appends ./pydent to list of directories to be searched 
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
    ot_ser = {}
    ot_ser["name"] = operation_type.name
    ot_ser["category"] = operation_type.category
    ot_ser["inputs"] = field_type_list(operation_type.field_types, 'input')
    ot_ser["outputs"] = field_type_list(operation_type.field_types, 'output')
    ot_ser["on_the_fly"] = operation_type.on_the_fly
#    ot_ser["timing"] = operation_type.timing
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
    path = os.path.join(category_path, 'protocol', simplename(operation_type.name))
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
    category_path = os.path.join(path, simplename(library.category))
    makedirectory(category_path)
    library_path = os.path.join(category_path, 'library')
    makedirectory(library_path)

    code_object = library.code("source")
    write_code(library_path, simplename(library.name) + '.rb', code_object)

def pull(directory, category, op_type_or_library):
    """
    Retrieves the OperationType definitions from the Aquarium instance.

    Arguments:
      directory (string): the path for the directory where files should be written
    """
#    name, password, url = "amycash", "ga@tsB1920Rb", "http://localhost:3000"
#    aq = AqSession(name, password, url)
    aq = AqSession(
        resources['aquarium']['login'],
        resources['aquarium']['password'],
        resources['aquarium']['url']
        ) 

    path = os.path.normpath(directory)
    makedirectory(path)

    if not (category and op_type_or_library):
      operation_types = aq.OperationType.all()
    else:
      operation_types = aq.OperationType.where({ "category": category, "name": op_type_or_library })
    
        # get op types where category == category 
    for operation_type in operation_types: 
      write_operation_type(path, operation_type)
    
    #for library in aq.Library.all():
    #    write_library(path, library)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="the directory to which files should be written")
    parser.add_argument("folder", help="the folder on Aquarium where your operation_type/library is located default is to include all folders")
    parser.add_argument("operation_type", help="the operation_type or library you want to pull, default is to include all types/libraries in folder")
    # you'll need to enter it in quotes if it's more than two words. 
    # ideally it can just pull the name from the repo you are in. 
    # if you enter nothing, pull all categories, ops, and libraries 
    # if you enter a category, pull everything in that category 
    # if you enter a category and a name, just pull that one library or operation type
    # default is to pull everything 
    args = parser.parse_args()
    pull(args.directory, args.folder, args.operation_type)

if __name__ == "__main__":
    main()
