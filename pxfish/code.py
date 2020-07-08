"""
Functions for writing code to files, or creating code objects
"""

def write_code(path, file_name, code_object):
    """
    Writes the aquarium code object to the given path.

    Arguments:
      path (string): the path of the file to be written
      file_name (string): the name of the file to be written
      code_object (Code): the code object
    """
    file_path = os.path.join(path, file_name)
    with open(file_path, 'w') as file:
        file.write(code_object.content)


def create_code_objects(aq, component_names):
    """
    Creates code objects for each named component.

    Arguments:
        aq (Session Object): Aquarium session object
        component_names (List): names of code components
    """
    code_objects = {}
    for name in component_names:
        code_objects[name] = aq.Code.new(name=name, content='')
    return code_objects
