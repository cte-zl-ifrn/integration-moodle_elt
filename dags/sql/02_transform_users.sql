-- =====================================================
-- STAGING: USERS Table
-- =====================================================
CREATE SCHEMA IF NOT EXISTS moodle_stg;

CREATE TABLE IF NOT EXISTS moodle_stg.users (
    instance VARCHAR(50) NOT NULL,
    moodle_user_id BIGINT NOT NULL,
    username VARCHAR(100),
    email VARCHAR(100),
    firstname VARCHAR(100),
    lastname VARCHAR(100),
    auth VARCHAR(50),
    confirmed SMALLINT,
    suspended SMALLINT,
    deleted SMALLINT,
    ts_extract TIMESTAMPTZ,
    PRIMARY KEY (instance, moodle_user_id)
);

-- Transform from RAW to STAGING
INSERT INTO moodle_stg.users (
    instance,
    moodle_user_id,
    username,
    email,
    firstname,
    lastname,
    auth,
    confirmed,
    suspended,
    deleted,
    ts_extract
)
SELECT DISTINCT ON (instance, moodle_id)
    instance,
    moodle_id,
    data_json->>'username',
    data_json->>'email',
    data_json->>'firstname',
    data_json->>'lastname',
    data_json->>'auth',
    (data_json->>'confirmed')::SMALLINT,
    (data_json->>'suspended')::SMALLINT,
    (data_json->>'deleted')::SMALLINT,
    ts_extract
FROM moodle_raw
WHERE entity = 'user'
    AND moodle_id IS NOT NULL
ORDER BY instance, moodle_id, ts_extract DESC
ON CONFLICT (instance, moodle_user_id) 
DO UPDATE SET
    username = EXCLUDED.username,
    email = EXCLUDED.email,
    firstname = EXCLUDED.firstname,
    lastname = EXCLUDED.lastname,
    auth = EXCLUDED.auth,
    confirmed = EXCLUDED.confirmed,
    suspended = EXCLUDED.suspended,
    deleted = EXCLUDED.deleted,
    ts_extract = EXCLUDED.ts_extract;
