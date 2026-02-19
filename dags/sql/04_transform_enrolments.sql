-- =====================================================
-- STAGING: ENROLMENTS Table
-- =====================================================
CREATE TABLE IF NOT EXISTS moodle_stg.enrolments (
    instance VARCHAR(50) NOT NULL,
    moodle_user_id BIGINT NOT NULL,
    moodle_course_id BIGINT NOT NULL,
    roleid_moodle INT,
    timecreated BIGINT,
    timemodified BIGINT,
    status INT,
    ts_extract TIMESTAMPTZ,
    PRIMARY KEY (instance, moodle_user_id, moodle_course_id)
);

-- Transform from RAW to STAGING
-- Note: enrol data comes from core_enrol_get_enrolled_users which returns users with their roles per course
INSERT INTO moodle_stg.enrolments (
    instance,
    moodle_user_id,
    moodle_course_id,
    roleid_moodle,
    timecreated,
    timemodified,
    status,
    ts_extract
)
SELECT DISTINCT ON (instance, user_id, course_id)
    instance,
    (data_json->>'id')::BIGINT as user_id,
    moodle_id as course_id,
    (data_json->'roles'->0->>'roleid')::INT as roleid,
    (data_json->>'firstaccess')::BIGINT as timecreated,
    (data_json->>'lastaccess')::BIGINT as timemodified,
    0 as status,  -- Default active status
    ts_extract
FROM moodle_raw
WHERE entity = 'enrol'
    AND moodle_id IS NOT NULL
    AND data_json->>'id' IS NOT NULL
ORDER BY instance, user_id, course_id, ts_extract DESC
ON CONFLICT (instance, moodle_user_id, moodle_course_id) 
DO UPDATE SET
    roleid_moodle = EXCLUDED.roleid_moodle,
    timecreated = EXCLUDED.timecreated,
    timemodified = EXCLUDED.timemodified,
    status = EXCLUDED.status,
    ts_extract = EXCLUDED.ts_extract;
