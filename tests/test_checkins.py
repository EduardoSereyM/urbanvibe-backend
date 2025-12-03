import pytest

def test_create_checkin_unauthorized(client):
    response = client.post("/api/v1/checkins/", json={
        "token_id": "fake",
        "user_lat": -33.0,
        "user_lng": -70.0
    })
    assert response.status_code == 401
