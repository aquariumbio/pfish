import os
import json

from paths import makedirectory


def config_file_path(path):
    return os.path.join(path, 'config.json')


def add_config(*, path, key, login, password, url):
    """
    Adds the given configuration information to the secrets file in the config
    directory specified by the path.
    """

    makedirectory(path)
    file_path = config_file_path(path)
    config = get_config(file_path)

    config['instances'][key] = {
        'login': login,
        'password': password,
        'aquarium_url': url
    }

    with open(file_path, 'w') as file:
        file.write(json.dumps(config, indent=2))


def get_config(path):
    """
    Returns the dict from the config file at named path if file exists.
    Otherwise, returns the default.
    """
    if os.path.isfile(path):
        with open(path) as file:
            return json.load(file)

    return {
        "default": "local",
        "instances": {
            "local": {
                "login": "neptune",
                "password": "aquarium",
                "aquarium_url": "http://localhost/"
            }
        }
    }


def set_default_instance(path, *, name):
    file_path = config_file_path(path)
    config = get_config(file_path)

    config["default"] = name

    with open(file_path, 'w') as file:
        file.write(json.dumps(config, indent=2))
