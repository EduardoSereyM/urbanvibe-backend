import pytest

# We need to mock the DB or have data. 
# Assuming seed data runs before tests or we mock the service response.
# For simplicity in this environment, we'll mock the service in a real test, 
# but here we can just write the test assuming the endpoint works.

def test_read_venues(client):
    response = client.get(f"/api/v1/venues/")
    # It might return 200 with empty list or list of venues
    assert response.status_code == 200
    assert isinstance(response.json(), list)
