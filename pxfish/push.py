

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
# Create new OT (or share) when you have different id numbers

def create_operation_type():
    pass 

def create_code_objects():
    pass

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
        with open(os.path.join(directory, file_name)) as f:
            read_file = f.read()

        new_code = aq.Code.new(
            name=name,
            parent_id=definitions['id'],
            parent_class=definitions['parent_class'],
            user_id=definitions['user_id'],
            content=read_file
        )

        aq.utils.update_code(new_code)
