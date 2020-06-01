"""Functions for pushing Library and Operation Type files to Aquarium"""

import json
import logging
import os
from paths import *


def select_library(aq, category_path, library_name):
    """
    Locates the library files to be pushed

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path for the directory where files should be written
        category (String): the category where the Library is to be found
        library (string): the Library whose files will be pushed
    """
    path = create_library_path(category_path, library_name)
    push(aq, path, ['source'])


def select_operation_type(aq, category_path, operation_type_name):
    """
    Locates the Operation Type whose files will be pushed

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path for the directory where files should be written
        category (String): the category where the Library is to be found
        library (string): the Library whose files will be pushed
    """
    path = create_operation_path(category_path, operation_type_name)
    push(aq, path, operation_type_code_names())

# Create new OT in database 
# Create all the associated code objects
# Create Code objects with no parent id 
# use those objects to create new Op Type 
# find id of new op type 
# update code ids to match 
# Create new OT (or share) when you have different id numbers
# Need to create Code objects to create Op types, but how to get id # for op type?
def create_operation_type(aq, category_path, operation_type_name):
    """
    Creates new operation type
    
    Arguments:
        aq (Session Object): Aquarium session object
    """
    code_objects = create_code_objects(aq, "test", operation_type_code_names())
    print(code_objects)
    new_operation_type = aq.OperationType.new(name=name, category=category, protocol=code_objects['protocol'], documentation=code_objects['documentation'], cost_model=code_objects['cost_model'], field_types=[])
    path = create_operation_path(category_path, operation_type_name)
    print("created new op type {}".format(new_operation_type))
    print("created path {}".format(path)) 
    

def create_code_objects(aq, category, component_names):
    code_objects = {}
    for name in component_names:
        file_name = "{}.rb".format(name)
        code_objects[name] = aq.Code.new( name=name, category=category )
    return code_objects


#def create_operation_object(aq, component_names):
    #abc = aq.OperationType.new(name="abc", category="test", protocol=a, documentation=b, precondition=c, cost_model=d)
    #aq.util.create_operation_type(ot instance)

# create dummy code objects 
# create OperationType
# create json data file/other files (should have template code in them?)
# push code just as you would for normal edits


def push(aq, directory, component_names):
    """
    Pushes files to the Aquarium instance

    Arguments:
        aq (Session Object): Aquarium session object
        directory (String): Directory where files are to be found
        files_to_write (List): List of files to push
    """
    with open(os.path.join(directory, 'definition.json')) as f:
        definitions = json.load(f)

    for name in component_names:
        file_name = "{}.rb".format(name)
        try:
            with open(os.path.join(directory, file_name)) as f:
                read_file = f.read()
        
        except FileNotFoundError as error:
            logging.warning(
                "Error {} writing file {} file does not exist".format(
                    error, file_name))
            continue

        local_op_type = aq.OperationType.where({"category": definitions['category'], "name": definitions['name'] })
       
        new_code = aq.Code.new(
            name=name,
            parent_id=local_op_type[0].id,    #definitions['id'],
            parent_class=definitions['parent_class'],
            user_id=local_op_type[0].protocol.user_id, # definitions['user_id'],
            content=read_file
        )

        aq.utils.update_code(new_code)

