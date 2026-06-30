"""
Admin Blueprint — Dashboard, Student/Faculty/Course Management
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from models.models import (
    db, Admin, Student, Faculty, Course, Enrollment, Exam, ExamResult,
    Attendance, Notification, PasswordRequest, ActivityLog, Certificate
)
from utils.helpers import (
    admin_required, generate_student_id, generate_faculty_id,
    validate_password, save_file, log_activity
)
from datetime import datetime
import io

admin_bp = Blueprint('admin', __name__)


def get_dashboard_stats():
    """Collect analytics for admin dashboard"""
    return {
        'total_students': Student.query.filter_by(is_active=True).count(),
        'total_faculty': Faculty.query.filter_by(is_active=True).count(),
        'total_courses': Course.query.filter_by(is_active=True).count(),
        'total_exams': Exam.query.filter_by(is_active=True).count(),
        'total_enrollments': Enrollment.query.count(),
        'pending_requests': PasswordRequest.query.filter_by(status='pending').count(),
        'recent_students': Student.query.order_by(Student.created_at.desc()).limit(5).all(),
        'recent_faculty': Faculty.query.order_by(Faculty.created_at.desc()).limit(5).all(),
        'recent_logs': ActivityLog.query.order_by(ActivityLog.logged_at.desc()).limit(10).all(),
    }


# ─── DASHBOARD ────────────────────────────────────────────────
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = get_dashboard_stats()
    return render_template('admin/dashboard.html', **stats)


# ─── STUDENT MANAGEMENT ───────────────────────────────────────
@admin_bp.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Student.query
    if search:
        query = query.filter(
            Student.name.ilike(f'%{search}%') |
            Student.email.ilike(f'%{search}%') |
            Student.student_id.ilike(f'%{search}%')
        )
    students = query.order_by(Student.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/students.html', students=students, search=search)


@admin_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        dob = request.form.get('date_of_birth')
        gender = request.form.get('gender')
        address = request.form.get('address', '')

        if Student.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/student_form.html', action='Add')

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'error')
            return render_template('admin/student_form.html', action='Add')

        student = Student(
            student_id=generate_student_id(),
            name=name, email=email, phone=phone,
            gender=gender, address=address
        )
        if dob:
            student.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()

        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            student.profile_image = save_file(profile_image, 'uploads/profiles')

        student.set_password(password)
        db.session.add(student)
        db.session.commit()
        log_activity(request.form.get('admin_id', 1), 'admin', 'Add Student', f'Added {name}')
        flash(f'Student added successfully. ID: {student.student_id}', 'success')
        return redirect(url_for('admin.students'))

    return render_template('admin/student_form.html', action='Add')


@admin_bp.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        student.name = request.form.get('name', student.name).strip()
        student.phone = request.form.get('phone', student.phone)
        student.gender = request.form.get('gender', student.gender)
        student.address = request.form.get('address', student.address)
        student.is_active = bool(request.form.get('is_active'))
        dob = request.form.get('date_of_birth')
        if dob:
            student.date_of_birth = datetime.strptime(dob, '%Y-%m-%d').date()

        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            student.profile_image = save_file(profile_image, 'uploads/profiles')

        new_password = request.form.get('new_password', '')
        if new_password:
            valid, msg = validate_password(new_password)
            if not valid:
                flash(msg, 'error')
                return render_template('admin/student_form.html', action='Edit', student=student)
            student.set_password(new_password)

        db.session.commit()
        flash('Student updated successfully.', 'success')
        return redirect(url_for('admin.students'))

    return render_template('admin/student_form.html', action='Edit', student=student)


@admin_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'success')
    return redirect(url_for('admin.students'))


@admin_bp.route('/students/view/<int:student_id>')
@login_required
@admin_required
def view_student(student_id):
    student = Student.query.get_or_404(student_id)
    enrollments = Enrollment.query.filter_by(student_id=student_id).all()
    results = ExamResult.query.filter_by(student_id=student_id).all()
    return render_template('admin/student_profile.html', student=student,
                           enrollments=enrollments, results=results)


# ─── FACULTY MANAGEMENT ───────────────────────────────────────
@admin_bp.route('/faculty')
@login_required
@admin_required
def faculty_list():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    query = Faculty.query
    if search:
        query = query.filter(
            Faculty.name.ilike(f'%{search}%') |
            Faculty.email.ilike(f'%{search}%') |
            Faculty.faculty_id.ilike(f'%{search}%')
        )
    faculty = query.order_by(Faculty.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin/faculty.html', faculty=faculty, search=search)


@admin_bp.route('/faculty/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_faculty():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '')
        password = request.form.get('password', '')
        department = request.form.get('department', '')
        qualification = request.form.get('qualification', '')
        specialization = request.form.get('specialization', '')

        if Faculty.query.filter_by(email=email).first():
            flash('Email already exists.', 'error')
            return render_template('admin/faculty_form.html', action='Add')

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'error')
            return render_template('admin/faculty_form.html', action='Add')

        faculty = Faculty(
            faculty_id=generate_faculty_id(),
            name=name, email=email, phone=phone,
            department=department, qualification=qualification,
            specialization=specialization
        )
        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            faculty.profile_image = save_file(profile_image, 'uploads/profiles')

        faculty.set_password(password)
        db.session.add(faculty)
        db.session.commit()
        flash(f'Faculty added. ID: {faculty.faculty_id}', 'success')
        return redirect(url_for('admin.faculty_list'))

    return render_template('admin/faculty_form.html', action='Add')


@admin_bp.route('/faculty/edit/<int:faculty_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_faculty(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    if request.method == 'POST':
        faculty.name = request.form.get('name', faculty.name).strip()
        faculty.phone = request.form.get('phone', faculty.phone)
        faculty.department = request.form.get('department', faculty.department)
        faculty.qualification = request.form.get('qualification', faculty.qualification)
        faculty.specialization = request.form.get('specialization', faculty.specialization)
        faculty.is_active = bool(request.form.get('is_active'))

        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            faculty.profile_image = save_file(profile_image, 'uploads/profiles')

        new_password = request.form.get('new_password', '')
        if new_password:
            valid, msg = validate_password(new_password)
            if not valid:
                flash(msg, 'error')
                return render_template('admin/faculty_form.html', action='Edit', faculty=faculty)
            faculty.set_password(new_password)

        db.session.commit()
        flash('Faculty updated.', 'success')
        return redirect(url_for('admin.faculty_list'))

    return render_template('admin/faculty_form.html', action='Edit', faculty=faculty)


@admin_bp.route('/faculty/delete/<int:faculty_id>', methods=['POST'])
@login_required
@admin_required
def delete_faculty(faculty_id):
    faculty = Faculty.query.get_or_404(faculty_id)
    db.session.delete(faculty)
    db.session.commit()
    flash('Faculty deleted.', 'success')
    return redirect(url_for('admin.faculty_list'))


# ─── COURSE MONITORING ────────────────────────────────────────
@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=courses)


# ─── EXAM MONITORING ──────────────────────────────────────────
@admin_bp.route('/exams')
@login_required
@admin_required
def exams():
    exams = Exam.query.order_by(Exam.created_at.desc()).all()
    return render_template('admin/exams.html', exams=exams)


# ─── ATTENDANCE MONITORING ────────────────────────────────────
@admin_bp.route('/attendance')
@login_required
@admin_required
def attendance():
    records = Attendance.query.order_by(Attendance.date.desc()).limit(200).all()
    return render_template('admin/attendance.html', records=records)


# ─── PASSWORD REQUESTS ────────────────────────────────────────
@admin_bp.route('/requests')
@login_required
@admin_required
def password_requests():
    requests_list = PasswordRequest.query.order_by(PasswordRequest.requested_at.desc()).all()
    return render_template('admin/password_requests.html', requests=requests_list)


@admin_bp.route('/requests/resolve/<int:req_id>', methods=['POST'])
@login_required
@admin_required
def resolve_request(req_id):
    pr = PasswordRequest.query.get_or_404(req_id)
    new_password = request.form.get('new_password', '')
    action = request.form.get('action', 'resolved')

    if action == 'resolved' and new_password:
        valid, msg = validate_password(new_password)
        if not valid:
            flash(msg, 'error')
            return redirect(url_for('admin.password_requests'))

        if pr.user_role == 'student':
            user = Student.query.get(pr.user_id)
        else:
            user = Faculty.query.get(pr.user_id)

        if user:
            user.set_password(new_password)
            pr.status = 'resolved'
            pr.resolved_at = datetime.utcnow()

            # ── Send notification to the user whose password was reset ──
            from utils.notification_helper import send_notification as _send
            _send(
                sender_id=current_user.id, sender_role='admin',
                recipient_type='individual',
                recipient_id=pr.user_id,
                recipient_role=pr.user_role,  # 'student' or 'faculty'
                title='🔑 Password Reset Successful',
                message=(
                    f'Hi {user.name}, your password reset request has been approved by the admin. '
                    f'Your new password has been set. Please log in and change it to something secure. '
                    f'If you did not request this, contact the admin immediately.'
                )
            )
            db.session.commit()
            flash('Password updated, request resolved and notification sent to user.', 'success')

    elif action == 'rejected':
        if pr.user_role == 'student':
            user = Student.query.get(pr.user_id)
        else:
            user = Faculty.query.get(pr.user_id)

        pr.status = 'rejected'
        pr.resolved_at = datetime.utcnow()

        # ── Notify the user their request was rejected ──
        if user:
            from utils.notification_helper import send_notification as _send
            _send(
                sender_id=current_user.id, sender_role='admin',
                recipient_type='individual',
                recipient_id=pr.user_id,
                recipient_role=pr.user_role,  # 'student' or 'faculty'
                title='❌ Password Reset Request Rejected',
                message=(
                    f'Hi {user.name}, your password reset request has been reviewed and rejected by the admin. '
                    f'If you believe this is a mistake, please submit a new request with more details.'
                )
            )

        db.session.commit()
        flash('Request rejected and notification sent to user.', 'info')

    return redirect(url_for('admin.password_requests'))


# ─── NOTIFICATIONS ────────────────────────────────────────────
@admin_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
@admin_required
def notifications():
    from utils.notification_helper import send_notification, get_notifications_for_admin

    if request.method == 'POST':
        title          = request.form.get('title', '').strip()
        message        = request.form.get('message', '').strip()
        recipient_type = request.form.get('recipient_type', 'all')
        individual_id  = request.form.get('individual_id', '').strip()
        individual_role= request.form.get('individual_role', '').strip()  # 'student' or 'faculty'

        if not title or not message:
            flash('Title and message are required.', 'error')
        else:
            if recipient_type == 'individual':
                # Resolve LMS ID to internal DB id
                recip_id   = None
                recip_role = None
                if individual_role == 'student':
                    user = Student.query.filter_by(student_id=individual_id).first()
                    if user:
                        recip_id   = user.id
                        recip_role = 'student'
                elif individual_role == 'faculty':
                    user = Faculty.query.filter_by(faculty_id=individual_id).first()
                    if user:
                        recip_id   = user.id
                        recip_role = 'faculty'

                if not recip_id:
                    flash(f'No {individual_role} found with ID: {individual_id}', 'error')
                else:
                    send_notification(
                        sender_id=current_user.id, sender_role='admin',
                        recipient_type='individual',
                        recipient_id=recip_id, recipient_role=recip_role,
                        title=title, message=message
                    )
                    flash(f'Notification sent to {individual_role} {individual_id}.', 'success')
            else:
                # Broadcast: all / students / faculty
                send_notification(
                    sender_id=current_user.id, sender_role='admin',
                    recipient_type=recipient_type,
                    title=title, message=message
                )
                flash('Notification sent.', 'success')

    # Admin sees: broadcasts + individual-to-admin messages
    all_notifications = Notification.query.filter(
        db.or_(
            Notification.recipient_type == 'all',
            Notification.recipient_type == 'students',
            Notification.recipient_type == 'faculty',
            db.and_(
                Notification.recipient_type == 'individual',
                Notification.recipient_role == 'admin',
                Notification.recipient_id == current_user.id,
            ),
            db.and_(Notification.recipient_type == 'admin'),
        )
    ).order_by(Notification.created_at.desc()).limit(100).all()

    all_students = Student.query.filter_by(is_active=True).order_by(Student.name).all()
    all_faculty  = Faculty.query.filter_by(is_active=True).order_by(Faculty.name).all()

    return render_template('admin/notifications.html',
                           notifications=all_notifications,
                           all_students=all_students,
                           all_faculty=all_faculty)


# ─── ACTIVITY LOGS ────────────────────────────────────────────
@admin_bp.route('/logs')
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.logged_at.desc()).paginate(page=page, per_page=30)
    return render_template('admin/activity_logs.html', logs=logs)


# ─── ADMIN PROFILE ────────────────────────────────────────────
@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if name:
            current_user.name = name

        # Profile image upload
        profile_image = request.files.get('profile_image')
        if profile_image and profile_image.filename:
            current_user.profile_image = save_file(profile_image, 'uploads/profiles')

        # Password change (optional)
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        if new_password:
            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('admin/profile.html')
            valid, msg = validate_password(new_password)
            if not valid:
                flash(msg, 'error')
                return render_template('admin/profile.html')
            current_user.set_password(new_password)

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('admin.profile'))

    return render_template('admin/profile.html')
