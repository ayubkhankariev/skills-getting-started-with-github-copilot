from fastapi.testclient import TestClient
import pytest

from src.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    # Basic expectations from seeded data
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_duplicate_and_unregister(client):
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # Ensure clean state: try to unregister if present
    client.delete(f"/activities/{activity}/unregister?email={email}")

    # Signup should succeed
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Duplicate signup should fail with 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # Verify participant is present
    r3 = client.get("/activities")
    participants = r3.json()[activity]["participants"]
    assert email in participants

    # Unregister should succeed
    r4 = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert r4.status_code == 200
    assert "Unregistered" in r4.json().get("message", "")

    # Ensure removed
    r5 = client.get("/activities")
    participants2 = r5.json()[activity]["participants"]
    assert email not in participants2


def test_signup_unknown_activity(client):
    r = client.post("/activities/NotAnActivity/signup?email=a@b.com")
    assert r.status_code == 404


def test_unregister_unknown_activity(client):
    r = client.delete("/activities/Nope/unregister?email=a@b.com")
    assert r.status_code == 404
