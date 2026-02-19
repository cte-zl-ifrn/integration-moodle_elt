-- =====================================================
-- RAW JSON Landing Zone
-- =====================================================
CREATE SCHEMA IF NOT EXISTS moodle_raw_schema;

CREATE TABLE IF NOT EXISTS moodle_raw (
    id BIGSERIAL PRIMARY KEY,
    instance VARCHAR(50) NOT NULL,     -- 'moodle1', 'moodle2', etc.
    entity VARCHAR(50) NOT NULL,       -- 'user', 'course', 'grade', etc.
    moodle_id BIGINT,                  -- ID original do Moodle
    data_json JSONB NOT NULL,
    ts_extract TIMESTAMPTZ DEFAULT NOW(),
    ts_load TIMESTAMPTZ,
    hash_content BYTEA,                -- MD5 do JSON para dedup
    UNIQUE(instance, entity, moodle_id, ts_extract)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_moodle_raw_instance ON moodle_raw(instance);
CREATE INDEX IF NOT EXISTS idx_moodle_raw_entity ON moodle_raw(entity);
CREATE INDEX IF NOT EXISTS idx_moodle_raw_ts_extract ON moodle_raw(ts_extract);
CREATE INDEX IF NOT EXISTS idx_moodle_raw_hash ON moodle_raw(hash_content);
CREATE INDEX IF NOT EXISTS idx_moodle_raw_data_json ON moodle_raw USING gin(data_json);
