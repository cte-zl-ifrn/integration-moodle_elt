-- =====================================================
-- STAGING: COMPLETIONS Table
-- =====================================================
CREATE TABLE IF NOT EXISTS moodle_stg.completions (
    instance VARCHAR(50) NOT NULL,
    moodle_user_id BIGINT NOT NULL,
    moodle_course_id BIGINT NOT NULL,
    completionstate INT,  -- 0=not, 1=complete, etc.
    viewed SMALLINT,
    timemodified BIGINT,
    ts_extract TIMESTAMPTZ,
    PRIMARY KEY (instance, moodle_user_id, moodle_course_id)
);

-- Transform from RAW to STAGING
INSERT INTO moodle_stg.completions (
    instance,
    moodle_user_id,
    moodle_course_id,
    completionstate,
    viewed,
    timemodified,
    ts_extract
)
SELECT DISTINCT ON (instance, user_id, course_id)
    instance,
    (data_json->>'userid')::BIGINT as user_id,
    moodle_id as course_id,
    (data_json->>'completionstate')::INT,
    (data_json->>'viewed')::SMALLINT,
    (data_json->>'timemodified')::BIGINT,
    ts_extract
FROM moodle_raw
WHERE entity = 'completion'
    AND moodle_id IS NOT NULL
    AND data_json->>'userid' IS NOT NULL
ORDER BY instance, user_id, course_id, ts_extract DESC
ON CONFLICT (instance, moodle_user_id, moodle_course_id) 
DO UPDATE SET
    completionstate = EXCLUDED.completionstate,
    viewed = EXCLUDED.viewed,
    timemodified = EXCLUDED.timemodified,
    ts_extract = EXCLUDED.ts_extract;
