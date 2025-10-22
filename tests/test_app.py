"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    """Test that root path redirects to static/index.html"""
    response = client.get("/")
    assert response.status_code == 200  # OK status for redirects to static files
    assert "text/html" in response.headers["content-type"].lower()


def test_get_activities():
    """Test retrieving the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    
    # Check that we get a dictionary of activities
    assert isinstance(activities, dict)
    
    # Check that each activity has the required fields
    for activity_name, details in activities.items():
        assert isinstance(activity_name, str)
        assert isinstance(details, dict)
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_for_activity():
    """Test signing up for an activity"""
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # Try signing up
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    
    # Verify the participant was added
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]
    
    # Try signing up again (should fail)
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup", 
                         params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_unregister_from_activity():
    """Test unregistering from an activity"""
    activity_name = "Chess Club"
    email = "test2@mergington.edu"
    
    # First sign up for the activity
    client.post(f"/activities/{activity_name}/signup", params={"email": email})
    
    # Now unregister
    response = client.delete(f"/activities/{activity_name}/unregister", 
                           params={"email": email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    
    # Verify the participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]
    
    # Try unregistering again (should fail)
    response = client.delete(f"/activities/{activity_name}/unregister", 
                           params={"email": email})
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.delete("/activities/NonexistentClub/unregister", 
                           params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]