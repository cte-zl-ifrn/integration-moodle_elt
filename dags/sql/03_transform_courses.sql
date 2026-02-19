-- =====================================================
-- STAGING: COURSES Table
-- =====================================================
CREATE TABLE IF NOT EXISTS moodle_stg.courses (
    instance VARCHAR(50) NOT NULL,
    moodle_course_id BIGINT NOT NULL,
    shortname VARCHAR(255),
    fullname TEXT,
    categoryid BIGINT,
    format VARCHAR(21) DEFAULT 'topics',
    visible SMALLINT,
    startdate BIGINT,
    enddate BIGINT,
    ts_extract TIMESTAMPTZ,
    PRIMARY KEY (instance, moodle_course_id)
);

-- Transform from RAW to STAGING
INSERT INTO moodle_stg.courses (
    instance,
    moodle_course_id,
    shortname,
    fullname,
    categoryid,
    format,
    visible,
    startdate,
    enddate,
    ts_extract
)
SELECT DISTINCT ON (instance, moodle_id)
    instance,
    moodle_id,
    data_json->>'shortname',
    data_json->>'fullname',
    (data_json->>'categoryid')::BIGINT,
    COALESCE(data_json->>'format', 'topics'),
    (data_json->>'visible')::SMALLINT,
    (data_json->>'startdate')::BIGINT,
    (data_json->>'enddate')::BIGINT,
    ts_extract
FROM moodle_raw
WHERE entity = 'course'
    AND moodle_id IS NOT NULL
ORDER BY instance, moodle_id, ts_extract DESC
ON CONFLICT (instance, moodle_course_id) 
DO UPDATE SET
    shortname = EXCLUDED.shortname,
    fullname = EXCLUDED.fullname,
    categoryid = EXCLUDED.categoryid,
    format = EXCLUDED.format,
    visible = EXCLUDED.visible,
    startdate = EXCLUDED.startdate,
    enddate = EXCLUDED.enddate,
    ts_extract = EXCLUDED.ts_extract;
