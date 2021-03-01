import os
import pydent
import pytest
from pxfish.code_component import (
    write,
    create_code_object,
    add_default_content,
    create_code_object,
    create_code_objects,
    read
)


class TestCode:

    def test_write_read(self, tmpdir):
        path = tmpdir.mkdir('read_write')
        dummy_content = 'dummy code content'
        code_object = pydent.models.Code(
            name="dummy_code", content=dummy_content)
        file_name = 'dummy_code_file.rb'
        file_path = os.path.join(path, file_name)

        assert not os.path.exists(
            file_path), "test configuration issue: File {} should not exist before write".format(file_path)
        write(path=path, file_name=file_name, code_object=code_object)
        assert os.path.exists(
            file_path), "File {} should exist after write".format(file_path)

        # read and write interfaces are inconsistent on extension
        code_content = read(path=path, name='dummy_code_file')
        assert code_content == dummy_content

    def test_create_object(self):
        class MockAqHTTP:
            def post(self, path, json_data):
                self.data = json_data
                return dict

        class MockSession:
            def __init__(self):
                self._aqhttp = MockAqHTTP()

        session = MockSession()
        op_type = pydent.models.OperationType()
        op_type.name = 'DummyType'
        op_type.id = 1
        create_code_object(session=session, name='protocol',
                           operation_type=op_type)
        assert 'id' in session._aqhttp.data
        assert 'content' in session._aqhttp.data
        assert 'name' in session._aqhttp.data

        # there is no error handling if name does not correspond to an op type component
        # not sure if it is needed

    def test_create_objects(self):
        class MockCodeInterface:
            @staticmethod
            def new(*, name, content):
                return pydent.models.Code(name=name, content=content)

        class MockSession:
            def __getattr__(self, name):
                return MockCodeInterface

        session = MockSession()
        code_objects = create_code_objects(session=session, component_names=['protocol'])
        
        assert 'protocol' in code_objects
