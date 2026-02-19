-- Initialize PostgreSQL databases and schemas for Moodle ELT

-- Create additional schemas for moodle data (airflow DB already exists)
CREATE SCHEMA IF NOT EXISTS moodle_raw_schema;
CREATE SCHEMA IF NOT EXISTS moodle_stg;
CREATE SCHEMA IF NOT EXISTS moodle_mart;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA moodle_raw_schema TO airflow;
GRANT ALL PRIVILEGES ON SCHEMA moodle_stg TO airflow;
GRANT ALL PRIVILEGES ON SCHEMA moodle_mart TO airflow;
