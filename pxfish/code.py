
def write_library(path, library):
    """
    Writes the files for the library to the path.

    Arguments:
      path (string): the path of the file to write
      library (Library): the library whose definition will be written
    """
    logging.info("writing library {}".format(library.name))

    category_path = create_named_path(path, library.category)
    makedirectory(category_path)
    library_path = create_library_path(category_path, library.name)
    makedirectory(library_path)

    code_object = library.code("source")
    if not code_object:
        logging.warning(
            "Ignored library {} missing library code".format(
                library.name)
        )
    file_name = 'source.rb'
    try:
        write_code(library_path, file_name, code_object)
    except OSError as error:
        logging.warning("Error {} writing file {} for library {}".format(
            error, file_name, library.name))
    except UnicodeError as error:
        logging.warning(
            "Encoding error {} writing file {} for library {}".format(
                error, file_name, library.name))

    write_library_definition_json(os.path.join(
        library_path, 'definition.json'), library)


# from push
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
