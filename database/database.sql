-- ============================================================
-- LMS Database Schema
-- Created for Learning Management System
-- ============================================================

CREATE DATABASE IF NOT EXISTS lms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lms_db;

-- ============================================================
-- ADMIN TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255) DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    last_login DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- STUDENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g. LMS/S/26/01
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255) DEFAULT NULL,
    date_of_birth DATE DEFAULT NULL,
    gender ENUM('Male','Female','Other') DEFAULT NULL,
    address TEXT DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    last_login DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- FACULTY TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS faculty (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g. LMS/F/26/01
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20) DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255) DEFAULT NULL,
    department VARCHAR(100) DEFAULT NULL,
    qualification VARCHAR(150) DEFAULT NULL,
    specialization VARCHAR(150) DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    last_login DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- COURSES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT NULL,
    duration VARCHAR(50) DEFAULT NULL,
    thumbnail VARCHAR(255) DEFAULT NULL,
    category VARCHAR(100) DEFAULT NULL,
    level ENUM('Beginner','Intermediate','Advanced') DEFAULT 'Beginner',
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- ENROLLMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress INT DEFAULT 0,
    is_completed TINYINT(1) DEFAULT 0,
    completed_at DATETIME DEFAULT NULL,
    UNIQUE KEY unique_enrollment (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- LIVE CLASSES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS live_classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    faculty_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT NULL,
    meeting_link VARCHAR(500) DEFAULT NULL,
    scheduled_at DATETIME NOT NULL,
    duration_minutes INT DEFAULT 60,
    recording_url VARCHAR(500) DEFAULT NULL,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- RECORDED LECTURES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS recorded_lectures (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    faculty_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT NULL,
    video_url VARCHAR(500) DEFAULT NULL,
    video_file VARCHAR(255) DEFAULT NULL,
    pdf_file VARCHAR(255) DEFAULT NULL,
    duration VARCHAR(20) DEFAULT NULL,
    sort_order INT DEFAULT 0,
    is_active TINYINT(1) DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- ATTENDANCE TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    faculty_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present','Absent','Late') DEFAULT 'Absent',
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- EXAMS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS exams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    faculty_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT NULL,
    duration_minutes INT DEFAULT 60,
    total_questions INT DEFAULT 0,
    passing_score INT DEFAULT 60,
    randomize_questions TINYINT(1) DEFAULT 1,
    is_active TINYINT(1) DEFAULT 1,
    start_time DATETIME DEFAULT NULL,
    end_time DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (faculty_id) REFERENCES faculty(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- EXAM QUESTIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS exam_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    question TEXT NOT NULL,
    option_a VARCHAR(500) NOT NULL,
    option_b VARCHAR(500) NOT NULL,
    option_c VARCHAR(500) NOT NULL,
    option_d VARCHAR(500) NOT NULL,
    correct_answer ENUM('A','B','C','D') NOT NULL,
    marks INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- EXAM RESULTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS exam_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    score INT DEFAULT 0,
    total_marks INT DEFAULT 0,
    percentage DECIMAL(5,2) DEFAULT 0.00,
    passed TINYINT(1) DEFAULT 0,
    time_taken INT DEFAULT 0,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answers JSON DEFAULT NULL,
    UNIQUE KEY unique_result (exam_id, student_id),
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- CHEATING LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS cheating_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    exam_id INT NOT NULL,
    student_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- CERTIFICATES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS certificates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    certificate_id VARCHAR(50) UNIQUE NOT NULL,
    student_id INT NOT NULL,
    course_id INT DEFAULT NULL,
    exam_id INT DEFAULT NULL,
    type ENUM('Course','Exam') DEFAULT 'Course',
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
    FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ============================================================
-- NOTIFICATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT DEFAULT NULL,
    sender_role ENUM('admin','faculty') DEFAULT 'admin',
    recipient_type ENUM('all','students','faculty','individual') DEFAULT 'all',
    recipient_id INT DEFAULT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- PASSWORD REQUESTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS password_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_role ENUM('student','faculty') NOT NULL,
    email VARCHAR(150) NOT NULL,
    status ENUM('pending','resolved','rejected') DEFAULT 'pending',
    message TEXT DEFAULT NULL,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME DEFAULT NULL
) ENGINE=InnoDB;

-- ============================================================
-- ACTIVITY LOGS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_role ENUM('admin','faculty','student') NOT NULL,
    action VARCHAR(200) NOT NULL,
    details TEXT DEFAULT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- DEFAULT ADMIN SEED
-- password: Admin@123 (bcrypt hashed)
-- ============================================================
INSERT INTO admin (name, email, password_hash) VALUES
('Super Admin', 'admin@lms.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW');

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_student_id ON students(student_id);
CREATE INDEX idx_faculty_email ON faculty(email);
CREATE INDEX idx_faculty_faculty_id ON faculty(faculty_id);
CREATE INDEX idx_enrollments_student ON enrollments(student_id);
CREATE INDEX idx_enrollments_course ON enrollments(course_id);
CREATE INDEX idx_attendance_student ON attendance(student_id);
CREATE INDEX idx_exam_results_student ON exam_results(student_id);
CREATE INDEX idx_notifications_recipient ON notifications(recipient_type, recipient_id);

-- ============================================================
-- MIGRATION: Add recipient_role column to notifications table
-- Run this ONCE in phpMyAdmin → lms_db → SQL tab
-- ============================================================

ALTER TABLE notifications
  ADD COLUMN recipient_role ENUM('student', 'faculty') DEFAULT NULL
  AFTER recipient_id;

-- Update existing individual notifications to set recipient_role
-- based on the password_requests table (best-effort backfill)
UPDATE notifications n
INNER JOIN password_requests pr
  ON pr.user_id = n.recipient_id
  AND n.recipient_type = 'individual'
SET n.recipient_role = pr.user_role
WHERE n.recipient_role IS NULL;

SELECT 'Migration complete. recipient_role column added.' AS status;

-- ============================================================
-- MIGRATION v2 — Run in phpMyAdmin → lms_db → SQL tab
-- ============================================================

-- 1. Add recipient_role to notifications (if not already added)
ALTER TABLE notifications
  ADD COLUMN IF NOT EXISTS recipient_role ENUM('student','faculty') DEFAULT NULL
  AFTER recipient_id;

-- 2. Add is_closed to courses (faculty can close a course)
ALTER TABLE courses
  ADD COLUMN IF NOT EXISTS is_closed TINYINT(1) DEFAULT 0
  AFTER is_active;

-- 3. Add lecture_completions table to track which lectures a student watched
CREATE TABLE IF NOT EXISTS lecture_completions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    lecture_id INT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_completion (student_id, lecture_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (lecture_id) REFERENCES recorded_lectures(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Fix existing individual notifications: if recipient_id matches a faculty
--    row that also exists as a student id, we rely on password_requests to
--    disambiguate (best-effort backfill)
UPDATE notifications n
INNER JOIN password_requests pr
    ON pr.user_id = n.recipient_id
    AND n.recipient_type = 'individual'
SET n.recipient_role = pr.user_role
WHERE n.recipient_role IS NULL;

SELECT 'Migration v2 complete.' AS status;

-- ============================================================
-- MIGRATION v2 — Run in phpMyAdmin → lms_db → SQL tab
-- ============================================================

-- 1. Add recipient_role to notifications (if not already added)
ALTER TABLE notifications
  ADD COLUMN IF NOT EXISTS recipient_role ENUM('student','faculty') DEFAULT NULL
  AFTER recipient_id;

-- 2. Add is_closed to courses (faculty can close a course)
ALTER TABLE courses
  ADD COLUMN IF NOT EXISTS is_closed TINYINT(1) DEFAULT 0
  AFTER is_active;

-- 3. Add lecture_completions table to track which lectures a student watched
CREATE TABLE IF NOT EXISTS lecture_completions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    lecture_id INT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_completion (student_id, lecture_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (lecture_id) REFERENCES recorded_lectures(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 4. Fix existing individual notifications: if recipient_id matches a faculty
--    row that also exists as a student id, we rely on password_requests to
--    disambiguate (best-effort backfill)
UPDATE notifications n
INNER JOIN password_requests pr
    ON pr.user_id = n.recipient_id
    AND n.recipient_type = 'individual'
SET n.recipient_role = pr.user_role
WHERE n.recipient_role IS NULL;

SELECT 'Migration v2 complete.' AS status;

-- 5. Add 'admin' to recipient_type enum (for faculty/student → admin messages)
ALTER TABLE notifications
  MODIFY COLUMN recipient_type ENUM('all','students','faculty','individual','admin') DEFAULT 'all';

-- 6. Add 'admin' to recipient_role enum
ALTER TABLE notifications
  MODIFY COLUMN recipient_role ENUM('student','faculty','admin') DEFAULT NULL;

SELECT 'Migration v2 additions complete.' AS status;

-- ============================================================
-- QUICK FIX: Run this in phpMyAdmin → lms_db → SQL tab
-- Adds 'admin' to the recipient_role ENUM column
-- ============================================================

ALTER TABLE notifications
  MODIFY COLUMN recipient_role ENUM('student', 'faculty', 'admin') DEFAULT NULL;

-- Also ensure recipient_type has 'admin' value
ALTER TABLE notifications
  MODIFY COLUMN recipient_type ENUM('all', 'students', 'faculty', 'individual', 'admin') DEFAULT 'all';

-- Verify
DESCRIBE notifications;

SELECT 'Fix complete. Enum updated.' AS status;
