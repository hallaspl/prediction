import pytest
import os


@pytest.fixture
def example_data_folder_path() -> str:
    this_folder_path = os.path.dirname(os.path.abspath(__file__))
    example_data_folder_name = "example_data"
    return os.path.join(this_folder_path, example_data_folder_name)
