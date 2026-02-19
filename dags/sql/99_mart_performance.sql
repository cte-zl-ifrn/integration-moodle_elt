-- =====================================================
-- MART: Course Performance Aggregated Table
-- =====================================================
CREATE SCHEMA IF NOT EXISTS moodle_mart;

-- Drop and recreate for full refresh
DROP TABLE IF EXISTS moodle_mart.course_performance;

CREATE TABLE moodle_mart.course_performance AS
SELECT 
    c.instance,
    c.moodle_course_id,
    c.fullname as course_name,
    c.shortname as course_shortname,
    u.moodle_user_id,
    u.username,
    u.firstname,
    u.lastname,
    u.email,
    r.moodle_role_id,
    r.shortname as role_name,
    r.name as role_fullname,
    COUNT(DISTINCT gi.moodle_item_id) as total_items,
    COUNT(g.moodle_item_id) as graded_items,
    AVG(CASE 
        WHEN gi.grademax > 0 THEN (g.finalgrade / gi.grademax * 100)
        ELSE NULL 
    END) as avg_performance_pct,
    MAX(CASE WHEN comp.completionstate = 1 THEN 1 ELSE 0 END) as completed_course,
    MAX(c.startdate) as course_startdate,
    MAX(c.enddate) as course_enddate,
    MAX(e.timecreated) as enrolment_timecreated,
    CURRENT_TIMESTAMP as ts_generated
FROM moodle_stg.courses c
JOIN moodle_stg.enrolments e 
    ON c.instance = e.instance 
    AND c.moodle_course_id = e.moodle_course_id
JOIN moodle_stg.users u 
    ON e.instance = u.instance 
    AND e.moodle_user_id = u.moodle_user_id 
JOIN moodle_stg.roles r 
    ON e.instance = r.instance 
    AND e.roleid_moodle = r.moodle_role_id
LEFT JOIN moodle_stg.grade_items gi 
    ON c.instance = gi.instance 
    AND c.moodle_course_id = gi.moodle_course_id
LEFT JOIN moodle_stg.grades g 
    ON gi.instance = g.instance
    AND gi.moodle_course_id = g.moodle_course_id 
    AND gi.moodle_item_id = g.moodle_item_id 
    AND u.moodle_user_id = g.moodle_user_id
LEFT JOIN moodle_stg.completions comp 
    ON c.instance = comp.instance
    AND c.moodle_course_id = comp.moodle_course_id
    AND u.moodle_user_id = comp.moodle_user_id
GROUP BY 
    c.instance,
    c.moodle_course_id,
    c.fullname,
    c.shortname,
    u.moodle_user_id,
    u.username,
    u.firstname,
    u.lastname,
    u.email,
    r.moodle_role_id,
    r.shortname,
    r.name;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_mart_performance_instance ON moodle_mart.course_performance(instance);
CREATE INDEX IF NOT EXISTS idx_mart_performance_course ON moodle_mart.course_performance(moodle_course_id);
CREATE INDEX IF NOT EXISTS idx_mart_performance_user ON moodle_mart.course_performance(moodle_user_id);
CREATE INDEX IF NOT EXISTS idx_mart_performance_role ON moodle_mart.course_performance(role_name);
