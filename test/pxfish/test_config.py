import os
import pytest
from config import (
    add_config,
    config_file_path,
    get_config,
    set_default_instance,
    show_config
)


@pytest.fixture
def configuration_path(tmpdir):
    path = tmpdir.mkdir('config')
    return path


@pytest.fixture
def configuration_file(configuration_path):
    return config_file_path(configuration_path)


class TestConfig:

    def test_default(self, configuration_file):
        config = get_config(configuration_file)
        assert type(config) is dict
        assert 'default' in config
        assert config['default'] == 'local'
        assert 'instances' in config
        assert config['default'] in config['instances']

    def test_add(self, configuration_path, configuration_file):
        if os.path.exists(configuration_file):
            os.remove(configuration_file)
        # sanity check on temporaries
        assert configuration_file.startswith(str(configuration_path))

        config_key = 'testing'
        add_config(
            path=configuration_path,
            key='testing',
            login=config_key,
            password='dummy_password',
            url='http://dummy_url'
        )
        config = get_config(configuration_file)
        assert type(config) is dict
        assert 'default' in config
        assert config['default'] == 'local'
        assert 'instances' in config
        assert config['default'] in config['instances']
        set_default_instance(configuration_path, name=config_key)
        config = get_config(configuration_file)
        assert type(config) is dict
        assert 'default' in config
        assert config['default'] == config_key
        assert 'instances' in config
        assert config['default'] in config['instances']
