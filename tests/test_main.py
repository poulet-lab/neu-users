from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_main():
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["service_name"] == "neu-users"
