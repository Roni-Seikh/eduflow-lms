-- ============================================================
-- Run this to confirm your schema is fully set up correctly
-- ============================================================

SELECT 'admin' AS table_name, COUNT(*) AS row_count FROM admin
UNION ALL
SELECT 'students', COUNT(*) FROM students
UNION ALL
SELECT 'faculty', COUNT(*) FROM faculty
UNION ALL
SELECT 'courses', COUNT(*) FROM courses
UNION ALL
SELECT 'enrollments', COUNT(*) FROM enrollments
UNION ALL
SELECT 'live_classes', COUNT(*) FROM live_classes
UNION ALL
SELECT 'recorded_lectures', COUNT(*) FROM recorded_lectures
UNION ALL
SELECT 'lecture_completions', COUNT(*) FROM lecture_completions
UNION ALL
SELECT 'attendance', COUNT(*) FROM attendance
UNION ALL
SELECT 'exams', COUNT(*) FROM exams
UNION ALL
SELECT 'exam_questions', COUNT(*) FROM exam_questions
UNION ALL
SELECT 'exam_results', COUNT(*) FROM exam_results
UNION ALL
SELECT 'cheating_logs', COUNT(*) FROM cheating_logs
UNION ALL
SELECT 'certificates', COUNT(*) FROM certificates
UNION ALL
SELECT 'notifications', COUNT(*) FROM notifications
UNION ALL
SELECT 'password_requests', COUNT(*) FROM password_requests
UNION ALL
SELECT 'activity_logs', COUNT(*) FROM activity_logs;

-- Should show admin = 1 row, everything else = 0 rows (fresh install)

-- Also confirm the admin login will work:
SELECT id, name, email, is_active FROM admin WHERE email = 'admin@lms.com';
