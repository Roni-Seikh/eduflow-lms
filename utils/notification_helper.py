"""
notification_helper.py
Centralised notification logic for EduFlow LMS.

Notification visibility rules:
  sender_role  | recipient_type   | recipient_role | recipient_id | Visible to
  -------------|------------------|----------------|--------------|---------------------------
  admin        | all              | NULL           | NULL         | ALL users (admin+faculty+student)
  admin        | students         | NULL           | NULL         | ALL students
  admin        | faculty          | NULL           | NULL         | ALL faculty
  admin        | individual       | student        | <student.id> | Only that student
  admin        | individual       | faculty        | <faculty.id> | Only that faculty
  faculty      | admin            | admin          | <admin.id>   | Only admin
  faculty      | students         | NULL           | NULL         | ALL students
  faculty      | individual       | student        | <student.id> | Only that student
  student      | admin            | admin          | <admin.id>   | Only admin
  student      | individual       | faculty        | <faculty.id> | Only that faculty
"""

from models.models import db, Notification, Student, Faculty, Admin


def send_notification(sender_id, sender_role, recipient_type, title, message,
                      recipient_id=None, recipient_role=None):
    """
    Create and persist one notification.
    Always sets recipient_role so individual notifications are never ambiguous.
    """
    notif = Notification(
        sender_id=sender_id,
        sender_role=sender_role,
        recipient_type=recipient_type,
        recipient_id=recipient_id,
        recipient_role=recipient_role,
        title=title,
        message=message,
    )
    db.session.add(notif)
    db.session.commit()
    return notif


# ── Query helpers ──────────────────────────────────────────────────────────

def get_notifications_for_admin(admin_id, limit=None):
    """Admin sees: all-user broadcasts + individual notifications sent TO admin."""
    q = Notification.query.filter(
        db.or_(
            Notification.recipient_type == 'all',
            db.and_(
                Notification.recipient_type == 'individual',
                Notification.recipient_role == 'admin',
                Notification.recipient_id == admin_id,
            ),
            # Also show faculty→admin and student→admin messages
            db.and_(
                Notification.recipient_type == 'admin',
            ),
        )
    ).order_by(Notification.created_at.desc())
    return q.limit(limit).all() if limit else q.all()


def get_notifications_for_faculty(faculty_id, limit=None):
    """
    Faculty sees:
      - admin broadcast to 'all'
      - admin broadcast to 'faculty'
      - individual addressed to THIS faculty (recipient_role='faculty' AND recipient_id=faculty_id)
      - student→admin messages are NOT shown here
    """
    candidates = Notification.query.filter(
        db.or_(
            Notification.recipient_type == 'all',
            Notification.recipient_type == 'faculty',
            db.and_(
                Notification.recipient_type == 'individual',
                Notification.recipient_role == 'faculty',
                Notification.recipient_id == faculty_id,
            ),
        )
    ).order_by(Notification.created_at.desc()).all()
    return candidates[:limit] if limit else candidates


def get_notifications_for_student(student_id, limit=None):
    """
    Student sees:
      - admin broadcast to 'all'
      - admin broadcast to 'students'
      - faculty broadcast to 'students'
      - individual addressed to THIS student (recipient_role='student' AND recipient_id=student_id)
      - faculty→individual THIS student (same condition)
    Never sees: faculty-to-admin, student-to-admin, student-to-faculty, other-student individual
    """
    candidates = Notification.query.filter(
        db.or_(
            Notification.recipient_type == 'all',
            Notification.recipient_type == 'students',
            db.and_(
                Notification.recipient_type == 'individual',
                Notification.recipient_role == 'student',
                Notification.recipient_id == student_id,
            ),
        )
    ).order_by(Notification.created_at.desc()).all()
    return candidates[:limit] if limit else candidates
