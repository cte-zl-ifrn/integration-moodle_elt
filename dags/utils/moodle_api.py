"""
Moodle Web Services API Client
Handles extraction from Moodle instances via REST API with rate limiting and error handling.
"""

import time
import hashlib
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# Constants
MIN_HTTPS_URL_LENGTH = 12  # Minimum valid HTTPS URL length (e.g., 'https://a.co')


class MoodleAPIClient:
    """
    Client for interacting with Moodle Web Services API.
    Supports rate limiting, retries, and error handling.
    """
    
    def __init__(
        self,
        base_url: str,
        token: str,
        rate_limit_delay: float = 1.0,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize Moodle API client.
        
        Args:
            base_url: Moodle base URL (e.g., 'https://moodle.example.com')
            token: Web services API token
            rate_limit_delay: Delay in seconds between API calls
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        # Validate and enforce https:// URL
        self.base_url = self._validate_url(base_url)
        self.token = token
        self.rate_limit_delay = rate_limit_delay
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _validate_url(self, url: str) -> str:
        """
        Validate and enforce https:// protocol for Moodle URL.
        
        Args:
            url: URL to validate
            
        Returns:
            Validated URL with https:// protocol
            
        Raises:
            ValueError: If URL is invalid or doesn't use https://
        """
        if not url:
            raise ValueError("Moodle URL cannot be empty")
        
        url = url.strip()
        
        # Check if URL starts with http:// (insecure)
        if url.lower().startswith('http://'):
            raise ValueError(
                f"Insecure HTTP protocol detected. Please use HTTPS for Moodle URL: {url}\n"
                "Change 'http://' to 'https://'"
            )
        
        # Add https:// if no protocol is specified
        if not url.lower().startswith('https://'):
            url = f'https://{url}'
            logger.info(f"Added https:// protocol to URL: {url}")
        
        # Remove trailing slash
        url = url.rstrip('/')
        
        # Basic URL validation
        if not url.startswith('https://') or len(url) < MIN_HTTPS_URL_LENGTH:
            raise ValueError(f"Invalid Moodle URL format: {url}")
        
        return url
    
    def _call_api(
        self,
        function: str,
        params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Make API call to Moodle Web Services.
        
        Args:
            function: Moodle web service function name
            params: Function parameters
            
        Returns:
            API response data
        """
        url = f"{self.base_url}/webservice/rest/server.php"
        
        payload = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json'
        }
        
        if params:
            payload.update(params)
        
        try:
            logger.info(f"Calling Moodle API: {function}")
            response = self.session.post(
                url,
                data=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Check for Moodle API errors
            if isinstance(data, dict) and 'exception' in data:
                raise Exception(f"Moodle API Error: {data.get('message', 'Unknown error')}")
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return data if isinstance(data, list) else [data]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed for {function}: {str(e)}")
            raise
    
    def get_users(self, criteria: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
        """
        Get users from Moodle using core_user_get_users.
        
        Args:
            criteria: Search criteria (e.g., [{'key': 'email', 'value': 'user@example.com'}])
            
        Returns:
            List of user dictionaries
        """
        params = {}
        if criteria:
            for idx, criterion in enumerate(criteria):
                params[f'criteria[{idx}][key]'] = criterion['key']
                params[f'criteria[{idx}][value]'] = criterion['value']
        
        result = self._call_api('core_user_get_users', params)
        return result.get('users', []) if isinstance(result, dict) else result
    
    def get_courses(self) -> List[Dict[str, Any]]:
        """
        Get all courses using core_course_get_courses.
        
        Returns:
            List of course dictionaries
        """
        return self._call_api('core_course_get_courses')
    
    def get_enrolled_users(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get enrolled users for a course using core_enrol_get_enrolled_users.
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of enrolled user dictionaries with roles
        """
        params = {'courseid': course_id}
        return self._call_api('core_enrol_get_enrolled_users', params)
    
    def get_roles(self) -> List[Dict[str, Any]]:
        """
        Get all roles using core_role_get_all_roles.
        
        Returns:
            List of role dictionaries
        """
        return self._call_api('core_role_get_all_roles')
    
    def get_enrolment_methods(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get enrolment methods for a course using core_enrol_get_course_enrolment_methods.
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of enrolment method dictionaries
        """
        params = {'courseid': course_id}
        return self._call_api('core_enrol_get_course_enrolment_methods', params)
    
    def get_course_grade_items(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Get grade items for a course using gradereport_user_get_grade_items.
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of grade item dictionaries
        """
        params = {'courseid': course_id}
        result = self._call_api('gradereport_user_get_grade_items', params)
        return result.get('usergrades', []) if isinstance(result, dict) else result
    
    def get_grades(self, course_id: int, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get grades for a course using gradereport_user_get_grades_table.
        
        Args:
            course_id: Moodle course ID
            user_id: Optional user ID to filter grades
            
        Returns:
            List of grade dictionaries
        """
        params = {'courseid': course_id}
        if user_id:
            params['userid'] = user_id
        
        result = self._call_api('gradereport_user_get_grades_table', params)
        return result.get('tables', []) if isinstance(result, dict) else result
    
    def get_course_completion(self, course_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get course completion status using core_completion_get_course_completion_status.
        
        Args:
            course_id: Moodle course ID
            user_id: Moodle user ID
            
        Returns:
            Completion status dictionary
        """
        params = {
            'courseid': course_id,
            'userid': user_id
        }
        result = self._call_api('core_completion_get_course_completion_status', params)
        return result[0] if isinstance(result, list) and result else result


def compute_hash(data: Any) -> str:
    """
    Compute MD5 hash of JSON data for deduplication.
    
    Args:
        data: Data to hash (will be JSON serialized)
        
    Returns:
        Hex digest of MD5 hash
    """
    json_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(json_str.encode()).hexdigest()


def prepare_raw_record(
    instance: str,
    entity: str,
    moodle_id: Optional[int],
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Prepare a record for insertion into moodle_raw table.
    
    Args:
        instance: Moodle instance identifier (e.g., 'moodle1')
        entity: Entity type (e.g., 'user', 'course')
        moodle_id: Moodle entity ID
        data: Raw data from API
        
    Returns:
        Dictionary ready for database insertion
    """
    return {
        'instance': instance,
        'entity': entity,
        'moodle_id': moodle_id,
        'data_json': json.dumps(data),
        'ts_extract': datetime.utcnow().isoformat(),
        'hash_content': compute_hash(data)
    }


def validate_json_schema(data: Dict[str, Any], entity: str) -> bool:
    """
    Validate JSON data against expected schema for entity type.
    
    Args:
        data: Data to validate
        entity: Entity type
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = {
        'user': ['id', 'username'],
        'course': ['id', 'fullname'],
        'role': ['id', 'shortname'],
        'grade': ['userid', 'itemid'],
        'grade_item': ['id', 'itemname'],
        'completion': ['userid', 'completionstate'],
    }
    
    if entity in required_fields:
        for field in required_fields[entity]:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' for entity '{entity}'")
    
    return True


def parse_moodle_config(urls_str: str, tokens_str: str) -> List[Dict[str, str]]:
    """
    Parse comma-separated Moodle URLs and tokens into a list of configurations.
    
    Args:
        urls_str: Comma-separated list of Moodle URLs
        tokens_str: Comma-separated list of Moodle tokens
        
    Returns:
        List of dictionaries with 'url' and 'token' keys
        
    Raises:
        ValueError: If URLs and tokens count mismatch or invalid format
        
    Example:
        >>> urls = "https://moodle1.com,https://moodle2.com"
        >>> tokens = "token1,token2"
        >>> configs = parse_moodle_config(urls, tokens)
        >>> len(configs)
        2
    """
    if not urls_str or not tokens_str:
        raise ValueError("Both URLs and tokens must be provided")
    
    # Split by comma and strip whitespace
    urls = [url.strip() for url in urls_str.split(',') if url.strip()]
    tokens = [token.strip() for token in tokens_str.split(',') if token.strip()]
    
    if len(urls) != len(tokens):
        raise ValueError(
            f"Number of URLs ({len(urls)}) must match number of tokens ({len(tokens)}). "
            "Ensure you have the same number of comma-separated URLs and tokens."
        )
    
    if not urls:
        raise ValueError("At least one Moodle URL and token must be provided")
    
    # Create configuration list
    configs = []
    for i, (url, token) in enumerate(zip(urls, tokens)):
        if not url or not token:
            raise ValueError(f"Empty URL or token at position {i+1}")
        
        configs.append({
            'url': url,
            'token': token,
            'instance': f'moodle{i+1}'
        })
    
    return configs


def get_moodle_instance_config(instance_id: str, urls_str: str, tokens_str: str) -> Dict[str, str]:
    """
    Get configuration for a specific Moodle instance from comma-separated lists.
    
    Args:
        instance_id: Instance identifier (e.g., 'moodle1', 'moodle2')
        urls_str: Comma-separated list of Moodle URLs
        tokens_str: Comma-separated list of Moodle tokens
        
    Returns:
        Dictionary with 'url' and 'token' for the specified instance
        
    Raises:
        ValueError: If instance not found in configuration
    """
    configs = parse_moodle_config(urls_str, tokens_str)
    
    for config in configs:
        if config['instance'] == instance_id:
            return config
    
    raise ValueError(
        f"Instance '{instance_id}' not found in configuration. "
        f"Available instances: {[c['instance'] for c in configs]}"
    )
