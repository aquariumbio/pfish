
def get_all(aq, path):
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
        libraries (List): list of Libraries whose files to pull
    """
    for operation_type in operation_types:
        write_operation_type(path, operation_type)

    for library in libraries:
        write_library(path, library)

