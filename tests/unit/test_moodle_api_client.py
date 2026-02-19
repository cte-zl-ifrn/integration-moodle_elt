"""
Unit tests for MoodleAPIClient based on TEST_SCENARIOS.md
Tests cover: Client initialization, URL validation, HTTPS enforcement
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Add dags to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'dags'))

from utils.moodle_api import MoodleAPIClient


class TestMoodleAPIClientInitialization:
    """Test 1.1: Client Initialization"""
    
    def test_1_1_1_initialize_with_valid_https_url(self):
        """Test 1.1.1: Initialize client with valid HTTPS URL"""
        # Arrange
        base_url = "https://moodle.example.com"
        token = "validtoken123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com"
        assert client.token == token
    
    def test_1_1_2_initialize_without_protocol_auto_add_https(self, caplog):
        """Test 1.1.2: Initialize client without protocol (auto-add https)"""
        # Arrange
        base_url = "moodle.example.com"
        token = "validtoken123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com"
        assert "Added https:// protocol to URL" in caplog.text
    
    def test_1_1_3_initialize_with_http_url_should_fail(self):
        """Test 1.1.3: Initialize client with HTTP URL (should fail)"""
        # Arrange
        base_url = "http://moodle.example.com"
        token = "validtoken123"
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            MoodleAPIClient(base_url=base_url, token=token)
        
        assert "Insecure HTTP protocol detected" in str(exc_info.value)
        assert "Please use HTTPS" in str(exc_info.value)
    
    def test_1_1_4_initialize_with_empty_url(self):
        """Test 1.1.4: Initialize client with empty URL"""
        # Arrange
        base_url = ""
        token = "validtoken123"
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            MoodleAPIClient(base_url=base_url, token=token)
        
        assert "Moodle URL cannot be empty" in str(exc_info.value)
    
    def test_1_1_5_initialize_with_trailing_slash(self):
        """Test 1.1.5: Initialize client with trailing slash in URL"""
        # Arrange
        base_url = "https://moodle.example.com/"
        token = "validtoken123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com"
    
    def test_1_1_6_initialize_with_custom_parameters(self):
        """Test 1.1.6: Initialize client with custom parameters"""
        # Arrange
        base_url = "https://moodle.example.com"
        token = "validtoken123"
        rate_limit_delay = 2.0
        max_retries = 5
        timeout = 60
        
        # Act
        client = MoodleAPIClient(
            base_url=base_url,
            token=token,
            rate_limit_delay=rate_limit_delay,
            max_retries=max_retries,
            timeout=timeout
        )
        
        # Assert
        assert client.base_url == "https://moodle.example.com"
        assert client.token == token
        assert client.rate_limit_delay == rate_limit_delay
        assert client.timeout == timeout


class TestURLValidation:
    """Test 1.2: URL Validation"""
    
    def test_1_2_1_validate_minimum_url_length(self):
        """Test 1.2.1: Validate minimum URL length"""
        # Arrange
        base_url = "https://a.co"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://a.co"
    
    def test_1_2_2_reject_url_shorter_than_minimum(self):
        """Test 1.2.2: Reject URL shorter than minimum"""
        # Arrange
        base_url = "https://a"
        token = "token123"
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            MoodleAPIClient(base_url=base_url, token=token)
        
        assert "Invalid Moodle URL format" in str(exc_info.value)
    
    def test_1_2_3_validate_url_with_path(self):
        """Test 1.2.3: Validate URL with path"""
        # Arrange
        base_url = "https://moodle.example.com/path"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com/path"
    
    def test_1_2_4_validate_url_with_port(self):
        """Test 1.2.4: Validate URL with port"""
        # Arrange
        base_url = "https://moodle.example.com:8080"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com:8080"


class TestHTTPSEnforcement:
    """Test 3.1: HTTPS Protocol Tests"""
    
    def test_3_1_1_accept_explicit_https_url(self):
        """Test 3.1.1: Accept explicit HTTPS URL"""
        # Arrange
        base_url = "https://moodle.example.com"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com"
    
    def test_3_1_2_reject_explicit_http_url(self):
        """Test 3.1.2: Reject explicit HTTP URL"""
        # Arrange
        base_url = "http://moodle.example.com"
        token = "token123"
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            MoodleAPIClient(base_url=base_url, token=token)
        
        assert "https" in str(exc_info.value).lower()
    
    def test_3_1_3_auto_add_https_to_url_without_protocol(self, caplog):
        """Test 3.1.3: Auto-add HTTPS to URL without protocol"""
        # Arrange
        base_url = "moodle.example.com"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com"
    
    def test_3_1_5_http_in_url_path_not_protocol(self):
        """Test 3.1.5: HTTP in URL path (not protocol)"""
        # Arrange
        base_url = "https://moodle.com/http/path"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.com/http/path"


class TestURLFormatTests:
    """Test 3.2: URL Format Tests"""
    
    def test_3_2_1_url_with_subdomain(self):
        """Test 3.2.1: URL with subdomain"""
        # Arrange
        base_url = "https://moodle.sub.example.com"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.sub.example.com"
    
    def test_3_2_2_url_with_port_number(self):
        """Test 3.2.2: URL with port number"""
        # Arrange
        base_url = "https://moodle.example.com:8443"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://moodle.example.com:8443"
    
    def test_3_2_3_url_with_path(self):
        """Test 3.2.3: URL with path"""
        # Arrange
        base_url = "https://example.com/moodle"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://example.com/moodle"
    
    def test_3_2_5_localhost_url(self):
        """Test 3.2.5: Localhost URL"""
        # Arrange
        base_url = "https://localhost:8080"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://localhost:8080"
    
    def test_3_2_6_ip_address_url(self):
        """Test 3.2.6: IP address URL"""
        # Arrange
        base_url = "https://192.168.1.100"
        token = "token123"
        
        # Act
        client = MoodleAPIClient(base_url=base_url, token=token)
        
        # Assert
        assert client.base_url == "https://192.168.1.100"


class TestAPICallOperations:
    """Test 1.3: API Call Operations"""
    
    @patch('utils.moodle_api.requests.Session.post')
    @patch('utils.moodle_api.time.sleep')
    def test_1_3_1_successful_api_call(self, mock_sleep, mock_post, caplog):
        """Test 1.3.1: Successful API call"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "name": "Test"}]
        mock_post.return_value = mock_response
        
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act
        result = client._call_api("test_function")
        
        # Assert
        assert result == [{"id": 1, "name": "Test"}]
        assert "Calling Moodle API: test_function" in caplog.text
        mock_sleep.assert_called_once()
    
    @patch('utils.moodle_api.requests.Session.post')
    @patch('utils.moodle_api.time.sleep')
    def test_1_3_2_api_call_with_parameters(self, mock_sleep, mock_post):
        """Test 1.3.2: API call with parameters"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "email": "test@example.com"}]
        mock_post.return_value = mock_response
        
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        params = {"criteria[0][key]": "email", "criteria[0][value]": "test@example.com"}
        
        # Act
        result = client._call_api("core_user_get_users", params)
        
        # Assert
        assert len(result) > 0
        call_args = mock_post.call_args
        assert params.items() <= call_args[1]['data'].items()
    
    @patch('utils.moodle_api.requests.Session.post')
    def test_1_3_3_handle_moodle_api_error_response(self, mock_post):
        """Test 1.3.3: Handle Moodle API error response"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"exception": "error", "message": "Invalid token"}
        mock_post.return_value = mock_response
        
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            client._call_api("test_function")
        
        assert "Moodle API Error: Invalid token" in str(exc_info.value)
    
    @patch('utils.moodle_api.requests.Session.post')
    def test_1_3_4_handle_network_timeout(self, mock_post):
        """Test 1.3.4: Handle network timeout"""
        # Arrange
        import requests
        mock_post.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act & Assert
        with pytest.raises(requests.exceptions.Timeout):
            client._call_api("test_function")
    
    @patch('utils.moodle_api.requests.Session.post')
    def test_1_3_5_handle_http_error_status(self, mock_post):
        """Test 1.3.5: Handle HTTP error status"""
        # Arrange
        import requests
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_post.return_value = mock_response
        
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act & Assert
        with pytest.raises(requests.exceptions.HTTPError):
            client._call_api("test_function")
    
    @patch('utils.moodle_api.time.sleep')
    @patch('utils.moodle_api.requests.Session.post')
    def test_1_3_6_rate_limiting_between_calls(self, mock_post, mock_sleep):
        """Test 1.3.6: Rate limiting between calls"""
        # Arrange
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_post.return_value = mock_response
        
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123", rate_limit_delay=1.0)
        
        # Act
        client._call_api("test_function1")
        client._call_api("test_function2")
        
        # Assert
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(1.0)


class TestSpecificAPIMethods:
    """Test 1.4: Specific API Methods"""
    
    @patch('utils.moodle_api.MoodleAPIClient._call_api')
    def test_1_4_1_get_users_without_criteria(self, mock_call_api):
        """Test 1.4.1: get_users() without criteria"""
        # Arrange
        mock_call_api.return_value = {"users": [{"id": 1, "username": "testuser"}]}
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act
        result = client.get_users()
        
        # Assert
        mock_call_api.assert_called_once_with('core_user_get_users', {})
        assert result == [{"id": 1, "username": "testuser"}]
    
    @patch('utils.moodle_api.MoodleAPIClient._call_api')
    def test_1_4_2_get_users_with_criteria(self, mock_call_api):
        """Test 1.4.2: get_users() with criteria"""
        # Arrange
        mock_call_api.return_value = {"users": [{"id": 1, "email": "user@example.com"}]}
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        criteria = [{"key": "email", "value": "user@example.com"}]
        
        # Act
        result = client.get_users(criteria=criteria)
        
        # Assert
        assert result == [{"id": 1, "email": "user@example.com"}]
        call_args = mock_call_api.call_args[0]
        assert call_args[0] == 'core_user_get_users'
    
    @patch('utils.moodle_api.MoodleAPIClient._call_api')
    def test_1_4_3_get_courses(self, mock_call_api):
        """Test 1.4.3: get_courses()"""
        # Arrange
        mock_call_api.return_value = [{"id": 1, "fullname": "Test Course"}]
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act
        result = client.get_courses()
        
        # Assert
        mock_call_api.assert_called_once_with('core_course_get_courses')
        assert result == [{"id": 1, "fullname": "Test Course"}]
    
    @patch('utils.moodle_api.MoodleAPIClient._call_api')
    def test_1_4_4_get_enrolled_users(self, mock_call_api):
        """Test 1.4.4: get_enrolled_users()"""
        # Arrange
        mock_call_api.return_value = [{"id": 1, "username": "student1"}]
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act
        result = client.get_enrolled_users(course_id=42)
        
        # Assert
        mock_call_api.assert_called_once_with('core_enrol_get_enrolled_users', {'courseid': 42})
        assert result == [{"id": 1, "username": "student1"}]
    
    @patch('utils.moodle_api.MoodleAPIClient._call_api')
    def test_1_4_5_get_roles(self, mock_call_api):
        """Test 1.4.5: get_roles()"""
        # Arrange
        mock_call_api.return_value = [{"id": 5, "shortname": "student"}]
        client = MoodleAPIClient(base_url="https://moodle.example.com", token="token123")
        
        # Act
        result = client.get_roles()
        
        # Assert
        mock_call_api.assert_called_once_with('core_role_get_all_roles')
        assert result == [{"id": 5, "shortname": "student"}]
