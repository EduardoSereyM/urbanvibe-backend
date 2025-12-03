from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_venues_map():
    response = client.get("/api/v1/venues/map")
    # Even if empty, it should be 200 OK, not 404
    assert response.status_code == 200
    assert isinstance(response.json(), list)
