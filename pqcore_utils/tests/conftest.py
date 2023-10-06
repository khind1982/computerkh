"""Global pytest config and fixtures."""
import configsetup  # noqa
import pytest
import os


@pytest.fixture
def huge_tree_xml():
    return os.path.join(os.path.dirname(__file__), "fixtures/huge_tree.xml")
