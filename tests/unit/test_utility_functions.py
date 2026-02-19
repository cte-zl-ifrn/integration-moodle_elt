"""
Unit tests for Utility Functions based on TEST_SCENARIOS.md
Tests cover: Hash computation, record preparation, schema validation
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add dags to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'dags'))

from utils.moodle_api import compute_hash, prepare_raw_record, validate_json_schema


class TestHashComputation:
    """Test 12.1: Hash Computation"""
    
    def test_12_1_1_compute_hash_for_dictionary(self):
        """Test 12.1.1: Compute hash for dictionary"""
        # Arrange
        data = {"id": 1, "name": "test"}
        
        # Act
        hash1 = compute_hash(data)
        hash2 = compute_hash(data)
        
        # Assert
        assert hash1 == hash2
        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 hash length
    
    def test_12_1_2_hash_order_independence(self):
        """Test 12.1.2: Hash order independence"""
        # Arrange
        data1 = {"id": 1, "name": "test", "value": "abc"}
        data2 = {"name": "test", "value": "abc", "id": 1}
        
        # Act
        hash1 = compute_hash(data1)
        hash2 = compute_hash(data2)
        
        # Assert
        assert hash1 == hash2
    
    def test_12_1_3_hash_for_complex_nested_structure(self):
        """Test 12.1.3: Hash for complex nested structure"""
        # Arrange
        data = {
            "id": 1,
            "users": [
                {"id": 1, "name": "user1"},
                {"id": 2, "name": "user2"}
            ],
            "metadata": {
                "created": "2024-01-01",
                "tags": ["tag1", "tag2"]
            }
        }
        
        # Act
        hash1 = compute_hash(data)
        hash2 = compute_hash(data)
        
        # Assert
        assert hash1 == hash2
        assert isinstance(hash1, str)


class TestRecordPreparation:
    """Test 12.2: Record Preparation"""
    
    def test_12_2_1_prepare_raw_record(self):
        """Test 12.2.1: Prepare raw record"""
        # Arrange
        instance = 'moodle1'
        entity = 'user'
        moodle_id = 42
        data = {"id": 42, "username": "testuser"}
        
        # Act
        record = prepare_raw_record(instance, entity, moodle_id, data)
        
        # Assert
        assert record['instance'] == 'moodle1'
        assert record['entity'] == 'user'
        assert record['moodle_id'] == 42
        assert 'data_json' in record
        assert 'ts_extract' in record
        assert 'hash_content' in record
        
        # Validate timestamp format (ISO 8601)
        datetime.fromisoformat(record['ts_extract'])
    
    def test_12_2_2_prepare_record_with_null_moodle_id(self):
        """Test 12.2.2: Prepare record with null moodle_id"""
        # Arrange
        instance = 'moodle1'
        entity = 'user'
        moodle_id = None
        data = {"username": "testuser"}
        
        # Act
        record = prepare_raw_record(instance, entity, moodle_id, data)
        
        # Assert
        assert record['instance'] == 'moodle1'
        assert record['entity'] == 'user'
        assert record['moodle_id'] is None
        assert 'data_json' in record


class TestSchemaValidation:
    """Test 12.3: Schema Validation"""
    
    def test_12_3_1_validate_user_schema(self):
        """Test 12.3.1: Validate user schema"""
        # Arrange
        valid_user = {"id": 1, "username": "test"}
        
        # Act
        result = validate_json_schema(valid_user, 'user')
        
        # Assert
        assert result is True
    
    def test_12_3_2_validate_course_schema(self):
        """Test 12.3.2: Validate course schema"""
        # Arrange
        valid_course = {"id": 1, "fullname": "Test Course"}
        
        # Act
        result = validate_json_schema(valid_course, 'course')
        
        # Assert
        assert result is True
    
    def test_12_3_3_validate_with_missing_field(self):
        """Test 12.3.3: Validate with missing field"""
        # Arrange
        invalid_user = {"id": 1}  # Missing username
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            validate_json_schema(invalid_user, 'user')
        
        assert "Missing required field" in str(exc_info.value)
        assert "username" in str(exc_info.value)
    
    def test_12_3_4_validate_unknown_entity(self):
        """Test 12.3.4: Validate unknown entity"""
        # Arrange
        data = {"id": 1, "value": "test"}
        
        # Act
        result = validate_json_schema(data, 'unknown_entity')
        
        # Assert
        # No validation for unknown entity, should return True
        assert result is True


class TestDataValidation:
    """Additional validation tests"""
    
    def test_validate_role_schema(self):
        """Test role schema validation"""
        # Arrange
        valid_role = {"id": 5, "shortname": "student"}
        
        # Act
        result = validate_json_schema(valid_role, 'role')
        
        # Assert
        assert result is True
    
    def test_validate_grade_schema(self):
        """Test grade schema validation"""
        # Arrange
        valid_grade = {"userid": 1, "itemid": 2, "grade": 85.5}
        
        # Act
        result = validate_json_schema(valid_grade, 'grade')
        
        # Assert
        assert result is True
    
    def test_validate_grade_item_schema(self):
        """Test grade_item schema validation"""
        # Arrange
        valid_grade_item = {"id": 1, "itemname": "Final Exam"}
        
        # Act
        result = validate_json_schema(valid_grade_item, 'grade_item')
        
        # Assert
        assert result is True
    
    def test_validate_completion_schema(self):
        """Test completion schema validation"""
        # Arrange
        valid_completion = {"userid": 1, "completionstate": 1}
        
        # Act
        result = validate_json_schema(valid_completion, 'completion')
        
        # Assert
        assert result is True
    
    def test_hash_different_data_different_hash(self):
        """Test that different data produces different hashes"""
        # Arrange
        data1 = {"id": 1, "name": "test1"}
        data2 = {"id": 2, "name": "test2"}
        
        # Act
        hash1 = compute_hash(data1)
        hash2 = compute_hash(data2)
        
        # Assert
        assert hash1 != hash2
