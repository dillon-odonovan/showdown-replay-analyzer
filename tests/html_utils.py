import os
import pathlib
import unittest


def _get_current_path() -> pathlib.Path:
    return pathlib.Path(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))


def get_resource(resource_name: str) -> str:
    return (_get_current_path() / 'resources' / resource_name).read_text()


def create_mock(resouce_name: str) -> unittest.mock.MagicMock:
    mock = unittest.mock.MagicMock()
    mock.text = get_resource(resource_name=resouce_name)
    return mock
