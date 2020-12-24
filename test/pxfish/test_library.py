import os
import pydent
import pytest

from pxfish.library import (
    is_library,
    pull,
    get_code_file_names,
    write_files,
    create,
    push
)


class TestLibrary:

    def test_pull(self, tmpdir):
        pytest.skip('mock is incomplete')

        class MockLibraryInterface:
            @staticmethod
            def where(arg_dict):
                library = pydent.models.Library()
                library.name = arg_dict['name']
                library.category = arg_dict['category']
                library.session = pydent.sessionabc.SessionABC()
                # TODO: this is wrong
                library.code = pydent.models.Code(
                    name='source', content='blah blah')
                return [library]

        class MockSession():
            def __getattr__(self, name):
                return MockLibraryInterface

        session = MockSession()
        path = tmpdir.mkdir('pull_test')
        dummy_category = 'Dummy Category'
        dummy_name = 'Dummy Name'
        pull(session=session, path=path, category=dummy_category, name=dummy_name)

        # TODO: check for files in path
        # TODO: or refactor to allow reading files
