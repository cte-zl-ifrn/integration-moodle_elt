# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Initial release of Moodle ELT Integration
- 4 parallel Airflow DAGs (moodle1-4) for data extraction
- Complete PostgreSQL schema (raw, staging, mart layers)
- Moodle API client with rate limiting and retry logic
- Docker Compose setup for Airflow + PostgreSQL + Superset
- Comprehensive documentation and setup scripts
- Support for 8 Moodle entities:
  - Users
  - Courses
  - Roles
  - Enrolments
  - Enrolment Methods
  - Grade Items
  - Grades
  - Course Completions
- JSON schema validation
- UPSERT operations for deduplication
- CKAN metadata integration (placeholder)
- Mart table for course performance analytics

### Features
- Daily scheduled extraction (configurable)
- Parallel task execution
- Error handling with retries
- Connection pooling
- Rate limiting (1s between API calls)
- Hash-based deduplication
- Superset-ready analytics tables

[1.0.0]: https://github.com/cte-zl-ifrn/integration-moodle_elt/releases/tag/v1.0.0
