# tests/conftest.py
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_response():
    """Create a mock response object."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    return mock

@pytest.fixture
def mock_requests(monkeypatch, mock_response):
    """Patch requests library with mock response."""
    mock_get = MagicMock(return_value=mock_response)
    mock_post = MagicMock(return_value=mock_response)
    
    monkeypatch.setattr("requests.get", mock_get)
    monkeypatch.setattr("requests.post", mock_post)
    
    return mock_get, mock_post
