import library
import logging
import operation_type


def pull(*, session, path):
    """
    Pulls OperationType and/or Library files from the Aquarium instance.

    Arguments:
        aq (Session Object): Aquarium session object
        path (String): the path to where the files will be written
    """
    operation_types = session.OperationType.all()
    libraries = session.Library.all()

    for op_type in operation_types:
        operation_type.write_files(path, op_type)

    for lib in libraries:
        library.write_files(path, lib)


def push(*, session, path):
    logging.error("push of directory not implemented")


def run_test(*, session, path):
    logging.error("all tests are not currently available")
