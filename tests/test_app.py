import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    # Store initial state
    initial_activities = {
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
        },
        "Basketball Team": {
            "description": "Competitive basketball practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Tennis training and tournaments",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["alex@mergington.edu"]
        },
        "Art Studio": {
            "description": "Painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater production, acting, and performance",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
            "max_participants": 12,
            "participants": ["mason@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through experiments and projects",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
        }
    }
    
    # Clear and restore initial state
    activities.clear()
    activities.update(initial_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(initial_activities)


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_all_activities(self, client):
        """Test retrieving all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_activities_have_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)

    def test_activities_have_correct_participants(self, client):
        """Test that activities have the correct initial participants."""
        response = client.get("/activities")
        data = response.json()
        
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in data["Programming Class"]["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant(self, client):
        """Test signing up a new participant for an activity."""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]

    def test_signup_adds_participant_to_list(self, client):
        """Test that signup actually adds the participant to the activity."""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Tennis%20Club/signup?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email in data["Tennis Club"]["participants"]

    def test_signup_duplicate_participant_fails(self, client):
        """Test that signing up the same participant twice fails."""
        email = "michael@mergington.edu"
        
        # First signup should succeed (already in Chess Club)
        response = client.post(f"/activities/Chess%20Club/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_increases_participant_count(self, client):
        """Test that signup increases the participant count."""
        activity_name = "Basketball Team"
        
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email=newstudent@mergington.edu"
        )
        
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        
        assert count_after == count_before + 1


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/participants endpoint."""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant."""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        email = "michael@mergington.edu"
        
        client.delete(f"/activities/Chess%20Club/participants?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_fails(self, client):
        """Test that unregistering a non-existent participant fails."""
        response = client.delete(
            "/activities/Chess%20Club/participants?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_from_nonexistent_activity_fails(self, client):
        """Test that unregistering from a non-existent activity fails."""
        response = client.delete(
            "/activities/Nonexistent%20Activity/participants?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"]

    def test_unregister_decreases_participant_count(self, client):
        """Test that unregister decreases the participant count."""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        response_before = client.get("/activities")
        count_before = len(response_before.json()[activity_name]["participants"])
        
        client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/participants?email={email}"
        )
        
        response_after = client.get("/activities")
        count_after = len(response_after.json()[activity_name]["participants"])
        
        assert count_after == count_before - 1


class TestEndtoEnd:
    """End-to-end integration tests."""

    def test_signup_and_unregister_flow(self, client):
        """Test the complete flow of signing up and then unregistering."""
        activity_name = "Tennis Club"
        email = "integration@mergington.edu"
        
        # Initial check
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        after_signup_count = len(response.json()[activity_name]["participants"])
        assert after_signup_count == initial_count + 1
        assert email in response.json()[activity_name]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name.replace(' ', '%20')}/participants?email={email}"
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        final_count = len(response.json()[activity_name]["participants"])
        assert final_count == initial_count
        assert email not in response.json()[activity_name]["participants"]

    def test_multiple_signups_and_unregisters(self, client):
        """Test multiple participants signing up and unregistering."""
        activity_name = "Art Studio"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]
        
        # Sign up multiple students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all signed up
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in emails:
            assert email in participants
        
        # Unregister all
        for email in emails:
            response = client.delete(
                f"/activities/{activity_name.replace(' ', '%20')}/participants?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all unregistered
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        for email in emails:
            assert email not in participants
