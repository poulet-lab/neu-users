from fastapi.testclient import TestClient

from src.main import app
from src.settings import settings

client = TestClient(app)


def test_main():
    response = client.get(f"/{settings.root_path}/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == settings.service_name
