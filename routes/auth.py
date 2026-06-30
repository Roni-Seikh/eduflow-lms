"""
Authentication Blueprint — Login, Register, Logout
Root cause fix: generate_captcha_text() is ONLY called on GET requests.
On POST, verify_captcha() reads the existing session value set during the GET.
Each route uses its own session key so pages don't overwrite each other.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.models import db, Admin, Student, Faculty
from utils.helpers import (
    generate_student_id, log_activity, generate_captcha_text,
    verify_captcha, validate_password
)
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/select')
def select_login():
    return render_template('auth/select_login.html')


# ─── ADMIN LOGIN ─────────────────────────────────────────────
@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.get_role() == 'admin':
        return redirect(url_for('admin.dashboard'))

    KEY = 'captcha_admin'

    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        captcha  = request.form.get('captcha', '')

        if not verify_captcha(captcha, key=KEY):
            flash('Incorrect CAPTCHA answer. Please try again.', 'error')
            # Generate a fresh question for the re-displayed form
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/admin_login.html', captcha=new_q)

        admin = Admin.query.filter_by(email=email).first()
        if admin and admin.check_password(password) and admin.is_active:
            login_user(admin, remember=False)
            admin.last_login = datetime.utcnow()
            db.session.commit()
            log_activity(admin.id, 'admin', 'Login',
                         f'Admin logged in from {request.remote_addr}')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/admin_login.html', captcha=new_q)

    # GET — generate fresh CAPTCHA
    captcha_question = generate_captcha_text(key=KEY)
    return render_template('auth/admin_login.html', captcha=captcha_question)


# ─── FACULTY LOGIN ────────────────────────────────────────────
@auth_bp.route('/faculty/login', methods=['GET', 'POST'])
def faculty_login():
    if current_user.is_authenticated and current_user.get_role() == 'faculty':
        return redirect(url_for('faculty.dashboard'))

    KEY = 'captcha_faculty'

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '')
        captcha    = request.form.get('captcha', '')

        if not verify_captcha(captcha, key=KEY):
            flash('Incorrect CAPTCHA answer. Please try again.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/faculty_login.html', captcha=new_q)

        faculty = Faculty.query.filter(
            (Faculty.email == identifier) | (Faculty.faculty_id == identifier)
        ).first()

        if faculty and faculty.check_password(password) and faculty.is_active:
            login_user(faculty, remember=False)
            faculty.last_login = datetime.utcnow()
            db.session.commit()
            log_activity(faculty.id, 'faculty', 'Login')
            return redirect(url_for('faculty.dashboard'))
        else:
            flash('Invalid credentials or account inactive.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/faculty_login.html', captcha=new_q)

    captcha_question = generate_captcha_text(key=KEY)
    return render_template('auth/faculty_login.html', captcha=captcha_question)


# ─── STUDENT LOGIN ────────────────────────────────────────────
@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if current_user.is_authenticated and current_user.get_role() == 'student':
        return redirect(url_for('student.dashboard'))

    KEY = 'captcha_student'

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '')
        captcha    = request.form.get('captcha', '')

        if not verify_captcha(captcha, key=KEY):
            flash('Incorrect CAPTCHA answer. Please try again.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/student_login.html', captcha=new_q)

        student = Student.query.filter(
            (Student.email == identifier) | (Student.student_id == identifier)
        ).first()

        if student and student.check_password(password) and student.is_active:
            login_user(student, remember=False)
            student.last_login = datetime.utcnow()
            db.session.commit()
            log_activity(student.id, 'student', 'Login')
            return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid credentials or account inactive.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/student_login.html', captcha=new_q)

    captcha_question = generate_captcha_text(key=KEY)
    return render_template('auth/student_login.html', captcha=captcha_question)


# ─── STUDENT REGISTER ─────────────────────────────────────────
@auth_bp.route('/student/register', methods=['GET', 'POST'])
def student_register():
    KEY = 'captcha_register'

    if request.method == 'POST':
        name             = request.form.get('name', '').strip()
        email            = request.form.get('email', '').strip()
        phone            = request.form.get('phone', '').strip()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        captcha          = request.form.get('captcha', '')

        if not verify_captcha(captcha, key=KEY):
            flash('Incorrect CAPTCHA answer. Please try again.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/student_register.html', captcha=new_q)

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/student_register.html', captcha=new_q)

        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/student_register.html', captcha=new_q)

        if Student.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            new_q = generate_captcha_text(key=KEY)
            return render_template('auth/student_register.html', captcha=new_q)

        student = Student(
            student_id=generate_student_id(),
            name=name,
            email=email,
            phone=phone
        )
        student.set_password(password)
        db.session.add(student)
        db.session.commit()

        flash(
            f'Registration successful! Your Student ID is {student.student_id}. Please login.',
            'success'
        )
        return redirect(url_for('auth.student_login'))

    captcha_question = generate_captcha_text(key=KEY)
    return render_template('auth/student_register.html', captcha=captcha_question)


# ─── FORGOT PASSWORD REQUEST ──────────────────────────────────
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email        = request.form.get('email', '').strip()
        role         = request.form.get('role', '')
        message_text = request.form.get('message', '')

        from models.models import PasswordRequest

        if role == 'student':
            user = Student.query.filter_by(email=email).first()
        elif role == 'faculty':
            user = Faculty.query.filter_by(email=email).first()
        else:
            user = None

        if user:
            pr = PasswordRequest(
                user_id=user.id,
                user_role=role,
                email=email,
                message=message_text
            )
            db.session.add(pr)
            db.session.commit()
            flash('Password reset request submitted. Admin will contact you soon.', 'success')
        else:
            flash('No account found with that email.', 'error')

    return render_template('auth/forgot_password.html')


# ─── LOGOUT ───────────────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    role = current_user.get_role() if current_user.is_authenticated else 'student'
    log_activity(current_user.id, role, 'Logout')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.select_login'))
