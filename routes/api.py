"""
API Blueprint — JSON endpoints for AJAX/JS
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models.models import db, Notification, ExamResult, Attendance, Course, Enrollment

api_bp = Blueprint('api', __name__)


@api_bp.route('/notifications/count')
@login_required
def notification_count():
    role = current_user.get_role()
    recipient_types = ['all', role + 's' if role != 'admin' else 'all']
    count = Notification.query.filter(
        Notification.recipient_type.in_(recipient_types),
        Notification.is_read == False
    ).count()
    return jsonify({'count': count})


@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    if current_user.get_role() == 'admin':
        from models.models import Student, Faculty, Exam
        return jsonify({
            'students': Student.query.filter_by(is_active=True).count(),
            'faculty': Faculty.query.filter_by(is_active=True).count(),
            'courses': Course.query.filter_by(is_active=True).count(),
            'exams': Exam.query.filter_by(is_active=True).count(),
        })
    return jsonify({})


@api_bp.route('/attendance/chart/<int:course_id>')
@login_required
def attendance_chart(course_id):
    from models.models import Attendance
    records = Attendance.query.filter_by(course_id=course_id).all()
    present = sum(1 for r in records if r.status == 'Present')
    absent = sum(1 for r in records if r.status == 'Absent')
    late = sum(1 for r in records if r.status == 'Late')
    return jsonify({'present': present, 'absent': absent, 'late': late})
