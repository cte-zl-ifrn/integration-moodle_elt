"""
Test fixtures for Moodle ELT Integration tests.
Provides reusable test data and mock objects.
"""

import pytest
from datetime import datetime


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "id": 123,
        "username": "testuser",
        "firstname": "Test",
        "lastname": "User",
        "email": "test@example.com",
        "auth": "manual"
    }


@pytest.fixture
def sample_course_data():
    """Sample course data for testing"""
    return {
        "id": 42,
        "fullname": "Introduction to Testing",
        "shortname": "TEST101",
        "categoryid": 1,
        "visible": 1,
        "startdate": 1640995200,
        "enddate": 1672531200
    }


@pytest.fixture
def sample_enrolment_data():
    """Sample enrolment data for testing"""
    return {
        "id": 123,
        "username": "testuser",
        "firstname": "Test",
        "lastname": "User",
        "roles": [
            {
                "roleid": 5,
                "name": "Student"
            }
        ],
        "course_id": 42
    }


@pytest.fixture
def sample_grade_data():
    """Sample grade data for testing"""
    return {
        "userid": 123,
        "itemid": 456,
        "itemname": "Final Exam",
        "grade": 85.5,
        "grademax": 100,
        "feedback": "Well done!",
        "course_id": 42
    }


@pytest.fixture
def sample_role_data():
    """Sample role data for testing"""
    return {
        "id": 5,
        "shortname": "student",
        "name": "Student",
        "description": "Students generally have fewer privileges within a course."
    }


@pytest.fixture
def sample_users_list():
    """Sample list of users for testing"""
    return [
        {"id": 1, "username": "user1", "email": "user1@example.com"},
        {"id": 2, "username": "user2", "email": "user2@example.com"},
        {"id": 3, "username": "user3", "email": "user3@example.com"}
    ]


@pytest.fixture
def sample_courses_list():
    """Sample list of courses for testing"""
    return [
        {"id": 1, "fullname": "Course 1", "shortname": "C1"},
        {"id": 2, "fullname": "Course 2", "shortname": "C2"},
        {"id": 3, "fullname": "Course 3", "shortname": "C3"}
    ]


@pytest.fixture
def moodle_api_error_response():
    """Sample Moodle API error response"""
    return {
        "exception": "invalid_parameter_exception",
        "errorcode": "invalidparameter",
        "message": "Invalid parameter value detected"
    }


@pytest.fixture
def valid_moodle_urls():
    """List of valid Moodle URLs for testing"""
    return [
        "https://moodle.example.com",
        "https://moodle.test.org",
        "https://learning.university.edu",
        "https://192.168.1.100"
    ]


@pytest.fixture
def invalid_moodle_urls():
    """List of invalid Moodle URLs for testing"""
    return [
        "http://moodle.example.com",  # HTTP instead of HTTPS
        "",  # Empty URL
        "ftp://moodle.example.com",  # Wrong protocol
        "https://a"  # Too short
    ]


@pytest.fixture
def comma_separated_urls():
    """Comma-separated URLs for configuration testing"""
    return "https://m1.example.com,https://m2.example.com,https://m3.example.com,https://m4.example.com"


@pytest.fixture
def comma_separated_tokens():
    """Comma-separated tokens for configuration testing"""
    return "token1_abc123,token2_def456,token3_ghi789,token4_jkl012"


@pytest.fixture
def mock_moodle_api_response():
    """Mock successful Moodle API response"""
    def _mock_response(data):
        from unittest.mock import Mock
        response = Mock()
        response.status_code = 200
        response.json.return_value = data
        response.raise_for_status = Mock()
        return response
    return _mock_response


@pytest.fixture
def mock_http_error_response():
    """Mock HTTP error response"""
    def _mock_error(status_code=500):
        from unittest.mock import Mock
        import requests
        response = Mock()
        response.status_code = status_code
        response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            f"{status_code} Server Error"
        )
        return response
    return _mock_error
