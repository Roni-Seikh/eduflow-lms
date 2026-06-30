"""
Student Blueprint
"""
import random
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_wtf.csrf import validate_csrf
from wtforms import ValidationError
from flask_login import login_required, current_user
from models.models import (
    db, Course, Enrollment, LiveClass, RecordedLecture,
    Exam, ExamQuestion, ExamResult, Attendance, Certificate, Notification, CheatingLog,
    LectureCompletion
)
from utils.helpers import (
    student_required, save_file, get_attendance_percentage,
    generate_certificate_id, generate_certificate_pdf, log_activity
)
from datetime import datetime
import os

student_bp = Blueprint('student', __name__)

def _get_student_notifications(student_id, limit=None):
    """
    Return notifications visible ONLY to this specific student.
    Rules:
      - recipient_type='all'        → everyone sees it
      - recipient_type='students'   → all students see it (broadcasts from admin/faculty)
      - recipient_type='individual' AND recipient_id=student_id AND recipient_role='student'
                                    → only this student sees it
    Faculty individual notifications (recipient_role='faculty') are NEVER shown to students.
    """
    # Fetch candidate notifications broadly then filter strictly in Python
    # This avoids crashing if recipient_role column doesn't exist yet in DB
    candidates = Notification.query.filter(
        (Notification.recipient_type == 'all') |
        (Notification.recipient_type == 'students') |
        (
            (Notification.recipient_type == 'individual') &
            (Notification.recipient_id == student_id)
        )
    ).order_by(Notification.created_at.desc()).all()

    result = []
    for n in candidates:
        if n.recipient_type == 'individual':
            # Strict check: must be addressed to THIS student specifically
            if n.recipient_id != student_id:
                continue
            # Must be role=student or role not set (old data before migration)
            role = getattr(n, 'recipient_role', None)
            if role is not None and role != 'student':
                continue  # This was sent to a faculty member — skip
        result.append(n)

    return result[:limit] if limit else result




def _calculate_progress(student_id, course_id):
    """
    Progress = weighted average:
      50% from lectures watched / total lectures
      50% from exams passed / total exams
    If no lectures and no exams → 0
    After all exams passed and all lectures watched → 100
    """
    total_lectures = RecordedLecture.query.filter_by(
        course_id=course_id, is_active=True).count()
    watched = LectureCompletion.query.filter_by(
        student_id=student_id).join(
        RecordedLecture, LectureCompletion.lecture_id == RecordedLecture.id
    ).filter(RecordedLecture.course_id == course_id).count()

    total_exams = Exam.query.filter_by(course_id=course_id, is_active=True).count()
    passed_exams = ExamResult.query.join(
        Exam, ExamResult.exam_id == Exam.id
    ).filter(
        Exam.course_id == course_id,
        ExamResult.student_id == student_id,
        ExamResult.passed == True
    ).count()

    lecture_pct = (watched / total_lectures * 100) if total_lectures > 0 else 100
    exam_pct    = (passed_exams / total_exams * 100) if total_exams > 0 else 100

    if total_lectures == 0 and total_exams == 0:
        return 0

    # Weight: 60% lectures, 40% exams (if both exist)
    if total_lectures > 0 and total_exams > 0:
        progress = int(lecture_pct * 0.6 + exam_pct * 0.4)
    elif total_lectures > 0:
        progress = int(lecture_pct)
    else:
        progress = int(exam_pct)

    return min(progress, 100)


def _sync_enrollment_progress(student_id, course_id):
    """Recalculate and save progress for one enrollment. Issue cert if 100%."""
    enrollment = Enrollment.query.filter_by(
        student_id=student_id, course_id=course_id).first()
    if not enrollment:
        return

    progress = _calculate_progress(student_id, course_id)
    enrollment.progress = progress

    if progress >= 100 and not enrollment.is_completed:
        enrollment.is_completed = True
        enrollment.completed_at = datetime.utcnow()
        # Auto-generate course completion certificate
        _issue_certificate(student_id, course_id, cert_type='Course')

    db.session.commit()


# ─── DASHBOARD ────────────────────────────────────────────────
@student_bp.route('/dashboard')
@login_required
@student_required
def dashboard():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    upcoming_exams = []
    for e in enrollments:
        exams = Exam.query.filter_by(course_id=e.course_id, is_active=True).all()
        for exam in exams:
            result = ExamResult.query.filter_by(exam_id=exam.id, student_id=current_user.id).first()
            if not result:
                upcoming_exams.append(exam)

    notifications = _get_student_notifications(current_user.id, limit=5)

    certificates = Certificate.query.filter_by(student_id=current_user.id).count()
    results = ExamResult.query.filter_by(student_id=current_user.id).all()
    avg_score = sum(r.percentage for r in results) / len(results) if results else 0

    return render_template('student/dashboard.html',
                           enrollments=enrollments,
                           upcoming_exams=upcoming_exams[:5],
                           notifications=notifications,
                           certificates=certificates,
                           avg_score=round(avg_score, 1))


# ─── PROFILE ──────────────────────────────────────────────────
@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@student_required
def profile():
    if request.method == 'POST':
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.address = request.form.get('address', current_user.address)

        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            current_user.profile_image = save_file(profile_image, 'uploads/profiles')

        db.session.commit()
        flash('Profile updated.', 'success')

    return render_template('student/profile.html')


# ─── COURSE ENROLLMENT ────────────────────────────────────────
@student_bp.route('/courses')
@login_required
@student_required
def courses():
    search = request.args.get('search', '')
    query = Course.query.filter_by(is_active=True)
    if search:
        query = query.filter(Course.title.ilike(f'%{search}%'))
    all_courses = query.all()
    enrolled_ids = [e.course_id for e in Enrollment.query.filter_by(student_id=current_user.id).all()]
    return render_template('student/courses.html', courses=all_courses,
                           enrolled_ids=enrolled_ids, search=search)


@student_bp.route('/courses/enroll/<int:course_id>', methods=['POST'])
@login_required
@student_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    existing = Enrollment.query.filter_by(student_id=current_user.id, course_id=course_id).first()
    if existing:
        flash('Already enrolled.', 'info')
    else:
        enrollment = Enrollment(student_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        log_activity(current_user.id, 'student', 'Enroll', f'Enrolled in {course.title}')
        flash(f'Enrolled in {course.title}!', 'success')
    return redirect(url_for('student.my_courses'))


@student_bp.route('/my-courses')
@login_required
@student_required
def my_courses():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('student/my_courses.html', enrollments=enrollments)


# ─── LEARNING ─────────────────────────────────────────────────
@student_bp.route('/course/<int:course_id>')
@login_required
@student_required
def course_detail(course_id):
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id, course_id=course_id
    ).first_or_404()

    # Sync progress on every page load
    _sync_enrollment_progress(current_user.id, course_id)
    db.session.refresh(enrollment)

    course = enrollment.course
    live_classes = LiveClass.query.filter_by(course_id=course_id, is_active=True).order_by(LiveClass.scheduled_at).all()
    lectures = RecordedLecture.query.filter_by(course_id=course_id, is_active=True).order_by(RecordedLecture.sort_order).all()
    exams = Exam.query.filter_by(course_id=course_id, is_active=True).all()
    attendance_pct = get_attendance_percentage(current_user.id, course_id)

    # Which lectures has this student already completed?
    completed_lecture_ids = set(
        lc.lecture_id for lc in
        LectureCompletion.query.filter_by(student_id=current_user.id).all()
    )

    exam_status = {}
    for exam in exams:
        result = ExamResult.query.filter_by(exam_id=exam.id, student_id=current_user.id).first()
        exam_status[exam.id] = result

    return render_template('student/course_detail.html',
                           course=course,
                           enrollment=enrollment,
                           live_classes=live_classes,
                           lectures=lectures,
                           exams=exams,
                           exam_status=exam_status,
                           attendance_pct=attendance_pct,
                           completed_lecture_ids=completed_lecture_ids)


# ─── ATTENDANCE ───────────────────────────────────────────────
@student_bp.route('/attendance')
@login_required
@student_required
def attendance():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    attendance_data = []
    for e in enrollments:
        pct = get_attendance_percentage(current_user.id, e.course_id)
        attendance_data.append({'course': e.course, 'percentage': pct})
    return render_template('student/attendance.html', attendance_data=attendance_data)


# ─── EXAM SYSTEM ──────────────────────────────────────────────
@student_bp.route('/exam/<int:exam_id>/start')
@login_required
@student_required
def start_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id, course_id=exam.course_id
    ).first()
    if not enrollment:
        flash('You are not enrolled in this course.', 'error')
        return redirect(url_for('student.dashboard'))

    existing_result = ExamResult.query.filter_by(exam_id=exam_id, student_id=current_user.id).first()
    if existing_result:
        flash('You have already attempted this exam.', 'info')
        return redirect(url_for('student.exam_result', result_id=existing_result.id))

    questions = ExamQuestion.query.filter_by(exam_id=exam_id).all()
    if exam.randomize_questions:
        random.shuffle(questions)

    return render_template('student/exam.html', exam=exam, questions=questions)


@student_bp.route('/exam/<int:exam_id>/submit', methods=['POST'])
@login_required
@student_required
def submit_exam(exam_id):
    exam = Exam.query.get_or_404(exam_id)
    existing_result = ExamResult.query.filter_by(exam_id=exam_id, student_id=current_user.id).first()
    if existing_result:
        return jsonify({'error': 'Already submitted'}), 400

    questions = ExamQuestion.query.filter_by(exam_id=exam_id).all()
    answers = {}
    score = 0
    total_marks = sum(q.marks for q in questions)
    time_taken = request.form.get('time_taken', 0, type=int)
    auto_submit = request.form.get('auto_submit', 'false')

    for q in questions:
        answer = request.form.get(f'answer_{q.id}', '')
        answers[str(q.id)] = answer
        if answer == q.correct_answer:
            score += q.marks

    percentage = (score / total_marks * 100) if total_marks > 0 else 0
    passed = percentage >= exam.passing_score

    result = ExamResult(
        exam_id=exam_id,
        student_id=current_user.id,
        score=score,
        total_marks=total_marks,
        percentage=round(percentage, 2),
        passed=passed,
        time_taken=time_taken,
        answers=answers
    )
    db.session.add(result)

    # Log if auto-submitted (potential cheating)
    if auto_submit == 'true':
        log = CheatingLog(
            exam_id=exam_id,
            student_id=current_user.id,
            action='auto_submit',
            description='Exam auto-submitted due to suspicious activity'
        )
        db.session.add(log)

    db.session.flush()

    db.session.commit()

    # Issue exam certificate immediately if passed
    if passed:
        _issue_certificate(
            current_user.id,
            exam.course_id,
            exam_id=result.id,
            cert_type='Exam'
        )

    # Sync course progress (may also trigger course completion certificate)
    _sync_enrollment_progress(current_user.id, exam.course_id)
    log_activity(current_user.id, 'student', 'Submit Exam', f'Exam {exam.title}, Score: {score}/{total_marks}')

    if request.is_json or request.form.get('ajax'):
        return jsonify({'redirect': url_for('student.exam_result', result_id=result.id)})

    return redirect(url_for('student.exam_result', result_id=result.id))


@student_bp.route('/exam/log-cheat', methods=['POST'])
@login_required
@student_required
def log_cheat():
    data = request.get_json()
    log = CheatingLog(
        exam_id=data.get('exam_id'),
        student_id=current_user.id,
        action=data.get('action', 'unknown'),
        description=data.get('description', '')
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'status': 'logged'})


@student_bp.route('/exam/result/<int:result_id>')
@login_required
@student_required
def exam_result(result_id):
    result = ExamResult.query.filter_by(id=result_id, student_id=current_user.id).first_or_404()
    exam = result.exam
    questions = ExamQuestion.query.filter_by(exam_id=exam.id).all()
    return render_template('student/exam_result.html', result=result, exam=exam, questions=questions)


# ─── RESULTS ──────────────────────────────────────────────────
@student_bp.route('/results')
@login_required
@student_required
def results():
    results = ExamResult.query.filter_by(student_id=current_user.id).order_by(ExamResult.submitted_at.desc()).all()
    return render_template('student/results.html', results=results)


# ─── CERTIFICATES ─────────────────────────────────────────────
@student_bp.route('/certificates')
@login_required
@student_required
def certificates():
    certs = Certificate.query.filter_by(student_id=current_user.id).all()
    return render_template('student/certificates.html', certificates=certs)


@student_bp.route('/certificates/claim', methods=['POST'])
@login_required
@student_required
def claim_certificates():
    """
    Retroactively issue certificates for exams already passed and
    courses already completed. Safe to call multiple times — won't duplicate.
    """
    issued = 0

    # ── Exam certificates ─────────────────────────────────────
    passed_results = ExamResult.query.filter_by(
        student_id=current_user.id, passed=True
    ).all()
    for result in passed_results:
        cert = _issue_certificate(
            current_user.id,
            result.exam.course_id,
            exam_id=result.id,
            cert_type='Exam'
        )
        if cert and cert.issued_at >= datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0):
            issued += 1

    # ── Course certificates ───────────────────────────────────
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    for enr in enrollments:
        _sync_enrollment_progress(current_user.id, enr.course_id)

    # Count newly issued
    total = Certificate.query.filter_by(student_id=current_user.id).count()
    flash(f'Certificates updated! You now have {total} certificate(s).', 'success')
    return redirect(url_for('student.certificates'))


@student_bp.route('/certificates/download/<int:cert_id>')
@login_required
@student_required
def download_certificate(cert_id):
    cert = Certificate.query.filter_by(id=cert_id, student_id=current_user.id).first_or_404()
    from flask import current_app
    cert_path = os.path.join(current_app.root_path, 'static', cert.file_path)
    if os.path.exists(cert_path):
        return send_file(cert_path, as_attachment=True, download_name=f'certificate_{cert.certificate_id}.pdf')
    flash('Certificate file not found.', 'error')
    return redirect(url_for('student.certificates'))


# ─── NOTIFICATIONS ────────────────────────────────────────────
@student_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
@student_required
def notifications():
    from models.models import Admin, Faculty as FacultyModel, Notification
    from utils.notification_helper import send_notification

    if request.method == 'POST':
        title          = request.form.get('title', '').strip()
        message        = request.form.get('message', '').strip()
        recipient_type = request.form.get('recipient_type', '')
        individual_id  = request.form.get('individual_id', '').strip()  # LMS/F/26/01

        if not title or not message:
            flash('Title and message are required.', 'error')
        elif recipient_type == 'admin':
            # Student → Admin only
            admin = Admin.query.first()
            if admin:
                send_notification(
                    sender_id=current_user.id, sender_role='student',
                    recipient_type='individual',
                    recipient_id=admin.id, recipient_role='admin',
                    title=title,
                    message=f'[From Student {current_user.student_id}: {current_user.name}] {message}'
                )
                flash('Your query has been sent to Admin.', 'success')
        elif recipient_type == 'individual_faculty' and individual_id:
            # Student → Specific faculty by LMS ID
            faculty = FacultyModel.query.filter_by(faculty_id=individual_id).first()
            if not faculty:
                flash(f'No faculty found with ID: {individual_id}', 'error')
            else:
                send_notification(
                    sender_id=current_user.id, sender_role='student',
                    recipient_type='individual',
                    recipient_id=faculty.id, recipient_role='faculty',
                    title=title,
                    message=f'[From Student {current_user.student_id}: {current_user.name}] {message}'
                )
                flash(f'Message sent to {faculty.name}.', 'success')
        elif recipient_type == 'course_faculty':
            # Student → Faculty of their enrolled courses
            sent_count = 0
            seen_faculty = set()
            for enr in Enrollment.query.filter_by(student_id=current_user.id).all():
                fid = enr.course.faculty_id
                if fid not in seen_faculty:
                    seen_faculty.add(fid)
                    send_notification(
                        sender_id=current_user.id, sender_role='student',
                        recipient_type='individual',
                        recipient_id=fid, recipient_role='faculty',
                        title=title,
                        message=f'[From Student {current_user.student_id}: {current_user.name}] {message}'
                    )
                    sent_count += 1
            flash(f'Message sent to {sent_count} faculty member(s).', 'success')
        else:
            flash('Please select a valid recipient.', 'error')

    received = _get_student_notifications(current_user.id)
    sent = Notification.query.filter_by(
        sender_id=current_user.id, sender_role='student'
    ).order_by(Notification.created_at.desc()).limit(30).all()

    return render_template('student/notifications.html',
                           notifications=received,
                           sent_notifications=sent)


# ─── HELPER ───────────────────────────────────────────────────
def _issue_certificate(student_id, course_id, exam_id=None, cert_type='Course'):
    """Issue and generate a PDF certificate. Returns cert or None."""
    from flask import current_app
    from models.models import Student as _Student, Course as _Course

    # Prevent duplicates — for exam certs check exam_id too
    if cert_type == 'Exam' and exam_id:
        existing = Certificate.query.filter_by(
            student_id=student_id, exam_id=exam_id, type='Exam'
        ).first()
    else:
        existing = Certificate.query.filter_by(
            student_id=student_id, course_id=course_id, type='Course'
        ).first()
    if existing:
        return existing

    student = db.session.get(_Student, student_id)
    course  = db.session.get(_Course, course_id)
    if not student or not course:
        return None

    # Get faculty name for course certificate signature
    faculty_name = None
    if course.faculty:
        faculty_name = course.faculty.name

    cert_id      = generate_certificate_id()
    filename     = f'certificates/{cert_id}.pdf'
    output_path  = os.path.join(current_app.root_path, 'static', filename)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        generate_certificate_pdf(
            student_name=student.name,
            course_name=course.title,
            certificate_id=cert_id,
            issued_date=datetime.utcnow(),
            output_path=output_path,
            faculty_name=faculty_name,
            cert_type=cert_type
        )
    except Exception as e:
        import traceback
        print(f'[CERT ERROR] PDF generation failed: {e}')
        traceback.print_exc()
        return None

    cert = Certificate(
        certificate_id=cert_id,
        student_id=student_id,
        course_id=course_id,
        exam_id=exam_id,
        type=cert_type,
        file_path=filename
    )
    db.session.add(cert)
    db.session.commit()   # ← was missing before
    return cert


# ─── MARK LECTURE COMPLETE ────────────────────────────────────
@student_bp.route('/lecture/<int:lecture_id>/complete', methods=['POST'])
@login_required
@student_required
def mark_lecture_complete(lecture_id):
    """Student marks a lecture as watched — triggers progress recalculation."""
    # Validate CSRF from either form data or X-CSRFToken header
    token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token', '')
    try:
        validate_csrf(token)
    except ValidationError:
        return jsonify({'error': 'Invalid CSRF token'}), 400

    lecture = RecordedLecture.query.get_or_404(lecture_id)

    # Verify student is enrolled
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id, course_id=lecture.course_id
    ).first()
    if not enrollment:
        return jsonify({'error': 'Not enrolled'}), 403

    # Toggle: if already completed, un-complete it
    existing = LectureCompletion.query.filter_by(
        student_id=current_user.id, lecture_id=lecture_id
    ).first()

    if existing:
        db.session.delete(existing)
        completed = False
    else:
        lc = LectureCompletion(student_id=current_user.id, lecture_id=lecture_id)
        db.session.add(lc)
        completed = True

    db.session.commit()
    _sync_enrollment_progress(current_user.id, lecture.course_id)

    progress = _calculate_progress(current_user.id, lecture.course_id)
    return jsonify({'completed': completed, 'progress': progress})


# ─── COURSE PROGRESS API ──────────────────────────────────────
@student_bp.route('/course/<int:course_id>/progress')
@login_required
@student_required
def course_progress(course_id):
    """Return current progress for a course."""
    enrollment = Enrollment.query.filter_by(
        student_id=current_user.id, course_id=course_id
    ).first_or_404()
    _sync_enrollment_progress(current_user.id, course_id)
    return jsonify({'progress': enrollment.progress, 'completed': enrollment.is_completed})
