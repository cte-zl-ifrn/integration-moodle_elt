-- =====================================================
-- STAGING: GRADE ITEMS Table
-- =====================================================
CREATE TABLE IF NOT EXISTS moodle_stg.grade_items (
    instance VARCHAR(50) NOT NULL,
    moodle_course_id BIGINT NOT NULL,
    moodle_item_id BIGINT NOT NULL,
    itemname TEXT,
    itemmodule VARCHAR(50),  -- 'assign', 'quiz', etc.
    iteminstance BIGINT,
    gradetype INT,
    grademax DECIMAL(10,5),
    grademin DECIMAL(10,5),
    ts_extract TIMESTAMPTZ,
    PRIMARY KEY (instance, moodle_course_id, moodle_item_id)
);

-- Transform from RAW to STAGING
INSERT INTO moodle_stg.grade_items (
    instance,
    moodle_course_id,
    moodle_item_id,
    itemname,
    itemmodule,
    iteminstance,
    gradetype,
    grademax,
    grademin,
    ts_extract
)
SELECT DISTINCT ON (instance, course_id, item_id)
    instance,
    moodle_id as course_id,
    (data_json->>'id')::BIGINT as item_id,
    data_json->>'itemname',
    data_json->>'itemmodule',
    (data_json->>'iteminstance')::BIGINT,
    (data_json->>'gradetype')::INT,
    (data_json->>'grademax')::DECIMAL(10,5),
    (data_json->>'grademin')::DECIMAL(10,5),
    ts_extract
FROM moodle_raw
WHERE entity = 'grade_item'
    AND moodle_id IS NOT NULL
    AND data_json->>'id' IS NOT NULL
ORDER BY instance, course_id, item_id, ts_extract DESC
ON CONFLICT (instance, moodle_course_id, moodle_item_id) 
DO UPDATE SET
    itemname = EXCLUDED.itemname,
    itemmodule = EXCLUDED.itemmodule,
    iteminstance = EXCLUDED.iteminstance,
    gradetype = EXCLUDED.gradetype,
    grademax = EXCLUDED.grademax,
    grademin = EXCLUDED.grademin,
    ts_extract = EXCLUDED.ts_extract;
