"""
LMS Utility Functions
"""
import os
import uuid
import string
import random
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, flash, request, current_app
from flask_login import current_user
from werkzeug.utils import secure_filename
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER


def generate_student_id():
    """Generate unique student ID: LMS/S/YY/NN"""
    from models.models import Student
    year = datetime.now().strftime('%y')
    count = Student.query.count() + 1
    return f"LMS/S/{year}/{count:02d}"


def generate_faculty_id():
    """Generate unique faculty ID: LMS/F/YY/NN"""
    from models.models import Faculty
    year = datetime.now().strftime('%y')
    count = Faculty.query.count() + 1
    return f"LMS/F/{year}/{count:02d}"


def generate_certificate_id():
    """Generate unique certificate ID"""
    return f"CERT-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"


def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    allowed = {
        'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
        'video': {'mp4', 'avi', 'mov', 'mkv', 'webm'},
        'pdf': {'pdf'},
    }
    return ext in allowed.get(file_type, set())


def save_file(file, subfolder='uploads'):
    """Save uploaded file and return filename"""
    if file and file.filename:
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        upload_path = os.path.join(current_app.root_path, 'static', subfolder)
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, unique_name))
        return unique_name
    return None


def log_activity(user_id, user_role, action, details=None):
    """Log user activity"""
    from models.models import ActivityLog, db
    log = ActivityLog(
        user_id=user_id,
        user_role=user_role,
        action=action,
        details=details,
        ip_address=request.remote_addr if request else None
    )
    db.session.add(log)
    db.session.commit()


def generate_certificate_pdf(student_name, course_name, certificate_id, issued_date,
                             output_path, faculty_name=None, cert_type='Course'):
    """
    Generate a premium PDF certificate.
    - Course certificates: full decorative design with QR code + faculty signature
    - Exam certificates: clean professional design
    """
    if cert_type == 'Course':
        return _generate_course_certificate(
            student_name, course_name, certificate_id,
            issued_date, output_path, faculty_name
        )
    else:
        return _generate_exam_certificate(
            student_name, course_name, certificate_id, issued_date, output_path
        )


def _generate_qr_code(cert_id, size=80):
    """Generate a QR code image for certificate verification."""
    import qrcode
    import io as _io
    verify_url = f"https://eduflow-lms-7ew2.onrender.com/verify/{cert_id}"
    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = _io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    from reportlab.lib.utils import ImageReader
    return ImageReader(buf)


def _generate_course_certificate(student_name, course_name, certificate_id,
                                  issued_date, output_path, faculty_name=None):
    """Premium course completion certificate with decorative border and QR code."""
    from reportlab.pdfgen import canvas as _canvas
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch, mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    W, H = landscape(letter)
    c = _canvas.Canvas(output_path, pagesize=landscape(letter))

    # ── Background gradient simulation (light cream) ──────────────────
    c.setFillColor(colors.HexColor('#FDFAF4'))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── Decorative outer border ───────────────────────────────────────
    margin = 18
    # Gold outer border
    c.setStrokeColor(colors.HexColor('#C9A84C'))
    c.setLineWidth(4)
    c.rect(margin, margin, W - 2*margin, H - 2*margin, fill=0, stroke=1)
    # Thin inner border
    c.setStrokeColor(colors.HexColor('#E8D08A'))
    c.setLineWidth(1.2)
    c.rect(margin+6, margin+6, W - 2*(margin+6), H - 2*(margin+6), fill=0, stroke=1)

    # ── Corner ornaments ──────────────────────────────────────────────
    def corner_ornament(cx, cy):
        c.setFillColor(colors.HexColor('#C9A84C'))
        c.setStrokeColor(colors.HexColor('#C9A84C'))
        c.setLineWidth(1)
        # Small diamond
        path = c.beginPath()
        path.moveTo(cx, cy+8)
        path.lineTo(cx+8, cy)
        path.lineTo(cx, cy-8)
        path.lineTo(cx-8, cy)
        path.close()
        c.drawPath(path, fill=1, stroke=0)

    for ox, oy in [(margin+16, margin+16), (W-margin-16, margin+16),
                   (margin+16, H-margin-16), (W-margin-16, H-margin-16)]:
        corner_ornament(ox, oy)

    # ── Top accent bar ────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#1B3A6B'))
    c.rect(margin+12, H-margin-55, W-2*(margin+12), 40, fill=1, stroke=0)

    # ── Institution name in top bar ───────────────────────────────────
    c.setFillColor(colors.white)
    c.setFont('Helvetica-Bold', 13)
    c.drawCentredString(W/2, H-margin-37, 'EduFlow Learning Management System')

    # ── Certificate of Completion title ──────────────────────────────
    c.setFillColor(colors.HexColor('#C9A84C'))
    c.setFont('Helvetica-Bold', 30)
    c.drawCentredString(W/2, H - margin - 100, 'Certificate of Completion')

    # ── Decorative line under title ───────────────────────────────────
    line_y = H - margin - 110
    c.setStrokeColor(colors.HexColor('#C9A84C'))
    c.setLineWidth(1.5)
    c.line(W/2 - 120, line_y, W/2 + 120, line_y)

    # ── "This is to certify that" ─────────────────────────────────────
    c.setFillColor(colors.HexColor('#555555'))
    c.setFont('Helvetica', 12)
    c.drawCentredString(W/2, H - margin - 140, 'This is to proudly certify that')

    # ── Student name ──────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#1B3A6B'))
    c.setFont('Helvetica-Bold', 34)
    c.drawCentredString(W/2, H - margin - 180, student_name)

    # ── Underline for name ────────────────────────────────────────────
    name_w = c.stringWidth(student_name, 'Helvetica-Bold', 34)
    c.setStrokeColor(colors.HexColor('#1B3A6B'))
    c.setLineWidth(1)
    c.line(W/2 - name_w/2, H-margin-186, W/2 + name_w/2, H-margin-186)

    # ── "has successfully completed" ─────────────────────────────────
    c.setFillColor(colors.HexColor('#555555'))
    c.setFont('Helvetica', 12)
    c.drawCentredString(W/2, H - margin - 212, 'has successfully completed the course')

    # ── Course name ───────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#C9A84C'))
    c.setFont('Helvetica-Bold', 20)
    # Truncate if too long
    course_display = course_name if len(course_name) <= 55 else course_name[:52] + '...'
    c.drawCentredString(W/2, H - margin - 245, f'"{course_display}"')

    # ── Date issued ───────────────────────────────────────────────────
    c.setFillColor(colors.HexColor('#666666'))
    c.setFont('Helvetica', 11)
    c.drawCentredString(W/2, H - margin - 278,
                        f'Issued on {issued_date.strftime("%B %d, %Y")}')

    # ── Bottom section: signatures + QR ──────────────────────────────
    bottom_y = margin + 55

    # Faculty signature (left)
    sig_lx = margin + 60
    c.setStrokeColor(colors.HexColor('#333333'))
    c.setLineWidth(0.8)
    c.line(sig_lx, bottom_y + 22, sig_lx + 110, bottom_y + 22)
    c.setFillColor(colors.HexColor('#333333'))
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(sig_lx + 55, bottom_y + 12,
                        faculty_name[:20] if faculty_name else 'Faculty')
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(sig_lx + 55, bottom_y + 2, 'Course Instructor')

    # Admin / Director signature (centre)
    sig_cx = W/2
    c.setStrokeColor(colors.HexColor('#333333'))
    c.setLineWidth(0.8)
    c.line(sig_cx - 55, bottom_y + 22, sig_cx + 55, bottom_y + 22)
    c.setFillColor(colors.HexColor('#333333'))
    c.setFont('Helvetica-Bold', 9)
    c.drawCentredString(sig_cx, bottom_y + 12, 'EduFlow Administration')
    c.setFont('Helvetica', 8)
    c.setFillColor(colors.HexColor('#888888'))
    c.drawCentredString(sig_cx, bottom_y + 2, 'Authorized Signatory')

    # QR code (right)
    try:
        qr_img = _generate_qr_code(certificate_id, size=70)
        qr_x = W - margin - 85
        qr_y = bottom_y - 2
        c.drawImage(qr_img, qr_x, qr_y, width=70, height=70)
        c.setFont('Helvetica', 7)
        c.setFillColor(colors.HexColor('#888888'))
        c.drawCentredString(qr_x + 35, qr_y - 8, 'Scan to verify')
    except Exception:
        pass  # QR optional

    # ── Certificate ID (bottom centre) ───────────────────────────────
    c.setFillColor(colors.HexColor('#AAAAAA'))
    c.setFont('Helvetica', 8)
    c.drawCentredString(W/2, margin + 20, f'Certificate ID: {certificate_id}')

    # ── EduFlow watermark (very subtle) ──────────────────────────────
    c.saveState()
    c.setFillColor(colors.HexColor('#F0EBD8'))
    c.setFont('Helvetica-Bold', 72)
    c.translate(W/2, H/2)
    c.rotate(30)
    c.drawCentredString(0, 0, 'EduFlow')
    c.restoreState()

    c.save()
    return output_path


def _generate_exam_certificate(student_name, course_name, certificate_id,
                                issued_date, output_path):
    """Clean professional exam pass certificate."""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(letter),
        rightMargin=0.5*inch,
        leftMargin=0.5*inch,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    styles = getSampleStyleSheet()
    elements = []

    ts = ParagraphStyle('T', parent=styles['Normal'], fontSize=32, fontName='Helvetica-Bold',
                        textColor=colors.HexColor('#1e3a5f'), alignment=TA_CENTER, spaceAfter=16)
    ss = ParagraphStyle('S', parent=styles['Normal'], fontSize=14, fontName='Helvetica',
                        textColor=colors.HexColor('#555'), alignment=TA_CENTER, spaceAfter=8)
    ns = ParagraphStyle('N', parent=styles['Normal'], fontSize=26, fontName='Helvetica-Bold',
                        textColor=colors.HexColor('#c0392b'), alignment=TA_CENTER, spaceAfter=12)
    cs = ParagraphStyle('C', parent=styles['Normal'], fontSize=18, fontName='Helvetica-Bold',
                        textColor=colors.HexColor('#1e3a5f'), alignment=TA_CENTER, spaceAfter=16)
    xs = ParagraphStyle('X', parent=styles['Normal'], fontSize=9, fontName='Helvetica',
                        textColor=colors.HexColor('#999'), alignment=TA_CENTER, spaceAfter=4)

    elements += [
        Spacer(1, 0.4*inch),
        Paragraph('Certificate of Achievement', ts),
        Spacer(1, 0.1*inch),
        Paragraph('This certifies that', ss),
        Paragraph(student_name, ns),
        Paragraph('has passed the examination in', ss),
        Paragraph(course_name, cs),
        Paragraph(f'Date: {issued_date.strftime("%B %d, %Y")}', ss),
        Spacer(1, 0.35*inch),
        Paragraph('_______________________', ss),
        Paragraph('EduFlow Administration', xs),
        Spacer(1, 0.15*inch),
        Paragraph(f'Certificate ID: {certificate_id}', xs),
    ]
    doc.build(elements)
    return output_path


def admin_required(f):
    """Decorator: require admin login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_role() != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated


def faculty_required(f):
    """Decorator: require faculty login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_role() != 'faculty':
            flash('Faculty access required.', 'error')
            return redirect(url_for('auth.faculty_login'))
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    """Decorator: require student login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.get_role() != 'student':
            flash('Student access required.', 'error')
            return redirect(url_for('auth.student_login'))
        return f(*args, **kwargs)
    return decorated


def generate_captcha_text(key='captcha_answer'):
    """Generate simple math CAPTCHA and store answer in session under `key`."""
    a = random.randint(1, 20)
    b = random.randint(1, 20)
    session[key] = str(a + b)
    session.modified = True
    return f"{a} + {b} = ?"


def verify_captcha(answer, key='captcha_answer'):
    """Verify CAPTCHA answer against session key, then clear it."""
    expected = session.pop(key, None)
    session.modified = True
    if not expected:
        return False
    return answer.strip() == expected


def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c in string.punctuation for c in password):
        return False, "Password must contain at least one special character."
    return True, "Strong password."


def get_attendance_percentage(student_id, course_id):
    """Calculate attendance percentage for a student in a course"""
    from models.models import Attendance
    total = Attendance.query.filter_by(student_id=student_id, course_id=course_id).count()
    present = Attendance.query.filter_by(
        student_id=student_id, course_id=course_id, status='Present'
    ).count()
    return round((present / total * 100), 1) if total > 0 else 0
