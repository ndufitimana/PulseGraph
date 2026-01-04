import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Worlds I am in here"}


def test_read_root_content_type():
    """Test the root endpoint returns JSON content type."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
