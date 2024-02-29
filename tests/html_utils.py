import os
import pathlib
import unittest


def _get_current_path() -> pathlib.Path:
    return pathlib.Path(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))))


def get_resource_location(resource_name: str) -> pathlib.Path:
    return _get_current_path() / 'resources' / resource_name


def get_resource(resource_name: str) -> str:
    return get_resource_location(resource_name).read_text()


def create_mock(resouce_name: str) -> unittest.mock.MagicMock:
    mock = unittest.mock.MagicMock()
    mock.text = get_resource(resouce_name)
    return mock
