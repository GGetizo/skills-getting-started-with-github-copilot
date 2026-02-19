"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_activities = {
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and discoveries",
            "schedule": "Thursdays, 3:30 PM - 4:45 PM",
            "max_participants": 18,
            "participants": ["james@mergington.edu", "lucy@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball training and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["marcus@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis skills development and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:15 PM",
            "max_participants": 12,
            "participants": ["sarah@mergington.edu", "ryan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["hannah@mergington.edu", "grace@mergington.edu"]
        },
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    activities.clear()
    activities.update(initial_activities)
    yield
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Debate Team" in data
        assert "Science Club" in data
        assert len(data) == 9
    
    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity
    
    def test_participants_are_lists(self, client):
        """Test that participants are returned as lists"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity in data.items():
            assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Debate Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in activities["Debate Team"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_registered(self, client):
        """Test signup for an activity when already registered"""
        response = client.post(
            "/activities/Debate Team/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up"""
        initial_count = len(activities["Science Club"]["participants"])
        
        response1 = client.post(
            "/activities/Science Club/signup?email=student1@mergington.edu"
        )
        response2 = client.post(
            "/activities/Science Club/signup?email=student2@mergington.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities["Science Club"]["participants"]) == initial_count + 2


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_successful_unregister(self, client):
        """Test successful unregister from an activity"""
        # First verify the student is registered
        assert "alex@mergington.edu" in activities["Debate Team"]["participants"]
        
        response = client.post(
            "/activities/Debate Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alex@mergington.edu" not in activities["Debate Team"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from a non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_registered_student(self, client):
        """Test unregister when student is not registered"""
        response = client.post(
            "/activities/Debate Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_multiple_students(self, client):
        """Test unregistering multiple students from the same activity"""
        initial_count = len(activities["Science Club"]["participants"])
        
        response1 = client.post(
            "/activities/Science Club/unregister?email=james@mergington.edu"
        )
        response2 = client.post(
            "/activities/Science Club/unregister?email=lucy@mergington.edu"
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert len(activities["Science Club"]["participants"]) == initial_count - 2


class TestIntegration:
    """Integration tests combining multiple endpoints"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test the complete workflow of signing up and unregistering"""
        email = "integration@mergington.edu"
        activity = "Chess Club"
        
        # Check initial state
        initial_participants = activities[activity]["participants"].copy()
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        assert email in activities[activity]["participants"]
        
        # Verify activities endpoint shows the new participant
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data[activity]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        assert email not in activities[activity]["participants"]
        
        # Verify we're back to initial state
        assert activities[activity]["participants"] == initial_participants
    
    def test_participant_count_accuracy(self, client):
        """Test that participant counts remain accurate"""
        activity = "Tennis Club"
        
        # Get initial count from activities endpoint
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity]["participants"])
        
        # Add a participant
        client.post(
            f"/activities/{activity}/signup?email=newplayer@mergington.edu"
        )
        
        # Verify count increased
        after_signup = client.get("/activities")
        after_data = after_signup.json()
        assert len(after_data[activity]["participants"]) == initial_count + 1
        
        # Remove a participant
        client.post(
            f"/activities/{activity}/unregister?email=newplayer@mergington.edu"
        )
        
        # Verify count is back to initial
        after_unregister = client.get("/activities")
        after_data = after_unregister.json()
        assert len(after_data[activity]["participants"]) == initial_count
