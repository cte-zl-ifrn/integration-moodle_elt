-- =====================================================
-- STAGING: ROLES Table
-- =====================================================
CREATE TABLE IF NOT EXISTS moodle_stg.roles (
    instance VARCHAR(50) NOT NULL,
    moodle_role_id INT NOT NULL,
    shortname VARCHAR(50),
    name VARCHAR(255),
    archetype VARCHAR(30),
    sortorder INT,
    ts_extract TIMESTAMPTZ,
    PRIMARY KEY (instance, moodle_role_id)
);

-- Transform from RAW to STAGING
INSERT INTO moodle_stg.roles (
    instance,
    moodle_role_id,
    shortname,
    name,
    archetype,
    sortorder,
    ts_extract
)
SELECT DISTINCT ON (instance, moodle_id)
    instance,
    moodle_id,
    data_json->>'shortname',
    data_json->>'name',
    data_json->>'archetype',
    (data_json->>'sortorder')::INT,
    ts_extract
FROM moodle_raw
WHERE entity = 'role'
    AND moodle_id IS NOT NULL
ORDER BY instance, moodle_id, ts_extract DESC
ON CONFLICT (instance, moodle_role_id) 
DO UPDATE SET
    shortname = EXCLUDED.shortname,
    name = EXCLUDED.name,
    archetype = EXCLUDED.archetype,
    sortorder = EXCLUDED.sortorder,
    ts_extract = EXCLUDED.ts_extract;
