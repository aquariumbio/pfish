"""Functions to create an Aquarium session object through pydent"""

from config import get_config, config_file_path
from pydent import AqSession


def create_session(*, path, name: str = None):
    """
    Creates an aquarium session connected to the named Aquarium instance.

    Arguements:
        path (String): the config directory path

    Returns:
        Aquarium Session Object
    """
    file_path = config_file_path(path)
    config = get_config(file_path)

    if not name:
        name = config["default"]

    if name not in config["instances"]:
        raise BadInstanceError(name)

    credentials = config["instances"][name]
    session = AqSession(
        credentials["login"],
        credentials["password"],
        credentials["aquarium_url"]
    )

    session.set_verbose(False)
    return session


class BadInstanceError(Exception):
    """
    Raises an Exception when an instance name is given that does not occur in
    the configuration file.
    """

    def __init__(self, name):
        self.instance_name = name
