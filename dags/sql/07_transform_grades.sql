-- =====================================================
-- STAGING: GRADES Table
-- =====================================================
CREATE TABLE IF NOT EXISTS moodle_stg.grades (
    instance VARCHAR(50) NOT NULL,
    moodle_user_id BIGINT NOT NULL,
    moodle_course_id BIGINT NOT NULL,
    moodle_item_id BIGINT NOT NULL,
    rawgrade DECIMAL(10,5),
    finalgrade DECIMAL(10,5),
    rawgrademax DECIMAL(10,5),
    rawgrademin DECIMAL(10,5),
    timecreated BIGINT,
    timemodified BIGINT,
    ts_extract TIMESTAMPTZ,
    PRIMARY KEY (instance, moodle_user_id, moodle_course_id, moodle_item_id)
);

-- Transform from RAW to STAGING
INSERT INTO moodle_stg.grades (
    instance,
    moodle_user_id,
    moodle_course_id,
    moodle_item_id,
    rawgrade,
    finalgrade,
    rawgrademax,
    rawgrademin,
    timecreated,
    timemodified,
    ts_extract
)
SELECT DISTINCT ON (instance, user_id, course_id, item_id)
    instance,
    (data_json->>'userid')::BIGINT as user_id,
    moodle_id as course_id,
    (data_json->>'itemid')::BIGINT as item_id,
    (data_json->>'rawgrade')::DECIMAL(10,5),
    (data_json->>'finalgrade')::DECIMAL(10,5),
    (data_json->>'rawgrademax')::DECIMAL(10,5),
    (data_json->>'rawgrademin')::DECIMAL(10,5),
    (data_json->>'timecreated')::BIGINT,
    (data_json->>'timemodified')::BIGINT,
    ts_extract
FROM moodle_raw
WHERE entity = 'grade'
    AND moodle_id IS NOT NULL
    AND data_json->>'userid' IS NOT NULL
    AND data_json->>'itemid' IS NOT NULL
ORDER BY instance, user_id, course_id, item_id, ts_extract DESC
ON CONFLICT (instance, moodle_user_id, moodle_course_id, moodle_item_id) 
DO UPDATE SET
    rawgrade = EXCLUDED.rawgrade,
    finalgrade = EXCLUDED.finalgrade,
    rawgrademax = EXCLUDED.rawgrademax,
    rawgrademin = EXCLUDED.rawgrademin,
    timecreated = EXCLUDED.timecreated,
    timemodified = EXCLUDED.timemodified,
    ts_extract = EXCLUDED.ts_extract;
