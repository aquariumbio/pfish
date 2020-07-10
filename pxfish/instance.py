from library import write_library
from operation_type import write_operation_type


def pull_all(aq, path):
    """
    Pulls OperationType and/or Library files from the Aquarium instance.

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the files will be written
    """
    operation_types = aq.OperationType.all()
    libraries = aq.Library.all()

    for operation_type in operation_types:
        write_operation_type(path, operation_type)

    for library in libraries:
        write_library(path, library)

