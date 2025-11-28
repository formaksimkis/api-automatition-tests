import pytest
from utils.api_client import ApiClient

@pytest.fixture
def api_client():
    return ApiClient()

@pytest.fixture
def sample_post_data():
    return {
        "title": "Test Post",
        "body": "This is a test post body",
        "userId": 1
    }

@pytest.fixture
def patch_data_all():
    return {
        "title": "Patched Title",
        "body": "Patched body content",
        "userId": 1,
    }

@pytest.fixture
def patch_data_multiple_fields():
    return {
        "title": "New Updated Title",
        "body": "New updated body content"
    }

@pytest.fixture
def patch_data_empty():
    return {}
