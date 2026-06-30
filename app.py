"""
LMS - Learning Management System
Main Application Entry Point
"""
import os
from flask import Flask, redirect, url_for, session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config.config import config
from models.models import db, Admin, Student, Faculty

# Extensions
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app(config_name='default'):
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Make every session permanent so the session cookie persists across POST
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # Login manager settings
    login_manager.login_view = 'auth.student_login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # User loader — handles admin_, faculty_, student_ prefixed IDs
    @login_manager.user_loader
    def load_user(user_id):
        if user_id.startswith('admin_'):
            return Admin.query.get(int(user_id.split('_')[1]))
        elif user_id.startswith('faculty_'):
            return Faculty.query.get(int(user_id.split('_')[1]))
        elif user_id.startswith('student_'):
            return Student.query.get(int(user_id.split('_')[1]))
        return None

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.faculty import faculty_bp
    from routes.student import student_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(faculty_bp, url_prefix='/faculty')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Root redirect
    @app.route('/')
    def index():
        return redirect(url_for('auth.select_login'))

    # Certificate public verification
    @app.route('/verify/<cert_id>')
    def verify_certificate(cert_id):
        from models.models import Certificate
        from flask import render_template
        cert = Certificate.query.filter_by(certificate_id=cert_id).first()
        if cert:
            return render_template('shared/verify_certificate.html', cert=cert,
                                   student=cert.student, course=cert.course)
        return render_template('shared/verify_certificate.html', cert=None), 404

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('shared/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('shared/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('shared/500.html'), 500

    # Create upload directories & init DB
    with app.app_context():
        for sub in ('profiles', 'thumbnails', 'videos', 'pdfs', 'certificates'):
            os.makedirs(os.path.join(app.root_path, 'static', 'uploads', sub), exist_ok=True)

        # Auto-create tables (safe on Render — runs every deploy)
        db.create_all()

        # Seed default admin if the table is empty
        from models.models import Admin as _Admin
        if not _Admin.query.first():
            _a = _Admin(name='Super Admin', email='admin@lms.com')
            _a.set_password('Admin@123')
            db.session.add(_a)
            db.session.commit()

    return app


app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # use_reloader=False is REQUIRED on Clever Cloud's free DEV plan.
    # The auto-reloader spawns a second process with its own DB
    # connection pool, which can push you over the 5-connection cap
    # even with a small pool_size. Restart manually after code changes.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)