"""
LMS Database Models
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import bcrypt

db = SQLAlchemy()


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def get_role(self):
        return 'admin'

    def get_id(self):
        return f'admin_{self.id}'


class Student(UserMixin, db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'))
    address = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments   = db.relationship('Enrollment',   backref='student', lazy='dynamic')
    attendance    = db.relationship('Attendance',   backref='student', lazy='dynamic')
    exam_results  = db.relationship('ExamResult',   backref='student', lazy='dynamic')
    certificates  = db.relationship('Certificate',  backref='student', lazy='dynamic')
    cheating_logs = db.relationship('CheatingLog',  backref='cheat_student',
                                    lazy='dynamic',  foreign_keys='CheatingLog.student_id')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def get_role(self):
        return 'student'

    def get_id(self):
        return f'student_{self.id}'


class Faculty(UserMixin, db.Model):
    __tablename__ = 'faculty'
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255))
    department = db.Column(db.String(100))
    qualification = db.Column(db.String(150))
    specialization = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses = db.relationship('Course', backref='faculty', lazy='dynamic')
    live_classes = db.relationship('LiveClass', backref='faculty', lazy='dynamic')
    lectures = db.relationship('RecordedLecture', backref='faculty', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def get_role(self):
        return 'faculty'

    def get_id(self):
        return f'faculty_{self.id}'


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    thumbnail = db.Column(db.String(255))
    category = db.Column(db.String(100))
    level = db.Column(db.Enum('Beginner', 'Intermediate', 'Advanced'), default='Beginner')
    is_active = db.Column(db.Boolean, default=True)
    is_closed = db.Column(db.Boolean, default=False)  # faculty closes course after teaching
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic')
    live_classes = db.relationship('LiveClass', backref='course', lazy='dynamic')
    lectures = db.relationship('RecordedLecture', backref='course', lazy='dynamic')
    exams = db.relationship('Exam', backref='course', lazy='dynamic')
    attendance = db.relationship('Attendance', backref='course', lazy='dynamic')


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id'),)


class LiveClass(db.Model):
    __tablename__ = 'live_classes'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    meeting_link = db.Column(db.String(500))
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    recording_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RecordedLecture(db.Model):
    __tablename__ = 'recorded_lectures'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    video_file = db.Column(db.String(255))
    pdf_file = db.Column(db.String(255))
    duration = db.Column(db.String(20))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class LectureCompletion(db.Model):
    """Tracks which recorded lectures a student has marked as watched."""
    __tablename__ = 'lecture_completions'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    lecture_id = db.Column(db.Integer, db.ForeignKey('recorded_lectures.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('student_id', 'lecture_id'),)


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Present', 'Absent', 'Late'), default='Absent')
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)


class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    duration_minutes = db.Column(db.Integer, default=60)
    total_questions = db.Column(db.Integer, default=0)
    passing_score = db.Column(db.Integer, default=60)
    randomize_questions = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questions = db.relationship('ExamQuestion', backref='exam', lazy='dynamic', cascade='all, delete-orphan')
    results = db.relationship('ExamResult', backref='exam', lazy='dynamic')
    cheating_logs = db.relationship('CheatingLog', backref='exam', lazy='dynamic')


class ExamQuestion(db.Model):
    __tablename__ = 'exam_questions'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(500), nullable=False)
    option_b = db.Column(db.String(500), nullable=False)
    option_c = db.Column(db.String(500), nullable=False)
    option_d = db.Column(db.String(500), nullable=False)
    correct_answer = db.Column(db.Enum('A', 'B', 'C', 'D'), nullable=False)
    marks = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ExamResult(db.Model):
    __tablename__ = 'exam_results'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_marks = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Numeric(5, 2), default=0.00)
    passed = db.Column(db.Boolean, default=False)
    time_taken = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.JSON)
    __table_args__ = (db.UniqueConstraint('exam_id', 'student_id'),)


class CheatingLog(db.Model):
    __tablename__ = 'cheating_logs'
    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Use overlaps to silence the SAWarning about conflicting join paths
    student = db.relationship(
        'Student',
        foreign_keys=[student_id],
        lazy='joined',
        overlaps='cheating_logs'
    )


class Certificate(db.Model):
    __tablename__ = 'certificates'
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.String(50), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'))
    type = db.Column(db.Enum('Course', 'Exam'), default='Course')
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(255))


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer)
    sender_role = db.Column(db.Enum('admin', 'faculty'), default='admin')
    recipient_type = db.Column(db.Enum('all', 'students', 'faculty', 'individual', 'admin'), default='all')
    recipient_id = db.Column(db.Integer)
    # recipient_role: when recipient_type='individual', specifies whether
    # recipient_id refers to a student or faculty row (both tables start at id=1)
    recipient_role = db.Column(db.Enum('student', 'faculty', 'admin'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PasswordRequest(db.Model):
    __tablename__ = 'password_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_role = db.Column(db.Enum('student', 'faculty'), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    status = db.Column(db.Enum('pending', 'resolved', 'rejected'), default='pending')
    message = db.Column(db.Text)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    user_role = db.Column(db.Enum('admin', 'faculty', 'student'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
