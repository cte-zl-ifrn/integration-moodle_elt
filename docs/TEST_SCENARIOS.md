# Test Scenarios - Moodle ELT Integration

## Overview

This document describes all test scenarios for the Moodle ELT Integration project. These scenarios will be used to write comprehensive unit and integration tests.

**Last Updated**: 2026-02-19  
**Status**: Complete - Ready for test implementation

---

## Table of Contents

1. [MoodleAPIClient Tests](#1-moodleapiclient-tests)
2. [Configuration Management Tests](#2-configuration-management-tests)
3. [URL Validation and HTTPS Enforcement Tests](#3-url-validation-and-https-enforcement-tests)
4. [Data Extraction Tests](#4-data-extraction-tests)
5. [Data Loading Tests](#5-data-loading-tests)
6. [Data Transformation Tests](#6-data-transformation-tests)
7. [DAG Workflow Tests](#7-dag-workflow-tests)
8. [Error Handling Tests](#8-error-handling-tests)
9. [Integration Tests](#9-integration-tests)
10. [Security Tests](#10-security-tests)
11. [Performance Tests](#11-performance-tests)

---

## 1. MoodleAPIClient Tests

### 1.1 Client Initialization

#### Test 1.1.1: Initialize client with valid HTTPS URL
**Input:**
- `base_url`: `"https://moodle.example.com"`
- `token`: `"validtoken123"`

**Expected Result:**
- Client created successfully
- `base_url` is `"https://moodle.example.com"` (no trailing slash)
- Token stored correctly

**Test Type:** Unit Test

---

#### Test 1.1.2: Initialize client without protocol (auto-add https)
**Input:**
- `base_url`: `"moodle.example.com"`
- `token`: `"validtoken123"`

**Expected Result:**
- Client created successfully
- `base_url` is `"https://moodle.example.com"`
- Log message: "Added https:// protocol to URL"

**Test Type:** Unit Test

---

#### Test 1.1.3: Initialize client with HTTP URL (should fail)
**Input:**
- `base_url`: `"http://moodle.example.com"`
- `token`: `"validtoken123"`

**Expected Result:**
- `ValueError` raised
- Error message contains: "Insecure HTTP protocol detected"
- Error message contains: "Please use HTTPS"

**Test Type:** Unit Test

---

#### Test 1.1.4: Initialize client with empty URL
**Input:**
- `base_url`: `""`
- `token`: `"validtoken123"`

**Expected Result:**
- `ValueError` raised
- Error message: "Moodle URL cannot be empty"

**Test Type:** Unit Test

---

#### Test 1.1.5: Initialize client with trailing slash in URL
**Input:**
- `base_url`: `"https://moodle.example.com/"`
- `token`: `"validtoken123"`

**Expected Result:**
- Client created successfully
- `base_url` is `"https://moodle.example.com"` (trailing slash removed)

**Test Type:** Unit Test

---

#### Test 1.1.6: Initialize client with custom parameters
**Input:**
- `base_url`: `"https://moodle.example.com"`
- `token`: `"validtoken123"`
- `rate_limit_delay`: `2.0`
- `max_retries`: `5`
- `timeout`: `60`

**Expected Result:**
- Client created with custom parameters
- All parameters stored correctly

**Test Type:** Unit Test

---

### 1.2 URL Validation

#### Test 1.2.1: Validate minimum URL length
**Input:**
- `base_url`: `"https://a.co"`

**Expected Result:**
- Valid URL (exactly MIN_HTTPS_URL_LENGTH characters)

**Test Type:** Unit Test

---

#### Test 1.2.2: Reject URL shorter than minimum
**Input:**
- `base_url`: `"https://a"`

**Expected Result:**
- `ValueError` raised
- Error message: "Invalid Moodle URL format"

**Test Type:** Unit Test

---

#### Test 1.2.3: Validate URL with path
**Input:**
- `base_url`: `"https://moodle.example.com/path"`

**Expected Result:**
- Valid URL (path preserved)

**Test Type:** Unit Test

---

#### Test 1.2.4: Validate URL with port
**Input:**
- `base_url`: `"https://moodle.example.com:8080"`

**Expected Result:**
- Valid URL (port preserved)

**Test Type:** Unit Test

---

### 1.3 API Call Operations

#### Test 1.3.1: Successful API call
**Mock Setup:**
- Mock response with status 200
- Response data: `[{"id": 1, "name": "Test"}]`

**Expected Result:**
- Returns list with data
- Rate limit delay applied
- Log message: "Calling Moodle API: test_function"

**Test Type:** Unit Test with Mocking

---

#### Test 1.3.2: API call with parameters
**Input:**
- `function`: `"core_user_get_users"`
- `params`: `{"criteria[0][key]": "email", "criteria[0][value]": "test@example.com"}`

**Mock Setup:**
- Mock response with filtered users

**Expected Result:**
- Parameters included in request payload
- Correct API endpoint called

**Test Type:** Unit Test with Mocking

---

#### Test 1.3.3: Handle Moodle API error response
**Mock Setup:**
- Response contains: `{"exception": "error", "message": "Invalid token"}`

**Expected Result:**
- Exception raised with message: "Moodle API Error: Invalid token"

**Test Type:** Unit Test with Mocking

---

#### Test 1.3.4: Handle network timeout
**Mock Setup:**
- Mock raises `requests.exceptions.Timeout`

**Expected Result:**
- Exception propagated
- Error logged

**Test Type:** Unit Test with Mocking

---

#### Test 1.3.5: Handle HTTP error status
**Mock Setup:**
- Mock response with status 500

**Expected Result:**
- `requests.exceptions.HTTPError` raised
- Error logged

**Test Type:** Unit Test with Mocking

---

#### Test 1.3.6: Rate limiting between calls
**Test:**
- Make two consecutive API calls
- Measure time between calls

**Expected Result:**
- Time difference ≥ rate_limit_delay (default 1.0 second)

**Test Type:** Unit Test with Timing

---

#### Test 1.3.7: Retry on transient failures
**Mock Setup:**
- First call: returns 503 (Service Unavailable)
- Second call: returns 200 with data

**Expected Result:**
- Request retried automatically
- Eventually succeeds

**Test Type:** Unit Test with Mocking

---

### 1.4 Specific API Methods

#### Test 1.4.1: get_users() without criteria
**Mock Setup:**
- API returns user list

**Expected Result:**
- Returns list of user dictionaries
- Calls `core_user_get_users` function

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.2: get_users() with criteria
**Input:**
- `criteria`: `[{"key": "email", "value": "user@example.com"}]`

**Expected Result:**
- Criteria formatted correctly in API call
- Returns filtered users

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.3: get_courses()
**Expected Result:**
- Calls `core_course_get_courses`
- Returns list of courses

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.4: get_enrolled_users()
**Input:**
- `course_id`: `42`

**Expected Result:**
- Calls `core_enrol_get_enrolled_users`
- Passes correct course_id parameter

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.5: get_roles()
**Expected Result:**
- Calls `core_role_get_all_roles`
- Returns list of roles

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.6: get_enrolment_methods()
**Input:**
- `course_id`: `42`

**Expected Result:**
- Calls `core_enrol_get_course_enrolment_methods`
- Returns enrolment methods for course

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.7: get_course_grade_items()
**Input:**
- `course_id`: `42`

**Expected Result:**
- Calls `gradereport_user_get_grade_items`
- Returns grade items
- Extracts 'usergrades' from response if dict

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.8: get_grades() without user_id
**Input:**
- `course_id`: `42`

**Expected Result:**
- Calls `gradereport_user_get_grades_table`
- Returns all grades for course

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.9: get_grades() with user_id
**Input:**
- `course_id`: `42`
- `user_id`: `123`

**Expected Result:**
- Passes both course_id and user_id
- Returns filtered grades

**Test Type:** Unit Test with Mocking

---

#### Test 1.4.10: get_course_completion()
**Input:**
- `course_id`: `42`
- `user_id`: `123`

**Expected Result:**
- Calls `core_completion_get_course_completion_status`
- Returns completion status

**Test Type:** Unit Test with Mocking

---

## 2. Configuration Management Tests

### 2.1 Comma-Separated Configuration Parsing

#### Test 2.1.1: Parse valid comma-separated config
**Input:**
- `urls_str`: `"https://m1.com,https://m2.com,https://m3.com"`
- `tokens_str`: `"token1,token2,token3"`

**Expected Result:**
- Returns list of 3 configurations
- Each config has 'url', 'token', 'instance' keys
- Instance names: moodle1, moodle2, moodle3

**Test Type:** Unit Test

---

#### Test 2.1.2: Parse config with whitespace
**Input:**
- `urls_str`: `"https://m1.com , https://m2.com , https://m3.com"`
- `tokens_str`: `"token1 , token2 , token3"`

**Expected Result:**
- Whitespace trimmed
- Returns 3 valid configurations

**Test Type:** Unit Test

---

#### Test 2.1.3: Mismatched URL and token count
**Input:**
- `urls_str`: `"https://m1.com,https://m2.com"`
- `tokens_str`: `"token1,token2,token3"`

**Expected Result:**
- `ValueError` raised
- Error message contains count mismatch information

**Test Type:** Unit Test

---

#### Test 2.1.4: Empty URLs string
**Input:**
- `urls_str`: `""`
- `tokens_str`: `"token1"`

**Expected Result:**
- `ValueError` raised
- Error message: "Both URLs and tokens must be provided"

**Test Type:** Unit Test

---

#### Test 2.1.5: Empty tokens string
**Input:**
- `urls_str`: `"https://m1.com"`
- `tokens_str`: `""`

**Expected Result:**
- `ValueError` raised
- Error message: "Both URLs and tokens must be provided"

**Test Type:** Unit Test

---

#### Test 2.1.6: Single instance configuration
**Input:**
- `urls_str`: `"https://moodle.example.com"`
- `tokens_str`: `"token1"`

**Expected Result:**
- Returns list with 1 configuration
- Instance name: moodle1

**Test Type:** Unit Test

---

#### Test 2.1.7: Four instances configuration
**Input:**
- `urls_str`: `"https://m1.com,https://m2.com,https://m3.com,https://m4.com"`
- `tokens_str`: `"t1,t2,t3,t4"`

**Expected Result:**
- Returns list with 4 configurations
- Instance names: moodle1, moodle2, moodle3, moodle4

**Test Type:** Unit Test

---

#### Test 2.1.8: Empty value in comma-separated list
**Input:**
- `urls_str`: `"https://m1.com,,https://m3.com"`
- `tokens_str`: `"token1,token2,token3"`

**Expected Result:**
- Empty values filtered out
- URL count = 2, token count = 3
- `ValueError` raised for mismatch

**Test Type:** Unit Test

---

### 2.2 Instance Configuration Retrieval

#### Test 2.2.1: Get configuration for moodle1
**Input:**
- `instance_id`: `"moodle1"`
- `urls_str`: `"https://m1.com,https://m2.com"`
- `tokens_str`: `"token1,token2"`

**Expected Result:**
- Returns config for moodle1
- URL: `"https://m1.com"`
- Token: `"token1"`

**Test Type:** Unit Test

---

#### Test 2.2.2: Get configuration for moodle4
**Input:**
- `instance_id`: `"moodle4"`
- `urls_str`: `"https://m1.com,https://m2.com,https://m3.com,https://m4.com"`
- `tokens_str`: `"t1,t2,t3,t4"`

**Expected Result:**
- Returns config for moodle4
- URL: `"https://m4.com"`
- Token: `"t4"`

**Test Type:** Unit Test

---

#### Test 2.2.3: Request invalid instance
**Input:**
- `instance_id`: `"moodle5"`
- `urls_str`: `"https://m1.com,https://m2.com"`
- `tokens_str`: `"token1,token2"`

**Expected Result:**
- `ValueError` raised
- Error message lists available instances

**Test Type:** Unit Test

---

### 2.3 DAG Configuration Loading

#### Test 2.3.1: Load individual variables (legacy)
**Mock Setup:**
- Airflow Variable `moodle1_url` = `"https://m1.com"`
- Airflow Variable `moodle1_token` = `"token1"`

**Expected Result:**
- Uses individual variables
- Log message: "Using individual variables for moodle1"

**Test Type:** Unit Test with Mocking

---

#### Test 2.3.2: Fallback to comma-separated config
**Mock Setup:**
- Individual variables not set (raise KeyError)
- Airflow Variable `MOODLE_URLS` = `"https://m1.com,https://m2.com"`
- Airflow Variable `MOODLE_TOKENS` = `"token1,token2"`

**Expected Result:**
- Falls back to comma-separated config
- Log message: "Using comma-separated configuration"

**Test Type:** Unit Test with Mocking

---

#### Test 2.3.3: No configuration available
**Mock Setup:**
- All variable retrieval raises KeyError

**Expected Result:**
- `ValueError` raised
- Error message explains both configuration methods

**Test Type:** Unit Test with Mocking

---

#### Test 2.3.4: Individual variables take precedence
**Mock Setup:**
- Both individual and comma-separated configs available

**Expected Result:**
- Uses individual variables
- Comma-separated config not evaluated

**Test Type:** Unit Test with Mocking

---

## 3. URL Validation and HTTPS Enforcement Tests

### 3.1 HTTPS Protocol Tests

#### Test 3.1.1: Accept explicit HTTPS URL
**Input:** `"https://moodle.example.com"`

**Expected Result:** Valid, no modifications

**Test Type:** Unit Test

---

#### Test 3.1.2: Reject explicit HTTP URL
**Input:** `"http://moodle.example.com"`

**Expected Result:**
- `ValueError` raised
- Helpful error message about using HTTPS

**Test Type:** Unit Test

---

#### Test 3.1.3: Auto-add HTTPS to URL without protocol
**Input:** `"moodle.example.com"`

**Expected Result:**
- Converted to `"https://moodle.example.com"`
- Info log message about protocol addition

**Test Type:** Unit Test

---

#### Test 3.1.4: Mixed case protocol handling
**Input:** `"HTTPS://moodle.example.com"`

**Expected Result:** Valid, normalized to lowercase

**Test Type:** Unit Test

---

#### Test 3.1.5: HTTP in URL path (not protocol)
**Input:** `"https://moodle.com/http/path"`

**Expected Result:** Valid (only protocol checked)

**Test Type:** Unit Test

---

### 3.2 URL Format Tests

#### Test 3.2.1: URL with subdomain
**Input:** `"https://moodle.sub.example.com"`

**Expected Result:** Valid

**Test Type:** Unit Test

---

#### Test 3.2.2: URL with port number
**Input:** `"https://moodle.example.com:8443"`

**Expected Result:** Valid

**Test Type:** Unit Test

---

#### Test 3.2.3: URL with path
**Input:** `"https://example.com/moodle"`

**Expected Result:** Valid

**Test Type:** Unit Test

---

#### Test 3.2.4: URL with query parameters
**Input:** `"https://moodle.com?param=value"`

**Expected Result:** Valid

**Test Type:** Unit Test

---

#### Test 3.2.5: Localhost URL
**Input:** `"https://localhost:8080"`

**Expected Result:** Valid

**Test Type:** Unit Test

---

#### Test 3.2.6: IP address URL
**Input:** `"https://192.168.1.100"`

**Expected Result:** Valid

**Test Type:** Unit Test

---

## 4. Data Extraction Tests

### 4.1 User Extraction

#### Test 4.1.1: Extract all users successfully
**Mock Setup:**
- API returns list of 100 users

**Expected Result:**
- Function returns 100
- Users pushed to XCom with key 'users'
- Log message with count

**Test Type:** Unit Test with Mocking

---

#### Test 4.1.2: Extract users with empty result
**Mock Setup:**
- API returns empty list

**Expected Result:**
- Function returns 0
- Empty list pushed to XCom

**Test Type:** Unit Test with Mocking

---

#### Test 4.1.3: Extract users with API error
**Mock Setup:**
- API raises exception

**Expected Result:**
- Exception propagated
- Error logged

**Test Type:** Unit Test with Mocking

---

### 4.2 Course Extraction

#### Test 4.2.1: Extract all courses successfully
**Mock Setup:**
- API returns list of 50 courses

**Expected Result:**
- Function returns 50
- Courses pushed to XCom
- Log message with count

**Test Type:** Unit Test with Mocking

---

#### Test 4.2.2: Extract courses from multiple categories
**Mock Setup:**
- API returns courses from different categories

**Expected Result:**
- All courses included regardless of category

**Test Type:** Unit Test with Mocking

---

### 4.3 Role Extraction

#### Test 4.3.1: Extract all roles
**Mock Setup:**
- API returns standard Moodle roles

**Expected Result:**
- All roles extracted
- Includes student, teacher, manager, etc.

**Test Type:** Unit Test with Mocking

---

### 4.4 Enrolment Extraction

#### Test 4.4.1: Extract enrolments for all courses
**Mock Setup:**
- 3 courses available
- Each course has enrolled users

**Expected Result:**
- Each enrolment includes course_id
- All enrolments aggregated

**Test Type:** Unit Test with Mocking

---

#### Test 4.4.2: Handle course with no enrolments
**Mock Setup:**
- Course returns empty user list

**Expected Result:**
- No error raised
- Empty list for that course

**Test Type:** Unit Test with Mocking

---

#### Test 4.4.3: Handle API error for specific course
**Mock Setup:**
- One course API call fails

**Expected Result:**
- Error logged for that course
- Continues with other courses

**Test Type:** Unit Test with Mocking

---

### 4.5 Grade Extraction

#### Test 4.5.1: Extract grade items for course
**Expected Result:**
- Grade items include course_id
- All grade items retrieved

**Test Type:** Unit Test with Mocking

---

#### Test 4.5.2: Extract grades for course
**Expected Result:**
- Grades include course_id
- All grades retrieved

**Test Type:** Unit Test with Mocking

---

### 4.6 Completion Extraction

#### Test 4.6.1: Extract completions for enrolments
**Mock Setup:**
- Enrolments available from previous task

**Expected Result:**
- Completion data includes course_id and userid
- API called for each enrolment

**Test Type:** Unit Test with Mocking

---

#### Test 4.6.2: Handle completion API failure gracefully
**Mock Setup:**
- Some completion calls fail

**Expected Result:**
- Warning logged
- Continues with other completions

**Test Type:** Unit Test with Mocking

---

## 5. Data Loading Tests

### 5.1 Raw Data Loading

#### Test 5.1.1: Load user data to moodle_raw
**Input:**
- Entity: 'users'
- Data: List of user dictionaries

**Expected Result:**
- Records inserted into moodle_raw table
- Instance field set correctly
- Hash computed for each record
- Timestamp recorded

**Test Type:** Integration Test (Database)

---

#### Test 5.1.2: Load with duplicate detection
**Input:**
- Same data loaded twice

**Expected Result:**
- ON CONFLICT DO NOTHING triggered
- No duplicate records created

**Test Type:** Integration Test (Database)

---

#### Test 5.1.3: Load empty dataset
**Input:**
- Empty list

**Expected Result:**
- Warning logged
- No database errors
- Function returns 0

**Test Type:** Unit Test

---

#### Test 5.1.4: Load with schema validation failure
**Input:**
- Data missing required fields

**Expected Result:**
- Validation warning logged
- Record still loaded (validation is warning, not error)

**Test Type:** Unit Test

---

### 5.2 Bulk Insert Operations

#### Test 5.2.1: Bulk insert multiple records
**Input:**
- 1000 records

**Expected Result:**
- All records inserted efficiently
- Single transaction
- Commit successful

**Test Type:** Integration Test (Database)

---

#### Test 5.2.2: Handle database connection failure
**Mock Setup:**
- Database connection fails

**Expected Result:**
- Exception raised
- Rollback attempted
- Connection closed

**Test Type:** Unit Test with Mocking

---

#### Test 5.2.3: Handle insert failure with rollback
**Mock Setup:**
- INSERT fails midway

**Expected Result:**
- Transaction rolled back
- No partial data committed
- Exception raised

**Test Type:** Unit Test with Mocking

---

## 6. Data Transformation Tests

### 6.1 User Transformation

#### Test 6.1.1: Transform users to staging table
**Input:**
- Raw user data in moodle_raw

**Expected Result:**
- Data normalized in moodle_stg.users
- JSON fields extracted to columns
- Data types correct

**Test Type:** Integration Test (Database)

---

#### Test 6.1.2: Handle null values in user data
**Input:**
- User records with optional null fields

**Expected Result:**
- Null values handled gracefully
- Record still transformed

**Test Type:** Integration Test (Database)

---

### 6.2 Course Transformation

#### Test 6.2.1: Transform courses to staging
**Expected Result:**
- Course data normalized
- Category information preserved
- Dates converted correctly

**Test Type:** Integration Test (Database)

---

### 6.3 Enrolment Transformation

#### Test 6.3.1: Transform enrolments to staging
**Expected Result:**
- User-course relationships established
- Role information included
- Timestamps preserved

**Test Type:** Integration Test (Database)

---

### 6.4 Grade Transformation

#### Test 6.4.1: Transform grades to staging
**Expected Result:**
- Numeric grades extracted correctly
- Grade items linked properly
- Null grades handled

**Test Type:** Integration Test (Database)

---

## 7. DAG Workflow Tests

### 7.1 Task Dependencies

#### Test 7.1.1: Verify schema creation runs first
**Expected Result:**
- create_raw_schema task has no upstream dependencies
- All extract tasks depend on schema creation

**Test Type:** DAG Structure Test

---

#### Test 7.1.2: Verify extract-load dependencies
**Expected Result:**
- Each load task depends on its corresponding extract task
- Load tasks can run in parallel

**Test Type:** DAG Structure Test

---

#### Test 7.1.3: Verify transform dependencies
**Expected Result:**
- Transform tasks depend on all necessary load tasks
- Transform tasks run sequentially

**Test Type:** DAG Structure Test

---

#### Test 7.1.4: Verify mart aggregation dependencies
**Expected Result:**
- Mart task depends on all transform tasks
- Mart runs after all transforms complete

**Test Type:** DAG Structure Test

---

### 7.2 DAG Scheduling

#### Test 7.2.1: Verify DAG schedule
**Expected Result:**
- Schedule interval: '0 2 * * *' (2 AM daily)
- Catchup disabled

**Test Type:** DAG Configuration Test

---

#### Test 7.2.2: Verify DAG timeout settings
**Expected Result:**
- Retry settings configured
- Retry delay: 5 minutes
- Max retries: 2

**Test Type:** DAG Configuration Test

---

### 7.3 XCom Communication

#### Test 7.3.1: Data passed via XCom
**Expected Result:**
- Extract tasks push data with correct keys
- Load tasks pull data with matching keys

**Test Type:** Integration Test

---

## 8. Error Handling Tests

### 8.1 Network Errors

#### Test 8.1.1: Handle connection timeout
**Mock Setup:**
- API call times out

**Expected Result:**
- Timeout exception raised
- Error logged with details
- Task marked as failed

**Test Type:** Unit Test with Mocking

---

#### Test 8.1.2: Handle connection refused
**Mock Setup:**
- Connection refused

**Expected Result:**
- Connection error raised
- Error logged
- Task fails

**Test Type:** Unit Test with Mocking

---

#### Test 8.1.3: Handle DNS resolution failure
**Mock Setup:**
- DNS lookup fails

**Expected Result:**
- DNS error raised
- Error logged

**Test Type:** Unit Test with Mocking

---

### 8.2 API Errors

#### Test 8.2.1: Handle invalid token
**Mock Setup:**
- API returns authentication error

**Expected Result:**
- Exception raised with clear message
- Error logged

**Test Type:** Unit Test with Mocking

---

#### Test 8.2.2: Handle insufficient permissions
**Mock Setup:**
- API returns permission denied

**Expected Result:**
- Exception raised
- Error logged with permission details

**Test Type:** Unit Test with Mocking

---

#### Test 8.2.3: Handle malformed API response
**Mock Setup:**
- API returns invalid JSON

**Expected Result:**
- JSON decode error handled
- Error logged

**Test Type:** Unit Test with Mocking

---

### 8.3 Database Errors

#### Test 8.3.1: Handle database connection failure
**Expected Result:**
- Connection error raised
- Error logged
- Transaction rolled back

**Test Type:** Integration Test

---

#### Test 8.3.2: Handle table not exists error
**Expected Result:**
- Clear error message
- Suggests running schema creation

**Test Type:** Integration Test

---

#### Test 8.3.3: Handle constraint violation
**Expected Result:**
- Constraint error raised
- Error logged with details

**Test Type:** Integration Test

---

### 8.4 Data Validation Errors

#### Test 8.4.1: Missing required field in schema validation
**Input:**
- User data without 'id' field

**Expected Result:**
- ValueError raised
- Error message specifies missing field

**Test Type:** Unit Test

---

#### Test 8.4.2: Invalid data type in schema validation
**Input:**
- Course data with string instead of int for id

**Expected Result:**
- Validation may log warning
- Flexible validation doesn't block

**Test Type:** Unit Test

---

## 9. Integration Tests

### 9.1 End-to-End Workflow

#### Test 9.1.1: Complete ELT pipeline for one instance
**Steps:**
1. Create schemas
2. Extract all entities
3. Load to raw tables
4. Transform to staging
5. Aggregate to mart

**Expected Result:**
- All steps complete successfully
- Data flows through all layers
- Final mart table populated

**Test Type:** End-to-End Integration Test

---

#### Test 9.1.2: Parallel execution of multiple instance DAGs
**Steps:**
- Trigger all 4 DAGs simultaneously

**Expected Result:**
- All DAGs execute without conflicts
- Each instance data isolated correctly
- No race conditions

**Test Type:** Integration Test

---

### 9.2 Configuration Integration

#### Test 9.2.1: Switch from individual to comma-separated config
**Steps:**
1. Configure with individual variables
2. Run DAG successfully
3. Switch to comma-separated config
4. Run DAG again

**Expected Result:**
- Both configurations work
- No data corruption
- Smooth transition

**Test Type:** Integration Test

---

## 10. Security Tests

### 10.1 HTTPS Enforcement

#### Test 10.1.1: Prevent HTTP connections
**Expected Result:**
- HTTP URLs rejected at initialization
- No actual HTTP connections attempted

**Test Type:** Security Test

---

#### Test 10.1.2: Token not exposed in logs
**Expected Result:**
- Token not present in log files
- Token not in error messages

**Test Type:** Security Test

---

### 10.2 SQL Injection Prevention

#### Test 10.2.1: Parameterized queries used
**Expected Result:**
- All database operations use parameterized queries
- No string concatenation for SQL

**Test Type:** Code Review / Security Test

---

### 10.3 Data Validation

#### Test 10.3.1: Hash computation for data integrity
**Input:**
- Same data computed twice

**Expected Result:**
- Same hash produced
- Hash consistent across runs

**Test Type:** Unit Test

---

#### Test 10.3.2: Prevent duplicate data insertion
**Expected Result:**
- Duplicate detection via hash
- ON CONFLICT clause prevents duplicates

**Test Type:** Integration Test

---

## 11. Performance Tests

### 11.1 Rate Limiting

#### Test 11.1.1: Rate limit enforced between calls
**Test:**
- Make 10 consecutive API calls
- Measure total time

**Expected Result:**
- Total time ≥ 9 seconds (9 delays × 1 second)
- Rate limit respected

**Test Type:** Performance Test

---

#### Test 11.1.2: Custom rate limit delay
**Input:**
- `rate_limit_delay`: `0.5`

**Expected Result:**
- Faster calls with shorter delay
- Delay still enforced

**Test Type:** Performance Test

---

### 11.2 Bulk Operations

#### Test 11.2.1: Bulk insert performance
**Input:**
- 10,000 records

**Expected Result:**
- All records inserted efficiently
- Time < threshold (e.g., 60 seconds)

**Test Type:** Performance Test

---

#### Test 11.2.2: Large dataset extraction
**Mock Setup:**
- API returns 1,000 courses

**Expected Result:**
- All courses extracted
- Reasonable time taken
- No memory issues

**Test Type:** Performance Test

---

### 11.3 Memory Management

#### Test 11.3.1: Large XCom data transfer
**Input:**
- Very large dataset pushed to XCom

**Expected Result:**
- No memory overflow
- Data transferred successfully

**Test Type:** Performance Test

---

## 12. Utility Function Tests

### 12.1 Hash Computation

#### Test 12.1.1: Compute hash for dictionary
**Input:**
- `{"id": 1, "name": "test"}`

**Expected Result:**
- Returns consistent MD5 hash
- Same input produces same hash

**Test Type:** Unit Test

---

#### Test 12.1.2: Hash order independence
**Input:**
- Two dicts with same data, different key order

**Expected Result:**
- Same hash produced (JSON sorted keys)

**Test Type:** Unit Test

---

#### Test 12.1.3: Hash for complex nested structure
**Input:**
- Nested dictionary with lists

**Expected Result:**
- Hash computed successfully
- Consistent result

**Test Type:** Unit Test

---

### 12.2 Record Preparation

#### Test 12.2.1: Prepare raw record
**Input:**
- Instance: 'moodle1'
- Entity: 'user'
- Moodle ID: 42
- Data: user dictionary

**Expected Result:**
- Record contains all required fields
- Timestamp is ISO format
- Hash computed

**Test Type:** Unit Test

---

#### Test 12.2.2: Prepare record with null moodle_id
**Input:**
- `moodle_id`: `None`

**Expected Result:**
- Record prepared successfully
- None stored in moodle_id field

**Test Type:** Unit Test

---

### 12.3 Schema Validation

#### Test 12.3.1: Validate user schema
**Input:**
- Valid user: `{"id": 1, "username": "test"}`

**Expected Result:**
- Returns True
- No exception raised

**Test Type:** Unit Test

---

#### Test 12.3.2: Validate course schema
**Input:**
- Valid course: `{"id": 1, "fullname": "Test Course"}`

**Expected Result:**
- Returns True

**Test Type:** Unit Test

---

#### Test 12.3.3: Validate with missing field
**Input:**
- User without username: `{"id": 1}`

**Expected Result:**
- ValueError raised
- Clear error message

**Test Type:** Unit Test

---

#### Test 12.3.4: Validate unknown entity
**Input:**
- Entity: 'unknown_entity'

**Expected Result:**
- No validation performed (no required fields defined)
- Returns True

**Test Type:** Unit Test

---

## Test Implementation Guidelines

### Test Organization

```
tests/
├── unit/
│   ├── test_moodle_api_client.py
│   ├── test_configuration.py
│   ├── test_url_validation.py
│   ├── test_utility_functions.py
│   └── test_dag_structure.py
├── integration/
│   ├── test_database_operations.py
│   ├── test_extraction_workflow.py
│   ├── test_transformation_workflow.py
│   └── test_end_to_end.py
├── performance/
│   ├── test_rate_limiting.py
│   └── test_bulk_operations.py
└── security/
    ├── test_https_enforcement.py
    └── test_data_validation.py
```

### Test Fixtures

Create reusable fixtures for:
- Mock Moodle API responses
- Sample user/course/grade data
- Database connections
- Airflow context objects

### Mocking Strategy

- Use `unittest.mock` for API calls
- Use `pytest-mock` for Airflow components
- Mock database connections for unit tests
- Use test database for integration tests

### Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: All critical paths
- **End-to-End Tests**: At least 1 complete workflow per DAG

### Continuous Integration

All tests should:
- Run automatically on PR
- Complete within 10 minutes
- Be independent (no order dependencies)
- Clean up after themselves

---

## Test Data Examples

### Sample User Data
```json
{
  "id": 123,
  "username": "testuser",
  "firstname": "Test",
  "lastname": "User",
  "email": "test@example.com",
  "auth": "manual"
}
```

### Sample Course Data
```json
{
  "id": 42,
  "fullname": "Introduction to Testing",
  "shortname": "TEST101",
  "categoryid": 1,
  "visible": 1,
  "startdate": 1640995200,
  "enddate": 1672531200
}
```

### Sample Enrolment Data
```json
{
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
```

### Sample Grade Data
```json
{
  "userid": 123,
  "itemid": 456,
  "itemname": "Final Exam",
  "grade": 85.5,
  "grademax": 100,
  "feedback": "Well done!",
  "course_id": 42
}
```

---

## Appendix A: Test Priorities

### Priority 1 (Critical - Must Have)
- URL validation and HTTPS enforcement
- Configuration parsing (comma-separated and individual)
- MoodleAPIClient initialization
- Basic API operations
- Data extraction workflows
- Error handling for network and API errors

### Priority 2 (Important - Should Have)
- Database operations (insert, transform)
- DAG workflow and dependencies
- Schema validation
- Integration tests for complete workflows
- Rate limiting

### Priority 3 (Nice to Have)
- Performance tests
- Security tests
- Edge cases and corner cases
- Load testing with large datasets

---

## Appendix B: Test Environment Setup

### Required Dependencies
```
pytest>=7.0.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
responses>=0.22.0
freezegun>=1.2.0
```

### Mock Moodle API Setup
Create a mock server that simulates Moodle API responses for testing without actual Moodle instance.

### Test Database Setup
Use PostgreSQL test database with:
- Same schema as production
- Isolated from production data
- Automatic cleanup after tests

---

## Document History

| Version | Date       | Changes                          | Author          |
|---------|------------|----------------------------------|-----------------|
| 1.0     | 2026-02-19 | Initial comprehensive test plan  | GitHub Copilot  |

---

**End of Test Scenarios Document**
