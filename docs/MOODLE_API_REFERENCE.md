# Moodle Web Services API Reference

This document provides a quick reference for the Moodle Web Services functions used in this integration.

## Core Functions Used

### User Management
- **core_user_get_users**: Get user information by criteria
- Returns: id, username, email, firstname, lastname, auth, confirmed, suspended, deleted

### Course Management  
- **core_course_get_courses**: Get all courses
- Returns: id, shortname, fullname, categoryid, format, visible, startdate, enddate

### Enrolment
- **core_enrol_get_enrolled_users**: Get enrolled users in a course with roles
- **core_enrol_get_course_enrolment_methods**: Get enrolment methods for a course

### Role Management
- **core_role_get_all_roles**: Get all system roles

### Grading
- **gradereport_user_get_grade_items**: Get grade items for a course
- **gradereport_user_get_grades_table**: Get grades table for a course

### Course Completion
- **core_completion_get_course_completion_status**: Get completion status

See full Moodle API documentation at https://docs.moodle.org/dev/Web_services
