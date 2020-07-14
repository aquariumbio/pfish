import library
import operation_type


def pull_all(aq, path):
    """
    Pulls OperationType and/or Library files from the Aquarium instance.

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the files will be written
    """
    operation_types = aq.OperationType.all()
    libraries = aq.Library.all()

    for op_type in operation_types:
        operation_type.write_files(path, op_type)

    for lib in libraries:
        library.write_files(path, lib)

