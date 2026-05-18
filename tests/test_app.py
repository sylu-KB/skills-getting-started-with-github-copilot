import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a clean state before each test."""
    original = {name: {**data, "participants": list(data["participants"])} for name, data in activities.items()}
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


# --- GET /activities ---

def test_get_activities_returns_200():
    # Arrange - no setup needed

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200


def test_get_activities_returns_dict():
    # Arrange - no setup needed

    # Act
    response = client.get("/activities")

    # Assert
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_expected_fields():
    # Arrange - no setup needed

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant():
    # Arrange
    email = "newstudent@mergington.edu"

    # Act
    client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    response = client.get("/activities")
    assert email in response.json()["Chess Club"]["participants"]


def test_signup_activity_not_found():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/Nonexistent Activity/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered():
    # Arrange
    email = "duplicate@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")

    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


# --- DELETE /activities/{activity_name}/unregister ---

def test_unregister_success():
    # Arrange
    email = "todelete@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")

    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    # Arrange
    email = "todelete@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")

    # Act
    client.delete(f"/activities/Chess Club/unregister?email={email}")

    # Assert
    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_activity_not_found():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/Nonexistent Activity/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_signed_up():
    # Arrange
    email = "notregistered@mergington.edu"

    # Act
    response = client.delete(f"/activities/Chess Club/unregister?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
