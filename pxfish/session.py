from config import get_config, config_file_path
from pydent import AqSession


def create_session(*, path):
    """
    Create an aquarium session connected to the named Aquarium instance.

    :param path: the config directory path
    :type path: str
    :return: new AqSession
    """
    file_path = config_file_path(path)
    config = get_config(file_path)

    name = config["default"]
    if name not in config["instances"]:
        raise BadInstanceError(name)

    credentials = config["instances"][name]
    session = AqSession(
        credentials["login"],
        credentials["password"],
        credentials["aquarium_url"]
    )

    return session


class BadInstanceError(Exception):
    """
    Exception raised when an instance name is given that does not occur in
    the configuration file.
    """

    def __init__(self, name):
        self.instance_name = name
