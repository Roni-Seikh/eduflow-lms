"""
Faculty Blueprint
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models.models import (
    db, Course, Enrollment, LiveClass, RecordedLecture,
    Exam, ExamQuestion, ExamResult, Attendance, Student, CheatingLog, Notification
)
from utils.helpers import faculty_required, save_file, log_activity
from datetime import datetime

faculty_bp = Blueprint('faculty', __name__)


# ─── DASHBOARD ────────────────────────────────────────────────
@faculty_bp.route('/dashboard')
@login_required
@faculty_required
def dashboard():
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    total_students = sum(c.enrollments.count() for c in courses)
    total_exams = Exam.query.filter_by(faculty_id=current_user.id).count()
    return render_template('faculty/dashboard.html',
                           courses=courses,
                           total_students=total_students,
                           total_exams=total_exams)


# ─── PROFILE ──────────────────────────────────────────────────
@faculty_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@faculty_required
def profile():
    if request.method == 'POST':
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.qualification = request.form.get('qualification', current_user.qualification)
        current_user.specialization = request.form.get('specialization', current_user.specialization)

        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            current_user.profile_image = save_file(profile_image, 'uploads/profiles')

        db.session.commit()
        flash('Profile updated.', 'success')

    return render_template('faculty/profile.html')


# ─── COURSE MANAGEMENT ────────────────────────────────────────
@faculty_bp.route('/courses')
@login_required
@faculty_required
def courses():
    courses = Course.query.filter_by(faculty_id=current_user.id).order_by(Course.created_at.desc()).all()
    return render_template('faculty/courses.html', courses=courses)


@faculty_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@faculty_required
def create_course():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '')
        duration = request.form.get('duration', '')
        category = request.form.get('category', '')
        level = request.form.get('level', 'Beginner')

        course = Course(
            faculty_id=current_user.id,
            title=title, description=description,
            duration=duration, category=category, level=level
        )
        thumbnail = request.files.get('thumbnail')
        if thumbnail and thumbnail.filename:
            course.thumbnail = save_file(thumbnail, 'uploads/thumbnails')

        db.session.add(course)
        db.session.commit()
        log_activity(current_user.id, 'faculty', 'Create Course', title)
        flash('Course created successfully.', 'success')
        return redirect(url_for('faculty.courses'))

    return render_template('faculty/course_form.html', action='Create')


@faculty_bp.route('/courses/edit/<int:course_id>', methods=['GET', 'POST'])
@login_required
@faculty_required
def edit_course(course_id):
    course = Course.query.filter_by(id=course_id, faculty_id=current_user.id).first_or_404()

    if request.method == 'POST':
        course.title = request.form.get('title', course.title).strip()
        course.description = request.form.get('description', course.description)
        course.duration = request.form.get('duration', course.duration)
        course.category = request.form.get('category', course.category)
        course.level = request.form.get('level', course.level)

        thumbnail = request.files.get('thumbnail')
        if thumbnail and thumbnail.filename:
            course.thumbnail = save_file(thumbnail, 'uploads/thumbnails')

        db.session.commit()
        flash('Course updated.', 'success')
        return redirect(url_for('faculty.courses'))

    return render_template('faculty/course_form.html', action='Edit', course=course)


@faculty_bp.route('/courses/delete/<int:course_id>', methods=['POST'])
@login_required
@faculty_required
def delete_course(course_id):
    course = Course.query.filter_by(id=course_id, faculty_id=current_user.id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'success')
    return redirect(url_for('faculty.courses'))


# ─── LIVE CLASSES ─────────────────────────────────────────────
@faculty_bp.route('/live-classes')
@login_required
@faculty_required
def live_classes():
    classes = LiveClass.query.filter_by(faculty_id=current_user.id).order_by(LiveClass.scheduled_at.desc()).all()
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    now = datetime.utcnow()
    return render_template('faculty/live_classes.html', classes=classes, courses=courses, now=now)


@faculty_bp.route('/live-classes/add', methods=['POST'])
@login_required
@faculty_required
def add_live_class():
    title = request.form.get('title', '').strip()
    course_id = request.form.get('course_id', type=int)
    meeting_link = request.form.get('meeting_link', '')
    scheduled_at = request.form.get('scheduled_at', '')
    duration_minutes = request.form.get('duration_minutes', 60, type=int)
    description = request.form.get('description', '')

    lc = LiveClass(
        course_id=course_id,
        faculty_id=current_user.id,
        title=title,
        description=description,
        meeting_link=meeting_link,
        scheduled_at=datetime.strptime(scheduled_at, '%Y-%m-%dT%H:%M'),
        duration_minutes=duration_minutes
    )
    db.session.add(lc)
    db.session.commit()
    flash('Live class scheduled.', 'success')
    return redirect(url_for('faculty.live_classes'))


# ─── RECORDED LECTURES ────────────────────────────────────────
@faculty_bp.route('/lectures')
@login_required
@faculty_required
def lectures():
    lectures = RecordedLecture.query.filter_by(faculty_id=current_user.id).order_by(RecordedLecture.created_at.desc()).all()
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    return render_template('faculty/lectures.html', lectures=lectures, courses=courses)


@faculty_bp.route('/lectures/add', methods=['POST'])
@login_required
@faculty_required
def add_lecture():
    title = request.form.get('title', '').strip()
    course_id = request.form.get('course_id', type=int)
    description = request.form.get('description', '')
    video_url = request.form.get('video_url', '')
    duration = request.form.get('duration', '')

    lecture = RecordedLecture(
        course_id=course_id,
        faculty_id=current_user.id,
        title=title,
        description=description,
        video_url=video_url,
        duration=duration
    )
    video_file = request.files.get('video_file')
    if video_file and video_file.filename:
        lecture.video_file = save_file(video_file, 'uploads/videos')

    pdf_file = request.files.get('pdf_file')
    if pdf_file and pdf_file.filename:
        lecture.pdf_file = save_file(pdf_file, 'uploads/pdfs')

    db.session.add(lecture)
    db.session.commit()
    flash('Lecture added.', 'success')
    return redirect(url_for('faculty.lectures'))


# ─── EXAM MANAGEMENT ──────────────────────────────────────────
@faculty_bp.route('/exams')
@login_required
@faculty_required
def exams():
    exams = Exam.query.filter_by(faculty_id=current_user.id).order_by(Exam.created_at.desc()).all()
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    return render_template('faculty/exams.html', exams=exams, courses=courses)


@faculty_bp.route('/exams/create', methods=['GET', 'POST'])
@login_required
@faculty_required
def create_exam():
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        course_id = request.form.get('course_id', type=int)
        description = request.form.get('description', '')
        duration_minutes = request.form.get('duration_minutes', 60, type=int)
        passing_score = request.form.get('passing_score', 60, type=int)
        randomize = bool(request.form.get('randomize_questions'))

        exam = Exam(
            course_id=course_id,
            faculty_id=current_user.id,
            title=title,
            description=description,
            duration_minutes=duration_minutes,
            passing_score=passing_score,
            randomize_questions=randomize
        )
        db.session.add(exam)
        db.session.flush()

        # Add questions
        questions = request.form.getlist('questions[]')
        opt_a = request.form.getlist('option_a[]')
        opt_b = request.form.getlist('option_b[]')
        opt_c = request.form.getlist('option_c[]')
        opt_d = request.form.getlist('option_d[]')
        correct = request.form.getlist('correct_answer[]')

        for i, q in enumerate(questions):
            if q.strip():
                question = ExamQuestion(
                    exam_id=exam.id,
                    question=q.strip(),
                    option_a=opt_a[i] if i < len(opt_a) else '',
                    option_b=opt_b[i] if i < len(opt_b) else '',
                    option_c=opt_c[i] if i < len(opt_c) else '',
                    option_d=opt_d[i] if i < len(opt_d) else '',
                    correct_answer=correct[i] if i < len(correct) else 'A'
                )
                db.session.add(question)

        exam.total_questions = len([q for q in questions if q.strip()])
        db.session.commit()
        flash('Exam created successfully.', 'success')
        return redirect(url_for('faculty.exams'))

    return render_template('faculty/exam_form.html', action='Create', courses=courses)


@faculty_bp.route('/exams/<int:exam_id>/questions')
@login_required
@faculty_required
def exam_questions(exam_id):
    exam = Exam.query.filter_by(id=exam_id, faculty_id=current_user.id).first_or_404()
    questions = ExamQuestion.query.filter_by(exam_id=exam_id).all()
    return render_template('faculty/exam_questions.html', exam=exam, questions=questions)


@faculty_bp.route('/exams/<int:exam_id>/results')
@login_required
@faculty_required
def exam_results(exam_id):
    exam = Exam.query.filter_by(id=exam_id, faculty_id=current_user.id).first_or_404()

    # results — student backref is auto-loaded via Student.exam_results backref
    results = ExamResult.query.filter_by(exam_id=exam_id).all()

    # cheating_logs — student loaded via CheatingLog.student relationship
    cheating_logs = CheatingLog.query.filter_by(exam_id=exam_id).all()

    return render_template('faculty/exam_results.html', exam=exam, results=results,
                           cheating_logs=cheating_logs)


# ─── ATTENDANCE ───────────────────────────────────────────────
@faculty_bp.route('/attendance')
@login_required
@faculty_required
def attendance():
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    return render_template('faculty/attendance.html', courses=courses)


@faculty_bp.route('/attendance/mark/<int:course_id>', methods=['GET', 'POST'])
@login_required
@faculty_required
def mark_attendance(course_id):
    course = Course.query.filter_by(id=course_id, faculty_id=current_user.id).first_or_404()
    enrolled_students = [e.student for e in Enrollment.query.filter_by(course_id=course_id).all()]
    today = datetime.utcnow().date()

    if request.method == 'POST':
        date_str = request.form.get('date', str(today))
        att_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        for student in enrolled_students:
            status = request.form.get(f'status_{student.id}', 'Absent')
            existing = Attendance.query.filter_by(
                student_id=student.id, course_id=course_id, date=att_date
            ).first()
            if existing:
                existing.status = status
            else:
                att = Attendance(
                    student_id=student.id,
                    course_id=course_id,
                    faculty_id=current_user.id,
                    date=att_date,
                    status=status
                )
                db.session.add(att)

        db.session.commit()
        flash('Attendance marked.', 'success')
        return redirect(url_for('faculty.attendance'))

    return render_template('faculty/mark_attendance.html', course=course,
                           students=enrolled_students, today=today)


@faculty_bp.route('/students')
@login_required
@faculty_required
def students():
    """View enrolled students across faculty's courses"""
    courses = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    course_data = []
    for course in courses:
        enrollments = Enrollment.query.filter_by(course_id=course.id).all()
        course_data.append({'course': course, 'enrollments': enrollments})
    return render_template('faculty/students.html', course_data=course_data)


# ─── NOTIFICATIONS ────────────────────────────────────────────
@faculty_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
@faculty_required
def notifications():
    from models.models import Notification, Admin
    from utils.notification_helper import send_notification, get_notifications_for_faculty

    if request.method == 'POST':
        title           = request.form.get('title', '').strip()
        message         = request.form.get('message', '').strip()
        recipient_type  = request.form.get('recipient_type', '')
        individual_id   = request.form.get('individual_id', '').strip()  # LMS/S/26/01
        course_id_str   = request.form.get('course_id', '').strip()

        if not title or not message:
            flash('Title and message are required.', 'error')
        elif recipient_type == 'admin':
            # Faculty → Admin
            admin = Admin.query.first()
            if admin:
                send_notification(
                    sender_id=current_user.id, sender_role='faculty',
                    recipient_type='individual',
                    recipient_id=admin.id, recipient_role='admin',
                    title=title, message=f'[From Faculty: {current_user.name}] {message}'
                )
                flash('Message sent to Admin.', 'success')
        elif recipient_type == 'all_students':
            # Faculty → All Students (broadcast)
            send_notification(
                sender_id=current_user.id, sender_role='faculty',
                recipient_type='students',
                title=title, message=message
            )
            flash('Notification sent to all students.', 'success')
        elif recipient_type == 'course_students' and course_id_str:
            # Faculty → Students in specific course
            enrollments = Enrollment.query.filter_by(course_id=int(course_id_str)).all()
            if not enrollments:
                flash('No students enrolled in that course.', 'error')
            else:
                for enr in enrollments:
                    send_notification(
                        sender_id=current_user.id, sender_role='faculty',
                        recipient_type='individual',
                        recipient_id=enr.student_id, recipient_role='student',
                        title=title, message=message
                    )
                flash(f'Notification sent to {len(enrollments)} student(s) in that course.', 'success')
        elif recipient_type == 'individual_student' and individual_id:
            # Faculty → One specific student by LMS ID
            student = Student.query.filter_by(student_id=individual_id).first()
            if not student:
                flash(f'No student found with ID: {individual_id}', 'error')
            else:
                send_notification(
                    sender_id=current_user.id, sender_role='faculty',
                    recipient_type='individual',
                    recipient_id=student.id, recipient_role='student',
                    title=title, message=message
                )
                flash(f'Notification sent to {student.name}.', 'success')
        else:
            flash('Please select a valid recipient.', 'error')

    my_courses  = Course.query.filter_by(faculty_id=current_user.id, is_active=True).all()
    # Faculty sees notifications sent TO them + broadcasts to faculty/all
    received = get_notifications_for_faculty(current_user.id, limit=100)
    sent     = Notification.query.filter_by(
        sender_id=current_user.id, sender_role='faculty'
    ).order_by(Notification.created_at.desc()).limit(50).all()

    return render_template('faculty/notifications.html',
                           courses=my_courses,
                           notifications=received,
                           sent_notifications=sent)


# ─── CLOSE / REOPEN COURSE ────────────────────────────────────
@faculty_bp.route('/courses/<int:course_id>/toggle-close', methods=['POST'])
@login_required
@faculty_required
def toggle_close_course(course_id):
    """Faculty closes or reopens a course. Closed = no new live classes, but
    students can still complete lectures and exams at their own pace."""
    course = Course.query.filter_by(id=course_id, faculty_id=current_user.id).first_or_404()
    course.is_closed = not course.is_closed
    action = 'closed' if course.is_closed else 'reopened'
    db.session.commit()

    # Notify enrolled students
    from models.models import Notification
    enrollments = Enrollment.query.filter_by(course_id=course_id).all()
    msg = (
        f'The course "{course.title}" has been {action} by the faculty. '
        + ('You can still complete all lectures and exams at your own pace to earn your certificate.'
           if course.is_closed else 'The course is now active again.')
    )
    for enr in enrollments:
        notif = Notification(
            sender_id=current_user.id,
            sender_role='faculty',
            recipient_type='individual',
            recipient_id=enr.student_id,
            recipient_role='student',
            title=f'📚 Course {"Closed" if course.is_closed else "Reopened"}: {course.title}',
            message=msg
        )
        db.session.add(notif)
    db.session.commit()

    flash(f'Course "{course.title}" has been {action}. Students have been notified.', 'success')
    return redirect(url_for('faculty.courses'))
